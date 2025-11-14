# Path Qualifier Tests - Percent Sign Encoding

## Goal

Tests path= qualifier behavior with percent-encoded vs literal percent signs. According to SWHID Specification v1.2 Section 6.2, percent signs in path qualifiers must be properly encoded as `%25`.

## Specification Reference

- SWHID Specification v1.2, Section 6.2 (Path Qualifier)
- Section 4 (Syntax) - Percent encoding: `%` → `%25`

## Structure

This directory contains:
- `file%25with%25percent/` - Directory with percent-encoded percent signs (`%25`)
- `file%with%percent/` - Directory with literal percent signs (`%`)
- `regular.txt` - Root-level file

## Expected Behavior

When computing qualified SWHIDs:
- `path=file%25with%25percent/content.txt` should resolve to the file in the percent-encoded directory
- `path=file%with%percent/content.txt` should resolve to the file in the literal percent directory
- These are **different** paths and should produce different qualified SWHIDs

## Key Test Cases

1. **Percent-encoded percent**: `file%25with%25percent` contains `%25` which decodes to `%`
2. **Literal percent**: `file%with%percent` contains literal `%` characters
3. **Encoding correctness**: Implementations must properly encode `%` as `%25` in qualifiers

## Known Variants

- Some implementations may double-encode `%25` incorrectly
- Some implementations may not distinguish between `%` and `%25` in filenames vs qualifiers

## Golden SWHIDs

(To be filled after computing with reference implementation)

- Directory SWHID: `swh:1:dir:...`
- Qualified with `path=file%25with%25percent/content.txt`: `swh:1:dir:...;path=file%25with%25percent/content.txt`
- Qualified with `path=file%25with%25percent/content.txt` (double-encoded): Should be rejected or normalized

