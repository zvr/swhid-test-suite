"""
Git utility functions for the SWHID Testing Harness.

This module provides shared utilities for Git operations including
commit resolution, branch discovery, and tag discovery.
"""

import subprocess
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def resolve_commit_reference(repo_path: str, commit: Optional[str] = None) -> Optional[str]:
    """
    Resolve a commit reference (branch name, tag, short SHA) to a full SHA.
    
    Args:
        repo_path: Path to Git repository
        commit: Commit reference (branch name, tag, short SHA, or None for HEAD)
        
    Returns:
        Full SHA if successful, or the original commit string if resolution fails
    """
    if not commit or commit == "HEAD" or len(commit) == 40:
        # HEAD, None, or already a full SHA - return as-is
        return commit
    
    # Try to resolve using git rev-parse (handles branch names, tags, short SHAs)
    try:
        result = subprocess.run(
            ["git", "rev-parse", commit],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True,
            timeout=5
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # Resolution failed - return original (let implementation handle it)
        return commit


def discover_branches(repo_path: str) -> List[str]:
    """
    Discover all branches in a Git repository.
    
    Args:
        repo_path: Path to Git repository
        
    Returns:
        List of branch names (sorted, without duplicates)
    """
    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True,
            timeout=10
        )
        branches = []
        for line in result.stdout.strip().split('\n'):
            branch = line.strip().lstrip('*').strip()
            # Remove remote prefix and filter out HEAD
            if branch.startswith('remotes/'):
                branch = branch.replace('remotes/origin/', '').replace('remotes/', '')
            if branch and branch != 'HEAD' and not branch.startswith('remotes/'):
                branches.append(branch)
        
        # Remove duplicates and sort
        return sorted(set(branches))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Failed to discover branches in {repo_path}: {e}")
        return []


def discover_annotated_tags(repo_path: str) -> List[str]:
    """
    Discover all annotated tags in a Git repository.
    
    Args:
        repo_path: Path to Git repository
        
    Returns:
        List of annotated tag names (sorted)
    """
    try:
        result = subprocess.run(
            ["git", "tag", "-l"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True,
            timeout=10
        )
        all_tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
        
        # Filter to only annotated tags
        annotated_tags = []
        for tag in all_tags:
            try:
                tag_type_result = subprocess.run(
                    ["git", "cat-file", "-t", tag],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=True,
                    timeout=5
                )
                if tag_type_result.stdout.strip() == "tag":
                    annotated_tags.append(tag)
            except subprocess.CalledProcessError:
                # Skip if we can't determine type
                continue
        
        return sorted(annotated_tags)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Failed to discover tags in {repo_path}: {e}")
        return []


def is_git_repository(path: str) -> bool:
    """
    Check if a path is a Git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is a Git repository, False otherwise
    """
    if not os.path.exists(path):
        return False
    
    # Check for regular Git repo (.git subdirectory)
    git_dir = os.path.join(path, ".git")
    if os.path.exists(git_dir):
        return True
    
    # Check for bare Git repository
    if (os.path.exists(os.path.join(path, "HEAD")) and
        os.path.exists(os.path.join(path, "refs")) and
        os.path.exists(os.path.join(path, "objects"))):
        return True
    
    return False

