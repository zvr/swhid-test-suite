#!/usr/bin/env python3
"""
Structured diff tool for SWHID test results.

Compares two result JSON files and emits structured diffs with JSON Pointer paths.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class ResultDiff:
    """Structured diff between two result objects."""
    
    def __init__(self):
        self.diffs: List[Dict[str, Any]] = []
    
    def add_diff(self, path: str, expected: Any, actual: Any, category: str = "value_mismatch"):
        """Add a diff entry."""
        self.diffs.append({
            "path": path,
            "expected": expected,
            "actual": actual,
            "category": category
        })
    
    def compare_values(self, path: str, expected: Any, actual: Any):
        """Recursively compare two values and record differences."""
        if expected == actual:
            return
        
        if type(expected) != type(actual):
            self.add_diff(path, expected, actual, "value_mismatch")
            return
        
        if isinstance(expected, dict):
            # Compare dictionaries
            all_keys = set(expected.keys()) | set(actual.keys())
            for key in sorted(all_keys):
                key_path = f"{path}/{key}" if path else f"/{key}"
                if key not in expected:
                    self.add_diff(key_path, None, actual[key], "missing_field")
                elif key not in actual:
                    self.add_diff(key_path, expected[key], None, "missing_field")
                else:
                    self.compare_values(key_path, expected[key], actual[key])
        elif isinstance(expected, list):
            # Compare lists (check for ordering differences)
            if len(expected) != len(actual):
                self.add_diff(path, len(expected), len(actual), "value_mismatch")
            else:
                # Check if same elements in different order
                if sorted(expected) == sorted(actual) and expected != actual:
                    self.add_diff(path, expected, actual, "ordering")
                else:
                    # Compare element by element
                    for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                        item_path = f"{path}/{i}"
                        self.compare_values(item_path, exp_item, act_item)
        else:
            # Primitive values
            self.add_diff(path, expected, actual, "value_mismatch")
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert to dictionary format."""
        return self.diffs
    
    def is_empty(self) -> bool:
        """Check if there are any differences."""
        return len(self.diffs) == 0


def diff_results(expected_file: str, actual_file: str) -> ResultDiff:
    """Compare two result JSON files."""
    with open(expected_file, 'r') as f:
        expected_data = json.load(f)
    
    with open(actual_file, 'r') as f:
        actual_data = json.load(f)
    
    diff = ResultDiff()
    diff.compare_values("", expected_data, actual_data)
    return diff


def format_diff(diff: ResultDiff, compact: bool = False) -> str:
    """Format diff for human reading."""
    if diff.is_empty():
        return "✅ No differences found"
    
    lines = [f"Found {len(diff.diffs)} difference(s):\n"]
    
    for d in diff.diffs:
        path = d["path"]
        category = d["category"]
        expected = d["expected"]
        actual = d["actual"]
        
        if compact:
            lines.append(f"  {path}: {category}")
            if expected is not None:
                lines.append(f"    Expected: {expected}")
            if actual is not None:
                lines.append(f"    Actual: {actual}")
        else:
            lines.append(f"  Path: {path}")
            lines.append(f"    Category: {category}")
            if expected is not None:
                exp_str = json.dumps(expected) if not isinstance(expected, str) else expected
                lines.append(f"    Expected: {exp_str}")
            if actual is not None:
                act_str = json.dumps(actual) if not isinstance(actual, str) else actual
                lines.append(f"    Actual: {act_str}")
            lines.append("")
    
    return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Compare two SWHID test result JSON files"
    )
    parser.add_argument("expected", help="Expected results file")
    parser.add_argument("actual", help="Actual results file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--compact", action="store_true", help="Compact output format")
    
    args = parser.parse_args()
    
    if not Path(args.expected).exists():
        print(f"Error: Expected file not found: {args.expected}", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.actual).exists():
        print(f"Error: Actual file not found: {args.actual}", file=sys.stderr)
        sys.exit(1)
    
    try:
        diff = diff_results(args.expected, args.actual)
        
        if args.json:
            print(json.dumps(diff.to_dict(), indent=2))
        else:
            print(format_diff(diff, compact=args.compact))
        
        sys.exit(0 if diff.is_empty() else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

