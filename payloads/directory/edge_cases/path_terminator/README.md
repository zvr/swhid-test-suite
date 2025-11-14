# Path Qualifier Tests - Slash Encoding

## Goal

Tests path= qualifier behavior with percent-encoded vs literal slashes. According to SWHID Specification v1.2 Section 6.2, path qualifiers must properly handle percent-encoding.

## Specification Reference

- SWHID Specification v1.2, Section 6.2 (Path Qualifier)
- Section 4 (Syntax) - Percent encoding rules

## Structure

This directory contains:
- `file%2Fwith%2Fslash/` - Directory with percent-encoded slashes in name
- `file/with/slash/` - Directory with literal slashes in name
- `root.txt` - Root-level file

## Expected Behavior

When computing qualified SWHIDs:
- `path=file%2Fwith%2Fslash/content.txt` should resolve to the file in the percent-encoded directory
- `path=file/with/slash/content.txt` should resolve to the file in the literal slash directory
- These are **different** paths and should produce different qualified SWHIDs

## Key Test Cases

1. **Percent-encoded slashes**: `file%2Fwith%2Fslash` must be treated as a single directory name, not a path separator
2. **Literal slashes**: `file/with/slash` contains actual path separators
3. **Ambiguity resolution**: Implementations must distinguish between encoded and literal slashes

## Known Variants

- Some implementations may normalize `%2F` to `/` incorrectly
- Some implementations may treat `%2F` as a path separator when it should be a literal character

## Golden SWHIDs

(To be filled after computing with reference implementation)

- Directory SWHID: `swh:1:dir:...`
- Qualified with `path=file%2Fwith%2Fslash/content.txt`: `swh:1:dir:...;path=file%2Fwith%2Fslash/content.txt`
- Qualified with `path=file/with/slash/content.txt`: `swh:1:dir:...;path=file/with/slash/content.txt`

