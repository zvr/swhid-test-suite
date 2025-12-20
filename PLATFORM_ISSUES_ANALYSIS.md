# Platform-Specific Test Failures Analysis

## Summary

Analysis of test failures in GitHub Actions workflows for macOS and Windows platforms.

## Test Results Overview

### macOS (macOS-14.8.3-arm64)
- **Total failures**: 1
- **git-cmd**: 1 failure (`unicode_normalization`)
- **All other implementations**: PASS

### Windows (Windows-2022Server-10.0.20348-SP0)
- **Total failures**: 11
- **git**: 3 failures (`comprehensive_permissions`, `mixed_types`, `permissions_dir`)
- **git-cmd**: 5 failures (`comprehensive_permissions`, `crlf_line_endings`, `mixed_line_endings`, `mixed_types`, `permissions_dir`)
- **rust**: 3 failures (`comprehensive_permissions`, `mixed_types`, `permissions_dir`)

### Linux (Ubuntu-24.04)
- **All tests**: PASS ✅

## Detailed Issue Analysis

### 1. Unicode Normalization (macOS) - `unicode_normalization` test

**Affected**: git-cmd on macOS

**Issue**: 
- Expected: `swh:1:dir:53d793e1a86c17e1c120e8cf1d9cec788a5c360f`
- Got: `swh:1:dir:14b9515fe044e24e7340ea89c5cc98275f181d43`

**Root Cause**:
macOS filesystems (APFS/HFS+) automatically normalize Unicode filenames. The test payload contains:
- `fileé.txt` (NFC: U+00E9)
- `nfd/fileé.txt` (NFD: U+0065 + U+0301)

When files are copied to a temporary Git repository, macOS may normalize the filenames, changing the byte sequence. SWHID requires byte-level comparison, so any normalization breaks the hash.

**Impact**: Medium - Affects only git-cmd on macOS, likely due to how Git handles filenames during `git add`.

**Recommendation**:
- Check if Git on macOS is configured with `core.precomposeunicode` or similar settings
- Consider using raw file system APIs that bypass normalization
- Document this as a known limitation for macOS

### 2. CRLF Line Endings (Windows) - `crlf_line_endings` and `mixed_line_endings` tests

**Affected**: git-cmd on Windows

**Issue**:
- `crlf_line_endings`: Expected `swh:1:cnt:08a29ba1a45a68c26a3326af2b32d0d53741b8e2`, got `swh:1:cnt:baa3d84af3432fc2165fbeedfd3d01a9ef8f1f8f`
- `mixed_line_endings`: Expected `swh:1:cnt:34f1257dbbb7e20b745654c0cd067ff24375d1d7`, got `swh:1:cnt:e5791419fa06dbc7637fd229a040a1f7e058e734`

**Root Cause**:
Git on Windows is typically configured with `core.autocrlf=true`, which automatically converts CRLF to LF when adding files to the index. This means:
- The test file has CRLF line endings
- Git normalizes them to LF when computing the hash
- The SWHID hash changes because the content bytes are different

**Impact**: High - Affects all content tests with CRLF on Windows

**Recommendation**:
- Configure Git with `core.autocrlf=false` for the test repository
- Or use `git hash-object --no-filters` to bypass line ending conversion
- Document that git-cmd on Windows requires specific Git configuration

### 3. File Permissions (Windows) - `permissions_dir` and `comprehensive_permissions` tests

**Affected**: git, git-cmd, rust on Windows

**Issue**:
- `permissions_dir`: All implementations get `swh:1:dir:1786880efb8d00c6bf9c56627155668769a46c21` instead of expected `swh:1:dir:bc3f7f74e7aa5fcb859eaaa3949d5cae29c28ca4`
- `comprehensive_permissions`: All implementations get `swh:1:dir:bbb968463c32959031f5962fef0cd51530dcf194` instead of expected `swh:1:dir:32798ac33695bd283d6e650c61a40bc2dbda3a2e`

**Root Cause**:
Windows uses ACLs (Access Control Lists) instead of Unix-style permissions. The implementations use `os.stat().st_mode & stat.S_IEXEC` to detect executable files, but:
- Windows doesn't have a reliable executable bit
- File permissions are stored differently
- Git on Windows may assign default permissions (644/755) regardless of actual file permissions

**Impact**: High - Affects all directory tests with permission variations on Windows

**Recommendation**:
- Check if files are executable using Windows-specific methods (file extension, ACLs)
- Consider using Git's default permission model for Windows
- Document that permission-based tests may behave differently on Windows
- Consider platform-specific expected values for permission tests

### 4. Mixed Types (Windows) - `mixed_types` test

**Affected**: git, git-cmd, rust on Windows

**Issue**:
- Expected: `swh:1:dir:6a805bfd6380e2e1e4412ac66933ebd244fb9d72`
- Got: `swh:1:dir:829dac03dfaf3dcafe01fe280aedb7cb00ee3282`

**Root Cause**:
The test payload contains:
- Regular files
- Executable files
- Symlinks
- Subdirectories

Windows handles symlinks differently:
- Requires administrator privileges or developer mode to create symlinks
- Symlinks may not be preserved during copy operations
- Git on Windows may store symlinks as regular files with special content

**Impact**: Medium - Affects directory tests with symlinks on Windows

**Recommendation**:
- Verify symlink creation is enabled on Windows runners
- Check if `shutil.copytree(..., symlinks=True)` works correctly on Windows
- Consider skipping symlink tests on Windows or using platform-specific handling

## Recommendations

### Immediate Actions

1. **Git Configuration for Windows**:
   - Set `core.autocrlf=false` in test repositories
   - Set `core.filemode=false` to ignore permission differences
   - Document required Git configuration for Windows testing

2. **Platform-Specific Test Expectations**:
   - Consider platform-specific expected values for:
     - Permission-based tests (Windows)
     - Unicode normalization tests (macOS)
     - Symlink tests (Windows)

3. **Implementation Improvements**:
   - **git-cmd**: Add Git configuration to disable line ending conversion
   - **git/git-cmd**: Improve Windows permission detection
   - **All**: Better symlink handling on Windows

### Long-term Solutions

1. **Test Framework Enhancements**:
   - Add platform detection in test configuration
   - Support platform-specific expected values
   - Add skip conditions for platform-incompatible tests

2. **Documentation**:
   - Document known platform limitations
   - Add troubleshooting guide for platform-specific issues
   - Include Git configuration requirements in CI setup

3. **CI/CD Improvements**:
   - Configure Git settings in workflow setup steps
   - Enable developer mode/symlinks on Windows runners
   - Add platform-specific test validation

## Test Status by Platform

| Test | Linux | macOS | Windows |
|------|-------|-------|---------|
| unicode_normalization | ✅ | ❌ git-cmd | ✅ |
| crlf_line_endings | ✅ | ✅ | ❌ git-cmd |
| mixed_line_endings | ✅ | ✅ | ❌ git-cmd |
| permissions_dir | ✅ | ✅ | ❌ git, git-cmd, rust |
| comprehensive_permissions | ✅ | ✅ | ❌ git, git-cmd, rust |
| mixed_types | ✅ | ✅ | ❌ git, git-cmd, rust |

## Next Steps

1. Investigate Git configuration in CI workflows
2. Test symlink creation on Windows runners
3. Implement platform-specific handling in implementations
4. Update test expectations or add platform-specific variants
5. Document findings and solutions

