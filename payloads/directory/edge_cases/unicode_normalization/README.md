# Unicode Normalization Test

## Goal
Tests that directory entry ordering and path qualifiers correctly handle Unicode normalization differences. The same visual character can be represented in different ways:
- **NFC (Normalization Form Canonical Composition)**: Single code point (U+00E9 = é)
- **NFD (Normalization Form Canonical Decomposition)**: Base character + combining mark (U+0065 + U+0301 = e + ́)

## Test Structure
- `fileé.txt` (NFC): Uses U+00E9 (é as single code point)
- `fileé.txt` (NFD): Uses U+0065 + U+0301 (e + combining acute accent)

## Expected Behavior
1. **Directory Entry Ordering**: Entries must be ordered by byte value, not by normalized form. NFC and NFD files will have different byte sequences and should appear in byte order.
2. **Path Qualifiers**: `path=` qualifiers must match the exact byte sequence in the directory entry, not a normalized form.

## Specification Reference
SWHID v1.2 requires byte-level comparison for directory entries and path qualifiers. Implementations must not normalize Unicode when computing SWHIDs.

