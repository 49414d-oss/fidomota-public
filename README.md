# FidoMota

## MOTION GATE

**Evidence & Trust Infrastructure for Physical Systems**

**Light Proof. Heavy Trust.**

I am building MOTION GATE as evidence infrastructure for physical and digital systems, under the FidoMota brand.

I designed it to transform observations from machines into traceable evidence, cryptographic proofs and verifiable blockchain commitments.

Machines continuously produce data. Receiving data, however, is not the same as possessing verifiable evidence. MOTION GATE is designed to bridge that gap.

## MOTION GATE — End-to-End Dual Finality Achieved

**MISSION-001 SUCCESS — `DUAL_FINALITY_MATCHED`**

November 28, 2026

Mission-001 has carried one operational evidence batch through the complete MOTION GATE lifecycle. The batch was sealed by MerklePress and anchored on Arc. Its RISC Zero proof journal commits to the same batch root, and the proof commitments are anchored on Ethereum Sepolia. Acceptance Verification then bound both lanes to one evidence identity.

| Result | Evidence |
| --- | --- |
| Batch root | `4d1569b7a06031e01e72cdc902ed22d92308c998ea9eeaabaac882a95846d15f` |
| Arc FAST root anchor | [Arc Testnet block 73250345](https://explorer.testnet.arc.io/tx/0x9c8084fdb78334f0300fcd304bebb8ddafeccd756e73f5c1345f4b2370539b96) |
| Sepolia ZK receipt anchor | [Ethereum Sepolia block 12223891](https://sepolia.etherscan.io/tx/0xf3f3984572c14c6cf08455171adbf92fb1d0f28736c40bb54f3fcbeaa25b55d1) |
| Acceptance Verification | `ACCEPTED`; post-run verification passed all seven criteria |
| Batch-root equality | Six representations matched across all 32 bytes |
| Dual Finality | `DUAL_FINALITY_MATCHED`, displayed by the L3 Evidence Explorer |

The acceptance record and a public evidence extract are published in the [Mission-001 verification package](verification/mission-001/README.md). The engineering account is in the [November 28 dev log](devlog/2026-11-28-mission-001-dual-finality-success.md).

## Philosophy

**Observe. Record. Prove. Verify.**

Record observations as observed.

Preserve their integrity.

Make cryptographic claims about the recorded evidence independently verifiable.

Cryptographic evidence establishes specific properties of recorded observations. It does not establish the absolute truth of the underlying physical event.

## System Architecture

```text
Source Observation
        │
        ▼
Native L1 Evidence
        │
        ▼
MerklePress — Sealed Batch Root
        │
        ├── FAST LANE
        │     Arc — Root Anchor
        │     Existence Finality
        │
        └── DEEP LANE
              RISC Zero Full Proof
              Ethereum Sepolia — ZK Receipt Anchor
              Validity Finality
        │
        ▼
Independent Verification
        │
        ▼
Dual Finality
        │
        ▼
L3 — Evidence Explorer
```

MOTION GATE is designed around two complementary verification paths.

**FAST Lane — Existence**

Records the batch root on Arc, establishing a blockchain commitment to the recorded evidence.

**DEEP Lane — Validity**

Generates a cryptographic proof using RISC Zero and records proof-associated commitments on Ethereum Sepolia.

The DEEP commitment must reference the preceding FAST root anchor. Both lanes must correspond to the same batch root.

Independent verification establishes whether the requirements for Dual Finality are satisfied.

Proof verification takes place off-chain. The blockchain contracts record commitments rather than directly verifying the RISC Zero proof.

See [Architecture](architecture/README.md) for the complete logical architecture and finality model.

## Development Status

### Mission-001 — Dual Finality

November 28, 2026

| Engineering checkpoint | Status |
| --- | --- |
| Virtual-device observation intake | Observed in the operational pipeline |
| Native L1 evidence recording | Observed |
| MerklePress batch construction | Observed — batch sealed |
| Arc FAST anchor for the target batch | Finalized; root match verified |
| RISC Zero receipt and journal | Verified; journal bound to the batch root |
| Ethereum Sepolia ZK receipt anchor | Recorded and accepted |
| Acceptance Verification | `ACCEPTED` |
| Dual Finality | `DUAL_FINALITY_MATCHED` |
| L3 Evidence Explorer | Dual Finality displayed for the target batch |

I set Mission-001 to carry recorded evidence for a single operational batch from observation to Dual Finality. That objective has been met.

### Circle Grants — Technical Progress Before Kickoff

The following results were obtained before formal grant kickoff. They describe technical progress only. They do not describe formal milestone acceptance, grant approval or disbursement.

| Proposed milestone | Technical progress |
| --- | --- |
| M1 — Arc Testnet compatibility | The technical success criteria of our proposed M1 milestone have been demonstrated ahead of formal grant kickoff. See the [M1 verification package](verification/m1-arc-testnet/README.md). |
| M2 — Payer-controlled USDC settlement | Next planned financial implementation. Not yet implemented. |
| M3 — Real pipeline batches on Arc | Mission-001 has achieved the internal end-to-end validation objective for the target batch, providing the technical foundation for our proposed M3 milestone. Additional batches across multiple runs, re-verification without the operational database and a tampered-batch rejection test remain ahead. |
| M4 — Public verification and external reproduction | Future deliverable. |

### Next

I am now connecting verifiable machine evidence to programmable USDC payments on Arc. The next step is payer-controlled settlement that acts on verified, failed and missing evidence.

## Verification Scope

Acceptance Verification is verification separated from evidence production. It is not a third-party audit, and the complete Mission-001 system has not yet been reproduced externally. The recorded assurance class is `SINGLE_PROVIDER_REDUCED`: each chain was read through a single RPC provider. The Rust verifier's build provenance is unresolved. The Mission-001 observations came from virtual devices, not physical measurements. MOTION GATE is not presented as a production or continuously operated service. See the [Mission-001 verification package](verification/mission-001/README.md#verification-scope) for details.

## Application Domains

MOTION GATE is designed for machine-generated observations across domains including:

- Electric vehicles and battery systems
- Energy infrastructure
- Industrial equipment
- IoT and connected devices
- Autonomous systems and machine networks

These are intended application domains, not claims of existing commercial deployments.

## Explore

- [Architecture](architecture/README.md)
- [Specifications](specifications/README.md)
- [Verification](verification/README.md)
- [Examples](examples/README.md)
- [Engineering Dev Log](devlog/)

## Public Repository

This repository provides public technical documentation and verification information for FidoMota and the MOTION GATE project.

The core engineering implementation is maintained separately in a private repository.

Public visibility does not constitute an open-source license or a claim of production readiness.

See [NOTICE.md](NOTICE.md) for publication information.

---

**FidoMota — MOTION GATE**

*Record what was observed. Make the evidence verifiable.*
