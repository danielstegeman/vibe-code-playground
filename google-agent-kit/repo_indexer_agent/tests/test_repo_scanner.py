import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.repo_scanner import clone_repository, scan_and_analyze_repository


class TestCloneRepository:
    """Tests for clone_repository function."""
    
    def test_clone_repository_success(self):
        """Test successful repository cloning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "test_repo"
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr='')
                
                result = clone_repository(
                    repo_url="https://github.com/test/repo.git",
                    target_dir=str(target_dir),
                    shallow=True
                )
                
                assert result["status"] == "success"
                assert "Successfully cloned" in result["message"]
                assert result["path"] is not None
                
                # Verify git clone command was called
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert "git" in call_args
                assert "clone" in call_args
                assert "--depth" in call_args
                assert "1" in call_args
    
    def test_clone_repository_already_exists(self):
        """Test cloning when directory already exists with content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "existing_repo"
            target_dir.mkdir(parents=True)
            (target_dir / "test.txt").write_text("test")
            
            result = clone_repository(
                repo_url="https://github.com/test/repo.git",
                target_dir=str(target_dir)
            )
            
            assert result["status"] == "exists"
            assert "already exists" in result["message"]
            assert result["path"] is not None
    
    def test_clone_repository_failure(self):
        """Test failed repository cloning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "test_repo"
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1, 
                    stderr='fatal: repository not found'
                )
                
                result = clone_repository(
                    repo_url="https://github.com/test/invalid.git",
                    target_dir=str(target_dir)
                )
                
                assert result["status"] == "error"
                assert "Failed to clone" in result["message"]
                assert result["path"] is None
    
    def test_clone_repository_timeout(self):
        """Test repository cloning timeout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "test_repo"
            
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(cmd='git', timeout=600)
                
                result = clone_repository(
                    repo_url="https://github.com/test/repo.git",
                    target_dir=str(target_dir)
                )
                
                assert result["status"] == "error"
                assert "timed out" in result["message"]
                assert result["path"] is None
    
    def test_clone_repository_no_shallow(self):
        """Test full clone (not shallow)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "test_repo"
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr='')
                
                result = clone_repository(
                    repo_url="https://github.com/test/repo.git",
                    target_dir=str(target_dir),
                    shallow=False
                )
                
                assert result["status"] == "success"
                
                # Verify --depth is NOT in the command
                call_args = mock_run.call_args[0][0]
                assert "git" in call_args
                assert "clone" in call_args
                assert "--depth" not in call_args


class TestScanAndAnalyzeRepository:
    """Tests for scan_and_analyze_repository function."""
    
    @pytest.fixture
    def test_repo(self):
        """Create a temporary test repository structure."""
        tmpdir = tempfile.mkdtemp()
        repo_path = Path(tmpdir)
        
        # Create directory structure
        (repo_path / "src").mkdir()
        (repo_path / "src" / "utils").mkdir()
        (repo_path / "tests").mkdir()
        (repo_path / "docs").mkdir()
        
        # Create files
        (repo_path / "README.md").write_text("# Test Repo")
        (repo_path / "setup.py").write_text("from setuptools import setup")
        (repo_path / "src" / "main.py").write_text("def main(): pass")
        (repo_path / "src" / "utils" / "helper.py").write_text("def helper(): pass")
        (repo_path / "tests" / "test_main.py").write_text("def test_main(): pass")
        (repo_path / "docs" / "guide.txt").write_text("User guide")
        
        # Create a node_modules folder (should be excluded)
        (repo_path / "node_modules").mkdir()
        (repo_path / "node_modules" / "package.json").write_text("{}")
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(tmpdir)
    
    def test_scan_basic_structure(self, test_repo):
        """Test basic directory scanning."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_url="https://github.com/test/repo.git",
            repo_name="test_repo"
        )
        
        assert result["status"] == "success"
        assert result["repository_name"] == "test_repo"
        assert result["repository_url"] == "https://github.com/test/repo.git"
        assert result["total_files"] >= 6  # At least 6 files (excluding node_modules)
        assert result["total_directories"] > 0
        assert result["total_size_bytes"] > 0
    
    def test_scan_file_type_distribution(self, test_repo):
        """Test file type distribution analysis."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_name="test_repo"
        )
        
        assert result["status"] == "success"
        file_types = result["file_type_distribution"]
        
        # Check for expected file types
        assert ".py" in file_types
        assert ".md" in file_types
        assert ".txt" in file_types
        
        # Verify counts
        assert file_types[".py"] >= 3  # main.py, helper.py, test_main.py
    
    def test_scan_excludes_directories(self, test_repo):
        """Test that excluded directories are not scanned."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_name="test_repo"
        )
        
        assert result["status"] == "success"
        
        # node_modules should be excluded
        all_paths = [f["path"] for f in result.get("largest_files", [])]
        assert not any("node_modules" in path for path in all_paths)
        
        dir_paths = [d["path"] for d in result["directory_stats"]]
        assert not any("node_modules" in path for path in dir_paths)
    
    def test_scan_largest_files(self, test_repo):
        """Test largest files detection."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_name="test_repo"
        )
        
        assert result["status"] == "success"
        largest_files = result["largest_files"]
        
        assert len(largest_files) > 0
        assert all("path" in f for f in largest_files)
        assert all("size_bytes" in f for f in largest_files)
        assert all("extension" in f for f in largest_files)
        
        # Verify files are sorted by size (descending)
        sizes = [f["size_bytes"] for f in largest_files]
        assert sizes == sorted(sizes, reverse=True)
    
    def test_scan_directory_stats(self, test_repo):
        """Test directory statistics."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_name="test_repo"
        )
        
        assert result["status"] == "success"
        dir_stats = result["directory_stats"]
        
        assert len(dir_stats) > 0
        
        # Check structure of directory stats
        for stat in dir_stats:
            assert "path" in stat
            assert "total_files" in stat
            assert "total_size_bytes" in stat
            assert "subdirectories" in stat
            assert "file_types" in stat
    
    def test_scan_nonexistent_path(self):
        """Test scanning non-existent path."""
        result = scan_and_analyze_repository(
            root_path="/nonexistent/path/to/repo",
            repo_name="test_repo"
        )
        
        assert result["status"] == "error"
        assert "does not exist" in result["message"]
    
    def test_scan_with_max_depth(self, test_repo):
        """Test scanning with maximum depth limit."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_name="test_repo",
            max_depth=1
        )
        
        assert result["status"] == "success"
        assert result["max_depth"] <= 1
        
        # Files in deeper directories should not be included
        all_paths = [f["path"] for f in result.get("largest_files", [])]
        # src/utils/helper.py should not be included (depth 2)
        assert not any("utils" in path for path in all_paths)
    
    def test_scan_repo_name_inference(self, test_repo):
        """Test repository name inference from path."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo)
        )
        
        assert result["status"] == "success"
        assert result["repository_name"] == test_repo.name
    
    def test_scan_indexed_at_timestamp(self, test_repo):
        """Test that indexed_at timestamp is included."""
        result = scan_and_analyze_repository(
            root_path=str(test_repo),
            repo_name="test_repo"
        )
        
        assert result["status"] == "success"
        assert "indexed_at" in result
        assert isinstance(result["indexed_at"], str)
        # Should be ISO format datetime string
        from datetime import datetime
        datetime.fromisoformat(result["indexed_at"])  # Should not raise
    
    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = scan_and_analyze_repository(
                root_path=tmpdir,
                repo_name="empty_repo"
            )
            
            assert result["status"] == "success"
            assert result["total_files"] == 0
            assert result["total_size_bytes"] == 0
