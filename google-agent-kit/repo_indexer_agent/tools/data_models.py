from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class FileInfo(BaseModel):
    """Information about a single file."""
    path: str
    size_bytes: int
    extension: str
    last_modified: Optional[datetime] = None


class DirectoryStats(BaseModel):
    """Statistics for a directory."""
    path: str
    total_files: int
    total_size_bytes: int
    subdirectories: int
    file_types: Dict[str, int] = Field(default_factory=dict)


class RepositoryIndex(BaseModel):
    """Complete repository index information."""
    repository_url: str
    repository_name: str
    indexed_at: datetime
    total_files: int
    total_directories: int
    total_size_bytes: int
    file_type_distribution: Dict[str, int] = Field(default_factory=dict)
    directory_stats: List[DirectoryStats] = Field(default_factory=list)
    largest_files: List[FileInfo] = Field(default_factory=list)
    depth_levels: int = 0
    
    def to_text_format(self) -> str:
        """Convert index to human-readable plain text format."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"REPOSITORY INDEX REPORT")
        lines.append("=" * 80)
        lines.append(f"Repository: {self.repository_name}")
        lines.append(f"URL: {self.repository_url}")
        lines.append(f"Indexed at: {self.indexed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("-" * 80)
        lines.append("SUMMARY STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Total Files: {self.total_files:,}")
        lines.append(f"Total Directories: {self.total_directories:,}")
        lines.append(f"Total Size: {self._format_bytes(self.total_size_bytes)}")
        lines.append(f"Maximum Depth: {self.depth_levels}")
        lines.append("")
        
        lines.append("-" * 80)
        lines.append("FILE TYPE DISTRIBUTION")
        lines.append("-" * 80)
        sorted_types = sorted(self.file_type_distribution.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:20]:  # Top 20 file types
            percentage = (count / self.total_files * 100) if self.total_files > 0 else 0
            ext_display = ext if ext else "(no extension)"
            lines.append(f"{ext_display:20} {count:8,} files ({percentage:5.2f}%)")
        lines.append("")
        
        lines.append("-" * 80)
        lines.append("LARGEST FILES")
        lines.append("-" * 80)
        for i, file_info in enumerate(self.largest_files[:10], 1):  # Top 10 largest
            lines.append(f"{i:2}. {self._format_bytes(file_info.size_bytes):>10} - {file_info.path}")
        lines.append("")
        
        lines.append("-" * 80)
        lines.append("DIRECTORY STATISTICS (Top 20 by file count)")
        lines.append("-" * 80)
        sorted_dirs = sorted(self.directory_stats, key=lambda x: x.total_files, reverse=True)
        for dir_stat in sorted_dirs[:20]:
            lines.append(f"\n{dir_stat.path}")
            lines.append(f"  Files: {dir_stat.total_files:,} | Subdirs: {dir_stat.subdirectories:,} | Size: {self._format_bytes(dir_stat.total_size_bytes)}")
            if dir_stat.file_types:
                top_types = sorted(dir_stat.file_types.items(), key=lambda x: x[1], reverse=True)[:5]
                type_str = ", ".join([f"{ext}({count})" for ext, count in top_types])
                lines.append(f"  Top types: {type_str}")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_bytes(bytes_val: int) -> str:
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
