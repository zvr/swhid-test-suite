"""
Unit tests for plugin system
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from harness.plugins.base import (
    SwhidImplementation, ImplementationInfo, SwhidTestResult, ComparisonResult, 
    BenchmarkResult, ImplementationCapabilities
)
from harness.plugins.discovery import ImplementationDiscovery


class MockImplementation(SwhidImplementation):
    """Mock implementation for testing."""
    
    def __init__(self, name="mock", available=True, swhid="swh:1:cnt:test123"):
        self._name = name
        self._available = available
        self._swhid = swhid
    
    def get_info(self) -> ImplementationInfo:
        return ImplementationInfo(
            name=self._name,
            version="1.0.0",
            language="python",
            description="Mock implementation for testing"
        )
    
    def is_available(self) -> bool:
        return self._available
    
    def get_capabilities(self):
        from harness.plugins.base import ImplementationCapabilities
        return ImplementationCapabilities(
            supported_types=["cnt", "dir"],
            supported_qualifiers=[],
            api_version="1.0",
            max_payload_size_mb=100,
            supports_unicode=True,
            supports_percent_encoding=True
        )
    
    def compute_swhid(self, payload_path: str, obj_type: str = None) -> str:
        if not self._available:
            raise RuntimeError("Implementation not available")
        return self._swhid


class TestImplementationInfo:
    """Test ImplementationInfo dataclass."""
    
    def test_implementation_info_creation(self):
        """Test creating ImplementationInfo with required fields."""
        info = ImplementationInfo(
            name="test-impl",
            version="1.0.0",
            language="python"
        )
        
        assert info.name == "test-impl"
        assert info.version == "1.0.0"
        assert info.language == "python"
        assert info.dependencies == []
    
    def test_implementation_info_with_dependencies(self):
        """Test creating ImplementationInfo with dependencies."""
        info = ImplementationInfo(
            name="test-impl",
            version="1.0.0",
            language="python",
            dependencies=["dep1", "dep2"]
        )
        
        assert info.dependencies == ["dep1", "dep2"]


class TestSwhidTestResult:
    """Test SwhidTestResult dataclass."""
    
    def test_test_result_creation(self):
        """Test creating SwhidTestResult."""
        result = SwhidTestResult(
            payload_name="test.txt",
            payload_path="/path/to/test.txt",
            implementation="test-impl",
            swhid="swh:1:cnt:test123",
            error=None,
            duration=1.5,
            success=True
        )
        
        assert result.payload_name == "test.txt"
        assert result.swhid == "swh:1:cnt:test123"
        assert result.success is True
        assert result.timestamp is not None


class TestComparisonResult:
    """Test ComparisonResult dataclass."""
    
    def test_comparison_result_creation(self):
        """Test creating ComparisonResult."""
        results = {
            "impl1": SwhidTestResult("test.txt", "/path", "impl1", "swh:1:cnt:test123", None, 1.0, True),
            "impl2": SwhidTestResult("test.txt", "/path", "impl2", "swh:1:cnt:test123", None, 1.5, True)
        }
        
        comparison = ComparisonResult(
            payload_name="test.txt",
            payload_path="/path/to/test.txt",
            results=results,
            all_match=True,
            expected_swhid="swh:1:cnt:test123"
        )
        
        assert comparison.payload_name == "test.txt"
        assert comparison.all_match is True
        assert len(comparison.results) == 2


class TestSwhidImplementation:
    """Test SwhidImplementation base class."""
    
    def test_mock_implementation(self):
        """Test mock implementation works correctly."""
        impl = MockImplementation()
        
        assert impl.get_info().name == "mock"
        assert impl.is_available() is True
        assert impl.compute_swhid("/test/path") == "swh:1:cnt:test123"
    
    def test_detect_object_type_file(self):
        """Test object type detection for files."""
        impl = MockImplementation()
        
        with tempfile.NamedTemporaryFile() as f:
            obj_type = impl.detect_object_type(f.name)
            assert obj_type == "content"
    
    def test_detect_object_type_directory(self):
        """Test object type detection for directories."""
        impl = MockImplementation()
        
        with tempfile.TemporaryDirectory() as d:
            obj_type = impl.detect_object_type(d)
            assert obj_type == "directory"
    
    def test_detect_object_type_nonexistent(self):
        """Test object type detection for nonexistent path."""
        impl = MockImplementation()
        
        with pytest.raises(ValueError):
            impl.detect_object_type("/nonexistent/path")
    
    def test_benchmark(self):
        """Test benchmark method."""
        impl = MockImplementation()
        
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"test content")
            f.flush()
            
            result = impl.benchmark(f.name, iterations=5)
            
            assert result.implementation == "mock"
            assert result.iterations == 5
            assert result.mean_duration_ms > 0
            assert result.min_duration_ms > 0
            assert result.max_duration_ms > 0
    
    def test_benchmark_failure(self):
        """Test benchmark with failing implementation."""
        impl = MockImplementation(available=False)
        
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"test content")
            f.flush()
            
            with pytest.raises(RuntimeError, match="All benchmark iterations failed"):
                impl.benchmark(f.name, iterations=5)


class TestImplementationDiscovery:
    """Test ImplementationDiscovery class."""
    
    def test_discovery_initialization(self):
        """Test discovery system initialization."""
        discovery = ImplementationDiscovery("test_implementations")
        assert discovery.implementations_dir == Path("test_implementations")
        assert discovery._implementations_cache == {}
    
    def test_discover_implementations_empty_dir(self):
        """Test discovery with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            discovery = ImplementationDiscovery(temp_dir)
            implementations = discovery.discover_implementations()
            assert implementations == {}
    
    def test_discover_implementations_with_mock(self):
        """Test discovery with mock implementation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock implementation directory
            impl_dir = Path(temp_dir) / "mock_impl"
            impl_dir.mkdir()
            
            # Create implementation.py file
            impl_file = impl_dir / "implementation.py"
            impl_file.write_text('''
from harness.plugins.base import SwhidImplementation, ImplementationInfo, ImplementationCapabilities

class Implementation(SwhidImplementation):
    def get_info(self):
        return ImplementationInfo("mock", "1.0.0", "python")
    
    def is_available(self):
        return True
    
    def get_capabilities(self):
        return ImplementationCapabilities(
            supported_types=["cnt", "dir"],
            supported_qualifiers=[],
            api_version="1.0",
            max_payload_size_mb=100,
            supports_unicode=True,
            supports_percent_encoding=True
        )
    
    def compute_swhid(self, payload_path, obj_type=None):
        return "swh:1:cnt:mock123"
''')
            
            discovery = ImplementationDiscovery(temp_dir)
            implementations = discovery.discover_implementations()
            
            assert len(implementations) == 1
            assert "mock" in implementations
            assert implementations["mock"].get_info().name == "mock"
    
    def test_get_implementation(self):
        """Test getting specific implementation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock implementation
            impl_dir = Path(temp_dir) / "mock_impl"
            impl_dir.mkdir()
            
            impl_file = impl_dir / "implementation.py"
            impl_file.write_text('''
from harness.plugins.base import SwhidImplementation, ImplementationInfo, ImplementationCapabilities

class Implementation(SwhidImplementation):
    def get_info(self):
        return ImplementationInfo("mock", "1.0.0", "python")
    
    def is_available(self):
        return True
    
    def get_capabilities(self):
        return ImplementationCapabilities(
            supported_types=["cnt", "dir"],
            supported_qualifiers=[],
            api_version="1.0",
            max_payload_size_mb=100,
            supports_unicode=True,
            supports_percent_encoding=True
        )
    
    def compute_swhid(self, payload_path, obj_type=None):
        return "swh:1:cnt:mock123"
''')
            
            discovery = ImplementationDiscovery(temp_dir)
            impl = discovery.get_implementation("mock")
            
            assert impl is not None
            assert impl.get_info().name == "mock"
    
    def test_get_nonexistent_implementation(self):
        """Test getting nonexistent implementation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            discovery = ImplementationDiscovery(temp_dir)
            impl = discovery.get_implementation("nonexistent")
            assert impl is None
    
    def test_list_available_implementations(self):
        """Test listing available implementations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock implementation
            impl_dir = Path(temp_dir) / "mock_impl"
            impl_dir.mkdir()
            
            impl_file = impl_dir / "implementation.py"
            impl_file.write_text('''
from harness.plugins.base import SwhidImplementation, ImplementationInfo, ImplementationCapabilities

class Implementation(SwhidImplementation):
    def get_info(self):
        return ImplementationInfo("mock", "1.0.0", "python")
    
    def is_available(self):
        return True
    
    def get_capabilities(self):
        return ImplementationCapabilities(
            supported_types=["cnt", "dir"],
            supported_qualifiers=[],
            api_version="1.0",
            max_payload_size_mb=100,
            supports_unicode=True,
            supports_percent_encoding=True
        )
    
    def compute_swhid(self, payload_path, obj_type=None):
        return "swh:1:cnt:mock123"
''')
            
            discovery = ImplementationDiscovery(temp_dir)
            available = discovery.list_available_implementations()
            
            assert "mock" in available
    
    def test_clear_cache(self):
        """Test clearing implementation cache."""
        discovery = ImplementationDiscovery()
        discovery._implementations_cache["test"] = Mock()
        
        discovery.clear_cache()
        assert discovery._implementations_cache == {}
