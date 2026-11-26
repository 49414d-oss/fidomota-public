# FidoMota — MOTION GATE

## System Architecture

**Evidence & Trust Infrastructure for Physical Systems**

### 1. Architectural Objective

MOTION GATE separates observation recording, cryptographic proof generation, blockchain commitment recording and independent verification.

Each stage has a distinct responsibility and a defined evidence boundary.

The architecture is designed to preserve a consistent evidence identity throughout the pipeline, from the original observation to the final verification result.

### 2. Logical Architecture

```text
MOTION GATE
│
├── Source Domain
│   ├── Physical systems
│   ├── Digital systems
│   └── Virtual devices
│
├── Intake & Trust Boundary
│   ├── Observation intake
│   ├── Authentication
│   └── Trust admission
│
├── L1 — Evidence Layer
│   ├── Native evidence recording
│   ├── Evidence integrity
│   ├── MerklePress
│   └── Sealed batch commitment
│
├── L2 — Proof & Anchoring Layer
│   │
│   ├── FAST LANE
│   │   ├── Batch root
│   │   ├── Arc root anchor
│   │   └── Existence Finality
│   │
│   └── DEEP LANE
│       ├── Full Proof
│       ├── RISC Zero zkVM
│       ├── Receipt and journal
│       ├── Off-chain receipt verification
│       ├── Ethereum Sepolia receipt anchor
│       └── Validity Finality
│
├── Independent Verification
│   ├── FAST anchor verification
│   ├── DEEP anchor verification
│   ├── Receipt verification
│   ├── Batch-root consistency
│   └── Dual Finality
│
└── L3 — Presentation Layer
    ├── Evidence Explorer
    ├── FAST / DEEP status
    └── Derived finality display
```

This diagram represents the logical architecture. Implementation and validation status are documented separately.

### 3. Source Intake and Trust Admission

MOTION GATE receives observations from physical and digital systems.

Authentication and trust admission determine whether observations are eligible to enter the evidence pipeline under the applicable admission policy.

Admission does not establish the objective truth of a reported physical measurement.

Authenticated observation intake has been observed in the operational virtual-device pipeline.

Device-bound cryptographic identity is a separate capability and is not claimed as a completed validation result.

### 4. L1 — Evidence Layer

L1 establishes the recorded evidence upon which subsequent proofs and commitments depend.

#### Native Evidence

Observations are recorded through the Native L1 evidence path.

Recorded evidence becomes the reference material for subsequent integrity checks and proof generation.

The responsibility of this layer is to preserve what was observed, not to reinterpret an observation as an assertion of physical truth.

#### MerklePress

MerklePress constructs Merkle commitments from recorded evidence and participates in the formation of sealed batches.

A sealed batch provides a batch identity and a batch root.

The batch root is the common cryptographic reference shared by the FAST and DEEP lanes.

### 5. L2 — Proof and Anchoring Layer

The FAST and DEEP lanes serve complementary verification objectives.

#### FAST Lane — Existence

The FAST lane records the batch root on Arc.

A finalized root anchor establishes evidence that the batch commitment was recorded on the designated blockchain.

The root anchor does not establish the validity of every underlying observation.

#### DEEP Lane — Validity

The DEEP lane generates cryptographic evidence using the recorded batch and a designated proof program.

The RISC Zero zkVM architecture separates host-side proof orchestration from guest-side predicate execution.

```text
Sealed Evidence Batch
        │
        ▼
Host — Proof Input Preparation
        │
        ▼
Guest — Evidence Predicate Execution
        │
        ├── Record integrity checks
        ├── Record-version checks
        ├── Merkle inclusion checks
        └── Batch-root consistency
        │
        ▼
RISC Zero Receipt + Journal
        │
        ▼
Off-chain Receipt Verification
        │
        ▼
ZK Receipt Commitment
        │
        ▼
Ethereum Sepolia
```

The receipt provides cryptographic evidence of execution under the expected proof program.

The journal binds the public proof output to the corresponding batch root.

The DEEP anchor records proof-associated commitments and must reference the prior FAST root anchor.

### 6. Finality Lifecycle

#### T0 — Batch Root Finalized

A sealed batch establishes the common batch root.

Outputs:

- Batch identity
- Batch root

#### T1 — Root Anchor Finalized

The FAST anchor is accepted and reaches the required blockchain finality.

Outputs:

- Root anchor transaction reference
- Anchored batch root
- Existence Finality

#### T2 — Proof Materialized

The proof path produces a RISC Zero receipt and journal.

The journal must commit to the same batch root established by the FAST anchor.

Outputs:

- Receipt
- Journal
- Journal batch root
- Proof-program identity

T2 alone does not establish Validity Finality.

#### T3 — ZK Receipt Anchor Finalized

The DEEP commitment is accepted on the designated blockchain and reaches the required finality.

The DEEP payload must bind the proof-related commitments to the prior FAST anchor.

Validity Finality requires an accepted FAST root anchor, an accepted DEEP receipt anchor, a verified proof and a consistent batch root.

### 7. Dual Finality

Dual Finality is the evidence-verification model of MOTION GATE.

| Property | Definition |
| --- | --- |
| Existence Finality | The batch root has a finalized FAST commitment. |
| Validity Finality | The corresponding proof verifies and its finalized DEEP commitment is bound to the same FAST-anchored batch. |
| Dual Finality | Both properties are established for the same evidence identity and satisfy the required independent verification. |

Dual Finality does not replace the consensus finality of either blockchain.

It is a derived evidence-verification result based on the recorded evidence, proof and corresponding blockchain commitments.

#### Core Invariants

```text
FAST_ANCHORED_BATCH_ROOT
           =
JOURNAL_BATCH_ROOT
           =
DEEP_COMMITTED_BATCH_ROOT
```

```text
DEEP_PAYLOAD
     │
     └── Binds prior ROOT_ANCHOR_REFERENCE
```

A mismatched batch root, invalid receipt, missing anchor reference or unverified commitment cannot produce an accepted Dual Finality result.

### 8. Blockchain Contract Boundary

The current testnet integration uses Arc for FAST commitments and Ethereum Sepolia for DEEP commitments.

The Arc contract records a batch-root commitment.

The reviewed Sepolia contract records six proof-associated commitment values:

- Payload hash
- Batch root
- Receipt-wrapper SHA-256
- Journal SHA-256
- Guest image ID
- Verifier-program hash

Neither commitment-recording operation substitutes for cryptographic verification of the RISC Zero receipt.

The reviewed Sepolia contract does not perform RISC Zero proof verification on-chain.

### 9. Independent Verification

Independent verification is a distinct responsibility, separate from evidence production.

The intended verification procedure checks:

1. FAST transaction and event identity.
2. FAST-anchored batch root.
3. Receipt and journal integrity.
4. Cryptographic receipt validity against the expected proof-program identity.
5. DEEP transaction and commitment identity.
6. Binding between the prior FAST anchor and the DEEP payload.
7. Batch-root consistency across the FAST and DEEP lanes.
8. Required blockchain finality conditions.

Verification results must be derived from the relevant evidence rather than accepted solely from the evidence producer's status.

### 10. L3 — Presentation Layer

L3 exposes evidence and verification information through the MOTION GATE Explorer.

Its responsibility is presentation.

L3 may display:

- Batch identity and root
- FAST anchor status
- DEEP anchor status
- Transaction references
- Verification results
- Derived finality status

L3 does not create evidence, execute proofs, authorize blockchain transactions or confer finality.

### 11. Implementation and Validation Status

November 26, 2026

| Component | Validation status |
| --- | --- |
| Authenticated virtual-device intake | Observed in the operational pipeline |
| Native L1 evidence recording | Observed |
| MerklePress and sealed batch | Observed |
| Arc FAST root anchor | Confirmed against on-chain records in project engineering records |
| RISC Zero proof generation | Real cryptographic proof generated and locally verified in isolation |
| Operational receipt and journal | Materialization reported; independent verification pending |
| Sepolia receipt commitment | Target-batch anchoring pending |
| Independent end-to-end verification | Pending |
| Dual Finality | Not achieved |
| L3 Explorer | Implemented; complete Dual Finality presentation not yet validated |

Operational observations and isolated cryptographic validation are different categories of evidence.

The complete public evidence package required to independently reproduce Mission-001 has not yet been published.

See the [Engineering Dev Log](../devlog/) for historical engineering results.

### 12. Trust Boundaries

MOTION GATE distinguishes:

- Observation from physical truth.
- Authentication from measurement accuracy.
- Evidence integrity from source authenticity.
- Cryptographic proof validity from unrestricted trust.
- Blockchain commitment from proof verification.
- Displayed status from independently established finality.

These distinctions define the technical boundaries of the system.

---

**FidoMota — MOTION GATE**

*Light Proof. Heavy Trust.*

*Evidence should remain verifiable beyond the system that produced it.*
