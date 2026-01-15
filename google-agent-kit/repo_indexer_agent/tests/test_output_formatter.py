import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.output_formatter import format_bytes, format_index_to_text, save_index_to_file


class TestFormatBytes:
    """Tests for format_bytes function."""
    
    def test_bytes(self):
        """Test formatting bytes."""
        assert format_bytes(512) == "512.00 B"
        assert format_bytes(0) == "0.00 B"
        assert format_bytes(1) == "1.00 B"
    
    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(2048) == "2.00 KB"
        assert format_bytes(1536) == "1.50 KB"
    
    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_bytes(1024 * 1024) == "1.00 MB"
        assert format_bytes(5 * 1024 * 1024) == "5.00 MB"
    
    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"
        assert format_bytes(10 * 1024 * 1024 * 1024) == "10.00 GB"
    
    def test_terabytes(self):
        """Test formatting terabytes."""
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.00 TB"
    
    def test_petabytes(self):
        """Test formatting petabytes."""
        assert format_bytes(1024 * 1024 * 1024 * 1024 * 1024) == "1.00 PB"


class TestFormatIndexToText:
    """Tests for format_index_to_text function."""
    
    @pytest.fixture
    def sample_index_data(self):
        """Sample index data for testing."""
        return {
            "repository_name": "test_repo",
            "repository_url": "https://github.com/test/repo.git",
            "indexed_at": "2026-01-12T21:00:00",
            "total_files": 150,
            "total_directories": 20,
            "total_size_bytes": 1024 * 1024 * 5,  # 5 MB
            "max_depth": 4,
            "file_type_distribution": {
                ".py": 80,
                ".md": 10,
                ".txt": 20,
                ".json": 15,
                ".yaml": 25
            },
            "largest_files": [
                {"path": "src/main.py", "size_bytes": 102400, "extension": ".py"},
                {"path": "docs/guide.md", "size_bytes": 51200, "extension": ".md"},
                {"path": "data/config.json", "size_bytes": 25600, "extension": ".json"}
            ],
            "directory_stats": [
                {
                    "path": "src",
                    "total_files": 50,
                    "subdirectories": 5,
                    "total_size_bytes": 2048000,
                    "file_types": {".py": 45, ".txt": 5}
                },
                {
                    "path": "tests",
                    "total_files": 30,
                    "subdirectories": 2,
                    "total_size_bytes": 512000,
                    "file_types": {".py": 30}
                }
            ]
        }
    
    def test_format_basic_structure(self, sample_index_data):
        """Test basic text formatting structure."""
        result = format_index_to_text(sample_index_data)
        
        assert "REPOSITORY INDEX REPORT" in result
        assert "test_repo" in result
        assert "https://github.com/test/repo.git" in result
        assert "2026-01-12T21:00:00" in result
    
    def test_format_summary_statistics(self, sample_index_data):
        """Test summary statistics section."""
        result = format_index_to_text(sample_index_data)
        
        assert "SUMMARY STATISTICS" in result
        assert "Total Files: 150" in result
        assert "Total Directories: 20" in result
        assert "5.00 MB" in result  # Total size formatted
        assert "Maximum Depth: 4" in result
    
    def test_format_file_type_distribution(self, sample_index_data):
        """Test file type distribution section."""
        result = format_index_to_text(sample_index_data)
        
        assert "FILE TYPE DISTRIBUTION" in result
        assert ".py" in result
        assert ".md" in result
        assert ".txt" in result
        
        # Check for counts and percentages
        assert "80" in result  # .py count
        assert "10" in result  # .md count
    
    def test_format_largest_files(self, sample_index_data):
        """Test largest files section."""
        result = format_index_to_text(sample_index_data)
        
        assert "LARGEST FILES" in result
        assert "src/main.py" in result
        assert "docs/guide.md" in result
        assert "100.00 KB" in result  # main.py size
        assert "50.00 KB" in result   # guide.md size
    
    def test_format_directory_statistics(self, sample_index_data):
        """Test directory statistics section."""
        result = format_index_to_text(sample_index_data)
        
        assert "DIRECTORY STATISTICS" in result
        assert "src" in result
        assert "tests" in result
        assert "Files: 50" in result
        assert "Subdirs: 5" in result
    
    def test_format_empty_data(self):
        """Test formatting with minimal data."""
        minimal_data = {
            "repository_name": "empty_repo",
            "total_files": 0,
            "total_directories": 0,
            "total_size_bytes": 0,
            "max_depth": 0
        }
        
        result = format_index_to_text(minimal_data)
        
        assert "REPOSITORY INDEX REPORT" in result
        assert "empty_repo" in result
        assert "Total Files: 0" in result
    
    def test_format_without_url(self, sample_index_data):
        """Test formatting when repository URL is not provided."""
        data = sample_index_data.copy()
        data["repository_url"] = ""
        
        result = format_index_to_text(data)
        
        assert "REPOSITORY INDEX REPORT" in result
        assert "test_repo" in result
        # URL line should not be present or should be handled gracefully
    
    def test_format_end_of_report(self, sample_index_data):
        """Test that report has proper ending."""
        result = format_index_to_text(sample_index_data)
        
        assert "END OF REPORT" in result
        assert result.strip().endswith("=" * 80)


class TestSaveIndexToFile:
    """Tests for save_index_to_file function."""
    
    @pytest.fixture
    def sample_index_data(self):
        """Sample index data for testing."""
        return {
            "repository_name": "test_repo",
            "repository_url": "https://github.com/test/repo.git",
            "indexed_at": "2026-01-12T21:00:00",
            "total_files": 100,
            "total_directories": 10,
            "total_size_bytes": 1024000,
            "max_depth": 3,
            "file_type_distribution": {".py": 50, ".md": 20, ".txt": 30},
            "largest_files": [],
            "directory_stats": []
        }
    
    def test_save_to_file_success(self, sample_index_data):
        """Test successful file saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.txt"
            
            result = save_index_to_file(sample_index_data, str(output_path))
            
            assert result["status"] == "success"
            assert "saved successfully" in result["message"]
            assert result["path"] == str(output_path.absolute())
            assert result["size_bytes"] > 0
            
            # Verify file was created and has content
            assert output_path.exists()
            content = output_path.read_text()
            assert "REPOSITORY INDEX REPORT" in content
            assert "test_repo" in content
    
    def test_save_creates_directories(self, sample_index_data):
        """Test that parent directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dirs" / "index.txt"
            
            result = save_index_to_file(sample_index_data, str(output_path))
            
            assert result["status"] == "success"
            assert output_path.exists()
            assert output_path.parent.exists()
    
    def test_save_overwrites_existing_file(self, sample_index_data):
        """Test that existing file is overwritten."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.txt"
            
            # Create existing file with different content
            output_path.write_text("old content")
            old_size = output_path.stat().st_size
            
            result = save_index_to_file(sample_index_data, str(output_path))
            
            assert result["status"] == "success"
            assert output_path.exists()
            
            # Content should be different
            new_content = output_path.read_text()
            assert "old content" not in new_content
            assert "REPOSITORY INDEX REPORT" in new_content
    
    def test_save_returns_correct_size(self, sample_index_data):
        """Test that returned size is positive and reasonable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.txt"
            
            result = save_index_to_file(sample_index_data, str(output_path))
            
            assert result["status"] == "success"
            # Size should be positive and greater than 0
            assert result["size_bytes"] > 0
            # File size on disk should also be positive
            actual_size = output_path.stat().st_size
            assert actual_size > 0
            # Sizes should be close (accounting for line ending differences)
            assert abs(result["size_bytes"] - actual_size) < 100
    
    def test_save_to_invalid_path(self, sample_index_data):
        """Test saving to an invalid path."""
        # Use a path that cannot be created (e.g., invalid characters on Windows)
        invalid_path = "/invalid/\x00/path/index.txt" if sys.platform != "win32" else "Z:\\nonexistent\\drive\\index.txt"
        
        result = save_index_to_file(sample_index_data, invalid_path)
        
        assert result["status"] == "error"
        assert "Failed to save" in result["message"]
        assert result["path"] is None
        assert result["size_bytes"] == 0
    
    def test_save_with_utf8_encoding(self, sample_index_data):
        """Test that file is saved with UTF-8 encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "index.txt"
            
            # Add some Unicode characters to the data
            sample_index_data["repository_name"] = "test_repo_with_émojis_🚀"
            
            result = save_index_to_file(sample_index_data, str(output_path))
            
            assert result["status"] == "success"
            
            # Read back and verify Unicode characters are preserved
            content = output_path.read_text(encoding='utf-8')
            assert "test_repo_with_émojis_🚀" in content
    
    def test_save_absolute_path_in_result(self, sample_index_data):
        """Test that result contains absolute path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use relative path
            output_path = Path(tmpdir) / "index.txt"
            
            result = save_index_to_file(sample_index_data, str(output_path))
            
            assert result["status"] == "success"
            result_path = Path(result["path"])
            assert result_path.is_absolute()
