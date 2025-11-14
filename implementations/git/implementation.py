"""
Git SWHID Implementation Plugin (dulwich)

This module provides an interface to Git-based SWHID computation using dulwich.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from harness.plugins.base import SwhidImplementation, ImplementationInfo, ImplementationCapabilities

try:
    import dulwich.objects
    import dulwich.repo
    DULWICH_AVAILABLE = True
except ImportError:
    DULWICH_AVAILABLE = False

class Implementation(SwhidImplementation):
    """Git SWHID implementation plugin using dulwich."""
    
    def get_info(self) -> ImplementationInfo:
        """Return implementation metadata."""
        return ImplementationInfo(
            name="git",
            version="1.0.0",
            language="python",
            description="Git SWHID implementation using dulwich library",
            dependencies=["dulwich"]
        )
    
    def is_available(self) -> bool:
        """Check if Git implementation is available."""
        return DULWICH_AVAILABLE
    
    def get_capabilities(self) -> ImplementationCapabilities:
        """Return implementation capabilities."""
        return ImplementationCapabilities(
            supported_types=["cnt", "dir", "rev", "rel", "snp"],
            supported_qualifiers=["origin", "visit", "anchor", "path", "lines"],
            api_version="1.0",
            max_payload_size_mb=1000,
            supports_unicode=True,
            supports_percent_encoding=True
        )
    
    def compute_swhid(self, payload_path: str, obj_type: Optional[str] = None) -> str:
        """Compute SWHID using Git's hashing algorithm via dulwich."""
        if not DULWICH_AVAILABLE:
            raise RuntimeError("dulwich library not available")
        
        payload_path = os.path.abspath(payload_path)
        
        if not os.path.exists(payload_path):
            raise FileNotFoundError(f"Payload not found: {payload_path}")
        
        # Auto-detect object type if not provided
        if obj_type is None:
            obj_type = self.detect_object_type(payload_path)
        
        # Skip snapshot objects as Git doesn't support them
        if obj_type == "snapshot":
            raise NotImplementedError("Git doesn't support snapshot objects")
        
        try:
            if obj_type == "content":
                return self._compute_content_swhid(payload_path)
            elif obj_type == "directory":
                return self._compute_directory_swhid(payload_path)
            elif obj_type == "revision":
                return self._compute_revision_swhid(payload_path)
            elif obj_type == "release":
                return self._compute_release_swhid(payload_path)
            else:
                raise ValueError(f"Unsupported object type: {obj_type}")
        except Exception as e:
            raise RuntimeError(f"Failed to compute Git SWHID: {e}")
    
    def _compute_content_swhid(self, file_path: str) -> str:
        """Compute content SWHID using Git blob hash."""
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Create Git blob object
        blob = dulwich.objects.Blob()
        blob.data = content
        
        # Get the hash
        blob_id = blob.id.decode('ascii')
        
        return f"swh:1:cnt:{blob_id}"
    
    def _compute_directory_swhid(self, dir_path: str) -> str:
        """Compute directory SWHID using Git tree hash."""
        # Create a temporary Git repository
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = os.path.join(temp_dir, "repo")
            os.makedirs(repo_path)
            
            # Initialize Git repository
            repo = dulwich.repo.Repo.init(repo_path)
            
            # Copy the directory contents maintaining the structure
            if os.path.isdir(dir_path):
                # Copy the entire directory structure, ignoring symlinks
                for root, dirs, files in os.walk(dir_path):
                    # Create corresponding directory in repo
                    rel_path = os.path.relpath(root, dir_path)
                    repo_dir = os.path.join(repo_path, rel_path)
                    os.makedirs(repo_dir, exist_ok=True)
                    
                    # Copy files and symlinks
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(repo_dir, file)
                        
                        # Handle symlinks - copy them as symlinks
                        if os.path.islink(src_file):
                            link_target = os.readlink(src_file)
                            os.symlink(link_target, dst_file)
                        # Copy regular files
                        elif os.path.isfile(src_file):
                            shutil.copy2(src_file, dst_file)
            else:
                # If it's a file, copy it to the repo root
                shutil.copy2(dir_path, repo_path)
            
            # Create tree for the root directory
            tree = self._create_git_tree(repo, repo_path)
            
            tree_id_str = tree.id.decode('ascii')
            return f"swh:1:dir:{tree_id_str}"
    
    def _create_git_tree(self, repo, dir_path):
        """Recursively create Git tree objects for a directory."""
        tree = dulwich.objects.Tree()
        
        # Get all entries in the directory
        entries = []
        for item in os.listdir(dir_path):
            # Skip .git directory (Git automatically excludes it)
            if item == '.git':
                continue
                
            item_path = os.path.join(dir_path, item)
            
            if os.path.islink(item_path):
                # Handle symlink - Git stores symlinks as blob with mode 0o120000
                link_target = os.readlink(item_path)
                blob = dulwich.objects.Blob()
                blob.data = link_target.encode('utf-8')
                repo.object_store.add_object(blob)
                entries.append((item.encode(), 0o120000, blob.id))
                
            elif os.path.isfile(item_path):
                # Handle file - check if executable
                with open(item_path, 'rb') as f:
                    content = f.read()
                
                blob = dulwich.objects.Blob()
                blob.data = content
                repo.object_store.add_object(blob)
                
                # Git uses 0o100755 for executable files, 0o100644 for regular files
                import stat
                file_mode = os.stat(item_path).st_mode
                mode = 0o100755 if (file_mode & stat.S_IEXEC) else 0o100644
                entries.append((item.encode(), mode, blob.id))
                
            elif os.path.isdir(item_path):
                # Handle subdirectory
                sub_tree = self._create_git_tree(repo, item_path)
                entries.append((item.encode(), 0o40000, sub_tree.id))
        
        # Sort entries (Git requires sorted tree entries)
        entries.sort(key=lambda x: x[0])
        
        # Add entries to tree
        for name, mode, sha in entries:
            tree.add(name, mode, sha)
        
        # Add tree to object store
        repo.object_store.add_object(tree)
        
        return tree
    
    def _compute_revision_swhid(self, repo_path: str) -> str:
        """Compute revision SWHID using Git commit hash."""
        # This would require parsing Git repository and finding the HEAD commit
        # For now, we'll skip this as it's complex and not needed for basic testing
        raise NotImplementedError("Git revision SWHID computation not implemented")
    
    def _compute_release_swhid(self, repo_path: str) -> str:
        """Compute release SWHID using Git tag hash."""
        # This would require parsing Git repository and finding tags
        # For now, we'll skip this as it's complex and not needed for basic testing
        raise NotImplementedError("Git release SWHID computation not implemented")
