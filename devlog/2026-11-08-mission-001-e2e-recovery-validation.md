# Valve E B2R: static closure and a launch-procedure evidence gate

**Date:** 2026-11-08
**Project:** FidoMota / MOTION GATE, Mission-001 (new-observation end-to-end recovery)
**Status:** In progress — isolated host regression not executed; production E2E not complete

## Summary

Since the November 3 update on pinned Rust proof binaries and descriptor-bound exporter execution, the recovery effort has advanced to an isolated regression candidate for **Valve E**, the compatibility boundary between newer v3 batch artifacts and the ZK proof path. The authoritative B2R package received separate static PASS findings from BLAME and Dr. DEX. These are source-level findings, **not** a successful host regression or permission to execute.

A subsequent independent static audit of the B2R host launch procedure found a new **procedure-only blocker**: a post-run manifest-content verification failure could be obscured by a later successful command, while the written acceptance criteria could still allow a successful classification. The procedure remains on HOLD pending a focused correction and re-audit. The audited B2R package itself has not been changed by that finding.

## 1. What the recovery is trying to restore

Mission-001 is intended to restore the **existing single operational pipeline**, rather than create a parallel demonstration path. New authentic observations from the designated device must be processed automatically through the original intake, Native L1, MerklePress and batch layers, and reach both anchoring lanes with independent verification and content binding.

FAST and ZK are distinct downstream lanes, not a single serial sequence in which FAST waits for RISC Zero. Historical evidence reached FAST anchoring and a ZK receipt-commitment anchor on Sepolia with recorded chain finality, but the ZK submission was manual and some other historical steps have uncertain operators. On-chain recording of a receipt commitment is not itself an independent cryptographic verification of the RISC Zero receipt. These historical results do not satisfy the new-observation, autonomous **Dual Finality** acceptance target.

New v3 batches encounter an existing compatibility boundary in the proof exporter/materializer. Valve E work addresses that ZK-lane boundary without replacing the operational pipeline.

## 2. From the earlier proof-tool work to B2R

The November 3 update documented the isolated build-and-pin of three Rust proof binaries, the proof exporter's move away from `cargo run` to descriptor-bound execution, and a 42-case isolated exporter regression. Those results remain scoped to their audited artifacts and tests; they were not a production activation.

The subsequent work developed an isolated Materializer regression candidate and a host launch boundary. Reviews of successive launcher-package revisions caught failures that could undermine the truthfulness of the eventual result:

- **B1:** the suspend-history check could start from `NONE_FOUND` even when the underlying capture or parse was unverifiable. That could permit a false completion outcome.
- **B2:** the suspend-history check was corrected, but the producer exit status traveled in-band with captured bytes. A forged or incomplete trailer could be mistaken for a successful status.
- **B2R:** the status was obtained separately through Bash `wait`, with the capture treated as invalid unless the required evidence checks succeeded.

BLAME's review and Dr. DEX's independent focused audit both reported **STATIC PASS** for B2R on November 8. The latter reported the suspend-history static closure as PASS and confirmed preservation of the earlier F1 fix. No real host regression was run to establish these verdicts.

## 3. A blocker found in the launch instructions

A step-by-step host launch procedure was written to verify the archive, inspect safe extraction, check manifests and host prerequisites, maintain an exclusive launch lock, separate preparation from the owner's execution decision, and retain post-run evidence.

The independent static audit returned **PROCEDURE_STATIC_HOLD** on its first revision. In the post-run step, strict verification of the retained evidence manifest could fail, yet a following `cat` command could succeed. The written three-part success criteria did not unambiguously require **successful verification of all manifest entries after the run**. Thus evidence altered after a correctly completed launch could potentially still be accepted as a success.

The required correction is deliberately narrow: propagate failure from every mandatory post-run verification and require consistency among the actual launcher disposition, exit status, verified seal, result files and **strict manifest-content validation**. The remaining identified preparation-command and process-observation limitations were classified as nonblocking within the established bounded safety model.

This is a defect in the **acceptance procedure**, not a reversal of the B2R package's static audit. The procedure must pass focused independent re-audit before any preparation or execution decision.

## 4. Verified status as of November 8

| Workstream | Recorded status |
| --- | --- |
| Isolated pinned Rust proof binaries and exporter boundary | Previously built, tested and audited within their defined scopes |
| Valve E B2R regression package | BLAME STATIC PASS; Dr. DEX STATIC PASS |
| B2R host launch procedure, revision 1 | PROCEDURE_STATIC_HOLD — post-run evidence acceptance blocker |
| B2R host regression | NOT EXECUTED |
| Production service/configuration changes for this run | NOT AUTHORIZED |
| New-observation automatic FAST and ZK anchoring, independent verification and Dual Finality | NOT DEMONSTRATED |
| Mission-001 final acceptance | NOT COMPLETE |

The host-specific behavior of Bash process-substitution `wait`, journal capture, inhibitors and process qualification is still unverified. One isolated dependency environment also resides in reboot-sensitive temporary storage, so the run plan explicitly prohibits reboot before its evidence is safely retained. These facts remain operational constraints, not claims of runtime success.

## Not done yet

- Correct and independently re-audit the launch procedure's post-run acceptance rule.
- Obtain an explicit, separate decision for host preparation, and later a separate decision for execution.
- Run and independently audit the isolated B2R Materializer regression on the actual host.
- Complete the necessary in-place production integration and restore the autonomous FAST and ZK lanes.
- Demonstrate independent cryptographic verification, original-content binding and Dual Finality for **new** authentic observations, without manual CLI substitution or a parallel pipeline.

## Next

The immediate step is a **document-only** correction to the launch procedure, followed by a focused independent static re-audit. Any host preparation or regression execution remains subject to a separate owner decision. Only observed and retained runtime evidence can move the regression from static review to a runtime verdict.

The project principle remains unchanged: record what was observed, preserve its provenance and integrity, and never confuse a cryptographic commitment—or a successful-looking log line—with proof of the underlying physical event or a verified end-to-end run.
