# Valve E Phase 1: production deployment and bounded observation closure

**Date:** 2026-11-12
**Project:** FidoMota / MOTION GATE, Mission-001 (new-observation end-to-end recovery)
**Status:** Phase 1 deployment complete — post-restoration observation accepted with exception; production E2E not complete

## Summary

Following the November 8 Valve E B2R static closure and launch-procedure review, the recovery effort progressed to an approved Phase 1 deployment into the existing MOTION GATE operational repository.

The deployment replaced 21 approved files, installed and verified the Materializer configuration, and restored four previously active operational timers.

One manually initiated Materializer tick and three subsequent automatically scheduled ticks completed successfully within the observed checks.

However, no eligible new v3 batch was processed during these executions. Full Proof generation, pinned Rust proof-tool execution on an eligible batch, and new-observation Dual Finality remain unverified.

The post-restoration observation also encountered a snapshot-tool precondition mismatch. Its original HOLD was preserved, and the final State was not independently validated.

The accepted disposition is:

**PHASE1_DEPLOYMENT_COMPLETE / POST_RESTORE_OBSERVATION_ACCEPTED_WITH_EXCEPTION**

## 1. Recovery objective and deployment boundary

Mission-001 aims to recover the original single operational pipeline, not establish a parallel demonstration path.

New authentic device observations must move through intake, Native L1, MerklePress, batching, proof generation, and the independent FAST and ZK anchoring lanes.

The final acceptance target also requires independent verification and original-content binding.

FAST and ZK are distinct downstream lanes. A successful Materializer execution is not equivalent to successful proof generation, and an on-chain commitment is not itself independent verification of a zkVM receipt.

Valve E Phase 1 addressed the v3 batch compatibility and Materializer operational boundary.

Phase 2 intake-worker activation was not authorized.

## 2. Deployment and configuration

The controlled deployment completed the following operations:

- Preserved the original timer states and pre-deployment evidence.
- Completed the approved preflight and staging procedures.
- Verified the existing Materializer State before deployment.
- Installed the required systemd environment and pinned proof-tool configuration.
- Confirmed the effective artifact mode was NOT_S3.
- Replaced exactly 21 approved files in the existing repository.
- Verified the deployed files and confirmed that excluded Phase 2 source files remained unchanged.
- Restored the supporting operational timers.
- Restored the Materializer timer after reviewing the first execution.

The recorded replacement and post-deployment verification both passed.

The existing operational pipeline remained the sole authoritative execution path.

## 3. First Materializer execution

The first manually initiated tick completed with:

- Service state: inactive / dead
- systemd result: success
- Exit status: 0
- Journal entries bound to that execution: 95 of 95
- Tick summary: present
- Matching failure-code patterns: zero

The original post-tick State validation encountered a procedure defect: it referenced a module in the staging directory after deployment had moved that file into the repository.

A separate recovery validation used the hash-pinned deployed State module and the preserved snapshot.

The recovered classification was STATE_VALID, with all 33 required keys present.

The original HOLD evidence was retained rather than overwritten.

## 4. Automatic execution after timer restoration

After restoring the Materializer timer, three additional scheduled executions were observed.

Each execution had:

- An invocation-bound successful systemd termination record.
- Exactly one application tick summary.
- Application-level ok:true.
- An empty failed_lanes list.
- Zero matches for the specified failure-code patterns.

The historical cutover batch was classified as historical_out_of_scope. The backlog query reported exhaustion.

These observations demonstrate successful repeated execution of the deployed no-work path.

They do not demonstrate actual v3 Full Proof generation.

## 5. Post-restoration observation exception

The dedicated observation checker independently assessed the three automatic executions.

Its final State snapshot step returned HOLD.

The reused snapshot tool requires both the Materializer service and timer to be inactive. That precondition was appropriate during the quiescent deployment phase but incompatible with observation after the timer was intentionally restored to active.


The observation wrapper also failed to preserve the child tool's stderr, initially obscuring the reason.

The successful tick observations remain recorded, but the final post-restoration State was not independently classified as STATE_VALID.

A STEP11_OBS_PASS result was not produced.

The closure decision explicitly accepts this observation exception without converting the failed check into PASS.

## 6. Independent review and remaining risks

Independent static review identified two State keys added through defaults:

- record_index
- last_materialized_record_index

No State cursor reset or persisted hold loss was identified from those additions within the audited scope.

The deployed backlog SQL ordering and follow-selection rules were compared with the preceding repository baseline.

Two outstanding risks remain:

**B-19 — Backlog discovery completeness**

A finalized batch becoming visible behind the persisted cursor ordering boundary might escape normal backlog selection.

The finalization writers, ordering rules, and actual finalized-batch inventory require further investigation before E2E.

**B-20 — Cutover-pin progression**

The new cutover-pin stop condition requires observation to ensure that backlog progress is not unexpectedly blocked.

These are open engineering issues, not completed fixes.

## 7. Verified status

| Workstream | Recorded status |
| --- | --- |
| Approved Phase 1 file deployment | PASS |
| Materializer configuration and NOT_S3 checks | PASS |
| First manually initiated Materializer tick | PASS, with separate State recovery validation |
| Restoration of operational timers | PASS |
| Three post-restoration automatic ticks | PASS within observed checks |
| Final independent State classification | UNVERIFIED — accepted observation exception |
| New v3 Full Proof generation | NOT DEMONSTRATED |
| Pinned proof-tool execution on an eligible batch | NOT DEMONSTRATED |
| B-19 / B-20 | OPEN |
| Phase 2 intake-worker activation | HOLD |
| New-observation FAST and ZK Dual Finality | NOT DEMONSTRATED |
| Mission-001 final acceptance | NOT COMPLETE |

## Not done yet

The remaining prerequisites include GRACE configuration, NC1–NC3 and FAST R4, key authority procedures, FAST/ZK/fleet operational readiness, verifier authority, legacy S3 configuration review, and the B-19 and B-20 investigations.

The first real v3 Full Proof and independent on-chain verification must still be demonstrated using authentic new observations.

## Next

The next target is the controlled single-device Mission-001 E2E using the existing operational pipeline.

Success requires authentic observation propagation, verifiable Full Proof generation, both FAST and ZK anchoring, and independent verification of the resulting commitments and content bindings.

The immediate Phase 1 deployment is closed, but the broader end-to-end mission remains unfinished.

The governing principle remains unchanged: record what was observed, preserve its provenance and integrity, and never confuse a successful-looking execution status with proof of an unobserved operation.
