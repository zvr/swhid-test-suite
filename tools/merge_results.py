#!/usr/bin/env python3
"""
Merge canonical results into dashboard layout.

This script takes canonical results files and creates the proper dashboard structure:
- site/data/runs/<run-id>.json (full canonical file)
- site/data/index.json (roll-up with metadata)
- site/data/latest.json (compatibility)
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def load_canonical_results(file_path: str) -> Dict[str, Any]:
    """Load a canonical results file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_index_data(results_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create index.json data from multiple results files."""
    runs = []
    total_tests = 0
    total_passed = 0
    implementations = set()
    
    for results in results_files:
        run_data = {
            "id": results["run"]["id"],
            "created_at": results["run"]["created_at"],
            "branch": results["run"]["branch"],
            "commit": results["run"]["commit"],
            "pass_rate": 0.0
        }
        
        # Calculate pass rate
        test_count = len(results["tests"])
        passed_count = 0
        for test in results["tests"]:
            for result in test["results"]:
                if result["status"] == "PASS":
                    passed_count += 1
        
        if test_count > 0:
            run_data["pass_rate"] = round(passed_count / (test_count * len(results["implementations"])) * 100, 2)
        
        runs.append(run_data)
        total_tests += test_count
        total_passed += passed_count
        
        # Collect implementations
        for impl in results["implementations"]:
            implementations.add(impl["id"])
    
    # Sort runs by created_at (newest first)
    runs.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_runs": len(runs),
        "total_tests": total_tests,
        "overall_pass_rate": round(total_passed / (total_tests * len(implementations)) * 100, 2) if total_tests > 0 else 0,
        "implementations": sorted(list(implementations)),
        "runs": runs
    }

def main():
    parser = argparse.ArgumentParser(description="Merge canonical results into dashboard layout")
    parser.add_argument("results_files", nargs="+", help="Canonical results JSON files")
    parser.add_argument("--site", default="site", help="Site directory")
    
    args = parser.parse_args()
    
    # Load all results files
    results_files = []
    for file_path in args.results_files:
        if os.path.exists(file_path):
            results_files.append(load_canonical_results(file_path))
        else:
            print(f"Warning: File not found: {file_path}")
    
    if not results_files:
        print("Error: No valid results files found")
        return 1
    
    # Create site directory structure
    site_dir = Path(args.site)
    data_dir = site_dir / "data"
    runs_dir = data_dir / "runs"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    # Write individual run files
    for results in results_files:
        run_id = results["run"]["id"]
        run_file = runs_dir / f"{run_id}.json"
        with open(run_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Wrote {run_file}")
    
    # Create and write index.json
    index_data = create_index_data(results_files)
    index_file = data_dir / "index.json"
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    print(f"Wrote {index_file}")
    
    # Write latest.json (compatibility)
    if results_files:
        latest_file = data_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump(results_files[0], f, indent=2)
        print(f"Wrote {latest_file}")
    
    print(f"Successfully merged {len(results_files)} results files")
    return 0

if __name__ == "__main__":
    exit(main())
