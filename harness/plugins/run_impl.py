#!/usr/bin/env python3
"""
Wrapper script for running implementations in subprocess with JSON protocol.

This script is used by SubprocessAdapter to run implementations in isolation.
Protocol: JSON over stdin/stdout
"""

import json
import sys
import os
import importlib
import traceback
from typing import Optional, Dict, Any

# Protocol version
PROTOCOL_VERSION = "1.0"


def load_implementation(impl_module_path: str, impl_class_name: str = "Implementation"):
    """
    Load an implementation class dynamically.
    
    Args:
        impl_module_path: Full module path (e.g., "implementations.python.implementation")
        impl_class_name: Class name (default: "Implementation")
    
    Returns:
        Implementation instance
    """
    try:
        module = importlib.import_module(impl_module_path)
        impl_class = getattr(module, impl_class_name)
        return impl_class()
    except Exception as e:
        raise RuntimeError(f"Failed to load implementation {impl_module_path}.{impl_class_name}: {e}")


def handle_request(request: Dict[str, Any], impl) -> Dict[str, Any]:
    """
    Handle a protocol request.
    
    Request format:
    {
        "op": "compute" | "capabilities" | "info",
        "payload_path": "...",  # for compute
        "obj_type": "...",       # optional for compute
        "impl_module": "...",   # for initialization
        "impl_class": "..."      # optional, defaults to "Implementation"
    }
    
    Response format:
    {
        "ok": true/false,
        "swhid": "...",          # for compute
        "capabilities": {...},   # for capabilities
        "info": {...},           # for info
        "error": {...}           # if ok=false
    }
    """
    op = request.get("op")
    
    if op == "compute":
        payload_path = request.get("payload_path")
        obj_type = request.get("obj_type")
        
        if not payload_path:
            return {
                "ok": False,
                "error": {"message": "Missing payload_path", "code": "INVALID_REQUEST"}
            }
        
        try:
            swhid = impl.compute_swhid(payload_path, obj_type)
            return {
                "ok": True,
                "swhid": swhid
            }
        except Exception as e:
            return {
                "ok": False,
                "error": {
                    "message": str(e),
                    "code": "COMPUTE_ERROR",
                    "traceback": traceback.format_exc()
                }
            }
    
    elif op == "capabilities":
        try:
            caps = impl.get_capabilities()
            return {
                "ok": True,
                "capabilities": caps.to_dict()
            }
        except Exception as e:
            return {
                "ok": False,
                "error": {
                    "message": str(e),
                    "code": "CAPABILITIES_ERROR"
                }
            }
    
    elif op == "info":
        try:
            info = impl.get_info()
            return {
                "ok": True,
                "info": {
                    "name": info.name,
                    "version": info.version,
                    "language": info.language,
                    "description": info.description
                }
            }
        except Exception as e:
            return {
                "ok": False,
                "error": {
                    "message": str(e),
                    "code": "INFO_ERROR"
                }
            }
    
    else:
        return {
            "ok": False,
            "error": {
                "message": f"Unknown operation: {op}",
                "code": "INVALID_OPERATION"
            }
        }


def main():
    """Main entry point for JSON protocol wrapper."""
    # Read request from stdin
    try:
        request_json = sys.stdin.read()
        if not request_json.strip():
            # Empty input - send protocol info
            response = {
                "ok": True,
                "protocol_version": PROTOCOL_VERSION,
                "message": "SWHID Implementation Wrapper"
            }
            print(json.dumps(response))
            return 0
        
        request = json.loads(request_json)
    except json.JSONDecodeError as e:
        response = {
            "ok": False,
            "error": {
                "message": f"Invalid JSON: {e}",
                "code": "JSON_ERROR"
            }
        }
        print(json.dumps(response))
        return 1
    except Exception as e:
        response = {
            "ok": False,
            "error": {
                "message": f"Failed to read request: {e}",
                "code": "IO_ERROR"
            }
        }
        print(json.dumps(response))
        return 1
    
    # Load implementation if needed
    impl_module = request.get("impl_module")
    impl_class = request.get("impl_class", "Implementation")
    
    if impl_module:
        try:
            impl = load_implementation(impl_module, impl_class)
        except Exception as e:
            response = {
                "ok": False,
                "error": {
                    "message": str(e),
                    "code": "LOAD_ERROR"
                }
            }
            print(json.dumps(response))
            return 1
    else:
        # Implementation should be passed via environment or pre-loaded
        response = {
            "ok": False,
            "error": {
                "message": "Missing impl_module in request",
                "code": "INVALID_REQUEST"
            }
        }
        print(json.dumps(response))
        return 1
    
    # Handle request
    try:
        response = handle_request(request, impl)
        print(json.dumps(response))
        return 0 if response.get("ok") else 1
    except Exception as e:
        response = {
            "ok": False,
            "error": {
                "message": f"Unexpected error: {e}",
                "code": "INTERNAL_ERROR",
                "traceback": traceback.format_exc()
            }
        }
        print(json.dumps(response))
        return 1


if __name__ == "__main__":
    sys.exit(main())

