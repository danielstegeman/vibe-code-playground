# Repository Indexer Agent Tests

This directory contains pytest tests for the repository indexer agent tools.

## Running Tests

### Run all tests
```bash
cd repo_indexer_agent
pytest
```

### Run specific test file
```bash
pytest tests/test_repo_scanner.py
pytest tests/test_output_formatter.py
```

### Run specific test class or function
```bash
pytest tests/test_repo_scanner.py::TestCloneRepository
pytest tests/test_repo_scanner.py::TestCloneRepository::test_clone_repository_success
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=tools --cov-report=html
```

### Run only fast tests (skip slow tests)
```bash
pytest -m "not slow"
```

## Test Structure

- `test_repo_scanner.py` - Tests for repository cloning and scanning functions
  - `TestCloneRepository` - Tests for `clone_repository` function
  - `TestScanAndAnalyzeRepository` - Tests for `scan_and_analyze_repository` function

- `test_output_formatter.py` - Tests for output formatting and file saving
  - `TestFormatBytes` - Tests for `format_bytes` function
  - `TestFormatIndexToText` - Tests for `format_index_to_text` function
  - `TestSaveIndexToFile` - Tests for `save_index_to_file` function

- `conftest.py` - Shared pytest configuration and fixtures

## Test Coverage

The tests cover:
- ✓ Successful operations
- ✓ Error handling
- ✓ Edge cases (empty directories, missing paths, etc.)
- ✓ File system operations
- ✓ Subprocess execution (mocked)
- ✓ Data validation
- ✓ Unicode/encoding handling

## Adding New Tests

When adding new functionality to the tools, please add corresponding tests following the existing patterns:

1. Create a test class for each function/feature
2. Use descriptive test method names (`test_<what_is_being_tested>`)
3. Use fixtures for common test data
4. Mock external dependencies (subprocess, file system when appropriate)
5. Test both success and failure paths
6. Clean up temporary resources
