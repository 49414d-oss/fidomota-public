# Arc Testnet ↔ Sepolia compatibility report — FidoMota M1

**Date:** 2026-11-23. Covers the M1 contract `MotionGateAnchorV0` and its anchor write/read path.

**Evidence labels:**
- **[OBS]** observed in the read-only run recorded in `../output/` (2026-11-23 08:09 UTC). The source is named for each item.
- **[REC]** recorded in FidoMota's sealed M1 execution records (2026-11-19), from which `m1_expected.json` was derived.
- **[DOC]** documented network characteristic, as recorded from docs.arc.io on 2026-11-19 by FidoMota. It was not re-fetched or re-observed for this report.
- **[UNV]** unverified, or an assumption.

**The Sepolia comparison point** is a single historical FidoMota anchor transaction on Sepolia (2026-10-13, `../expected/sepolia_reference.json`):
- contract `0x1aa4484a17b3d5925da8cff2cf5235e719bf920b`;
- tx `0xd2511a65c80abad0963908294cad3bed0f0ad35b3c1b58bd5775af45f8b3e7f7`.

**What was not done:** M1 itself was not run on Sepolia. No Sepolia deployment or transaction was made for this report, and the comparison does not go beyond what that one transaction and the live chain heads show.

## 1. Chain ID and network configuration

| item | Arc Testnet | Sepolia |
|---|---|---|
| `eth_chainId` | 5042002 (`0x4cef52`) [OBS, both Arc sources] | 11155111 [OBS, Tenderly] |
| `net_version` | 5042002 [OBS] | 11155111 [OBS] |
| client string | `arc/v1` (rpc.testnet.arc.io); `reth/v2.2.0-508cbdf` (Blockdaemon) [OBS] | `Tenderly/1.0` [OBS] |
| block gas limit | 30,000,000 [OBS latest; DOC] | ≈200,000,000 at the time of reading [OBS] |
| `latest` / `safe` / `finalized` | same block on rpc.testnet.arc.io; Blockdaemon `finalized` ≥ `latest` within sequential calls [OBS]. This is consistent with documented deterministic finality [DOC] | `finalized` 72 blocks / 876 s behind `latest` at the time of reading [OBS] |
| public no-key endpoints used | rpc.testnet.arc.io; rpc.blockdaemon.testnet.arc.io [OBS] | sepolia.gateway.tenderly.co. sepolia.drpc.org answered HTTP 400 "chain is not available on free plan" [OBS] |

## 2. USDC gas payment behaviour

**Gas is paid in native USDC with 18 decimals [OBS].**
- The signer's native balance was exactly `20000000000000000000` before block 73005198 and `19995608396000000000` after block 73006326 [OBS, rpc.testnet.arc.io, historical `eth_getBalance`].
- The difference, 4,391,604 gwei-units (0.004391604 USDC), equals Σ `gasUsed × effectiveGasPrice` over the four M1 receipts [OBS].
- The match is exact, so there was no net balance change other than the fees. The M1 transactions use the consecutive nonces 0–3, so no other transaction from this sender falls inside the span.

**What documentation adds:**
- USDC is the native gas unit with 18 decimals, and its ERC-20 view has 6 decimals over the same balance [DOC].
- The ERC-20 view was **not** read for this report [UNV].

**Sepolia** pays gas in Sepolia ETH. The reference tx paid 21,287,819,264 wei: 19,352 gas × 1,100,032 wei [OBS].

## 3. Contract deployment and bytecode / interface compatibility

**Deployment on Arc:**
- Plain `CREATE` deployment worked [OBS]: deploy tx type 2, status `0x1`, `contractAddress` = `0x19fcc7ee…57d2`, which equals `CREATE(0xc627…42b8, 0)` as computed by the verifier.
- The init code is the unmodified solc 0.8.33 output (optimizer off, `evmVersion: prague`, which includes PUSH0) [REC]. It deployed with no recompilation [OBS: runtime code matches the artifact].

**Same bytecode on both chains [OBS]:**
- `eth_getCode` returns byte-identical runtime code on both chains: 377 bytes, sha256 `298af41a…1363`, keccak256 `0xf7e2b1b3…e486`.
- Arc read: contract `0x19fc…57d2`, from both Arc sources. Sepolia read: contract `0x1aa4…920b`.

**Same interface [OBS]:**
- `anchor(bytes32,bytes32)`, selector `0xa21f3c6a`, in calldata on both chains.
- The same `Anchored` topic0 `0xef9ad88e…8151`.
- The same event layout: three indexed topics (root, meta, who) and data = `uint256 ts`.

**Gas used is not identical.**
- **Arc:** the deploy used 134,751 gas and the anchors 24,795 / 24,795 / 24,783 [OBS]. These equal the values measured beforehand on a local Prague EVM (134,751 and 24,795) [REC].
- **Sepolia:** the reference anchor (block 11905576, 2026-10-13 10:48:24 UTC) used 19,352 gas with a 19,516 gas limit [OBS]. Both are **below** the pre-Glamsterdam intrinsic cost for that tx: 21,000 flat plus calldata, which comes to 21,704.
- **Why the two chains differ.** Two documented protocol facts [DOC]:
  - The Glamsterdam upgrade activated on Sepolia on 2026-10-06 at 13:53:36 UTC (timestamp 1791294816), per the activation table of the Glamsterdam meta EIP: https://eips.ethereum.org/EIPS/eip-7773.
  - Glamsterdam includes EIP-2780, "Resource-Based Intrinsic Transaction Gas": https://eips.ethereum.org/EIPS/eip-2780.
    - EIP-2780 replaces the flat 21,000 intrinsic cost with resource components: `TX_BASE_COST` 12,000, a cold recipient access of 3,000, and `TX_VALUE_COST` 6,000 only when value is transferred.
    - It states that calldata and access-list metering are unchanged.
    - The EIP page showed status "Last Call" when read on 2026-11-23.
- **What this means for the reference tx.** It came after activation. A zero-value call is no longer charged the old flat 21,000, so its observed gas use and gas limit are **consistent with** the EIP-2780 accounting model [OBS + DOC].
- **What was not done.** The exact EIP-2780 arithmetic for this transaction was **not independently reconstructed**: the per-component intrinsic cost plus execution cost, checked against 19,352 [UNV]. The match is consistency with a documented protocol change, not a transaction-level verification.
- **Arc in M1:** its gas use equals the local Prague-EVM (pre-EIP-2780) measurement [OBS + REC]. That it followed the flat-21,000 schedule is an inference from this match [UNV]. Practical consequence: gas limits must be set or estimated per chain and per fork, not copied between chains.

## 4. RPC and fee-handling differences

**Arc base fee [OBS]:** 20 gwei on every block read, the M1 blocks included. That matches the documented floor [DOC]: minimum base fee 20 gwei, maximum 20,000 gwei, `maxFeePerGas` must be ≥ 20 gwei, and transactions below the floor may be dropped without a receipt.

**M1 fee settings [OBS]:**
- `maxFeePerGas` 41 gwei and `maxPriorityFeePerGas` 1 gwei, giving an effective 21 gwei.
- The run used the rule `max(floor, 2 × base + tip)` [REC].

**Fee suggestions differ by provider [OBS]:**
- `eth_gasPrice` and `eth_maxPriorityFeePerGas` gave 25 / 5 gwei on rpc.testnet.arc.io and 27.5 / ≈7.5 gwei on Blockdaemon, while the actual base fee was 20 gwei.
- An earlier read the same day gave 32.5 / 12.5 gwei on Blockdaemon.
- So suggestions are not a reliable fee oracle on Arc. Fees should come from the block base fee and the documented floor.

**Sepolia [OBS]:**
- Base fee 15–20 wei.
- The reference tx's priority fee (1,100,012 wei) dominated its effective price.

**Response encoding [OBS]:** Blockdaemon answers with `Content-Encoding: br` (brotli stored blocks), even for `Accept-Encoding: identity`. A client that cannot decode brotli cannot read that endpoint. The verifier carries a strict stored-block decoder.

**History retention [OBS]:**
- rpc.testnet.arc.io served transaction, receipt and historical-state (`eth_getBalance`) queries for blocks back to M1 (about 660k blocks).
- Blockdaemon served blocks, code and `eth_getLogs` for those heights, but returned `null` for transaction and receipt lookups older than roughly 100k–300k blocks. It also refused historical state with "state at block … is pruned".
- Older recorded probes found `eth_getLogs` range and rate limits on rpc.testnet.arc.io: 10,000-block ranges were rejected, and bursts were rate-limited with `-32005` [REC]. These were not re-tested here.

## 5. Transaction receipt and event behaviour

**Receipt fields on Arc [OBS]:** `blockHash, blockNumber, contractAddress, cumulativeGasUsed, effectiveGasPrice, from, gasUsed, logs, logsBloom, status, to, transactionHash, transactionIndex, type`.
- The Sepolia reference receipt (Tenderly) has the same set plus `blobGasUsed`.
- Clients should not require `blobGasUsed`.

**Log objects [OBS]:** carry `blockTimestamp` on both chains, as served by these endpoints.

**Event `ts` [OBS]:** equals the block timestamp on both chains: Arc anchors 1795084953 / 1795085127 / 1795085319; Sepolia 1791888504.

**Inclusion latency.** Not measured here.
- Arc documents deterministic finality [DOC], and at the time of reading `finalized` = `latest` on rpc.testnet.arc.io [OBS].
- Recorded M1 timing: each transaction's receipt was observed within the runner's first observation poll [REC].

## 6. Anchor write/read behaviour

- **Write [OBS]:** each anchor is a type-2 call to `anchor(root, meta)` with 68 bytes of calldata. It succeeded (status `0x1`), and each emitted exactly one `Anchored` log.
- **Read-back [OBS]:**
  - The verifier recovers root, meta, who and ts from the receipt log.
  - It recovers the same data through a separate `eth_getLogs` query on the anchor block.
  - On both Arc sources, `eth_getLogs` returned the same records; the receipt is from rpc.testnet.arc.io only, see §4.
- **No contract storage.** `MotionGateAnchorV0` keeps none, so an anchor is identified by (chain, contract, tx, logIndex). Its author is `who` (the sender).
- **Permissionless.** The contract has no access control [REC: source], so consumers must filter by `who`.
- **Sepolia [OBS].** The reference anchor reads back the same way: topics [topic0, root `0xf454bcdd…f290`, meta `0x00…00`, who `0xc931…ad86`] and ts = block timestamp.
  - Its meta is all zero (a production FAST root anchor). M1 used the synthetic marker `MG-M1-SYNTHETIC-V1`.

## 7. Limitations and unresolved differences

1. **No M1-on-Sepolia run.** The Sepolia side is one historical transaction from a different signer and a different period. Equal bytecode, selector and event layout are shown; equal end-to-end behaviour under identical inputs is **not**.
2. **Sepolia gas is below the pre-Glamsterdam intrinsic cost** (§3). It was observed on one transaction made after the 2026-10-06 Sepolia Glamsterdam activation, and it is consistent with EIP-2780's resource-based intrinsic gas [DOC]. The transaction-level EIP-2780 arithmetic has not been independently reconstructed [UNV].
3. **The second Arc source cannot re-verify old receipts.** M1 receipts are fully verified on one public Arc source only (verdict `VERIFIED_SINGLE_SOURCE`).
4. **dRPC Sepolia** is no longer usable without a paid plan. Sepolia observations come from one provider (Tenderly).
5. **Fee policy statements are [DOC] as recorded on 2026-11-19.** Only the 20 gwei base fee was observed. Neither the ceiling nor the below-floor drop behaviour was tested.
6. **The USDC ERC-20 interface (6 decimals) was not exercised** [UNV].
7. **Testnet results only.** Nothing here is a statement about Arc mainnet.
