"""
Result comparison for the SWHID Testing Harness.

This module handles comparison of test results across implementations
and detection of consensus.
"""

from typing import Dict, Optional
from .plugins.base import SwhidTestResult, ComparisonResult
import logging

logger = logging.getLogger(__name__)


class ResultComparator:
    """Compares test results across implementations."""
    
    def is_unsupported_result(self, result: SwhidTestResult) -> bool:
        """
        Return True if the result represents an unsupported object type.
        
        Args:
            result: Test result to check
            
        Returns:
            True if result indicates unsupported object type
        """
        if result.success:
            return False
        if not result.error:
            return False
        err = str(result.error).lower()
        return "object type" in err and "not support" in err
    
    def compare_results(
        self,
        payload_name: str,
        payload_path: str,
        results: Dict[str, SwhidTestResult],
        expected_swhid: Optional[str] = None,
        expected_swhid_sha256: Optional[str] = None,
        expected_error: Optional[str] = None
    ) -> ComparisonResult:
        """
        Compare results across implementations.
        
        Args:
            payload_name: Name of the test payload
            payload_path: Path to the test payload
            results: Dictionary mapping implementation names to test results
            expected_swhid: Expected SWHID v1 (optional)
            expected_swhid_sha256: Expected SWHID v2 (optional)
            expected_error: Expected error code for negative tests (optional)
            
        Returns:
            ComparisonResult with comparison outcome
        """
        supported_results = {
            name: result for name, result in results.items()
            if not self.is_unsupported_result(result)
        }
        
        if not supported_results:
            all_unsupported = results and all(self.is_unsupported_result(r) for r in results.values())
            if all_unsupported:
                return ComparisonResult(
                    payload_name=payload_name,
                    payload_path=payload_path,
                    results=results,
                    all_match=True,
                    expected_swhid=expected_swhid
                )
            # Fall through to regular comparison (e.g., missing payloads)
            supported_results = results
        
        # Handle negative tests: if expected_error is set, all supporting implementations should fail
        if expected_error and supported_results:
            all_failed = all(not r.success for r in supported_results.values())
            if all_failed:
                # All supporting implementations correctly rejected the invalid input
                return ComparisonResult(
                    payload_name=payload_name,
                    payload_path=payload_path,
                    results=results,
                    all_match=True,
                    expected_swhid=expected_swhid,
                    expected_swhid_sha256=expected_swhid_sha256
                )
        
        # Check if all implementations succeeded
        all_success = all(r.success for r in supported_results.values())
        
        if not all_success:
            return ComparisonResult(
                payload_name=payload_name,
                payload_path=payload_path,
                results=results,
                all_match=False,
                expected_swhid=expected_swhid,
                expected_swhid_sha256=expected_swhid_sha256
            )
        
        # Get all SWHIDs, grouped by version
        v1_swhids = [r.swhid for r in supported_results.values() 
                     if r.swhid and r.version == 1]
        v2_swhids = [r.swhid for r in supported_results.values() 
                     if r.swhid and r.version == 2]
        
        # Check if all SWHIDs match within each version group
        v1_match = len(set(v1_swhids)) == 1 if v1_swhids else True  # True if no v1 results
        v2_match = len(set(v2_swhids)) == 1 if v2_swhids else True  # True if no v2 results
        
        all_match = v1_match and v2_match
        
        # Check against expected SWHIDs if provided
        if all_match:
            if v1_swhids and expected_swhid:
                all_match = v1_swhids[0] == expected_swhid
            if v2_swhids and expected_swhid_sha256:
                all_match = all_match and (v2_swhids[0] == expected_swhid_sha256)
        
        return ComparisonResult(
            payload_name=payload_name,
            payload_path=payload_path,
            results=results,
            all_match=all_match,
            expected_swhid=expected_swhid,
            expected_swhid_sha256=expected_swhid_sha256
        )

