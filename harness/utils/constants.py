"""
Constants and enums for the SWHID Testing Harness.

This module provides named constants and enums to replace magic values
throughout the codebase.
"""

from enum import Enum
from typing import Literal


# SWHID format constants
SWHID_PREFIX = "swh:"
SWHID_V1_PREFIX = "swh:1:"
SWHID_V2_PREFIX = "swh:2:"

# SWHID type codes
class SwhidTypeCode(str, Enum):
    """SWHID object type codes."""
    CONTENT = "cnt"
    DIRECTORY = "dir"
    REVISION = "rev"
    RELEASE = "rel"
    SNAPSHOT = "snp"


# Object types
class ObjectType(str, Enum):
    """Object type names."""
    CONTENT = "content"
    DIRECTORY = "directory"
    REVISION = "revision"
    RELEASE = "release"
    SNAPSHOT = "snapshot"
    AUTO = "auto"


# Test status
class TestStatus(str, Enum):
    """Test result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


# Status literal type for type hints
Status = Literal["PASS", "FAIL", "SKIPPED"]

# Timeout constants (in seconds)
DEFAULT_TIMEOUT = 30
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 300
GIT_OPERATION_TIMEOUT = 10

# Path constants
DEFAULT_RESULTS_DIR = "results"
DEFAULT_CONFIG_FILE = "config.yaml"
IMPLEMENTATIONS_DIR = "implementations"

# Default settings
DEFAULT_PARALLEL_TESTS = 4
MAX_PARALLEL_TESTS = 32
DEFAULT_MAX_FILE_SIZE = "100MB"

# Object type to SWHID code mapping
OBJ_TYPE_TO_SWHID_CODE: dict[str, str] = {
    ObjectType.CONTENT: SwhidTypeCode.CONTENT,
    ObjectType.DIRECTORY: SwhidTypeCode.DIRECTORY,
    ObjectType.REVISION: SwhidTypeCode.REVISION,
    ObjectType.RELEASE: SwhidTypeCode.RELEASE,
    ObjectType.SNAPSHOT: SwhidTypeCode.SNAPSHOT,
}

# SWHID code to object type mapping (reverse)
SWHID_CODE_TO_OBJ_TYPE: dict[str, str] = {
    SwhidTypeCode.CONTENT: ObjectType.CONTENT,
    SwhidTypeCode.DIRECTORY: ObjectType.DIRECTORY,
    SwhidTypeCode.REVISION: ObjectType.REVISION,
    SwhidTypeCode.RELEASE: ObjectType.RELEASE,
    SwhidTypeCode.SNAPSHOT: ObjectType.SNAPSHOT,
}


def obj_type_to_swhid_code(obj_type: str) -> str:
    """
    Convert object type to SWHID type code.
    
    Args:
        obj_type: Object type name (e.g., "content", "directory")
        
    Returns:
        SWHID type code (e.g., "cnt", "dir")
    """
    return OBJ_TYPE_TO_SWHID_CODE.get(obj_type, obj_type)


def swhid_code_to_obj_type(swhid_code: str) -> str:
    """
    Convert SWHID type code to object type.
    
    Args:
        swhid_code: SWHID type code (e.g., "cnt", "dir")
        
    Returns:
        Object type name (e.g., "content", "directory")
    """
    return SWHID_CODE_TO_OBJ_TYPE.get(swhid_code, swhid_code)

