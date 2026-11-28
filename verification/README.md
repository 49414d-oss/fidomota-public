# Verification

This directory hosts externally reviewable verification
procedures, evidence packages and, where approved, portable verifier
implementations.

## Published Packages

| Package | Contents |
| --- | --- |
| [Mission-001 — Dual Finality](mission-001/README.md) | Acceptance record, public acceptance-evidence extract and SHA-256 manifest for the Mission-001 target batch: `DUAL_FINALITY_MATCHED` |
| [M1 — Arc Testnet compatibility](m1-arc-testnet/README.md) | Standalone read-only verifier, expected values, contract artifacts, recorded output and Arc–Sepolia compatibility report for three synthetic Arc Testnet anchors |

Each package states its own scope and limitations.

A complete public end-to-end verifier for Mission-001 is not yet
published. External reproduction of the complete workflow is a future
deliverable.

Isolated LC1 Writer tests are internal component-validation evidence,
not proof of production operation or independent trust finality.

## Publication Requirements

Each verification release should identify:

- Inputs and expected outputs
- Reproducible execution instructions
- Artifact integrity and provenance
- Cryptographic assumptions
- Trust and authority boundaries
- Positive and negative test cases
- Explicit limitations

Only approved, release-safe artifacts may be added here.
