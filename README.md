# FidoMota

**Evidence & Trust Infrastructure for Physical Systems**

FidoMota is developing infrastructure for turning observations
into traceable evidence, verifiable commitments, and independently
checkable trust results.

This repository is the public-facing documentation and
verification workspace for FidoMota.

## The Core Idea

Observation -> Evidence -> Proof -> Verification

**Light Proof. Heavy Trust.**

Observations may be complex. Proofs should be portable.
Verification should not require trusting the evidence producer.

Cryptographic proofs establish only their stated predicates. They do not
by themselves establish the accuracy or authenticity of physical inputs.

## Explore

- [Architecture](architecture/README.md)
- [Specifications](specifications/README.md)
- [Verification](verification/README.md)
- [Examples](examples/README.md)
- [Engineering Dev Log](devlog/2026-10-18-native-l1.md)

## Development Status

FidoMota is under active development.

Maintainer-reported Native L1 component results include PASS outcomes for
selected isolated synthetic scenarios. Supporting test records are not
included in this repository. The original full end-to-end pipeline,
including FAST and ZK anchoring and independent on-chain
verification for Mission-001, has not yet passed.

This repository does not claim production readiness.

## Transparency

We distinguish:

- Implemented functionality
- Test-verified behavior
- Known failures and limitations
- Planned or incomplete integrations

Public verification artifacts will be provided only after
their provenance, reproducibility, security, and release
conditions have been reviewed.

## Source and Licensing

The original FidoMota engineering repository is private.

It remains the sole authoritative implementation and operational pipeline.
This repository publishes documentation and verification information only.

The contents of this repository are not automatically
open-source licensed. No redistribution or reuse license
is granted merely by publishing the material.

Licensing and contribution policies are under review.

## Publication Clarification — 2026-10-21

- Status: Human Owner approved documentation correction.
- Reason: Clarify verification limits, reported test provenance and operational authority before public release.
- Scope: Documentation only; historical measurements and operational behavior are unchanged.
- Publication status: This approval does not authorize public visibility.
