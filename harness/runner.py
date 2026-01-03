"""
Test runner for the SWHID Testing Harness.

This module handles test execution, orchestration, and parallel execution.
"""

import os
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .plugins.base import SwhidImplementation, SwhidTestResult, TestMetrics
from .config import HarnessConfig, PayloadConfig
from .utils.constants import obj_type_to_swhid_code, SWHID_V1_PREFIX, SWHID_V2_PREFIX
from .utils.git_utils import resolve_commit_reference
from .git_manager import GitManager
from .resource_manager import ResourceManager
import logging

logger = logging.getLogger(__name__)


class TestRunner:
    """Runs tests for SWHID implementations."""
    
    def __init__(
        self,
        config: HarnessConfig,
        config_path: str,
        implementations: Dict[str, SwhidImplementation],
        resource_manager: ResourceManager,
        git_manager: GitManager
    ):
        """
        Initialize test runner.
        
        Args:
            config: Validated configuration
            config_path: Path to config file (for resolving relative paths)
            implementations: Dictionary of implementations to test
            resource_manager: Resource manager for temp dirs
            git_manager: Git manager for Git operations
        """
        self.config = config
        self.config_path = config_path
        self.implementations = implementations
        self.resource_manager = resource_manager
        self.git_manager = git_manager
    
    def run_single_test(
        self,
        implementation: SwhidImplementation,
        payload_path: str,
        payload_name: str,
        category: Optional[str] = None,
        commit: Optional[str] = None,
        tag: Optional[str] = None,
        version: Optional[int] = None,
        hash_algo: Optional[str] = None
    ) -> SwhidTestResult:
        """
        Run a single test for one implementation.
        
        Args:
            implementation: Implementation to test
            payload_path: Path to test payload
            payload_name: Name of the test payload
            category: Test category (optional)
            commit: Commit reference for revision tests (optional)
            tag: Tag name for release tests (optional)
            version: SWHID version to test (optional)
            hash_algo: Hash algorithm to use (optional)
            
        Returns:
            SwhidTestResult with test outcome
        """
        start_time = time.time()
        
        try:
            # Extract tarball if needed
            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            actual_payload_path = self.resource_manager.extract_tarball_if_needed(payload_path, config_dir)
            
            # Determine object type from category if available, otherwise auto-detect
            if category:
                # Map category to object type
                if category == "content" or category.startswith("content/"):
                    obj_type = "content"
                elif category == "directory" or category.startswith("directory/"):
                    obj_type = "directory"
                elif category == "git":
                    obj_type = "snapshot"
                elif category == "git-repository":
                    obj_type = implementation.detect_object_type(actual_payload_path)
                elif category == "revision":
                    obj_type = "revision"
                elif category == "release":
                    obj_type = "release"
                else:
                    obj_type = implementation.detect_object_type(actual_payload_path)
            else:
                obj_type = implementation.detect_object_type(actual_payload_path)
            
            # Check if implementation supports this object type
            capabilities = implementation.get_capabilities()
            swhid_code = obj_type_to_swhid_code(obj_type)
            
            if swhid_code not in capabilities.supported_types:
                logger.info(f"Skipping {payload_name} for {implementation.get_info().name}: unsupported type '{obj_type}' (SWHID code '{swhid_code}')")
                return SwhidTestResult(
                    payload_name=payload_name,
                    payload_path=payload_path,
                    implementation=implementation.get_info().name,
                    swhid=None,
                    error=f"Object type '{obj_type}' (SWHID code '{swhid_code}') not supported by implementation",
                    duration=0.0,
                    success=False,
                    version=version if version is not None else 1
                )
            
            # Resolve commit reference to full SHA if needed
            resolved_commit = commit
            if commit and obj_type == "revision":
                resolved_commit = self.git_manager.resolve_commit(actual_payload_path, commit)
            
            # Prepare compute arguments
            compute_kwargs = {"commit": resolved_commit, "tag": tag}
            if version is not None:
                compute_kwargs["version"] = version
            if hash_algo is not None:
                compute_kwargs["hash_algo"] = hash_algo
            
            swhid = implementation.compute_swhid(actual_payload_path, obj_type, **compute_kwargs)
            duration = time.time() - start_time
            
            # Determine SWHID version from result
            if version is not None:
                result_version = version
            elif swhid and swhid.startswith(SWHID_V2_PREFIX):
                result_version = 2
            elif swhid and swhid.startswith(SWHID_V1_PREFIX):
                result_version = 1
            else:
                result_version = 1
            
            return SwhidTestResult(
                payload_name=payload_name,
                payload_path=payload_path,
                implementation=implementation.get_info().name,
                swhid=swhid,
                error=None,
                duration=duration,
                success=True,
                version=result_version
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_str = str(e)
            # Check if this is an "unsupported type" error that should be skipped
            if any(phrase in error_str.lower() for phrase in [
                "doesn't support", "does not support", "not support", 
                "unsupported", "not supported"
            ]):
                logger.info(f"Skipping {payload_name} for {implementation.get_info().name}: {error_str}")
                return SwhidTestResult(
                    payload_name=payload_name,
                    payload_path=payload_path,
                    implementation=implementation.get_info().name,
                    swhid=None,
                    error=f"Object type not supported: {error_str}",
                    duration=0.0,
                    success=False,
                    version=version if version is not None else 1
                )
            return SwhidTestResult(
                payload_name=payload_name,
                payload_path=payload_path,
                implementation=implementation.get_info().name,
                swhid=None,
                error=error_str,
                duration=duration,
                success=False,
                version=version if version is not None else 1
            )

