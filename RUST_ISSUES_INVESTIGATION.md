# Rust Implementation Issues - Investigation Summary for swhid-rs

## Executive Summary

**Total tests where Rust produces different SWHID**: 24  
**Rust-only outliers (critical)**: 24  
**Rust matches some implementations**: 0

All 24 issues are **critical** - Rust is the only implementation producing different SWHIDs, while all other implementations (git, git-cmd, pygit2, python) agree on the correct SWHID.

## Issues by Object Type

### REV (Revision) - 11 issues

Rust produces incorrect revision SWHIDs for all tested branches and commits. The Rust tool appears to be computing different commit SHAs than what Git actually contains.

**Pattern**: Rust consistently produces different commit SHAs that don't match the actual Git repository commits.

**Affected tests**:
1. `comprehensive_branch_develop` - Rust: `swh:1:rev:f71741a120d98e47080c3dda3f3fc9cc8496eb9b` vs Consensus: `swh:1:rev:5e8a55e005e0003cd976ac876b2a598bf0d91362`
2. `comprehensive_branch_feature-a` - Rust: `swh:1:rev:47f0e7d194be219cedbf513a370469a72d941a7f` vs Consensus: `swh:1:rev:870dcb724e95453ab9dd2f4a58f98aeb0dcb7764`
3. `comprehensive_branch_feature-b` - Rust: `swh:1:rev:0c613e9bb38be853505aa7e44d91d9f746907378` vs Consensus: `swh:1:rev:229740cdc7665b5718e34e04a59fd9e981f2c149`
4. `comprehensive_branch_hotfix` - Rust: `swh:1:rev:e685cfe42940552b757dc8476b2a91204d00ba6c` vs Consensus: `swh:1:rev:bfe454d11532e851d36ac5c2c014f12a19c9f720`
5. `comprehensive_branch_main` - Rust: `swh:1:rev:168b909d160d44771999f031729f4048900a6550` vs Consensus: `swh:1:rev:997cc01b55bd38cbcc49f113c9f796e528559adf`
6. `initial_revision` - Rust: `swh:1:rev:e41b70b56ccc1bcb8229f77f420be4cb097552ef` vs Consensus: `swh:1:rev:d8693ad0daffe017605f67d723b66e0c213035cb`
7. `merge_commits_head` - Rust: `swh:1:rev:27130276084fcdb3be6c5dd40f5c6bcb5e173a67` vs Consensus: `swh:1:rev:b644fc71fa76537858cb421f5bc6fd2f0f475d88`
8. `merge_revision` - Rust: `swh:1:rev:7490f27fc53282764129d4b23cf83b5ff2156dca` vs Consensus: `swh:1:rev:395d056259d91ef412349c5f6bc8273724e82d4b`
9. `simple_revision` - Rust: `swh:1:rev:7490f27fc53282764129d4b23cf83b5ff2156dca` vs Consensus: `swh:1:rev:395d056259d91ef412349c5f6bc8273724e82d4b`
10. `simple_revisions_first` - Rust: `swh:1:rev:2af49aff8d6f1855f1423b833de046cb3f629e11` vs Consensus: `swh:1:rev:b7fdd35912b16682ac6e989f75d41870a0f9d904`
11. `simple_revisions_head` - Rust: `swh:1:rev:2af49aff8d6f1855f1423b833de046cb3f629e11` vs Consensus: `swh:1:rev:b7fdd35912b16682ac6e989f75d41870a0f9d904`

**Investigation needed in swhid-rs**:
- How does the Rust tool resolve branch names to commit SHAs?
- How does it handle short commit SHAs (7 characters)?
- How does it handle HEAD resolution?
- Verify the commit SHA computation logic matches Git's behavior

### REL (Release) - 8 issues

Rust produces incorrect release SWHIDs for all tested annotated tags. The Rust tool appears to be computing different tag object SHAs.

**Pattern**: Rust consistently produces different tag object SHAs that don't match the actual Git tag objects.

**Affected tests**:
1. `comprehensive_tag_v1.0.0` - Rust: `swh:1:rel:38e0b95b302dcbc4bd55c5a2666d54ee15df1b84` vs Consensus: `swh:1:rel:5286f13487f495993f96ae05b33d10f5f93b82f4`
2. `comprehensive_tag_v1.0.1` - Rust: `swh:1:rel:a8e1a39d8a764f766f47d424ac68a152db6050be` vs Consensus: `swh:1:rel:bce2af7aab2b64d3198976a83cefffcd6f5b8f54`
3. `comprehensive_tag_v1.1.0` - Rust: `swh:1:rel:6ca69b71710e85844017bb2a84da268e1f962934` vs Consensus: `swh:1:rel:00f5b371d166cff902716f88c59e97eb21d18a7a`
4. `comprehensive_tag_v2.0.0` - Rust: `swh:1:rel:9f98583e5ae332ce0d4e3afb953878fc82fa96b6` vs Consensus: `swh:1:rel:eb40be8808a4c33f3d3daab634344b673996a49f`
5. `comprehensive_tag_v2.1.0` - Rust: `swh:1:rel:b5271cff087e0b87508df9df233739b6d171ef9b` vs Consensus: `swh:1:rel:edaf91f706742fcb19591f59b5397b0a7a09ac39`
6. `annotated_release_v1` - Rust: `swh:1:rel:3e3709e0650b55c17f4c5a886720b3fa0a71bd68` vs Consensus: `swh:1:rel:976993709ac2245f5128a5205653b26eab703fe1`
7. `annotated_release_v2` - Rust: `swh:1:rel:f5b5fb130f927c1cb50d1c336b54f8b7e03bb86c` vs Consensus: `swh:1:rel:a7c9921fab18efe11882532bdf751f44a704917a`
8. `tag_types_annotated` - Rust: `swh:1:rel:50cbfa7951b84d69da951d936a57e67654bcb7d9` vs Consensus: `swh:1:rel:302822701a46791d97f5e372255b7db078a342e2`

**Investigation needed in swhid-rs**:
- How does the Rust tool resolve tag names to tag object SHAs?
- Verify it correctly identifies annotated tags (not lightweight tags)
- Check tag object SHA computation matches Git's `git cat-file -t <tag>` and `git rev-parse <tag>` behavior
- Ensure it's using the tag object SHA, not the commit SHA the tag points to

### SNP (Snapshot) - 5 issues

Rust produces different snapshot SWHIDs compared to Python implementation. Note: Git-based implementations (git, git-cmd, pygit2) don't support snapshots, so only Python and Rust can be compared.

**Pattern**: Rust and Python disagree on snapshot SWHIDs for all git-repository payloads.

**Affected tests**:
1. `branch_ordering` - Rust: `swh:1:snp:6af89977bb9778bff542886fc872892057c40ea7` vs Python: `swh:1:snp:e44a647204ef944dd0fd28302a0d65124b93cd36`
2. `complex_merges` - Rust: `swh:1:snp:007da37517ac622c72faffd68b6338f8b44e57cd` vs Python: `swh:1:snp:604524a5decb4c927258eb4d9f5a121c48218bd4`
3. `merge_commits` - Rust: `swh:1:snp:6349a0fabe9bcea2a4c4712637cf4f91880e0bc0` vs Python: `swh:1:snp:5c9c3c9be880d0ac89707304017006716d6749a6`
4. `simple_revisions` - Rust: `swh:1:snp:4beb495cdf279920339b8400a8aa0a1bfd6ad3e3` vs Python: `swh:1:snp:2f1450c1be7a6945b69d2c3724ac30a3be025e92`
5. `tag_types` - Rust: `swh:1:snp:ee1b5ffe457469e0cd4192ad3a9a99cb24fd872e` vs Python: `swh:1:snp:98a720761e59ff1704a84b38e0f3f683a6c2d5d9`

**Investigation needed in swhid-rs**:
- Verify snapshot computation logic (branch ordering, tag handling, etc.)
- Compare with Python's `swh.model` implementation behavior
- Check branch ordering algorithm (natural byte order)
- Verify tag/branch inclusion in snapshot computation

## Root Cause Analysis

### Revision Issues (11 issues)
The Rust tool appears to have issues with:
1. **Branch name resolution**: When given a branch name (e.g., "main", "develop"), it may not be resolving it correctly to the commit SHA
2. **Short SHA resolution**: When given a 7-character short SHA, it may not be resolving it to the full 40-character SHA
3. **Commit SHA computation**: The computed commit SHAs don't exist in the Git repository, suggesting the tool may be computing them incorrectly

### Release Issues (8 issues)
The Rust tool appears to have issues with:
1. **Tag object identification**: It may be using the wrong object (commit vs tag object)
2. **Tag SHA computation**: The computed tag object SHAs don't match Git's tag object SHAs

### Snapshot Issues (5 issues)
The Rust tool appears to have issues with:
1. **Snapshot computation algorithm**: May differ from the SWHID specification
2. **Branch/tag ordering**: May not be using natural byte order
3. **Reference inclusion**: May be including/excluding references differently

## Recommended Investigation Steps

1. **Verify commit SHA resolution**:
   - Test: `git rev-parse <branch>` vs Rust tool's resolution
   - Test: `git rev-parse <short-sha>` vs Rust tool's resolution
   - Check if Rust tool is correctly using Git's object database

2. **Verify tag object handling**:
   - Test: `git cat-file -t <tag>` to verify tag type
   - Test: `git rev-parse <tag>` to get tag object SHA
   - Verify Rust tool is using tag object SHA, not commit SHA

3. **Compare snapshot computation**:
   - Use `swh identify --type snapshot <repo>` as reference
   - Compare branch ordering
   - Compare tag handling

4. **Check command-line interface**:
   - Verify the Rust CLI is receiving correct parameters
   - Check if there are any parameter parsing issues
   - Verify working directory handling

## Test Payloads for Debugging

All issues can be reproduced using:
- `payloads/git-repository/comprehensive/` - For comprehensive branch/tag testing
- `payloads/git/merge_commits/` - For revision testing
- `payloads/git-repository/simple_revisions/` - For simple revision testing
- `payloads/git/with_tags/` - For release testing

