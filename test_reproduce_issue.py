import os
import tempfile
from pathlib import Path

from serena.tools.file_tools import ReplaceRegexTool

# Mock classes needed for testing
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

# Create a temporary directory for testing
with tempfile.TemporaryDirectory() as temp_dir:
    # Create a test file that mimics the issue described
    test_file_path = os.path.join(temp_dir, "test_file.py")
    with open(test_file_path, "w") as f:
        f.write("                  print(f'Some text')\n")
    
    # Setup mock project and agent
    project = MockProject(temp_dir)
    agent = MockAgent(project)
    
    # Create the tool
    tool = ReplaceRegexTool(agent)
    
    # Test 1: Apply the replacement using a raw string (as in our original test)
    result1 = tool.apply(
        relative_path="test_file.py",
        regex=r"print\(f'Some text'\)",
        repl=r"print(f'\n    Confidence Calculation Breakdown:')",
    )
    
    # Read the file and check the content
    with open(test_file_path, "r") as f:
        content1 = f.read()
    
    print("Test 1 Result:", result1)
    print("File content after Test 1:")
    print(repr(content1))
    
    # Check if the issue is present (newline is interpreted literally)
    if "print(f'\n" in content1:
        print("ISSUE DETECTED in Test 1: Newline is being interpreted literally!")
    else:
        print("No issue detected in Test 1: Newline is properly escaped.")
    
    # Reset the file for the next test
    with open(test_file_path, "w") as f:
        f.write("                  print(f'Some text')\n")
    
    # Test 2: Apply the replacement using a JSON-style string (as might come from API)
    # In JSON, \n would be escaped as \\n
    json_style_repl = "print(f'\\n    Confidence Calculation Breakdown:')"
    result2 = tool.apply(
        relative_path="test_file.py",
        regex=r"print\(f'Some text'\)",
        repl=json_style_repl,
    )
    
    print("Test 2 Result:", result2)
    
    # Read the file and check the content
    with open(test_file_path, "r") as f:
        content2 = f.read()
    
    print("File content after Test 2:")
    print(repr(content2))
    
    # Check if the issue is present (newline is interpreted literally)
    if "print(f'\n" in content2:
        print("ISSUE DETECTED in Test 2: Newline is being interpreted literally!")
    else:
        print("No issue detected in Test 2: Newline is properly escaped.")
        
    # Test 3: Simulate the exact JSON object from the issue description
    # Reset the file for the next test
    with open(test_file_path, "w") as f:
        f.write("                  print(f'Some text')\n")
    
    # This is the exact repl string from the issue description (from @skerit's comment)
    json_object_repl = "    // Get file position BEFORE reading\n    long preReadPos = -1;\n    if (m_pFile) {\n        preReadPos = m_pFile->GetPosition();\n    }\n    \n    *this >> wTag;\n    \n    fprintf(stderr, \"DEBUG: ReadClass at file pos 0x%lX, read wTag=0x%04X\\n\", preReadPos, wTag);"
    
    result3 = tool.apply(
        relative_path="test_file.py",
        regex=r"print\(f'Some text'\)",
        repl=json_object_repl,
    )
    
    print("Test 3 Result:", result3)
    
    # Read the file and check the content
    with open(test_file_path, "r") as f:
        content3 = f.read()
    
    print("File content after Test 3:")
    print(repr(content3))
    
    # Check if the issue is present (newlines are interpreted literally)
    if "\n" in content3 and "\\n" not in content3:
        print("ISSUE DETECTED in Test 3: Newlines are being interpreted literally!")
    else:
        print("No issue detected in Test 3: Newlines are properly handled.")