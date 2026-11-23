#!/usr/bin/env python3
"""Read-only Arc Testnet vs Sepolia observation for the M1 compatibility report.

Collects public JSON-RPC facts for:
  * Arc Testnet: the M1 MotionGateAnchorV0 contract and transactions (m1_expected.json);
  * Sepolia: a historical MotionGateAnchorV0-style FAST anchor recorded by FidoMota on
    2026-10-13 (identifiers in sepolia_reference.json), used only as a comparison point.

It prints observations; it does not judge M1 (m1_public_verifier.py does that).
Python 3 standard library only; read methods only; no key, no signing, no sending.

Usage: python3 -I arc_sepolia_observe.py [--out-json FILE] [--arc-rpc URL ...] [--sepolia-rpc URL ...]
"""
import argparse, hashlib, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m1_public_verifier import Source, RpcError, keccak256, DEFAULT_RPCS  # noqa: E402

ALLOWED = {"eth_chainId", "eth_getCode", "eth_getTransactionByHash", "eth_getTransactionReceipt",
           "eth_getBlockByNumber", "eth_getBalance", "eth_gasPrice", "eth_maxPriorityFeePerGas",
           "net_version", "web3_clientVersion"}
# Sepolia public endpoints named in FidoMota records as no-key second sources (2026-11-19/20).
DEFAULT_SEPOLIA = ["https://sepolia.gateway.tenderly.co", "https://sepolia.drpc.org"]


def I(x):
    return int(x, 16) if isinstance(x, str) and x.startswith("0x") else x


def try_call(src, method, params):
    try:
        return {"ok": True, "result": src.call(method, params)}
    except RpcError as e:
        return {"ok": False, "error": str(e)}


def chain_common(src):
    o = {"rpc": src.url}
    for m in ("eth_chainId", "net_version", "web3_clientVersion", "eth_gasPrice", "eth_maxPriorityFeePerGas"):
        r = try_call(src, m, [])
        o[m] = I(r["result"]) if r["ok"] and m in ("eth_chainId", "eth_gasPrice", "eth_maxPriorityFeePerGas") else (r.get("result") if r["ok"] else {"error": r["error"]})
    for tag in ("latest", "safe", "finalized"):
        r = try_call(src, "eth_getBlockByNumber", [tag, False])
        if r["ok"] and r["result"]:
            b = r["result"]
            o["block_" + tag] = {"number": I(b["number"]), "timestamp": I(b["timestamp"]), "hash": b["hash"],
                                 "baseFeePerGas": I(b.get("baseFeePerGas")), "gasLimit": I(b.get("gasLimit"))}
        else:
            o["block_" + tag] = {"error": r.get("error") or "null"}
    return o


def tx_view(src, h):
    t = try_call(src, "eth_getTransactionByHash", [h])
    r = try_call(src, "eth_getTransactionReceipt", [h])
    out = {"tx_hash": h, "tx_lookup": "ok" if (t["ok"] and t["result"]) else (t.get("error") or "null"),
           "receipt_lookup": "ok" if (r["ok"] and r["result"]) else (r.get("error") or "null")}
    tx, rc = (t.get("result") or {}), (r.get("result") or {})
    bn = rc.get("blockNumber") or tx.get("blockNumber")
    blk = (try_call(src, "eth_getBlockByNumber", [bn, False]).get("result") or {}) if bn else {}
    if tx:
        out.update({"type": I(tx.get("type")), "from": tx.get("from"), "to": tx.get("to"), "nonce": I(tx.get("nonce")),
                    "gas_limit": I(tx.get("gas")), "maxFeePerGas": I(tx.get("maxFeePerGas")),
                    "maxPriorityFeePerGas": I(tx.get("maxPriorityFeePerGas")), "gasPrice": I(tx.get("gasPrice")),
                    "input_selector": (tx.get("input") or "")[:10], "input_bytes": (len(tx.get("input") or "0x") - 2) // 2})
    if rc:
        gu, eg = I(rc.get("gasUsed")), I(rc.get("effectiveGasPrice"))
        logs = rc.get("logs") or []
        out.update({"status": rc.get("status"), "block_number": I(rc.get("blockNumber")), "gas_used": gu,
                    "effective_gas_price": eg, "fee_wei": gu * eg if gu is not None and eg is not None else None,
                    "contract_address": rc.get("contractAddress"),
                    "logs": [{"address": lg.get("address"), "topics": lg.get("topics"), "data": lg.get("data"),
                              "logIndex": I(lg.get("logIndex")), "has_blockTimestamp": "blockTimestamp" in lg,
                              "removed": lg.get("removed")} for lg in logs],
                    "receipt_fields": sorted(rc.keys())})
    if blk:
        out["block"] = {"number": I(blk.get("number")), "hash": blk.get("hash"), "timestamp": I(blk.get("timestamp")),
                        "baseFeePerGas": I(blk.get("baseFeePerGas"))}
    return out


def code_view(src, addr):
    r = try_call(src, "eth_getCode", [addr, "latest"])
    if not r["ok"]:
        return {"error": r["error"]}
    c = bytes.fromhex((r["result"] or "0x")[2:])
    return {"address": addr, "bytes": len(c), "sha256": hashlib.sha256(c).hexdigest(),
            "keccak256": "0x" + keccak256(c).hex(), "contains_selector_a21f3c6a": bytes.fromhex("a21f3c6a") in c,
            "runtime_without_cbor_metadata_sha256": hashlib.sha256(strip_metadata(c)).hexdigest() if c else None}


def strip_metadata(c):
    # Solidity appends CBOR metadata; its length is the last 2 bytes (big endian).
    if len(c) < 2:
        return c
    n = int.from_bytes(c[-2:], "big")
    return c[:-(n + 2)] if n + 2 <= len(c) else c


def balance_delta(src, who, before_block, after_block):
    a = try_call(src, "eth_getBalance", [who, hex(before_block)])
    b = try_call(src, "eth_getBalance", [who, hex(after_block)])
    if not (a["ok"] and b["ok"]):
        return {"error": (a.get("error") or "") + " | " + (b.get("error") or "")}
    return {"block_before": before_block, "block_after": after_block, "balance_before_wei": I(a["result"]),
            "balance_after_wei": I(b["result"]), "delta_wei": I(a["result"]) - I(b["result"])}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected", default=os.path.join(here, "..", "expected", "m1_expected.json"))
    ap.add_argument("--sepolia-ref", default=os.path.join(here, "..", "expected", "sepolia_reference.json"))
    ap.add_argument("--arc-rpc", action="append")
    ap.add_argument("--sepolia-rpc", action="append")
    ap.add_argument("--out-json")
    a = ap.parse_args()
    exp = json.load(open(a.expected))
    ref = json.load(open(a.sepolia_ref))
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    topic0 = "0x" + keccak256(exp["contract"]["event_signature"].encode()).hex()
    doc = {"schema": "FIDOMOTA-ARC-SEPOLIA-OBSERVATION-V1", "started_utc": t0, "anchored_topic0": topic0,
           "arc": [], "sepolia": []}
    for url in a.arc_rpc or DEFAULT_RPCS:
        s = Source(url, allowed=ALLOWED)
        o = chain_common(s)
        o["m1_contract_code"] = code_view(s, exp["contract"]["address"])
        o["m1_txs"] = {t["tx_id"]: tx_view(s, t["tx_hash"]) for t in exp["transactions"]}
        bns = [t["receipt"]["block_number"] for t in exp["transactions"]]
        o["signer_balance_delta_over_m1"] = balance_delta(s, exp["contract"]["deployer"], min(bns) - 1, max(bns))
        o["rpc_calls"] = len(s.log)
        doc["arc"].append(o)
    for url in a.sepolia_rpc or DEFAULT_SEPOLIA:
        s = Source(url, allowed=ALLOWED)
        o = chain_common(s)
        o["reference_contract_code"] = code_view(s, ref["contract"])
        o["reference_tx"] = tx_view(s, ref["tx_hash"])
        o["rpc_calls"] = len(s.log)
        doc["sepolia"].append(o)
    doc["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(json.dumps(doc, indent=1))
    if a.out_json:
        with open(a.out_json, "x") as f:
            json.dump(doc, f, indent=1); f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
