"""
Plugin system for SWHID implementations.
"""

from .base import (
    SwhidImplementation, ImplementationInfo, SwhidTestResult, ComparisonResult,
    ErrorCode, ErrorContext, TestMetrics, ImplementationCapabilities
)
from .discovery import ImplementationDiscovery

__all__ = [
    "SwhidImplementation",
    "ImplementationInfo", 
    "SwhidTestResult",
    "ComparisonResult",
    "ErrorCode",
    "ErrorContext",
    "TestMetrics",
    "ImplementationCapabilities",
    "ImplementationDiscovery"
]
