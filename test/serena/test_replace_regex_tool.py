import os
import re
import tempfile
from pathlib import Path
import pytest

from serena.tools.file_tools import ReplaceRegexTool
from serena.tools import SUCCESS_RESULT


class MockProject:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.project_root = root_dir
        self.project_config = MockProjectConfig()

    def validate_relative_path(self, path):
        return True

    def read_file(self, path):
        with open(os.path.join(self.root_dir, path), 'r') as f:
            return f.read()

    def is_ignored_path(self, path):
        return False
        
class MockProjectConfig:
    def __init__(self):
        self.encoding = 'utf-8'


class MockAgent:
    def __init__(self, project):
        self.project = project
        self._active_project = project
        self.lines_read = None
        self.serena_config = None
        
    def get_active_project_or_raise(self):
        return self.project
        
    def get_active_project(self):
        return self.project
        
    def is_using_language_server(self):
        return False
        
    def record_tool_usage_if_enabled(self, *args, **kwargs):
        pass
        
    def issue_task(self, task, name):
        from concurrent.futures import Future
        future = Future()
        future.set_result(task())
        return future


class TestReplaceRegexTool:
    @pytest.fixture
    def setup(self):
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file_path = os.path.join(temp_dir, "test_file.py")
            with open(test_file_path, "w") as f:
                f.write("print(f'Some text')\n")
                f.write("print(f'Another line')\n")

            # Setup mock project and agent
            project = MockProject(temp_dir)
            agent = MockAgent(project)
            
            # Create the tool
            tool = ReplaceRegexTool(agent)
            
            yield temp_dir, "test_file.py", tool

    def test_replace_with_newline(self, setup):
        """Test replacing text with a string containing newline escape sequences."""
        temp_dir, test_file_path, tool = setup
        
        # Replace text with a string containing \n
        result = tool.apply(
            relative_path=test_file_path,
            regex=r"print\(f'Some text'\)",
            repl=r"print(f'\n    Confidence Calculation Breakdown:')",
        )
        
        assert result == SUCCESS_RESULT
        
        # Read the file and check the content
        with open(os.path.join(temp_dir, test_file_path), "r") as f:
            content = f.read()
        
        # The newline should be preserved as \n, not converted to a literal newline
        assert "print(f'\\n    Confidence Calculation Breakdown:')" in content
        assert "print(f'\n    Confidence" not in content
        
    def test_replace_with_tab(self, setup):
        """Test replacing text with a string containing tab escape sequences."""
        temp_dir, test_file_path, tool = setup
        
        # Replace text with a string containing \t
        result = tool.apply(
            relative_path=test_file_path,
            regex=r"print\(f'Some text'\)",
            repl=r"print(f'\t    Indented text')",
        )
        
        assert result == SUCCESS_RESULT
        
        # Read the file and check the content
        with open(os.path.join(temp_dir, test_file_path), "r") as f:
            content = f.read()
        
        # The tab should be preserved as \t, not converted to a literal tab
        assert "print(f'\\t    Indented text')" in content
        
    def test_replace_with_multiple_escapes(self, setup):
        """Test replacing text with a string containing multiple escape sequences."""
        temp_dir, test_file_path, tool = setup
        
        # Replace text with a string containing multiple escape sequences
        result = tool.apply(
            relative_path=test_file_path,
            regex=r"print\(f'Some text'\)",
            repl=r"print(f'\n\t\r    Multiple escapes')",
        )
        
        assert result == SUCCESS_RESULT
        
        # Read the file and check the content
        with open(os.path.join(temp_dir, test_file_path), "r") as f:
            content = f.read()
        
        # All escape sequences should be preserved
        assert "print(f'\\n\\t\\r    Multiple escapes')" in content
        
    def test_replace_with_backreferences(self, setup):
        """Test replacing text with backreferences."""
        temp_dir, test_file_path, tool = setup

        # Create a file with content to test backreferences
        backrefs_file = os.path.join(temp_dir, "backrefs.py")
        with open(backrefs_file, "w") as f:
            f.write("def function_name(arg1, arg2):\n")
            f.write("    return arg1 + arg2\n")

        # Replace using backreferences and newlines
        result = tool.apply(
            relative_path="backrefs.py",
            regex=r"def (\w+)\((.*?)\):",
            repl=r"def \1(\2):\n    # Function with arguments: \2\n    # Returns the sum",
        )

        assert result == SUCCESS_RESULT

        # Read the file and check the content
        with open(backrefs_file, "r") as f:
            content = f.read()

        # Backreferences should work and newlines should be preserved
        assert "def function_name(arg1, arg2):" in content
        assert "    # Function with arguments: arg1, arg2" in content
        assert "    # Returns the sum" in content
        
    def test_simulated_api_call(self, setup):
        """Test that simulates how the tool is called through the API."""
        temp_dir, test_file_path, tool = setup
        
        # Create a test file with an f-string
        fstring_file = os.path.join(temp_dir, "fstring.py")
        with open(fstring_file, "w") as f:
            f.write("print(f'Some text')\n")
        
        # This is how the replacement string might look when it comes from JSON
        # The \n is already escaped once in the JSON string
        json_style_repl = "print(f'\\n    Confidence Calculation Breakdown:')"
        
        # Apply the replacement
        result = tool.apply(
            relative_path="fstring.py",
            regex=r"print\(f'Some text'\)",
            repl=json_style_repl,
        )
        
        assert result == SUCCESS_RESULT
        
        # Read the file and check the content
        with open(fstring_file, "r") as f:
            content = f.read()
        
        # The newline should be preserved as \n, not converted to a literal newline
        assert "print(f'\\n    Confidence Calculation Breakdown:')" in content
        # This is what we don't want to see - a literal newline in the string
        assert "print(f'\n    Confidence" not in content
        
    def test_real_world_scenario(self, setup):
        """Test that simulates the real-world scenario where the issue occurs."""
        temp_dir, test_file_path, tool = setup
        
        # Create a test file with an indented f-string (similar to the issue description)
        fstring_file = os.path.join(temp_dir, "real_world.py")
        with open(fstring_file, "w") as f:
            f.write("                  print(f'Some text')\n")
        
        # This simulates how the replacement string might be processed in production
        # The issue description shows the newline being interpreted literally
        repl = "print(f'\n   Confidence Calculation Breakdown:')"
        
        # Apply the replacement directly using re.sub to simulate what might be happening
        # in production without the double-escaping
        with open(fstring_file, "r") as f:
            content = f.read()
        
        # This is what might be happening in production - direct substitution without proper escaping
        broken_content = re.sub(r"print\(f'Some text'\)", repl, content, flags=re.DOTALL | re.MULTILINE)
        
        with open(fstring_file, "w") as f:
            f.write(broken_content)
        
        # Read the file and check if it contains the broken string (literal newline)
        with open(fstring_file, "r") as f:
            content = f.read()
        
        # This should be true if the issue is reproduced - the string is broken across lines
        assert "print(f'\n   Confidence" in content
        
        # Now fix the file and try with our tool
        with open(fstring_file, "w") as f:
            f.write("                  print(f'Some text')\n")
        
        # Apply the replacement using our tool
        result = tool.apply(
            relative_path="real_world.py",
            regex=r"print\(f'Some text'\)",
            repl=r"print(f'\n   Confidence Calculation Breakdown:')",
        )
        
        assert result == SUCCESS_RESULT
        
        # Read the file and check the content
        with open(fstring_file, "r") as f:
            content = f.read()
        
        # The newline should be preserved as \n, not converted to a literal newline
        assert "print(f'\\n   Confidence Calculation Breakdown:')" in content
        # This is what we don't want to see - a literal newline in the string
        assert "print(f'\n   Confidence" not in content