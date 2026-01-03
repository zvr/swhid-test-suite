"""
Custom exception hierarchy for the SWHID Testing Harness.

This module provides a structured exception system that integrates
with the ErrorCode and ErrorContext system for consistent error handling.
"""

from typing import Optional, Dict, Any
from .plugins.base import ErrorCode, ErrorContext


class SwhidHarnessError(Exception):
    """Base exception for all SWHID Testing Harness errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        subtype: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize SWHID harness error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code from ErrorCode enum
            subtype: Optional error subtype (e.g., "file_not_found", "timeout")
            context: Optional additional context dictionary
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.subtype = subtype
        self.context = context or {}
    
    def to_error_context(self) -> Optional[ErrorContext]:
        """Convert to ErrorContext if error_code is set."""
        if self.error_code is None:
            return None
        return ErrorContext(
            code=self.error_code,
            subtype=self.subtype or "generic",
            message=self.message,
            context=self.context
        )
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code.value}] {self.message}"
        return self.message


class ConfigurationError(SwhidHarnessError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_path: Optional[str] = None,
        field: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_path: Path to configuration file (if applicable)
            field: Configuration field that caused the error (if applicable)
            **kwargs: Additional arguments passed to base class
        """
        context = kwargs.pop("context", {})
        if config_path:
            context["config_path"] = config_path
        if field:
            context["field"] = field
        
        super().__init__(
            message,
            error_code=ErrorCode.VALIDATION_ERROR,
            subtype="configuration",
            context=context,
            **kwargs
        )
        self.config_path = config_path
        self.field = field


class ImplementationError(SwhidHarnessError):
    """Exception raised for implementation-related errors."""
    
    def __init__(
        self,
        message: str,
        implementation: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        **kwargs
    ):
        """
        Initialize implementation error.
        
        Args:
            message: Error message
            implementation: Name of implementation that caused the error
            error_code: Specific error code (defaults to COMPUTE_ERROR)
            **kwargs: Additional arguments passed to base class
        """
        context = kwargs.pop("context", {})
        if implementation:
            context["implementation"] = implementation
        
        super().__init__(
            message,
            error_code=error_code or ErrorCode.COMPUTE_ERROR,
            subtype=kwargs.pop("subtype", "implementation"),
            context=context,
            **kwargs
        )
        self.implementation = implementation


class TestExecutionError(SwhidHarnessError):
    """Exception raised for test execution errors."""
    
    def __init__(
        self,
        message: str,
        payload_name: Optional[str] = None,
        payload_path: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        **kwargs
    ):
        """
        Initialize test execution error.
        
        Args:
            message: Error message
            payload_name: Name of the test payload
            payload_path: Path to the test payload
            error_code: Specific error code (defaults to COMPUTE_ERROR)
            **kwargs: Additional arguments passed to base class
        """
        context = kwargs.pop("context", {})
        if payload_name:
            context["payload_name"] = payload_name
        if payload_path:
            context["payload_path"] = payload_path
        
        super().__init__(
            message,
            error_code=error_code or ErrorCode.COMPUTE_ERROR,
            subtype=kwargs.pop("subtype", "test_execution"),
            context=context,
            **kwargs
        )
        self.payload_name = payload_name
        self.payload_path = payload_path


class ResultError(SwhidHarnessError):
    """Exception raised for result processing errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        **kwargs
    ):
        """
        Initialize result error.
        
        Args:
            message: Error message
            error_code: Specific error code (defaults to MISMATCH_ERROR)
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(
            message,
            error_code=error_code or ErrorCode.MISMATCH_ERROR,
            subtype=kwargs.pop("subtype", "result"),
            context=kwargs.pop("context", {}),
            **kwargs
        )


class TimeoutError(SwhidHarnessError):
    """Exception raised when an operation times out."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: Timeout value in seconds
            **kwargs: Additional arguments passed to base class
        """
        context = kwargs.pop("context", {})
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds
        
        super().__init__(
            message,
            error_code=ErrorCode.TIMEOUT,
            subtype="wall_clock",
            context=context,
            **kwargs
        )
        self.timeout_seconds = timeout_seconds


class ResourceLimitError(SwhidHarnessError):
    """Exception raised when resource limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        limit: Optional[Any] = None,
        actual: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize resource limit error.
        
        Args:
            message: Error message
            resource_type: Type of resource (e.g., "memory", "cpu")
            limit: Resource limit value
            actual: Actual resource usage
            **kwargs: Additional arguments passed to base class
        """
        context = kwargs.pop("context", {})
        if resource_type:
            context["resource_type"] = resource_type
        if limit is not None:
            context["limit"] = limit
        if actual is not None:
            context["actual"] = actual
        
        super().__init__(
            message,
            error_code=ErrorCode.RESOURCE_LIMIT,
            subtype=resource_type or "resource",
            context=context,
            **kwargs
        )
        self.resource_type = resource_type
        self.limit = limit
        self.actual = actual


class IOError(SwhidHarnessError):
    """Exception raised for I/O related errors."""
    
    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize I/O error.
        
        Args:
            message: Error message
            path: File or path that caused the error
            operation: I/O operation that failed (e.g., "read", "write")
            **kwargs: Additional arguments passed to base class
        """
        context = kwargs.pop("context", {})
        if path:
            context["path"] = path
        if operation:
            context["operation"] = operation
        
        super().__init__(
            message,
            error_code=ErrorCode.IO_ERROR,
            subtype=kwargs.pop("subtype", "io"),
            context=context,
            **kwargs
        )
        self.path = path
        self.operation = operation

