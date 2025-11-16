# Rust Implementation Issues - Investigation Summary for swhid-rs

**Total tests where Rust produces different SWHID**: 24
**Rust-only outliers (critical)**: 24
**Rust matches some implementations**: 0

## Issues by Object Type

### REV (11 issues)

- ⚠️ **CRITICAL** `comprehensive_branch_develop` (git/basic)
  - Rust: `swh:1:rev:f71741a120d98e47080c3dda3f3fc9cc8496eb9b`
  - Others (git-cmd): `swh:1:rev:5e8a55e005e0003cd976ac876b2a598bf0d91362`

- ⚠️ **CRITICAL** `comprehensive_branch_feature-a` (git/basic)
  - Rust: `swh:1:rev:47f0e7d194be219cedbf513a370469a72d941a7f`
  - Others (pygit2, git, git-cmd): `swh:1:rev:870dcb724e95453ab9dd2f4a58f98aeb0dcb7764`

- ⚠️ **CRITICAL** `comprehensive_branch_feature-b` (git/basic)
  - Rust: `swh:1:rev:0c613e9bb38be853505aa7e44d91d9f746907378`
  - Others (git, pygit2, git-cmd): `swh:1:rev:229740cdc7665b5718e34e04a59fd9e981f2c149`

- ⚠️ **CRITICAL** `comprehensive_branch_hotfix` (git/basic)
  - Rust: `swh:1:rev:e685cfe42940552b757dc8476b2a91204d00ba6c`
  - Others (pygit2, git, git-cmd): `swh:1:rev:bfe454d11532e851d36ac5c2c014f12a19c9f720`

- ⚠️ **CRITICAL** `comprehensive_branch_main` (git/basic)
  - Rust: `swh:1:rev:168b909d160d44771999f031729f4048900a6550`
  - Others (pygit2, git, git-cmd): `swh:1:rev:997cc01b55bd38cbcc49f113c9f796e528559adf`

- ⚠️ **CRITICAL** `initial_revision` (git/basic)
  - Rust: `swh:1:rev:e41b70b56ccc1bcb8229f77f420be4cb097552ef`
  - Others (pygit2, git, git-cmd): `swh:1:rev:d8693ad0daffe017605f67d723b66e0c213035cb`

- ⚠️ **CRITICAL** `merge_commits_head` (git/basic)
  - Rust: `swh:1:rev:27130276084fcdb3be6c5dd40f5c6bcb5e173a67`
  - Others (git-cmd, git, pygit2): `swh:1:rev:b644fc71fa76537858cb421f5bc6fd2f0f475d88`

- ⚠️ **CRITICAL** `merge_revision` (git/basic)
  - Rust: `swh:1:rev:7490f27fc53282764129d4b23cf83b5ff2156dca`
  - Others (pygit2, git, git-cmd): `swh:1:rev:395d056259d91ef412349c5f6bc8273724e82d4b`

- ⚠️ **CRITICAL** `simple_revision` (git/basic)
  - Rust: `swh:1:rev:7490f27fc53282764129d4b23cf83b5ff2156dca`
  - Others (pygit2, git, git-cmd): `swh:1:rev:395d056259d91ef412349c5f6bc8273724e82d4b`

- ⚠️ **CRITICAL** `simple_revisions_first` (git/basic)
  - Rust: `swh:1:rev:2af49aff8d6f1855f1423b833de046cb3f629e11`
  - Others (git, git-cmd, pygit2): `swh:1:rev:b7fdd35912b16682ac6e989f75d41870a0f9d904`

- ⚠️ **CRITICAL** `simple_revisions_head` (git/basic)
  - Rust: `swh:1:rev:2af49aff8d6f1855f1423b833de046cb3f629e11`
  - Others (pygit2, git, git-cmd): `swh:1:rev:b7fdd35912b16682ac6e989f75d41870a0f9d904`

### REL (8 issues)

- ⚠️ **CRITICAL** `comprehensive_tag_v1.0.0` (git/basic)
  - Rust: `swh:1:rel:38e0b95b302dcbc4bd55c5a2666d54ee15df1b84`
  - Others (git, pygit2, git-cmd): `swh:1:rel:5286f13487f495993f96ae05b33d10f5f93b82f4`

- ⚠️ **CRITICAL** `comprehensive_tag_v1.0.1` (git/basic)
  - Rust: `swh:1:rel:a8e1a39d8a764f766f47d424ac68a152db6050be`
  - Others (pygit2, git, git-cmd): `swh:1:rel:bce2af7aab2b64d3198976a83cefffcd6f5b8f54`

- ⚠️ **CRITICAL** `comprehensive_tag_v1.1.0` (git/basic)
  - Rust: `swh:1:rel:6ca69b71710e85844017bb2a84da268e1f962934`
  - Others (git, pygit2, git-cmd): `swh:1:rel:00f5b371d166cff902716f88c59e97eb21d18a7a`

- ⚠️ **CRITICAL** `comprehensive_tag_v2.0.0` (git/basic)
  - Rust: `swh:1:rel:9f98583e5ae332ce0d4e3afb953878fc82fa96b6`
  - Others (git, pygit2, git-cmd): `swh:1:rel:eb40be8808a4c33f3d3daab634344b673996a49f`

- ⚠️ **CRITICAL** `comprehensive_tag_v2.1.0` (git/basic)
  - Rust: `swh:1:rel:b5271cff087e0b87508df9df233739b6d171ef9b`
  - Others (pygit2, git, git-cmd): `swh:1:rel:edaf91f706742fcb19591f59b5397b0a7a09ac39`

- ⚠️ **CRITICAL** `annotated_release_v1` (git/basic)
  - Rust: `swh:1:rel:3e3709e0650b55c17f4c5a886720b3fa0a71bd68`
  - Others (pygit2, git, git-cmd): `swh:1:rel:976993709ac2245f5128a5205653b26eab703fe1`

- ⚠️ **CRITICAL** `annotated_release_v2` (git/basic)
  - Rust: `swh:1:rel:f5b5fb130f927c1cb50d1c336b54f8b7e03bb86c`
  - Others (git, pygit2, git-cmd): `swh:1:rel:a7c9921fab18efe11882532bdf751f44a704917a`

- ⚠️ **CRITICAL** `tag_types_annotated` (git/basic)
  - Rust: `swh:1:rel:50cbfa7951b84d69da951d936a57e67654bcb7d9`
  - Others (git, pygit2, git-cmd): `swh:1:rel:302822701a46791d97f5e372255b7db078a342e2`

### SNP (5 issues)

- ⚠️ **CRITICAL** `branch_ordering` (git/basic)
  - Rust: `swh:1:snp:6af89977bb9778bff542886fc872892057c40ea7`
  - Others (python): `swh:1:snp:e44a647204ef944dd0fd28302a0d65124b93cd36`

- ⚠️ **CRITICAL** `complex_merges` (git/basic)
  - Rust: `swh:1:snp:007da37517ac622c72faffd68b6338f8b44e57cd`
  - Others (python): `swh:1:snp:604524a5decb4c927258eb4d9f5a121c48218bd4`

- ⚠️ **CRITICAL** `merge_commits` (git/basic)
  - Rust: `swh:1:snp:6349a0fabe9bcea2a4c4712637cf4f91880e0bc0`
  - Others (python): `swh:1:snp:5c9c3c9be880d0ac89707304017006716d6749a6`

- ⚠️ **CRITICAL** `simple_revisions` (git/basic)
  - Rust: `swh:1:snp:4beb495cdf279920339b8400a8aa0a1bfd6ad3e3`
  - Others (python): `swh:1:snp:2f1450c1be7a6945b69d2c3724ac30a3be025e92`

- ⚠️ **CRITICAL** `tag_types` (git/basic)
  - Rust: `swh:1:snp:ee1b5ffe457469e0cd4192ad3a9a99cb24fd872e`
  - Others (python): `swh:1:snp:98a720761e59ff1704a84b38e0f3f683a6c2d5d9`
