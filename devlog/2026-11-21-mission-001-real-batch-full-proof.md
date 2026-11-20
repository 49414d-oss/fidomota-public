# Engineering Dev Log — 2026-11-21

## Mission-001: Real SEALED Batch and RISC Zero Full-Proof Validation

**Status:** UPSTREAM PIPELINE VALIDATED — END-TO-END INCOMPLETE  
**Scope:** Controlled virtual-EV observations, operational Native L1 and MerklePress batching, isolated real RISC Zero proof generation, and FAST/ZK contract review  
**Production FAST/ZK Activation:** NOT PERFORMED FOR THIS BATCH  
**Full End-to-End Mission-001:** INCOMPLETE — DUAL FINALITY NOT ACHIEVED

## What We Worked On

Following our November 20 update on Arc testnet compatibility and end-to-end recovery preparation, Mission-001 reached an important integration milestone.

Three newly generated virtual-EV observations passed through the existing operational MQTT intake and Native L1 evidence path. MerklePress subsequently produced a genuine **SEALED batch**, confirmed by matching database records, daemon events, and settlement artifacts.

Separately, the same batch was used to generate and locally verify a **real RISC Zero cryptographic proof** in an isolated workspace.

These results demonstrate progress in the original FidoMota evidence pipeline. They do not establish completed automatic on-chain anchoring, independent end-to-end verification, or Dual Finality.

No alternative production pipeline has been accepted.

## Operational Pipeline: Observation to SEALED Batch

Maintainer-reported operational observations confirm the following:

| Checkpoint | Reported result | Evidence boundary |
| --- | --- | --- |
| Virtual-EV observations | 3 accepted messages | Software-generated observations, not physical EV telemetry |
| MQTT intake | 3 authenticated observations | Operational intake |
| Native L1 evidence | 3 records, 216 bytes | Operational evidence segment |
| MerklePress | Segment root and manifest generated | Root consistent with batch artifacts |
| Batch database | New row 5641, status SEALED | Read-only operational query |
| Settlement artifacts | Manifest, local receipt, settlement metadata | Same batch identifier and root |
| On-chain FAST/ZK | Not demonstrated for this batch | End-to-end incomplete |

**Target batch:**

`MG_BATCH_blake3_v1_20261120_1795198336847`

**Batch root:**

`4d1569b7a06031e01e72cdc902ed22d92308c998ea9eeaabaac882a95846d15f`

The operational batch remained SEALED during the latest recorded checks.

The local L1 receipt contains a signature, but that signature was not independently validated during this exercise. The receipt's naming and timestamp fields do not establish blockchain anchoring.

The matching Merkle roots also do not constitute an independent recomputation from the underlying evidence.

## Real RISC Zero Full Proof: Isolated Validation

A separate, network-isolated execution used the target batch and the existing proof-export and RISC Zero host code paths.

The R-17 engineering report records:

| Verification | Reported result |
| --- | --- |
| RISC0 development mode | Unset |
| Receipt type | Composite, not Fake |
| Local receipt verification | PASS |
| Mutated journal negative control | Rejected |
| Mutated image ID negative control | Rejected |
| Actual Rust report `journal_hex` | Present |
| Batch-root binding | PASS |
| Journal-hash binding | PASS |
| Prover command elapsed time | 14.46 seconds |
| Peak single-process RSS | 616,292 kB |

This result resolves a previously identified compatibility concern: the actual Rust host report contains the `journal_hex` needed by the updated binding checks.

The receipt was produced using real cryptographic proving rather than synthetic or fake proof fixtures.

However, the result has important limitations.

The local verification used the same host implementation rather than an independent third-party verifier.

The RISC Zero journal commits to the batch root but does not contain a dedicated `leaf_count=3` commitment. The record count is supported by related L1 and export artifacts, not directly by that journal field.

The isolated receipt is measurement evidence. It has not been inserted into the operational anchoring pipeline and must not substitute for an automatically produced operational receipt.

## What Arc FAST and Sepolia ZK Actually Do

A subsequent source and ABI review clarified the contracts' actual behavior.

**Arc Testnet FAST**

The FAST contract receives a batch root and zero-valued metadata and emits an anchoring event. It does not perform RISC Zero proof verification.

**Sepolia ZK Commitment**

The Sepolia contract receives six 32-byte values:

1. Payload hash
2. Batch root
3. Receipt-wrapper file SHA-256
4. Journal SHA-256
5. Guest image ID
6. Verifier-program hash

The contract rejects zero inputs and repeated payload hashes, records the payload commitment, and emits an event.

**It does not cryptographically verify the RISC Zero proof on-chain.**

Cryptographic proof verification takes place off-chain, through the RISC Zero host and the designated receipt-verification path.

Accordingly, describing the implementation as "RISC Zero proof verified on Sepolia" would be incorrect.

The intended Sepolia operation records commitments associated with an off-chain-verified proof. The existing contract interface does not require Groth16 conversion of the Composite receipt.

## Mission-001 End-to-End Status

| Capability | Status |
| --- | --- |
| New virtual observations → MQTT intake | **Observed PASS** |
| Native L1 evidence generation | **Observed PASS** |
| Native L1 → MerklePress root | **Observed PASS** |
| MerklePress → operational SEALED batch | **Observed PASS** |
| Local L1 receipt generation | **Observed; signature not independently verified** |
| Real RISC Zero proof generation and local verification | **PASS in isolation** |
| Automatic operational Full Proof generation and retention | **Not demonstrated** |
| Arc FAST anchor for the target batch | **Not demonstrated** |
| Operational FINALIZED transition | **Not demonstrated** |
| Sepolia proof-commitment anchor | **Not demonstrated** |
| Independent cross-chain receipt/event verification | **Not demonstrated** |
| Dual Finality | **Not achieved** |

The three synthetic Arc compatibility anchors discussed in the November 20 update remain separate from this operational batch.

They must not be counted as evidence that the Mission-001 target batch has been anchored.

This update does not establish completion of Questbook grant acceptance milestones.

## Safety and Deployment Boundary

The updated journal-binding code passed maintainer-reported isolated regression tests:

- X6r2 focused tests: 11 PASS, 0 FAIL
- Mission-001 regression tests: 46 PASS, 0 FAIL

The correction was applied to the engineering worktree. The relevant anchoring services were not started or restarted as part of that application.

The isolated RISC Zero proof exercise did not modify operational evidence, the production database, or blockchain state.

The observed results do not replace the remaining authorization, signer, transaction-inclusion, fee-policy, or receipt-retention requirements.

No manual proof substitution or alternative pipeline will be treated as an acceptable Mission-001 end-to-end completion.

## Open Validation Items

- Complete operational signing-key and authorization gates.
- Establish safe Arc FAST transaction-fee, inclusion, reconciliation, and retry behavior.
- Anchor the existing SEALED batch through the approved Arc FAST path.
- Establish the operational FINALIZED transition.
- Generate and retain a fresh RISC Zero receipt through the automatic operational path.
- Record the six associated proof commitments on Sepolia.
- Independently retrieve and compare both chains' events.
- Recompute receipt and journal hashes from preserved artifacts.
- Verify the receipt against the expected image ID and journal through an independent validation procedure.
- Demonstrate the required Dual Finality and complete Mission-001 acceptance.

## Important Integration Boundary

**Proof generation, cryptographic verification, and blockchain commitment recording are distinct operations.**

The isolated RISC Zero result demonstrates that the selected batch can be processed by a real prover and that its output passes local cryptographic checks.

It does not establish automatic production proof handling or on-chain cryptographic verification.

The independent verification stage must check both blockchain events against preserved evidence and repeat the relevant off-chain proof verification.

## What This Does Not Prove

This work does not establish physical-source authenticity, independently recomputed L1 Merkle roots, independently validated L1 signatures, automatic operational proof acceptance, commercial USDC settlement, production readiness, or completed Dual Finality.

Cryptographic evidence can attest to properties of recorded observations and their integrity. It does not independently establish the objective truth of an underlying physical event.

## Next Engineering Focus

The next milestone is to complete the original single operational pipeline:

**SEALED Batch → Arc FAST → FINALIZED → Operational RISC Zero Full Proof → Sepolia Commitment → Independent Verification → Dual Finality**

The goal is an independently checkable Mission-001 end-to-end result, without manual substitutions or alternative operational paths.

Until that entire path is demonstrated, the overall mission remains **INCOMPLETE**.

We are building evidence infrastructure where **observations are recorded as observed, and trust claims must remain independently checkable**.

## Publication Clarification — 2026-11-21

This entry is a public engineering progress summary based on maintainer-supplied operational observations, isolated execution reports, and focused source and ABI analysis.

This public documentation repository does not contain the complete private operational source, raw production database, credential material, complete proof artifacts, or all records necessary to independently reproduce every reported PASS.

Publication does not authorize service activation, blockchain transactions, or changes to grant commitments.
