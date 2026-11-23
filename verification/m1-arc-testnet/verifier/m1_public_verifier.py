#!/usr/bin/env python3
"""FidoMota Circle Arc Grant M1 - standalone public read-only verifier.

Re-derives, from Arc Testnet public JSON-RPC data only, that the four M1
transactions (1 MotionGateAnchorV0 deployment + 3 SYNTHETIC anchors) exist
and match the expected values in m1_expected.json byte for byte.

* Python 3.8+ standard library only. No wallet, no key, no signing, no
  eth_sendRawTransaction: every RPC method used is a read (see READ_METHODS).
* Keccak-256 is implemented below and self-tested against published vectors
  at import time.
* The original M1 run verdicts are NOT inputs. Expected values come from the
  transaction records of the approved M1 execution bundle (see provenance in
  m1_expected.json); every pass/fail is computed here from fresh RPC data.

Usage:
  python3 -I m1_public_verifier.py verify   [--expected FILE] [--rpc URL ...] [--out-json FILE] [--save-responses FILE]
  python3 -I m1_public_verifier.py negative [--expected FILE] [--rpc URL ...]   # negative controls
  python3 -I m1_public_verifier.py selftest                                    # offline: keccak/RLP vectors

Verdicts / exit codes:
  0 VERIFIED                 every assertion passes on every source contacted, sources agree
  4 VERIFIED_SINGLE_SOURCE   every assertion passes on exactly one source; the other source(s)
                             could not serve some data (UNAVAILABLE) and nothing they did serve
                             disagrees (reduced assurance: stated, never upgraded)
  1 FAIL                     an assertion failed on some source, or sources disagree
  2 INCOMPLETE               no source could serve every datum; nothing failed
  3                          usage or input error
Index-gap rule: a null eth_getTransactionByHash / eth_getTransactionReceipt answer is
UNAVAILABLE (not FAIL) only if the same source's block at the expected height lists the tx
hash; the tx object is then read from that block body. Any other null is a FAIL.
"""
import argparse, gzip, hashlib, json, os, sys, time, urllib.error, urllib.request

# Public Arc Testnet endpoints, as fixed by the approved M1 verifier sources
# record (two independent operators). Override with --rpc.
DEFAULT_RPCS = ["https://rpc.testnet.arc.io", "https://rpc.blockdaemon.testnet.arc.io"]
READ_METHODS = {"eth_chainId", "eth_getCode", "eth_getTransactionByHash", "eth_getTransactionReceipt",
                "eth_getBlockByNumber", "eth_getLogs"}
USER_AGENT = "fidomota-m1-public-verifier/1"

# ---------------------------------------------------------------- keccak-256
_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
       0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
       0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
       0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
       0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
_M = (1 << 64) - 1


def _rol(v, n):
    return ((v << n) | (v >> (64 - n))) & _M if n else v


def _f(A):
    for rc in _RC:
        C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
        D = [C[(x - 1) % 5] ^ _rol(C[(x + 1) % 5], 1) for x in range(5)]
        A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]
        B = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2 * x + 3 * y) % 5] = _rol(A[x][y], _ROT[x][y])
        A = [[B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
        A[0][0] ^= rc
    return A


def keccak256(data: bytes) -> bytes:
    rate = 136
    msg = bytearray(data) + b"\x01"
    msg += b"\x00" * ((-len(msg)) % rate)
    msg[-1] |= 0x80
    A = [[0] * 5 for _ in range(5)]
    for off in range(0, len(msg), rate):
        blk = msg[off:off + rate]
        for i in range(rate // 8):
            A[i % 5][i // 5] ^= int.from_bytes(blk[8 * i:8 * i + 8], "little")
        A = _f(A)
    return b"".join(A[i % 5][i // 5].to_bytes(8, "little") for i in range(4))


_VECTORS = [(b"", "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"),
            (b"abc", "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"),
            (b"Transfer(address,address,uint256)", "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"),
            (b"a" * 200, None)]  # multi-block input: only checked for determinism/length
for _m, _h in _VECTORS:
    _d = keccak256(_m).hex()
    if (_h and _d != _h) or len(_d) != 64:
        raise SystemExit(f"KECCAK_SELFTEST_FAILED {_m[:20]!r}")


def create_address(sender_hex: str, nonce: int) -> str:
    """CREATE address = keccak256(rlp([sender, nonce]))[12:]."""
    s = bytes.fromhex(sender_hex[2:])
    assert len(s) == 20
    if nonce == 0:
        n = b"\x80"
    elif nonce < 0x80:
        n = bytes([nonce])
    else:
        nb = nonce.to_bytes((nonce.bit_length() + 7) // 8, "big")
        n = bytes([0x80 + len(nb)]) + nb
    payload = bytes([0x80 + 20]) + s + n
    return "0x" + keccak256(bytes([0xC0 + len(payload)]) + payload)[12:].hex()


# ---------------------------------------------------------------- JSON-RPC
class RpcError(Exception):
    pass


def brotli_stored_decode(buf: bytes) -> bytes:
    """Strict RFC 7932 decoder for brotli streams made ONLY of uncompressed
    (stored) meta-blocks and metadata blocks. Some public RPC endpoints answer
    with Content-Encoding: br regardless of Accept-Encoding, using stored
    blocks. Any compressed meta-block is refused (RpcError), never guessed."""
    pos = 0  # bit position

    def bits(n):
        nonlocal pos
        v = 0
        for i in range(n):
            byte = pos >> 3
            if byte >= len(buf):
                raise RpcError("brotli: truncated stream")
            v |= ((buf[byte] >> (pos & 7)) & 1) << i
            pos += 1
        return v

    def align():
        nonlocal pos
        while pos & 7:
            if bits(1):
                raise RpcError("brotli: non-zero padding")

    if bits(1):  # WBITS
        if bits(3) == 0:
            bits(3)
    out = bytearray()
    while True:
        islast = bits(1)
        if islast and bits(1):  # ISLASTEMPTY
            break
        mn = bits(2)
        if mn == 3:  # metadata block: reserved, MSKIPBYTES, MSKIPLEN, skip
            if bits(1):
                raise RpcError("brotli: reserved bit set")
            nb = bits(2)
            skip = (bits(8 * nb) + 1) if nb else 0
            align()
            pos += 8 * skip
            if islast:
                break
            continue
        mlen = bits(4 * (mn + 4)) + 1
        if islast:
            raise RpcError("brotli: compressed meta-block (unsupported by this stdlib verifier)")
        if not bits(1):  # ISUNCOMPRESSED
            raise RpcError("brotli: compressed meta-block (unsupported by this stdlib verifier)")
        align()
        start = pos >> 3
        if start + mlen > len(buf):
            raise RpcError("brotli: truncated stored block")
        out += buf[start:start + mlen]
        pos += 8 * mlen
    if (pos + 7) >> 3 != len(buf):
        raise RpcError("brotli: trailing bytes")
    return bytes(out)


class Source:
    def __init__(self, url, timeout=20, retries=5, allowed=None):
        self.url, self.timeout, self.retries, self.n = url, timeout, retries, 0
        self.allowed = READ_METHODS if allowed is None else allowed
        self.log = []  # (method, params, result|error) - public chain data only

    def call(self, method, params):
        if method not in self.allowed or method.startswith(("eth_send", "eth_sign", "personal_", "wallet_")):
            raise RpcError(f"method {method} is not on the read-only allow list")
        delay = 1.0
        for attempt in range(1, self.retries + 1):
            self.n += 1
            body = json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}).encode()
            req = urllib.request.Request(self.url, data=body, method="POST",
                                         headers={"Content-Type": "application/json", "User-Agent": USER_AGENT,
                                                  "Accept-Encoding": "identity"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    enc = r.headers.get("Content-Encoding", "").lower().strip()
                    # some public endpoints encode the body even when asked for identity
                    if enc == "gzip":
                        raw = gzip.decompress(raw)
                    elif enc == "br":
                        raw = brotli_stored_decode(raw)
                    elif enc not in ("", "identity"):
                        raise RpcError(f"{method}: unsupported Content-Encoding {enc}")
                    resp = json.loads(raw)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < self.retries:
                    time.sleep(delay); delay *= 2; continue
                self.log.append([method, params, {"transport_error": f"HTTP {e.code}"}])
                raise RpcError(f"{method}: HTTP {e.code}")
            except RpcError as e:
                self.log.append([method, params, {"transport_error": str(e)}])
                raise
            except Exception as e:  # network / TLS / timeout / bad JSON
                self.log.append([method, params, {"transport_error": type(e).__name__ + ": " + str(e)[:200]}])
                raise RpcError(f"{method}: {type(e).__name__}: {str(e)[:200]}")
            if "error" in resp:
                code = resp["error"].get("code")
                if code == -32005 and attempt < self.retries:  # rate limit: transient, never a 'not found'
                    time.sleep(delay); delay *= 2; continue
                self.log.append([method, params, {"error": resp["error"]}])
                raise RpcError(f"{method}: rpc error {code} {str(resp['error'].get('message'))[:200]}")
            self.log.append([method, params, resp.get("result")])
            return resp.get("result")
        raise RpcError(f"{method}: retries exhausted")


def fetch(src: Source, exp: dict) -> dict:
    """Collect every public datum the checks need. Raises RpcError on unavailability."""
    c = exp["contract"]["address"]
    d = {"chain_id": src.call("eth_chainId", []), "code": src.call("eth_getCode", [c, "latest"]), "tx": {}}
    for t in exp["transactions"]:
        h = t["tx_hash"]
        tx = src.call("eth_getTransactionByHash", [h])
        rc = src.call("eth_getTransactionReceipt", [h])
        bn = (rc or {}).get("blockNumber") or (tx or {}).get("blockNumber") or hex(t["receipt"]["block_number"])
        blk = src.call("eth_getBlockByNumber", [bn, False])
        tx_from_block = None
        if tx is None:  # hash index gap on this source: read the tx object from the block body instead
            full = src.call("eth_getBlockByNumber", [bn, True]) or {}
            m = [x for x in full.get("transactions") or [] if isinstance(x, dict) and _h(x.get("hash")) == h]
            tx_from_block = m[0] if len(m) == 1 else None
        logs = None
        if "anchor" in t:
            logs = src.call("eth_getLogs", [{"fromBlock": bn, "toBlock": bn, "address": c}])
        d["tx"][t["tx_id"]] = {"tx": tx, "tx_from_block": tx_from_block, "receipt": rc, "block": blk,
                               "logs_by_query": logs}
    return d


# ---------------------------------------------------------------- checks (pure)
def _h(x):
    return x.lower() if isinstance(x, str) else x


def _int(x):
    return int(x, 16) if isinstance(x, str) else x


def _pad32(addr):
    return "0x" + "00" * 12 + addr[2:].lower()


def check(exp: dict, d: dict) -> list:
    """Return a list of assertions [id, expected, observed, pass]."""
    A = []

    def a(aid, expected, observed, unavailable=False):
        # pass: True / False / None (None = this source cannot serve the datum; see index-gap rule)
        A.append({"id": aid, "expected": expected, "observed": None if unavailable else observed,
                  "pass": None if unavailable else expected == observed})

    net, con = exp["network"], exp["contract"]
    caddr = con["address"]
    a("chain.id", net["chain_id"], _int(d["chain_id"]))
    code = bytes.fromhex((d["code"] or "0x")[2:])
    a("contract.create_address(deployer,nonce)", caddr, create_address(con["deployer"], con["deployer_nonce"]))
    a("contract.runtime_code.bytes", con["runtime_code_bytes"], len(code))
    a("contract.runtime_code.sha256", con["runtime_code_sha256"], hashlib.sha256(code).hexdigest())
    a("contract.runtime_code.contains_anchor_selector", True, bytes.fromhex(con["anchor_selector"][2:]) in code)
    topic0 = "0x" + keccak256(con["event_signature"].encode()).hex()
    a("contract.anchor_selector=keccak(sig)[:4]", con["anchor_selector"],
      "0x" + keccak256(con["anchor_function"].encode())[:4].hex())

    for t in exp["transactions"]:
        p = "tx." + t["tx_id"]
        o = d["tx"][t["tx_id"]]
        blk = o["block"] or {}
        in_block = t["tx_hash"] in [_h(x) for x in (blk.get("transactions") or [])]
        # Index-gap rule: a null by-hash answer counts as UNAVAILABLE (not FAIL) only when the same
        # source's block at the expected height lists the tx hash. Otherwise null is a FAIL.
        tx_gap = o["tx"] is None and in_block and o.get("tx_from_block") is not None
        rc_gap = o["receipt"] is None and in_block
        tx = (o["tx"] or (o.get("tx_from_block") if tx_gap else None) or {})
        rc = o["receipt"] or {}
        a(p + ".tx_found", True, bool(tx))
        a(p + ".tx_read_path", "eth_getTransactionByHash", "eth_getTransactionByHash" if o["tx"] else
          ("block_body" if tx_gap else None), unavailable=tx_gap)
        a(p + ".receipt_found", True, bool(o["receipt"]), unavailable=rc_gap)
        a(p + ".hash", t["tx_hash"], _h(tx.get("hash")))
        a(p + ".from", t["from"], _h(tx.get("from")))
        a(p + ".nonce", t["nonce"], _int(tx.get("nonce")))
        a(p + ".to", t["to"], _h(tx.get("to")))
        a(p + ".type", t["type"], _int(tx.get("type")))
        a(p + ".chain_id", t["chain_id"], _int(tx.get("chainId")))
        a(p + ".value_wei", t["value_wei"], str(_int(tx.get("value"))))
        a(p + ".gas_limit", t["gas_limit"], _int(tx.get("gas")))
        a(p + ".max_fee_per_gas_wei", t["max_fee_per_gas_wei"], str(_int(tx.get("maxFeePerGas"))))
        a(p + ".max_priority_fee_per_gas_wei", t["max_priority_fee_per_gas_wei"],
          str(_int(tx.get("maxPriorityFeePerGas"))))
        inp = _h(tx.get("input") or tx.get("data") or "")
        a(p + ".input.bytes_identical", t["input_hex"], inp)
        a(p + ".input.sha256", t["input_sha256"], hashlib.sha256(bytes.fromhex(inp[2:])).hexdigest() if inp else None)
        r = t["receipt"]
        a(p + ".receipt.status", r["status"], _h(rc.get("status")), unavailable=rc_gap)
        a(p + ".receipt.transactionHash", t["tx_hash"], _h(rc.get("transactionHash")), unavailable=rc_gap)
        a(p + ".receipt.block_number", r["block_number"], _int(rc.get("blockNumber")), unavailable=rc_gap)
        a(p + ".receipt.block_hash", r["block_hash"], _h(rc.get("blockHash")), unavailable=rc_gap)
        a(p + ".receipt.contract_address", r["contract_address"], _h(rc.get("contractAddress")), unavailable=rc_gap)
        a(p + ".receipt.log_count", r["log_count"], len(rc.get("logs") or []), unavailable=rc_gap)
        a(p + ".tx.block_hash", r["block_hash"], _h(tx.get("blockHash")))
        a(p + ".block.hash", r["block_hash"], _h(blk.get("hash")))
        a(p + ".block.number", r["block_number"], _int(blk.get("number")))
        a(p + ".block.includes_tx", True, in_block)
        if "anchor" in t:
            an = t["anchor"]
            root_calc = "0x" + keccak256(an["preimage_utf8"].encode()).hex()
            a(p + ".anchor.root=keccak256(preimage)", an["root"], root_calc)
            a(p + ".anchor.meta_ascii", an["meta_ascii"], bytes.fromhex(an["meta"][2:]).rstrip(b"\0").decode())
            expected_input = con["anchor_selector"] + an["root"][2:] + an["meta"][2:]
            a(p + ".anchor.input=selector||root||meta", expected_input, inp)
            ts = _int(blk.get("timestamp"))
            want_log = {"address": caddr, "topics": [topic0, an["root"], an["meta"], _pad32(an["who"])],
                        "data": "0x" + (ts or 0).to_bytes(32, "big").hex(),
                        "blockHash": r["block_hash"], "transactionHash": t["tx_hash"]}
            logs = rc.get("logs") or []
            lg = logs[0] if len(logs) == 1 else {}
            got = {"address": _h(lg.get("address")), "topics": [_h(x) for x in lg.get("topics") or []],
                   "data": _h(lg.get("data")), "blockHash": _h(lg.get("blockHash")),
                   "transactionHash": _h(lg.get("transactionHash"))}
            a(p + ".event.receipt_log=Anchored(root,meta,who,ts=block.timestamp)", want_log, got, unavailable=rc_gap)
            q = [x for x in (o["logs_by_query"] or []) if _h(x.get("transactionHash")) == t["tx_hash"]]
            qg = q[0] if len(q) == 1 else {}
            got_q = {"address": _h(qg.get("address")), "topics": [_h(x) for x in qg.get("topics") or []],
                     "data": _h(qg.get("data")), "blockHash": _h(qg.get("blockHash")),
                     "transactionHash": _h(qg.get("transactionHash"))}
            a(p + ".event.eth_getLogs_readback", want_log, got_q)
            a(p + ".event.logIndex_receipt=getLogs", _int(lg.get("logIndex")), _int(qg.get("logIndex")), unavailable=rc_gap)
            look = [x for x in (o["logs_by_query"] or []) if _h(x.get("transactionHash")) != t["tx_hash"]
                    and [_h(y) for y in x.get("topics") or []][1:2] == [an["root"]]]
            a(p + ".event.no_other_log_with_same_root_in_block", 0, len(look))
    return A


def facts(d: dict) -> dict:
    """Informational per-tx values (not assertions): fees, timestamps, log index."""
    out = {}
    for tid, o in d["tx"].items():
        rc, blk = o["receipt"] or {}, o["block"] or {}
        gu, eg = _int(rc.get("gasUsed")), _int(rc.get("effectiveGasPrice"))
        logs = rc.get("logs") or []
        out[tid] = {"block_timestamp": _int(blk.get("timestamp")), "base_fee_per_gas_wei": _int(blk.get("baseFeePerGas")),
                    "gas_used": gu, "effective_gas_price_wei": eg,
                    "fee_wei": (gu * eg) if (gu is not None and eg is not None) else None,
                    "log_index": _int(logs[0].get("logIndex")) if len(logs) == 1 else None}
    return out


def _canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def run(exp, rpcs, timeout):
    per = []
    for url in rpcs:
        s = Source(url, timeout=timeout)
        ent = {"rpc": url, "status": None, "error": None, "assertions": [], "facts": None, "data": None, "log": s.log}
        try:
            d = fetch(s, exp)
            ent["data"] = d
            ent["assertions"] = check(exp, d)
            ent["facts"] = facts(d)
            ps = [x["pass"] for x in ent["assertions"]]
            ent["status"] = "FAIL" if False in ps else ("PARTIAL" if None in ps else "PASS")
        except RpcError as e:
            ent["status"], ent["error"] = "UNAVAILABLE", str(e)
        per.append(ent)
    ok = [e for e in per if e["status"] == "PASS"]
    part = [e for e in per if e["status"] == "PARTIAL"]
    bad = [e for e in per if e["status"] == "FAIL"]
    # cross-source agreement: every assertion observed (non-null) by two or more sources must agree
    agree = None
    readable = ok + part
    if len(readable) >= 2:
        agree = True
        ids = [x["id"] for x in readable[0]["assertions"]]
        for i, aid in enumerate(ids):
            vals = [_canon(e["assertions"][i]["observed"]) for e in readable if e["assertions"][i]["pass"] is not None]
            if len(set(vals)) > 1:
                agree = False
    if bad or agree is False:
        verdict = "FAIL"
    elif ok and len(ok) == len(per):
        verdict = "VERIFIED"
    elif ok:
        verdict = "VERIFIED_SINGLE_SOURCE" if len(ok) == 1 else "VERIFIED_REDUCED_SOURCES"
    else:
        verdict = "INCOMPLETE"
    txv = {}
    for t in exp["transactions"]:
        pre = "tx." + t["tx_id"] + "."
        sts = []
        for e in per:
            if e["status"] == "UNAVAILABLE":
                sts.append("UNAVAILABLE")
            else:
                ps = [x["pass"] for x in e["assertions"] if x["id"].startswith(pre)]
                sts.append("FAIL" if False in ps else ("PARTIAL" if None in ps else "PASS"))
        txv[t["tx_id"]] = sts
    return verdict, per, agree, txv


def load_expected(path):
    with open(path) as f:
        exp = json.load(f)
    if exp.get("schema") != "FIDOMOTA-M1-PUBLIC-EXPECTED-V1":
        raise SystemExit(3)
    return exp


def cmd_verify(args):
    exp = load_expected(args.expected)
    rpcs = args.rpc or DEFAULT_RPCS
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    verdict, per, agree, txv = run(exp, rpcs, args.timeout)
    t1 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    expected_sha = hashlib.sha256(open(args.expected, "rb").read()).hexdigest()
    self_sha = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    print(f"FidoMota M1 public verifier  started {t0}  finished {t1}")
    print(f"verifier sha256 {self_sha}")
    print(f"expected file   {os.path.basename(args.expected)} sha256 {expected_sha}")
    print(f"network {exp['network']['name']} chain_id {exp['network']['chain_id']}  contract {exp['contract']['address']}")
    for e in per:
        n = len(e["assertions"]); np_ = sum(x["pass"] is True for x in e["assertions"])
        nu = sum(x["pass"] is None for x in e["assertions"]); nf = sum(x["pass"] is False for x in e["assertions"])
        print(f"\nsource {e['rpc']}: {e['status']}  assertions pass {np_}/{n}, unavailable {nu}, fail {nf}  rpc_calls {len(e['log'])}")
        if e["error"]:
            print(f"  error: {e['error']}")
        for x in e["assertions"]:
            if x["pass"] is not True or args.verbose:
                tag = {True: "PASS", False: "FAIL", None: "UNAVAILABLE"}[x["pass"]]
                print(f"  [{tag}] {x['id']}\n      expected {x['expected']}\n      observed {x['observed']}")
        if e["facts"]:
            for tid, f in e["facts"].items():
                print(f"  {tid}: block_ts {f['block_timestamp']} gas_used {f['gas_used']} effective_gas_price {f['effective_gas_price_wei']} fee_wei {f['fee_wei']} log_index {f['log_index']}")
    print("\nper transaction (one column per source):")
    for t in exp["transactions"]:
        print(f"  {t['tx_id']:8s} {t['tx_hash']}  {' '.join(txv[t['tx_id']])}")
    print(f"\ncross-source agreement: {agree}")
    nall = sum(1 for v in txv.values() if all(s == "PASS" for s in v))
    for i, e in enumerate(per):
        nsrc = sum(1 for v in txv.values() if v[i] == "PASS")
        print(f"  {e['rpc']}: {nsrc}/{len(txv)} transactions pass every assertion")
    print(f"RESULT: {verdict}  ({nall}/{len(txv)} transactions pass every assertion on every source contacted)")
    if args.out_json:
        doc = {"schema": "FIDOMOTA-M1-PUBLIC-VERIFY-OUTPUT-V1", "started_utc": t0, "finished_utc": t1,
               "verifier_sha256": self_sha, "expected_sha256": expected_sha, "verdict": verdict,
               "cross_source_agreement": agree, "per_tx": txv,
               "sources": [{k: v for k, v in e.items() if k not in ("data", "log")} for e in per]}
        with open(args.out_json, "x") as f:
            json.dump(doc, f, indent=1); f.write("\n")
    if args.save_responses:
        with open(args.save_responses, "x") as f:
            json.dump([{"rpc": e["rpc"], "calls": e["log"]} for e in per], f, indent=1); f.write("\n")
    return {"VERIFIED": 0, "FAIL": 1, "INCOMPLETE": 2, "VERIFIED_SINGLE_SOURCE": 4, "VERIFIED_REDUCED_SOURCES": 4}[verdict]


def _mutations(exp):
    """(name, mutator) pairs; each must turn a correct expectation into a FAIL."""
    def flip(h):  # flip last hex nibble
        return h[:-1] + ("0" if h[-1] != "0" else "1")
    M = []
    M.append(("chain_id+1", lambda e: e["network"].__setitem__("chain_id", e["network"]["chain_id"] + 1)))
    M.append(("contract.runtime_sha256 flipped", lambda e: e["contract"].__setitem__("runtime_code_sha256", flip(e["contract"]["runtime_code_sha256"]))))
    M.append(("contract.address flipped", lambda e: e["contract"].__setitem__("address", flip(e["contract"]["address"]))))
    for i, t in enumerate(exp["transactions"]):
        M.append((f"{t['tx_id']}.block_hash flipped", lambda e, i=i: e["transactions"][i]["receipt"].__setitem__("block_hash", flip(e["transactions"][i]["receipt"]["block_hash"]))))
        M.append((f"{t['tx_id']}.input last byte flipped", lambda e, i=i: e["transactions"][i].__setitem__("input_hex", flip(e["transactions"][i]["input_hex"]))))
        M.append((f"{t['tx_id']}.nonce+1", lambda e, i=i: e["transactions"][i].__setitem__("nonce", e["transactions"][i]["nonce"] + 1)))
        if "anchor" in t:
            M.append((f"{t['tx_id']}.root flipped", lambda e, i=i: e["transactions"][i]["anchor"].__setitem__("root", flip(e["transactions"][i]["anchor"]["root"]))))
            M.append((f"{t['tx_id']}.meta flipped", lambda e, i=i: e["transactions"][i]["anchor"].__setitem__("meta", flip(e["transactions"][i]["anchor"]["meta"]))))
            M.append((f"{t['tx_id']}.who flipped", lambda e, i=i: e["transactions"][i]["anchor"].__setitem__("who", flip(e["transactions"][i]["anchor"]["who"]))))
            M.append((f"{t['tx_id']}.preimage changed", lambda e, i=i: e["transactions"][i]["anchor"].__setitem__("preimage_utf8", e["transactions"][i]["anchor"]["preimage_utf8"] + "x")))
    # swapped anchors: anchor1 expectations against anchor2's tx hash
    def swap(e):
        a1 = [t for t in e["transactions"] if t["tx_id"] == "anchor1"][0]
        a2 = [t for t in e["transactions"] if t["tx_id"] == "anchor2"][0]
        a1["anchor"], a2["anchor"] = a2["anchor"], a1["anchor"]
    M.append(("anchor1<->anchor2 anchor contents swapped", swap))
    return M


def cmd_negative(args):
    exp = load_expected(args.expected)
    url = (args.rpc or DEFAULT_RPCS)[0]
    s = Source(url, timeout=args.timeout)
    try:
        d = fetch(s, exp)
    except RpcError as e:
        print(f"negative controls INCOMPLETE: {url}: {e}"); return 2
    base = check(exp, d)
    print(f"negative controls against {url} (data fetched once, {len(s.log)} rpc calls)")
    print(f"  baseline: {sum(x['pass'] is True for x in base)}/{len(base)} assertions pass")
    if not all(x["pass"] is True for x in base):
        print("  baseline is not all-pass: controls not meaningful"); return 1
    bad = 0
    for name, mut in _mutations(exp):
        e2 = json.loads(json.dumps(exp)); mut(e2)
        fails = [x["id"] for x in check(e2, d) if x["pass"] is False]
        ok = len(fails) > 0
        bad += 0 if ok else 1
        print(f"  [{'DETECTED' if ok else 'MISSED'}] {name}: {len(fails)} failing assertion(s) e.g. {fails[:2]}")
    n = len(_mutations(exp))
    # index-gap rule controls (response mutations, not expectation mutations)
    for t in exp["transactions"]:
        tid = t["tx_id"]
        # G1: tx + receipt null AND block does not list the tx -> must FAIL
        d1 = json.loads(json.dumps(d))
        o = d1["tx"][tid]; o["tx"] = None; o["receipt"] = None; o["tx_from_block"] = None
        o["block"]["transactions"] = [x for x in o["block"]["transactions"] if _h(x) != t["tx_hash"]]
        r1 = check(exp, d1)
        g1 = any(x["pass"] is False for x in r1 if x["id"].startswith("tx." + tid + "."))
        # G2: receipt null but block lists the tx -> UNAVAILABLE for receipt data, never PASS
        d2 = json.loads(json.dumps(d))
        d2["tx"][tid]["receipt"] = None
        r2 = [x for x in check(exp, d2) if x["id"].startswith("tx." + tid + ".receipt")]
        g2 = all(x["pass"] is None for x in r2) and len(r2) > 0
        for name, ok in ((f"{tid}: null tx+receipt, block omits tx -> FAIL", g1),
                         (f"{tid}: null receipt, block lists tx -> UNAVAILABLE (not PASS)", g2)):
            n += 1; bad += 0 if ok else 1
            print(f"  [{'DETECTED' if ok else 'MISSED'}] {name}")
    print(f"RESULT: {n - bad}/{n} controls detected")
    return 0 if bad == 0 else 1


def cmd_selftest(_args):
    for m, h in _VECTORS:
        print(f"keccak256({m[:24]!r}{'...' if len(m) > 24 else ''}) = {keccak256(m).hex()}" + (f"  expected {h}  {'OK' if keccak256(m).hex() == h else 'BAD'}" if h else ""))
    # Widely cited CREATE example: sender 0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0,
    # nonce 0 -> 0xcd234a471b72ba2f1ccf0a70fcaba648a5eecd8d, nonce 1 -> 0x343c43a37d37dff08ae8c4a11544c718abb4fcf8
    # brotli stored-block frame (shape observed from a public endpoint): WBITS=22, 1 stored block, empty last
    body = b'{"jsonrpc":"2.0","id":1,"result":"0x4cef52"}'
    hdr = bytes([0x8b, ((len(body) - 1) >> 1) & 0xff, 0x80 | (((len(body) - 1) >> 9) & 0x7f)])
    frame = hdr + body + b"\x03"
    bok = brotli_stored_decode(frame) == body
    try:
        brotli_stored_decode(bytes([0x8b, 0x15, 0x00]) + b"x" * 44 + b"\x03"); bneg = False
    except RpcError:
        bneg = True
    print(f"brotli stored-block decode {'OK' if bok else 'BAD'}; compressed-block refusal {'OK' if bneg else 'BAD'}")
    got = create_address("0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0", 0)
    want = "0xcd234a471b72ba2f1ccf0a70fcaba648a5eecd8d"
    print(f"create_address(0x6ac7…dbf0, 0) = {got}  expected {want}  {'OK' if got == want else 'BAD'}")
    got1 = create_address("0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0", 1)
    want1 = "0x343c43a37d37dff08ae8c4a11544c718abb4fcf8"
    print(f"create_address(0x6ac7…dbf0, 1) = {got1}  expected {want1}  {'OK' if got1 == want1 else 'BAD'}")
    return 0 if (got == want and got1 == want1 and bok and bneg) else 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("verify", "negative", "selftest"):
        p = sp.add_parser(name)
        p.add_argument("--expected", default=os.path.join(here, "..", "expected", "m1_expected.json"))
        p.add_argument("--rpc", action="append", help="public JSON-RPC URL (repeatable); default: the two approved Arc Testnet endpoints")
        p.add_argument("--timeout", type=int, default=20)
        p.add_argument("--out-json")
        p.add_argument("--save-responses")
        p.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    return {"verify": cmd_verify, "negative": cmd_negative, "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
