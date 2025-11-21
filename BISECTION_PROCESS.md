# Harness Bisection Process

## Overview
This document describes the process for bisecting issues in the harness test matrix.

## Quick Start

### 1. Run Bisection Script
```bash
./bisect_harness.sh [start_commit] [end_commit] [test_name]
```

Example:
```bash
./bisect_harness.sh cd0c1dc HEAD binary_file
```

### 2. Manual Bisection
```bash
# Test a specific commit
git checkout <commit>
swhid-harness --payload <test_name> --output-format canonical --dashboard-output /tmp/results.json

# Analyze results
python3 -c "
import json
with open('/tmp/results.json') as f:
    data = json.load(f)
    tests = data.get('tests', [])
    for t in tests:
        results = t.get('results', [])
        swhids = [r.get('swhid') for r in results if r.get('swhid')]
        print(f\"{t.get('id')}: {len(set(swhids))} unique SWHIDs\")
"
```

## Analyzing Results

### Check for Regressions
1. Compare `all_agree` count between commits
2. Check for new disagreements
3. Verify expected SWHIDs still match

### Common Issues to Check
- Path resolution changes affecting payload access
- Logic changes in `_compare_results`
- Summary calculation bugs
- Status determination in `get_canonical_results`

## Debugging Tips

1. **Check ComparisonResult.all_match**: This is set by `_compare_results()`
2. **Check Summary Calculation**: `_print_summary()` recalculates from canonical results
3. **Verify Path Resolution**: Ensure absolute paths are used consistently
4. **Check Expected SWHIDs**: Verify they match actual computed values

