"""
Subprocess utility functions for the SWHID Testing Harness.

This module provides shared utilities for subprocess execution,
environment preparation, and resource limit management.
"""

import os
import signal
import resource
from pathlib import Path
from typing import Dict, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


def prepare_subprocess_environment(
    clean_env: bool = True,
    project_root: Optional[str] = None
) -> Dict[str, str]:
    """
    Prepare environment for subprocess execution.
    
    Args:
        clean_env: If True, use minimal environment with only essential variables.
                   If False, copy current environment and add project root to PYTHONPATH.
        project_root: Path to project root (auto-detected if None)
        
    Returns:
        Environment dictionary for subprocess
    """
    if project_root is None:
        # Auto-detect project root (3 levels up from this file: harness/utils/subprocess_utils.py)
        project_root = str(Path(__file__).parent.parent.parent.absolute())
    
    if not clean_env:
        env = os.environ.copy()
        # Ensure project root is in PYTHONPATH
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{project_root}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = project_root
        return env
    
    # Whitelist essential environment variables
    env = {}
    
    # Essential paths
    path = os.environ.get("PATH", "/usr/bin:/bin")
    env["PATH"] = path
    
    # Home directory
    home = os.environ.get("HOME", "/tmp")
    env["HOME"] = home
    
    # Python path - include project root for module imports
    if "PYTHONPATH" in os.environ:
        env["PYTHONPATH"] = f"{project_root}:{os.environ['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = project_root
    
    # Locale
    for var in ["LANG", "LC_ALL", "LC_CTYPE"]:
        if var in os.environ:
            env[var] = os.environ[var]
    
    return env


def set_resource_limits(
    max_rss_mb: int,
    max_cpu_time: int
) -> None:
    """
    Set resource limits for subprocess (Unix only).
    
    Args:
        max_rss_mb: Maximum resident set size in MB
        max_cpu_time: Maximum CPU time in seconds
        
    Note:
        This function only works on Unix systems. On Windows, it does nothing.
    """
    if os.name == 'nt':
        # Windows doesn't support resource limits via setrlimit
        return
    
    try:
        # Set RSS limit (virtual memory as proxy)
        max_rss_bytes = max_rss_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (max_rss_bytes, max_rss_bytes))
        
        # Set CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_time, max_cpu_time))
    except (ValueError, OSError) as e:
        logger.warning(f"Could not set resource limits: {e}")


def run_with_timeout(
    func: Callable[[], Any],
    timeout: float
) -> Any:
    """
    Run a function with timeout using signal (Unix only).
    
    Args:
        func: Function to execute
        timeout: Timeout in seconds
        
    Returns:
        Function result
        
    Raises:
        TimeoutError: If function exceeds timeout (Unix only)
        
    Note:
        On Windows, timeout is not enforced (function runs without timeout).
    """
    if os.name == 'nt':
        # Windows doesn't support SIGALRM
        return func()
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout}s")
    
    # Set up signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(timeout))
    
    try:
        result = func()
        return result
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

