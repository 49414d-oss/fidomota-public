# FidoMota — Circle Arc Grant M1: public read-only verification

This package lets anyone check, from public Arc Testnet data only, that FidoMota's M1 transactions exist and match the published expected values byte for byte. M1 is one `MotionGateAnchorV0` contract deployment and three **synthetic** anchors on Arc Testnet (chain id 5042002).

**Scope.** The three anchor inputs are synthetic test values (`MG-M1-SYNTHETIC-V1|run=…|anchor=N`), not device observations. M1 shows that a permissionless anchoring contract can be deployed and called on Arc Testnet and read back independently. It is **not** the Mission-001 end-to-end pipeline, not a ZK proof, and not dual finality.

## Contents

| Path | What |
|---|---|
| `verifier/m1_public_verifier.py` | Standalone verifier. Python 3.8+ standard library only; read-only JSON-RPC |
| `verifier/arc_sepolia_observe.py` | Read-only observation tool behind the compatibility report |
| `expected/m1_expected.json` | Expected values: transactions, contract, anchor contents, provenance |
| `expected/VERIFIED_TRANSACTIONS.md` | The same identifiers and anchor values as a table |
| `expected/sepolia_reference.json` | A historical Sepolia anchor, used only as a comparison point |
| `contract/MotionGateAnchorV0.sol`, `contract/MotionGateAnchorV0.abi_and_runtime.json` | Contract source (MIT), ABI and runtime bytecode |
| `report/ARC_SEPOLIA_COMPATIBILITY_REPORT.md` | Arc–Sepolia compatibility report |
| `output/` | Output of the run recorded on 2026-11-23: console logs, JSON results, raw RPC responses |
| `SHA256SUMS` | SHA-256 manifest of every file above |

## Reproduce

```sh
# 1. integrity of this package
sha256sum -c SHA256SUMS

# 2. offline self-test (Keccak-256 and CREATE-address vectors, brotli stored-block decoder)
python3 -I -B verifier/m1_public_verifier.py selftest

# 3. live, read-only verification against the two public Arc Testnet endpoints
python3 -I -B verifier/m1_public_verifier.py verify --verbose
#    choose endpoints:  --rpc https://rpc.testnet.arc.io --rpc <another public Arc Testnet RPC>
#    save results:      --out-json result.json --save-responses responses.json   (files must not exist)

# 4. negative controls: corrupted expectations and simulated missing data must be detected
python3 -I -B verifier/m1_public_verifier.py negative

# 5. optional: the observations behind the compatibility report (Arc + Sepolia, read-only)
python3 -I -B verifier/arc_sepolia_observe.py
```

`-I` isolates Python from the environment and `-B` stops it writing `__pycache__` files. No wallet, key, account or API key is needed. The verifier sends only these read methods: `eth_chainId`, `eth_getCode`, `eth_getTransactionByHash`, `eth_getTransactionReceipt`, `eth_getBlockByNumber`, `eth_getLogs`. Any other method, and anything starting `eth_send`, `eth_sign`, `personal_` or `wallet_`, is refused in code.

## What is checked

The checks run on each RPC source separately; in the recorded run there were 127 assertions per source.

- **Network:** `eth_chainId` = 5042002.
- **Contract:**
  - the address equals `CREATE(deployer, nonce 0)`;
  - the deployed runtime code is 377 bytes with SHA-256 `298af41a…1363`;
  - the code contains the `anchor(bytes32,bytes32)` selector `0xa21f3c6a`.
- **Each transaction** (one deploy, three anchors):
  - hash, sender, nonce, recipient, type 2, chain id and value 0;
  - gas limit, `maxFeePerGas` and `maxPriorityFeePerGas`;
  - the calldata, byte-identical to the expected input;
  - the receipt: status `0x1`, block number and hash, contract address (deploy), and log count;
  - the block: its hash, and that it lists the transaction.
- **Each anchor:**
  - `root = keccak256(utf8(preimage))`;
  - the calldata is `selector ‖ root ‖ meta`;
  - the receipt holds exactly one `Anchored(root, meta, who, ts)` log from the contract, with topic0 = keccak256 of the event signature, `who` = the signer and `ts` = the block timestamp;
  - `eth_getLogs` returns the same log, and no other log in that block carries the same root.

`MotionGateAnchorV0` has no storage. `anchor()` only emits the `Anchored` event, so the event log *is* the stored anchor record that gets read back.

## Verdicts and exit codes

| exit | verdict | meaning |
|---|---|---|
| 0 | `VERIFIED` | every assertion passes on every source contacted, and the sources agree |
| 4 | `VERIFIED_SINGLE_SOURCE` | every assertion passes on one source; another source could not serve some data, and nothing it did serve disagrees (reduced assurance) |
| 1 | `FAIL` | an assertion failed on some source, or the sources disagree |
| 2 | `INCOMPLETE` | no source could serve every datum, and nothing failed |
| 3 | — | usage or input error |

**Missing-data rule.** A `null` answer to a transaction or receipt lookup counts as UNAVAILABLE, not FAIL, only when the same source's block at the expected height lists that transaction. The transaction is then read from the block body instead. Any other `null` is a FAIL. The negative-control suite checks both sides of this rule.

## Recorded result (2026-11-23, `output/`)

- **`rpc.testnet.arc.io`:** 127/127 assertions pass, so all 4 transactions pass every assertion.
- **`rpc.blockdaemon.testnet.arc.io`:** 89 pass, 0 fail, 38 unavailable.
  - Its blocks, contract code, transaction bodies and `eth_getLogs` records agree with the first source.
  - It no longer answers hash lookups for blocks this old: in a probe on 2026-11-23 it served transaction and receipt lookups 100,000 blocks back but not 300,000; the M1 blocks are about 660,000 back.
  - All 38 unavailable assertions depend on receipts.
- **Verdict: `VERIFIED_SINGLE_SOURCE`.** All 4 transactions are fully verified on one public source and corroborated, but not fully re-verified, on a second, independent one.
  - The summary line `0/4 … on every source contacted` counts only transactions that pass on *both* sources. The per-source lines just above it give the single-source result.
- **Negative controls:** 36/36 detected.

The result depends on whatever public endpoints are reachable when you run it, and on how long they keep history.

## Trust assumptions and limitations

- **What the result rests on:** the JSON-RPC endpoints you query; this verifier's Keccak-256 (self-tested against published vectors); and `m1_expected.json`, which comes from FidoMota's sealed M1 execution records (provenance inside the file).
- **What it does not use:** the original M1 run's own verdicts.
- **What the anchors are:** M1 anchors are synthetic. A successful check shows that the calls happened on Arc Testnet with these exact contents. It says nothing about any physical-world event.
- **The contract is permissionless.** Anyone can call `anchor()`. A record's origin is shown by `who` (the transaction sender), not by the contract.
- **Testnet only.** Testnet history may be pruned by RPC providers over time.
