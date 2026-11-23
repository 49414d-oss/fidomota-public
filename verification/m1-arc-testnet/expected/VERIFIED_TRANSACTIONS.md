# M1 verified transaction identifiers and expected anchor values

Arc Testnet, chain id 5042002 (`0x4cef52`). Values are copied from `m1_expected.json`. Block timestamps are as read from chain on 2026-11-23.

**Contract `MotionGateAnchorV0`:**

| field | value |
|---|---|
| address | `0x19fcc7ee063349051441ca89dc9dc894ffa457d2` |
| deployer (signer of all four transactions) | `0xc627615380dbfb7e145046156457739a4d6142b8` |
| deployer nonce | 0 |
| runtime code | 377 bytes; sha256 `298af41a62f9a192a64c4b159b27b4d9e590cdba3d9eae1350696d3dcb5f1363`; keccak256 `0xf7e2b1b3b05d144b2225fb3c31a4503cb99e4aff9b1f7cd442b75fa356f4e486` |
| init code | 405 bytes; sha256 `7d6453d0a4fe0bc9cbebd0d3100599468ef706fe99dc5a9c4bc1ed19bee1d07a` |
| function | `anchor(bytes32 root, bytes32 meta)`, selector `0xa21f3c6a` |
| event | `Anchored(bytes32 indexed root, bytes32 indexed meta, address indexed who, uint256 ts)`, topic0 `0xef9ad88ed81d42bc0ea6682949bb2f6da6a414e7221999a4c5bcbd5b21108151` |

**Transactions:**

| # | tx | nonce | block | block hash | block time (UTC) | gas used | fee (USDC) |
|---|---|---|---|---|---|---|---|
| deploy | `0xa9b68fdd1461b495efb6badfb757211869e82209754993e35fbf256a0c9d02c7` | 0 | 73005199 | `0x41e02c1329681bbc1b5edd7e82e2f5222c72c87bbf7eebd808e45802b2572cbc` | 2026-11-19 10:39:07 | 134,751 | 0.002829771 |
| anchor 1 | `0x4a50e85bbb93d6aae4e714bec1889783bdd3372541cebb33d9a42bb9d4e37122` | 1 | 73005604 | `0x84ae65ef85afeb35277360ed66a2937450b292ece086f7220ab9d0b00f5a7729` | 2026-11-19 10:42:33 | 24,795 | 0.000520695 |
| anchor 2 | `0x9e11e64f6b23cf78077452910d171bec241a921690415a0071911ef39722d7c1` | 2 | 73005947 | `0xc4d155d564bd111566f189d4739ea6276374449ebad007403459fc065e077090` | 2026-11-19 10:45:27 | 24,795 | 0.000520695 |
| anchor 3 | `0x3d3a2d56857b986bc68c18008aa69ee3cd79cef08a059f4c6522e2e3cfb5a3f6` | 3 | 73006326 | `0x4293f1d715cb546a538d29bf80842ddc61d20989ba3e76fbeedd9db7e3af22a3` | 2026-11-19 10:48:39 | 24,783 | 0.000520443 |

- **Total fees:** 0.004391604 USDC. This equals the signer's native-balance drop between block 73005198 and block 73006326 (20.000000000 → 19.995608396 USDC), as read on 2026-11-23.
- **Fee settings:** every transaction is type 2, with max fee 41 gwei and priority fee 1 gwei. The effective gas price was 21 gwei: base fee 20 gwei plus the 1 gwei tip.

**Anchor contents (synthetic).** `meta` = `0x4d472d4d312d53594e5448455449432d56310000000000000000000000000000` (ASCII `MG-M1-SYNTHETIC-V1`, zero-padded), and `who` is the signer in every case.

| # | preimage (UTF-8) | root = keccak256(preimage) | event `ts` | log index |
|---|---|---|---|---|
| 1 | `MG-M1-SYNTHETIC-V1\|run=M1-ARC-20261119T103000Z\|anchor=1` | `0x8f6ae6a81a75993fe7d96f709286b3ac9464c817efdca618820a4288f1295d5a` | 1795084953 | 17 |
| 2 | `MG-M1-SYNTHETIC-V1\|run=M1-ARC-20261119T103000Z\|anchor=2` | `0xb91ebc8cc914c17a5ab6bee4cccfb813200ba569db189df64c37dcda7f2e9a1e` | 1795085127 | 8 |
| 3 | `MG-M1-SYNTHETIC-V1\|run=M1-ARC-20261119T103000Z\|anchor=3` | `0xe81205670509ecc716b91b7655430011affb9348facf10c6920f4aab59c4242e` | 1795085319 | 13 |

Each anchor transaction's calldata is exactly `0xa21f3c6a ‖ root ‖ meta`, 68 bytes.
