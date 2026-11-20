# Engineering Dev Log — 2026-11-20

## Mission-001: Arc Testnet Compatibility and End-to-End Recovery Preparation

**Status:** PARTIALLY VALIDATED — PRE-ACTIVATION HOLD
**Scope:** Arc testnet synthetic anchors, isolated regression, focused source audits, and offline production cutover preparation
**Production Activation:** NOT AUTHORIZED
**Full End-to-End Mission-001:** INCOMPLETE / NOT TESTED

## What We Worked On

We continued recovery of the original FidoMota evidence pipeline, from Native L1 observations through MerklePress batching, full-proof generation, Arc FAST anchoring, Sepolia ZK receipt anchoring, and independent verification. The intended outcome includes independently checkable evidence on both chains; no alternative production pipeline has been accepted.

The current work concentrated on testnet compatibility, target-batch isolation, transaction and finality guards, automated verification handoffs, credential separation, provider-assurance policy, and a controlled deployment procedure. The new changes remain in sealed offline correction bundles rather than being activated in the production repository.

## Arc Testnet: Synthetic Compatibility Evidence

Maintainer records report deployment of a root-anchor contract to **Arc Testnet (chain ID 5042002)** and **three synthetic test anchor transactions**, with native gas paid in USDC. Deployment and anchor transaction references are available on the public Arc explorer:

| Transaction | Reference |
| --- | --- |
| Contract deployment | [0xa9b68fdd…02c7](https://explorer.testnet.arc.io/tx/0xa9b68fdd1461b495efb6badfb757211869e82209754993e35fbf256a0c9d02c7) |
| Test anchor 1 | [0x4a50e85b…7122](https://explorer.testnet.arc.io/tx/0x4a50e85bbb93d6aae4e714bec1889783bdd3372541cebb33d9a42bb9d4e37122) |
| Test anchor 2 | [0x9e11e64f…d7c1](https://explorer.testnet.arc.io/tx/0x9e11e64f6b23cf78077452910d171bec241a921690415a0071911ef39722d7c1) |
| Test anchor 3 | [0x3d3a2d56…3f6](https://explorer.testnet.arc.io/tx/0x3d3a2d56857b986bc68c18008aa69ee3cd79cef08a059f4c6522e2e3cfb5a3f6) |

**Evidence boundary:** These are synthetic Arc compatibility exercises, **not real device-to-chain end-to-end evidence**, commercial USDC payments, or proof of a completed grant milestone. The Questbook M1 acceptance criterion also requires an independently reproducible byte-for-byte readback of three test anchors, a public test script, and a compatibility report. This public log does not itself substantiate completion of those deliverables.

A maintainer-reported read-only RPC comparison found the Arc contract's emitted event topic to match the existing event-topic configuration. This supports event signature compatibility, not the full reconcile execution path.

## Maintainer-Reported Engineering and Test Results

The following counts are from sealed offline test reports provided by the maintainers. This public documentation repository does not include the underlying isolated fixtures, full TAP records, or complete private operational source required for independent reproduction. They must **not** be represented as independently verified public execution evidence.

| Area | Reported result | Boundary |
| --- | --- | --- |
| FAST executor, mission targeting, daemon | 105 PASS, 0 FAIL | Isolated regression |
| Finalization and daemon | 51 PASS, 0 FAIL | Isolated regression |
| ZK CLI and acceptance policy | 132 PASS, 0 FAIL, 2 TODO | Synthetic fixtures and stubs |
| Compatibility/regression suite | 125 PASS, 0 FAIL, 2 TODO | Isolated validation |
| Explorer isolation regression | 8 PASS, 0 FAIL | Sandbox with synthetic credentials |
| **Combined reported total** | **421 PASS, 0 FAIL, 4 TODO (425 cases)** | **NOT an overall PASS** |

The four TODO cases remain untested. Real RISC Zero verification flowing through automatic acceptance persistence is **NOT TESTED**. Stub or fake-acquirer outcomes do not prove the operational end-to-end path.

The prior R4 code correction received a focused independent source-audit PASS. A later operational-configuration correction bundle changed additional source and unit proposals; its independent final review and deployment approval remain pending. The earlier focused PASS does not extend automatically to subsequent changes.

## Safety and Deployment Boundary

Changes under review include exact mission-batch gating, Arc transaction identity and fee controls, duplicate-broadcast safeguards, chain-specific finalization, acceptance-provider policy, and separation of credentials from read-only services. Offline proposals also specify restricted service environments and a staged cutover and recovery procedure.

**As of this report, the operational cutover (A5) remains on HOLD.** The maintainer reports that production services and on-chain state were not changed by the latest offline correction work. No claim is made that the proposed corrections have been deployed or validated under the actual runtime identity.

Public details intentionally omit credential locations, secret-bearing environment names, sensitive endpoint behavior, and operational recovery commands. Those are handled in controlled engineering evidence and security review.

## Open Validation Items

- Independent final review of the latest credential-isolation, provider-policy, and deployment changes.
- Owner authorization and verification of the effective production configuration and trust-policy inputs.
- Controlled activation of the existing pipeline under its approved execution gates.
- A **new** Native L1 observation successfully consumed by MerklePress and sealed into a batch.
- Real full-proof/RISC Zero verification feeding automatic persisted acceptance.
- Arc FAST and Sepolia ZK on-chain anchoring with independent verification and the required dual-finality evidence.
- Independent, reproducible byte-for-byte readback and public evidence package for Arc test anchors.

## Important Integration Boundary

**Arc synthetic test anchors are not the same as real FidoMota pipeline batches.** The Questbook Arc compatibility milestone (M1) concerns isolated test anchors. A separate real-batch milestone (M3) requires three real batches from at least two pipeline runs, independent readback without the operational database, and rejection of a tampered batch file. Neither requirement should be conflated with Mission-001's intended single new-observation end-to-end acceptance.

## What This Does Not Prove

This work does not establish physical-source authenticity, production key safety, real RISC Zero operational success, automatic on-chain dual finality, commercial payment capability, live customer traction, or completion of all Questbook milestones. Cryptographic evidence can attest to a recorded observation and its integrity; it does not itself establish the objective truth of the underlying physical event.

## Next Engineering Focus

Complete the independent review and owner-approved cutover gates, then run the original single pipeline using a new real observation. The target is a verifiable end-to-end Mission-001 result; if that result cannot be demonstrated, progress will be reported as incomplete rather than presented as success.

We are building evidence infrastructure where **observations are recorded as observed, and trust claims must remain independently checkable**.

## Publication Clarification — 2026-11-20

This entry is a public engineering status summary based on maintainer-supplied reports, sealed-artifact descriptions, and separately identified focused audit findings. It is not a publication of the private test evidence, production logs, credentials, or an independent replication of the complete system. Publication of this text does not authorize operational activation, code application, or changes to grant commitments.
