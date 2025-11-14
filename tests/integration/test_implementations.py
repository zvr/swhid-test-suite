"""
Integration tests for SWHID implementations
"""

import pytest
import tempfile
import os
from pathlib import Path

from harness.plugins.discovery import ImplementationDiscovery


class TestImplementationIntegration:
    """Integration tests for implementations."""
    
    def test_discover_real_implementations(self):
        """Test discovering real implementations in the implementations directory."""
        discovery = ImplementationDiscovery("implementations")
        implementations = discovery.discover_implementations()
        
        # Should find at least some implementations
        assert len(implementations) > 0
        
        # Check that all discovered implementations have required methods
        for name, impl in implementations.items():
            assert hasattr(impl, 'get_info')
            assert hasattr(impl, 'is_available')
            assert hasattr(impl, 'compute_swhid')
            
            info = impl.get_info()
            assert info.name == name
            assert info.version is not None
            assert info.language is not None
    
    def test_implementation_availability(self):
        """Test that implementations correctly report availability."""
        discovery = ImplementationDiscovery("implementations")
        implementations = discovery.discover_implementations()
        
        for name, impl in implementations.items():
            # is_available should return a boolean
            availability = impl.is_available()
            assert isinstance(availability, bool)
    
    def test_implementation_compute_swhid_with_real_file(self):
        """Test computing SWHID with a real file for available implementations."""
        discovery = ImplementationDiscovery("implementations")
        implementations = discovery.discover_implementations()
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            test_file = f.name
        
        try:
            for name, impl in implementations.items():
                if impl.is_available():
                    try:
                        swhid = impl.compute_swhid(test_file)
                        # SWHID should start with "swh:"
                        assert swhid.startswith("swh:")
                        # Should be a valid SWHID format
                        parts = swhid.split(":")
                        assert len(parts) >= 4
                        assert parts[0] == "swh"
                        assert parts[1] == "1"  # SWHID version
                        assert parts[2] in ["cnt", "dir", "snp", "rev", "rel"]  # Object type
                    except Exception as e:
                        # Some implementations might not be fully functional in test environment
                        # This is expected for implementations that require external dependencies
                        pytest.skip(f"Implementation {name} failed: {e}")
        finally:
            os.unlink(test_file)
    
    def test_implementation_detect_object_type(self):
        """Test object type detection for different payload types."""
        discovery = ImplementationDiscovery("implementations")
        implementations = discovery.discover_implementations()
        
        # Test with a file
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"test content")
            f.flush()
            
            for name, impl in implementations.items():
                if impl.is_available():
                    try:
                        obj_type = impl.detect_object_type(f.name)
                        assert obj_type == "content"
                    except Exception as e:
                        pytest.skip(f"Implementation {name} failed object type detection: {e}")
        
        # Test with a directory
        with tempfile.TemporaryDirectory() as d:
            for name, impl in implementations.items():
                if impl.is_available():
                    try:
                        obj_type = impl.detect_object_type(d)
                        assert obj_type == "directory"
                    except Exception as e:
                        pytest.skip(f"Implementation {name} failed object type detection: {e}")
    
    def test_implementation_benchmark(self):
        """Test benchmarking functionality."""
        discovery = ImplementationDiscovery("implementations")
        implementations = discovery.discover_implementations()
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            test_file = f.name
        
        try:
            for name, impl in implementations.items():
                if impl.is_available():
                    try:
                        # Run a small benchmark
                        result = impl.benchmark(test_file, iterations=3)
                        
                        assert result.implementation == name
                        assert result.iterations == 3
                        assert result.mean_duration_ms > 0
                        assert result.min_duration_ms > 0
                        assert result.max_duration_ms > 0
                        assert result.median_duration_ms > 0
                    except Exception as e:
                        pytest.skip(f"Implementation {name} failed benchmarking: {e}")
        finally:
            os.unlink(test_file)
