# Negative Test Payloads

This directory contains test payloads designed to trigger specific error conditions.

## Error Code Coverage

### PARSE_ERROR
**Trigger**: Invalid SWHID format returned by implementation
- Invalid scheme (not "swh")
- Invalid version (not "1")
- Invalid object type
- Invalid hash format
- Invalid qualifier syntax

**Test Payloads**: None (requires implementation that returns malformed SWHID)

### NORMALIZE_ERROR
**Trigger**: Valid parse but canonicalization fails
- Valid syntax but invalid hash length
- Valid syntax but invalid qualifier values
- Case sensitivity issues

**Test Payloads**: None (requires implementation that returns unnormalizable SWHID)

### VALIDATION_ERROR
**Trigger**: Semantically invalid but well-formed SWHID
- Hash doesn't match content
- Qualifiers conflict
- Object type mismatch

**Test Payloads**: None (requires implementation that returns invalid SWHID)

### COMPUTE_ERROR
**Trigger**: Failure computing SWHID from payload
- Implementation raises exception
- Implementation returns error
- Missing dependencies

**Test Payloads**:
- `nonexistent_file.txt` - File that doesn't exist
- `permission_denied/` - Directory without read permission

### MISMATCH_ERROR
**Trigger**: Value differs from reference implementation
- Different implementations produce different SWHIDs
- Implementation produces wrong SWHID

**Test Payloads**: Covered by regular test suite (any payload where implementations disagree)

### TIMEOUT
**Trigger**: Exceeded wall clock budget
- Implementation takes too long
- SubprocessAdapter timeout exceeded

**Test Payloads**: None (requires slow implementation or artificial delay)

### RESOURCE_LIMIT
**Trigger**: Memory/CPU cap exceeded
- RSS limit exceeded
- CPU time limit exceeded

**Test Payloads**: None (requires memory-intensive implementation or artificial limits)

### IO_ERROR
**Trigger**: Plugin crashed / bad exit / protocol violation
- File not found
- Permission denied
- Protocol violation (invalid JSON)
- Process crash

**Test Payloads**:
- `nonexistent_file.txt` - File that doesn't exist
- `permission_denied/` - Directory without read permission

## Usage

Negative tests are run as part of the test suite:

```bash
# Run negative tests
pytest tests/negative/

# Run with coverage
pytest tests/negative/ --cov=harness
```

## Adding New Negative Tests

1. Create test payload in `payloads/negative/`
2. Add test case to `tests/negative/test_error_codes.py`
3. Document expected error code in this README
4. Update `config.yaml` if needed

