# FidoMota — MOTION GATE

## Mission-001 Verification Evidence

**Result:** MISSION-001 SUCCESS — `DUAL_FINALITY_MATCHED`

This package publishes the acceptance record and a field-level public evidence extract for the Mission-001 target batch. Together they bind the batch identity, the Arc FAST root anchor, the Ethereum Sepolia ZK receipt anchor, the RISC Zero receipt and journal commitments and the acceptance verdict to a single 32-byte batch root.

### Target Batch

| Field | Value |
| --- | --- |
| Batch reference | 5641 |
| Batch ID | `MG_BATCH_blake3_v1_20261120_1795198336847` |
| Leaf index | 0 |
| Batch root | `4d1569b7a06031e01e72cdc902ed22d92308c998ea9eeaabaac882a95846d15f` |
| Payload hash | `ca6dcc25b63e4e27374f3bda6e03afa2f1b05bccf5b770f3d420ffdea35355fa` |

### FAST Lane — Arc Testnet Root Anchor

| Field | Value |
| --- | --- |
| Chain ID | 5042002 |
| Block | 73250345 |
| Block hash | `0x7711f8052d25e01f9e3ccbf748c3c02b01687e83dc5d541221471f3b7858c611` |
| Log index | 10 |
| Contract | `0x19fcc7ee063349051441ca89dc9dc894ffa457d2` |
| Transaction | [`0x9c8084fd…9b96`](https://explorer.testnet.arc.io/tx/0x9c8084fdb78334f0300fcd304bebb8ddafeccd756e73f5c1345f4b2370539b96) |

The FAST contract is the `MotionGateAnchorV0` deployment documented in the [M1 verification package](../m1-arc-testnet/README.md).

### DEEP Lane — Ethereum Sepolia ZK Receipt Anchor

| Field | Value |
| --- | --- |
| Chain ID | 11155111 |
| Block | 12223891 |
| Block hash | `0x6ca690f704243fdcff57b0eaf9699a4a06b6927066ad6cd07ab10dbb4d80093e` |
| Contract | `0x76f09023e0ce912ff62ad796c2838630f8975f6f` |
| Transaction | [`0xf3f39845…5d1`](https://sepolia.etherscan.io/tx/0xf3f3984572c14c6cf08455171adbf92fb1d0f28736c40bb54f3fcbeaa25b55d1) |

### Proof Commitments

| Commitment | Value |
| --- | --- |
| Batch root | `0x4d1569b7a06031e01e72cdc902ed22d92308c998ea9eeaabaac882a95846d15f` |
| Receipt SHA-256 | `0x5a862ac8cd4539c9db37d521ab30b7f4c9a45222cb715ede9bb6fc84f856e16b` |
| Journal SHA-256 | `0x7ab63e9ed7696c29a84ff26f79762f9b021064e6ee2416d2628a1472f932d59f` |
| Guest image ID | `0x365a458af01b335e1855f7f878eaa3976ed42ad16edad4c4bdb679cdfb66621b` |
| Verifier-program hash | `0x29ed94405f9e722f8aed9304feaa8be295c7886aa90bd4680fbfebfa77ffe015` |

The 109-byte RISC Zero journal carries the segment root (bytes 13–44), the batch root (bytes 45–76) and the verifier-program hash (bytes 77–108). For this single-segment batch, the segment root and the batch root are equal.

### Acceptance Verification Result

| Check | Recorded result |
| --- | --- |
| Acceptance outcome | `P73_ACCEPTED` |
| Acceptance verdict | `ACCEPTED` — `ACCEPTANCE_EVIDENCE_VERIFIED` |
| Acceptance execution | `S3_EXIT 0 PIPE 0 0 0` |
| Bound input artifact set | `keys_ok True` |
| Bound input artifact hashes | 8 of 8 match |
| Journal format | `journal_format_ok True` |
| FAST evidence hash | `fast_evidence_sha_ok True` |
| FAST transaction facts | `fast_facts_ok True` — chain 5042002, block 73250345, log index 10 |
| Batch-root equality | `ROOT_EQUAL_ALL True` |
| Acceptance record status | `VALID`, `acceptance_verified: true`, `invalid_reason: null` |
| Dual Finality | `DUAL_FINALITY_MATCHED` |
| Root match | `ROOT_MATCH_TRUE` |
| L3 Evidence Explorer binding | `L3_BOUND_OK true` |
| Post-run verification | `S4_DONE` |

All seven final verification criteria passed.

Six representations of the batch root matched across all 32 bytes: the journal batch root, the acceptance identity batch root, the FAST anchor root, the DEEP payload's root-anchor batch root, and the anchored and journal roots displayed by the L3 Evidence Explorer.

These six are the values compared in post-run verification; the `batch_root_equality` section of the public extract compares a different set of five values held in the evidence file, including the segment root.

The submission's operational state label remains `TX_OBSERVED_ACCEPTANCE_UNVERIFIED`, exactly as observed. This is the lifecycle label of the submission record. It is separate from the acceptance record status, which is `VALID`. The acceptance record carries no lifecycle-write authority, and the operational state was not changed during acceptance verification.

The `boundary` flags in the published `acceptance.json` (`execution_authority`, `lifecycle_write_authority` and `validity_finality`, all `false`) declare that the record itself holds no such authority or determination; validity finality is derived by the L3 projection layer from a valid, bound acceptance record, and L3 reported `validity_finality: true`.

The console and L3 results above come from the recorded execution evidence of the Mission-001 acceptance-verification run on November 28, 2026.

### Package Contents

| Path | Contents |
| --- | --- |
| `evidence/acceptance.json` | Original acceptance record, published byte for byte |
| `evidence/acceptance_evidence_public_extract.json` | Public extract of the accepted acceptance evidence, using allowlisted fields |
| `SHA256SUMS` | SHA-256 manifest of the published files |

#### Acceptance Record

`evidence/acceptance.json` is the original acceptance record, unmodified.

SHA-256: `d3200866d46c7bf829a8c6b4d17363376bffd00b729bdbe5412e82967e687e60`

#### Acceptance Evidence Extract

The accepted acceptance evidence contains private host paths and is not published. `evidence/acceptance_evidence_public_extract.json` reproduces its public identifiers and results through an explicit field allowlist. Two sections, `artifact_hash_binding` and `batch_root_equality`, are derived comparisons and are marked as such.

| Artifact | SHA-256 |
| --- | --- |
| Public extract (this package) | `aca97bbdef12c7e08abd5ddfb2650ce1f76eb187c95310de18ecbfebae0460d5` |
| Preserved private source artifact | `6755941518fb55d1fb4b523e47606fe7c3197322230d436b77c0ffbd4876159d` |

The second value is the SHA-256 of the preserved private source artifact. It is a provenance reference and cannot be reproduced from the public extract alone.

### What You Can Check

```sh
cd verification/mission-001

# 1. Integrity of the published files
sha256sum -c SHA256SUMS

# 2. Journal structure and journal hash, from the published acceptance record
python3 -I -B -c '
import json, hashlib
a = json.load(open("evidence/acceptance.json"))
j = bytes.fromhex(a["expected_journal_hex"])
root = a["identity"]["batch_root"]
print("journal_bytes", len(j))
print("segment_root_at_13_equals_batch_root", j[13:45].hex() == root)
print("batch_root_at_45", j[45:77].hex() == root)
print("journal_sha256", hashlib.sha256(j).hexdigest())
'
```

The journal SHA-256 printed by step 2 should equal the journal commitment above (`7ab63e9e…d59f`).

Both anchor transactions can be inspected on the public explorers linked above. They should show the listed contracts, and the Arc anchor event should carry the batch root.

### Verification Scope

- **Acceptance Verification.** Acceptance Verification was performed by a dedicated acceptance evaluator (`zk_receipt_anchor_acceptance_v1`). In this document, independence means that verification is separated from evidence production. The evaluator holds no execution or lifecycle-write authority. It is not a third-party audit, and no external organization has reproduced the complete Mission-001 system.
- **Assurance classification: `SINGLE_PROVIDER_REDUCED`.** Live chain data for each chain came from a single RPC provider selected by the project (`OWNER_SELECTED_ENDPOINT_TRUST`). Confirmation depth was not recorded. The acceptance policy requires `FINALIZED` and canonical-chain inclusion on both chains.
- **Verifier provenance: unresolved.** The Rust verifier binary is pinned by SHA-256 and its hash was measured at run time. Its build provenance is recorded as `UNKNOWN`.
- **Receipt scope.** Receipt verification binds the guest image ID and the journal roots (`IMAGE_AND_JOURNAL_ROOTS_ONLY`). It does not establish a record-specific guest execution.
- **On-chain boundary.** The Sepolia contract records proof-associated commitments. RISC Zero proof verification takes place off-chain.
- **Source observations.** The batch was formed from software-generated virtual-EV observations, not physical measurements.
- **Public tooling.** This package does not include a complete public end-to-end verifier. External reproduction of the complete Mission-001 workflow is a future deliverable.

---

**FidoMota — MOTION GATE**

*Light Proof. Heavy Trust.*
