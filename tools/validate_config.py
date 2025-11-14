#!/usr/bin/env python3
"""
Validate that all payloads referenced in config.yaml actually exist.

This script checks that every payload path in config.yaml points to an existing file or directory.
"""

import sys
import yaml
from pathlib import Path

def main():
    config_path = Path("config.yaml")
    if not config_path.exists():
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    errors = []
    warnings = []
    
    for category, payloads in config.get("payloads", {}).items():
        for payload in payloads:
            path_str = payload.get("path", "")
            name = payload.get("name", "unnamed")
            
            if not path_str:
                warnings.append(f"{category}/{name}: Missing path")
                continue
            
            path = Path(path_str)
            if not path.exists():
                errors.append(f"{category}/{name}: Path does not exist: {path_str}")
    
    if errors:
        print("Errors (payloads missing from filesystem):", file=sys.stderr)
        for error in errors:
            print(f"  ✗ {error}", file=sys.stderr)
        sys.exit(1)
    
    if warnings:
        print("Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"  ⚠ {warning}", file=sys.stderr)
    
    print("✓ All payload paths in config.yaml exist")
    sys.exit(0)

if __name__ == "__main__":
    main()

