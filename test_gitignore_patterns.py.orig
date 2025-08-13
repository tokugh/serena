#!/usr/bin/env python3
"""
Test script to verify the GitignoreParser implementation correctly handles nested .gitignore patterns.
"""

import os
import shutil
import tempfile
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

try:
    from serena.util.file_system import GitignoreParser
except ImportError:
    print("Error: Could not import GitignoreParser. Make sure the Python path is set correctly.")
    sys.exit(1)


def setup_test_repo():
    """Set up a test repository with nested .gitignore files and test files."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    repo_path = Path(test_dir)
    
    # Create directory structure
    foo_dir = repo_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "bar").mkdir()
    (foo_dir / "bar" / "baz").mkdir()
    
    # Create test files
    (repo_path / "foo.txt").touch()
    (foo_dir / "foo.txt").touch()
    (foo_dir / "bar" / "foo.txt").touch()
    (foo_dir / "bar" / "baz" / "foo.txt").touch()
    
    return repo_path


def test_anchored_pattern(repo_path):
    """Test anchored pattern (/foo.txt) in subdirectory .gitignore."""
    print("\n=== Testing anchored pattern (/foo.txt) in subdirectory .gitignore ===")
    
    # Create .gitignore in foo/ with anchored pattern
    foo_dir = repo_path / "foo"
    gitignore = foo_dir / ".gitignore"
    gitignore.write_text("/foo.txt")
    
    parser = GitignoreParser(str(repo_path))
    
    # Test cases
    test_cases = [
        ("foo/foo.txt", True, "foo/foo.txt should be ignored"),
        ("foo/bar/foo.txt", False, "foo/bar/foo.txt should NOT be ignored"),
        ("foo.txt", False, "/foo.txt should NOT be ignored"),
    ]
    
    all_passed = True
    for path, expected, message in test_cases:
        result = parser.should_ignore(path)
        passed = result == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {message} (got {result}, expected {expected})")
    
    return all_passed


def test_double_star_pattern(repo_path):
    """Test **/ pattern (**/foo.txt) in subdirectory .gitignore."""
    print("\n=== Testing **/ pattern (**/foo.txt) in subdirectory .gitignore ===")
    
    # Create .gitignore in foo/ with **/ pattern
    foo_dir = repo_path / "foo"
    gitignore = foo_dir / ".gitignore"
    gitignore.write_text("**/foo.txt")
    
    parser = GitignoreParser(str(repo_path))
    
    # Test cases
    test_cases = [
        ("foo/foo.txt", True, "foo/foo.txt should be ignored"),
        ("foo/bar/foo.txt", True, "foo/bar/foo.txt should be ignored"),
        ("foo/bar/baz/foo.txt", True, "foo/bar/baz/foo.txt should be ignored"),
        ("foo.txt", False, "/foo.txt should NOT be ignored"),
    ]
    
    all_passed = True
    for path, expected, message in test_cases:
        result = parser.should_ignore(path)
        passed = result == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {message} (got {result}, expected {expected})")
    
    return all_passed


def test_slash_double_star_pattern(repo_path):
    """Test /**/ pattern (/**/foo.txt) in subdirectory .gitignore."""
    print("\n=== Testing /**/ pattern (/**/foo.txt) in subdirectory .gitignore ===")
    
    # Create .gitignore in foo/ with /**/ pattern
    foo_dir = repo_path / "foo"
    gitignore = foo_dir / ".gitignore"
    gitignore.write_text("/**/foo.txt")
    
    parser = GitignoreParser(str(repo_path))
    
    # Test cases
    test_cases = [
        ("foo/foo.txt", True, "foo/foo.txt should be ignored"),
        ("foo/bar/foo.txt", True, "foo/bar/foo.txt should be ignored"),
        ("foo/bar/baz/foo.txt", True, "foo/bar/baz/foo.txt should be ignored"),
        ("foo.txt", False, "/foo.txt should NOT be ignored"),
    ]
    
    all_passed = True
    for path, expected, message in test_cases:
        result = parser.should_ignore(path)
        passed = result == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {message} (got {result}, expected {expected})")
    
    return all_passed


def main():
    """Run all tests."""
    print("Testing GitignoreParser implementation for nested .gitignore patterns")
    
    repo_path = setup_test_repo()
    try:
        anchored_passed = test_anchored_pattern(repo_path)
        double_star_passed = test_double_star_pattern(repo_path)
        slash_double_star_passed = test_slash_double_star_pattern(repo_path)
        
        all_passed = anchored_passed and double_star_passed and slash_double_star_passed
        
        print("\n=== Test Summary ===")
        print(f"Anchored pattern test: {'PASS' if anchored_passed else 'FAIL'}")
        print(f"**/ pattern test: {'PASS' if double_star_passed else 'FAIL'}")
        print(f"/**/ pattern test: {'PASS' if slash_double_star_passed else 'FAIL'}")
        print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
        
        return 0 if all_passed else 1
    finally:
        # Clean up
        shutil.rmtree(repo_path)


if __name__ == "__main__":
    sys.exit(main())