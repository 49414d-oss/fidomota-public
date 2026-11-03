# Pinned Rust proof binaries and descriptor-bound execution in the proof exporter

**Date:** 2026-11-03
**Project:** FidoMota / MOTION GATE, Mission-001 (new-observation end-to-end recovery)

## Summary

Mission-001 moved from source checks to real artifacts today. The Rust proof tools were built once in an isolated sandbox, and the binaries were published as read-only, hash-pinned copies that passed an independent audit. The proof exporter no longer runs these tools through `cargo run`. It now executes the exact audited bytes through a pinned file descriptor. A compatibility test against a real historical proof is designed, and its database input has been captured. The production server has not been changed. The final pre-execution audit found three blockers in the isolated test runner; no real D2 compatibility run has been authorized.

## 1. One isolated build, three pinned binaries

The build-and-pin step compiled exactly three binaries in a dev profile:

- `mg_l2_verify_full_proof`
- `mg_l2_build_full_proof`
- `mg_l2_encode_guest_input`

The build ran offline in a sandbox:

- no network, read-only sources, and 30 vendored crates checked against `Cargo.lock`
- a 3 GiB memory cap with swap disabled, and a 30-minute limit
- 24 preflight checks before Cargo started

The build finished in 6.5 seconds with a memory peak of about 350 MiB and no out-of-memory events. Every crate compiled fresh. The build produced six dead-code warnings and no errors. Each binary was matched to exactly one Cargo artifact record and copied to a new directory as an independent file:

- file mode 0500
- link count 1
- the same SHA256 across five separate records

The run sealed 100 evidence files. A separate audit then verified the seal, the file identities and the Cargo records. The binaries are accepted as the reference for the next steps, with no operational use yet.

The execution procedure went through four revisions before the run. Each revision closed a case where a failure would have been reported incorrectly or evidence could have been lost. The pre-run check also stopped the run once, because available memory was 305 MiB below the threshold. The run was started only after memory recovered.

## 2. Descriptor-bound execution in the exporter

The exporter used to run the proof builder and the guest-input encoder with `cargo run`, so Cargo decided which bytes ran. Both call sites now follow the same contract as the existing pinned verifier:

- capture the configured file through a pinned descriptor (no symlinks, regular file, size limit, owner and mode checks)
- check the SHA256 of the captured bytes on every call
- execute that same descriptor as `/proc/self/fd/3`, with an empty environment, a timeout and output limits
- re-check the file identity after the run, and reject the result if anything changed
- no Cargo fallback

An isolated regression suite checks this contract with test-only executables. It covers 42 cases, including:

- symlinks, wrong owner or mode, hash mismatch, and empty or oversized files
- timeouts and signals
- the executable being modified while running
- partial outputs kept without retry

The unmodified exporter fails the suite, so the cases measure the change itself.

Two defects in failure reporting were found and fixed along the way:

- Large error output could be cut off mid-JSON.
- A combined failure (output limit and executable change in one run) recorded a wrong flag.

Testing also showed that Node 20's `spawnSync` applies its output limit to stdout and stderr **combined**, not per stream. The documentation was corrected.

## 3. Compatibility test against a historical proof

The builder source changed substantially since the historical proofs were made. The next test therefore checks whether the new builder preserves the v2 proof content for one real historical batch (August 2026, 162 records). It does not test whether a rebuild of the same source is reproducible.

- **Comparison rule:** every key, type, value and array position must match. The only exception is the value of one top-level timestamp, `generated_at`. The guest input must match byte for byte.
- **Database input:** one row, read once from the live SQLite store.
  - A plain read-only SQLite connection can still rewrite the shared-memory `-shm` file of a WAL database. The lookup therefore used `mode=ro&readonly_shm=1`.
  - A control test with a bogus URI parameter first confirmed that the installed SQLite CLI actually applies this option.
  - Before and after the query, metadata for the database, `-wal`, and `-shm` were unchanged; the `-wal` and `-shm` content hashes were also unchanged. The database body was not hashed.
- **Test runner:** single-use. It takes an exclusive lock that is never removed, pins every input and tool, and invokes the exporter once. It passed 69 test-only cases.

## Not done yet

- the real run of the pinned binaries on the historical inputs: the independent G3 pre-execution audit returned HOLD, identifying three G4 blockers
- complete external identity checks for the runner, Node and GNU time before entering the one-shot runner
- isolate the runner startup environment from inherited preload and loader settings
- supervise and terminate the protected exporter process tree on timeout, retaining partial evidence and the consumed-attempt lock
- switching the verifier wrapper used by Content Binding verification to pinned execution
- timeout values for production callers
- applying the changes to the host, and the Mission-001 new-observation end-to-end run

## Next

The independent G3 audit verified the retained G1 evidence, historical bindings, source hashes, and all 69 TEST_ONLY regression records. It also identified three execution-safety blockers: incomplete external identity preflight, inherited runner startup environment, and incomplete descendant termination on timeout. Next, correct only those boundaries, rerun the affected isolated tests, and obtain a focused independent re-audit and an explicit separate authorization before any real D2 compatibility run. Production E2E remains pending.
