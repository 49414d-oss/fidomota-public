# FidoMota

## MOTION GATE

**Evidence & Trust Infrastructure for Physical Systems**

**Light Proof. Heavy Trust.**

MOTION GATE is an evidence and trust infrastructure project developed under the FidoMota brand.

It is designed to transform observations from physical and digital systems into traceable evidence, cryptographic proofs and independently verifiable commitments.

Machines continuously produce data. Receiving data, however, is not the same as possessing verifiable evidence.

MOTION GATE is designed to bridge that gap.

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

## Application Domains

MOTION GATE is designed for machine-generated observations across domains including:

- Electric vehicles and battery systems
- Energy infrastructure
- Industrial equipment
- IoT and connected devices
- Autonomous systems and machine networks

These are intended application domains, not claims of existing commercial deployments.

## Development Status

### Mission-001 — Original Pipeline Integration

November 26, 2026

| Engineering checkpoint | Status |
| --- | --- |
| Virtual-device observation intake | Observed in the operational pipeline |
| Native L1 evidence recording | Observed |
| MerklePress batch construction | Observed |
| Arc FAST anchor for the target batch | Confirmed against on-chain records in project engineering records |
| RISC Zero cryptographic proof | Generated and locally verified in isolation |
| Operational receipt and journal | Materialization reported in engineering execution records |
| Ethereum Sepolia ZK receipt anchor | Pending |
| Independent end-to-end verification | Pending |
| Dual Finality | Not yet achieved |

Mission-001 remains incomplete.

The objective is to demonstrate the original end-to-end pipeline without manual proof substitution or alternative execution paths.

The observed results and isolated validation results represent different evidence scopes. A complete, independently reproducible public evidence package has not yet been published.

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
