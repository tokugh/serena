# Adding New Language Support to Serena

This guide provides step-by-step instructions for adding support for a new programming language to Serena, including comprehensive testing setup.

## Overview

Adding a new language to Serena involves:
1. Creating a language server implementation
2. Adding the language to the configuration system
3. Creating test repositories and test suites
4. Setting up language-specific fixtures and configuration
5. Implementing comprehensive tests

## Prerequisites

Before adding a new language, ensure you have:
- A working Language Server Protocol (LSP) implementation for the target language
- Understanding of the language's ecosystem and dependencies
- Access to the language's runtime/compiler for testing

## Step-by-Step Implementation Guide

### Step 1: Add Language to Configuration

First, add your language to the `Language` enum in `src/solidlsp/ls_config.py`:

```python
class Language(str, Enum):
    # ... existing languages ...
    KOTLIN = "kotlin"
    DART = "dart"
    YOUR_LANGUAGE = "your_language"  # Add your language here
```

Then add the file pattern matcher in the same file:

```python
def get_source_fn_matcher(self) -> FilenameMatcher:
    match self:
        # ... existing patterns ...
        case self.YOUR_LANGUAGE:
            return FilenameMatcher("*.your_ext", "*.your_ext2")  # Your file extensions
```

### Step 2: Create Language Server Implementation

Create a new file `src/solidlsp/language_servers/your_language_server.py`. There are three main patterns to choose from:

#### Pattern A: Simple Command-Based Server (like Python/Pyright)

```python
"""
Your Language Server implementation using [Language Server Name].
"""

import logging
import os
import pathlib
import threading
from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo


class YourLanguageServer(SolidLanguageServer):
    """Your Language specific instantiation of the LanguageServer class."""

    def __init__(self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str):
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd="your-language-server --stdio", cwd=repository_root_path),
            "your_language",
        )
        self.analysis_complete = threading.Event()

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        return super().is_ignored_dirname(dirname) or dirname in ["your_build_dir", "your_cache_dir"]

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        return {
            "processId": os.getpid(),
            "rootPath": repository_absolute_path,
            "rootUri": pathlib.Path(repository_absolute_path).as_uri(),
            "capabilities": {
                # Standard LSP capabilities
                "workspace": {
                    "workspaceEdit": {"documentChanges": True},
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "didChangeWatchedFiles": {"dynamicRegistration": True},
                    "symbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                },
                "textDocument": {
                    "synchronization": {"dynamicRegistration": True, "willSave": True, "didSave": True},
                    "hover": {"dynamicRegistration": True, "contentFormat": ["markdown", "plaintext"]},
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                        "hierarchicalDocumentSymbolSupport": True,
                    },
                },
            },
        }

    def _start_server(self):
        def do_nothing(params):
            return

        def window_log_message(msg):
            message_text = msg.get("message", "")
            self.logger.log(f"LSP: {message_text}", logging.INFO)
            
            # Look for completion signals specific to your language server
            if "analysis complete" in message_text.lower():
                self.analysis_complete.set()
                self.completions_available.set()

        # Set up notification handlers
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)
        # Add other handlers as needed

        self.logger.log("Starting your-language-server process", logging.INFO)
        self.server.start()

        # Initialize the server
        initialize_params = self._get_initialize_params(self.repository_root_path)
        init_response = self.server.send.initialize(initialize_params)
        
        # Verify capabilities
        assert "textDocumentSync" in init_response["capabilities"]
        assert "definitionProvider" in init_response["capabilities"]
        assert "referencesProvider" in init_response["capabilities"]
        
        self.server.notify.initialized({})
        
        # Wait for analysis completion
        if self.analysis_complete.wait(timeout=30.0):
            self.logger.log("Your language server ready", logging.INFO)
        else:
            self.logger.log("Timeout waiting for analysis completion", logging.WARNING)
            self.analysis_complete.set()
            self.completions_available.set()
```

#### Pattern B: Complex Server with Runtime Dependencies (like C#)

For languages requiring downloaded binaries or complex setup:

```python
"""
Your Language Server with runtime dependency management.
"""

import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import cast

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_exceptions import LanguageServerException
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo

from .common import RuntimeDependency


# Define runtime dependencies
RUNTIME_DEPENDENCIES = [
    RuntimeDependency(
        id="YourLanguageServer",
        description="Your Language Server for Linux (x64)",
        url="https://releases.example.com/your-language-server-linux-x64.tar.gz",
        platform_id="linux-x64",
        archive_type="tar.gz",
        binary_name="your-language-server",
    ),
    RuntimeDependency(
        id="YourLanguageServer",
        description="Your Language Server for Windows (x64)",
        url="https://releases.example.com/your-language-server-win-x64.zip",
        platform_id="win-x64",
        archive_type="zip",
        binary_name="your-language-server.exe",
    ),
    # Add more platforms as needed
]


class YourLanguageServer(SolidLanguageServer):
    """Your Language Server with automatic dependency management."""

    def __init__(self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str):
        server_path = self._ensure_server_installed(logger, config)
        
        # Build command
        cmd = [server_path, "--stdio"]
        
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=cmd, cwd=repository_root_path),
            "your_language",
        )

    @classmethod
    def _ensure_server_installed(cls, logger: LanguageServerLogger, config: LanguageServerConfig) -> str:
        """Ensure language server binary is available."""
        runtime_id = cls._get_runtime_id()
        dependency = cls._get_dependency_for_platform(runtime_id)
        
        server_dir = Path(cls.ls_resources_dir()) / f"your-language-server-{dependency.platform_id}"
        server_binary = server_dir / dependency.binary_name
        
        if server_binary.exists():
            logger.log(f"Using cached server from {server_binary}", logging.INFO)
            return str(server_binary)
        
        # Download and install
        logger.log(f"Downloading {dependency.description}...", logging.INFO)
        # Implementation depends on your download/extraction logic
        # See csharp_language_server.py for a complete example
        
        return str(server_binary)

    # ... rest of the implementation
```

#### Pattern C: Project-Specific Setup (like Elixir)

For languages requiring project compilation or setup:

```python
"""
Your Language Server with project setup requirements.
"""

import os
import subprocess
from pathlib import Path

from solidlsp.ls import SolidLanguageServer
# ... other imports


def ensure_project_compiled(repo_path: str) -> None:
    """Ensure the project is compiled and ready for analysis."""
    project_file = os.path.join(repo_path, "your_project_file")
    if not os.path.exists(project_file):
        return
    
    try:
        # Run project setup commands
        subprocess.run(["your-build-command"], cwd=repo_path, check=True, timeout=180)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Project setup failed: {e}")
    except FileNotFoundError:
        print("Warning: Build tools not found")


class YourLanguageServer(SolidLanguageServer):
    def __init__(self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str):
        # Ensure project is set up
        ensure_project_compiled(repository_root_path)
        
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd="your-language-server --stdio", cwd=repository_root_path),
            "your_language",
        )
    
    # ... rest of implementation
```

### Step 3: Update SolidLanguageServer Factory

Add your language server to the factory method in `src/solidlsp/ls.py`:

```python
@classmethod
def create(cls, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str) -> "SolidLanguageServer":
    """Factory method to create appropriate language server instance."""
    match config.code_language:
        # ... existing cases ...
        case Language.YOUR_LANGUAGE:
            from .language_servers.your_language_server import YourLanguageServer
            return YourLanguageServer(config, logger, repository_root_path)
        case _:
            raise ValueError(f"Unsupported language: {config.code_language}")
```

### Step 4: Create Test Repository

Create a test repository structure in `test/resources/repos/your_language/test_repo/`:

```
test/resources/repos/your_language/test_repo/
├── your_project_config_file  # e.g., package.json, Cargo.toml, etc.
├── src/
│   ├── main.your_ext          # Main file with classes/functions
│   ├── models.your_ext        # Data models
│   └── services.your_ext      # Service layer
└── README.md                  # Optional documentation
```

#### Example Test Repository Content

**Main file** (`src/main.your_ext`):
```your_language
// Include basic program structure
// Classes, functions, variables that will be tested
class Calculator {
    function add(a, b) {
        return a + b;
    }
    
    function subtract(a, b) {
        return a - b;
    }
}

class Program {
    function main() {
        calculator = new Calculator();
        result = calculator.add(5, 3);
        print("Result: " + result);
    }
}
```

**Models file** (`src/models.your_ext`):
```your_language
class User {
    string name;
    int age;
    string email;
    
    function new(name, age, email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }
    
    function toString() {
        return "User: " + this.name;
    }
}

class Item {
    string title;
    double price;
    
    function new(title, price) {
        this.title = title;
        this.price = price;
    }
}
```

**Services file** (`src/services.your_ext`):
```your_language
class UserService {
    function create_user(name, age, email) {
        return new User(name, age, email);
    }
    
    function get_user(id) {
        // Mock implementation
        return new User("Test User", 25, "test@example.com");
    }
}
```

### Step 5: Create Test Suite

Create the test directory structure:

```
test/solidlsp/your_language/
├── __init__.py
├── conftest.py (if needed for special setup)
└── test_your_language_basic.py
```

#### Basic Test Implementation

**`test/solidlsp/your_language/test_your_language_basic.py`:**

```python
"""
Basic integration tests for Your Language server functionality.

These tests validate the functionality of the language server APIs
like request_references using the test repository.
"""

import os
import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language
from solidlsp.ls_utils import SymbolUtils


@pytest.mark.your_language  # Add your language marker
class TestYourLanguageBasic:
    """Basic Your Language server functionality tests."""

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_find_symbol(self, language_server: SolidLanguageServer) -> None:
        """Test finding symbols in the full symbol tree."""
        symbols = language_server.request_full_symbol_tree()
        
        # Test for expected symbols from your test repository
        assert SymbolUtils.symbol_tree_contains_name(symbols, "Calculator"), "Calculator class not found"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "User"), "User class not found"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "add"), "add method not found"

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_get_document_symbols(self, language_server: SolidLanguageServer) -> None:
        """Test getting document symbols from a source file."""
        file_path = os.path.join("src", "main.your_ext")
        symbols = language_server.request_document_symbols(file_path)

        # Check that we have symbols
        assert len(symbols) > 0

        # Flatten symbols if nested (adapt based on your server's response format)
        if isinstance(symbols[0], list):
            symbols = symbols[0]

        # Look for expected classes (adjust kind numbers based on LSP spec)
        class_names = [s.get("name") for s in symbols if s.get("kind") == 5]  # 5 is typically class
        assert "Calculator" in class_names
        assert "Program" in class_names

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_find_references(self, language_server: SolidLanguageServer) -> None:
        """Test finding references to a symbol."""
        file_path = os.path.join("src", "main.your_ext")
        symbols = language_server.request_document_symbols(file_path)
        
        # Find the 'add' method symbol
        add_symbol = None
        symbol_list = symbols[0] if symbols and isinstance(symbols[0], list) else symbols
        
        for sym in symbol_list:
            if sym.get("name") == "add":
                add_symbol = sym
                break
        
        assert add_symbol is not None, "Could not find 'add' method symbol"
        
        # Get references using the symbol's position
        sel_start = add_symbol["selectionRange"]["start"]
        refs = language_server.request_references(file_path, sel_start["line"], sel_start["character"])
        
        # Should find at least the definition itself
        assert len(refs) > 0, "Should find at least one reference to 'add' method"

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_cross_file_references(self, language_server: SolidLanguageServer) -> None:
        """Test finding references across multiple files."""
        models_file = os.path.join("src", "models.your_ext")
        symbols = language_server.request_document_symbols(models_file)
        
        # Find User class
        user_symbol = None
        symbol_list = symbols[0] if symbols and isinstance(symbols[0], list) else symbols
        
        for sym in symbol_list:
            if sym.get("name") == "User" and sym.get("kind") == 5:  # Class
                user_symbol = sym
                break
        
        assert user_symbol is not None, "Could not find 'User' class symbol"
        
        # Get references - should find uses in services file
        sel_start = user_symbol["selectionRange"]["start"]
        refs = language_server.request_references(models_file, sel_start["line"], sel_start["character"])
        
        # Should find references in services.your_ext
        services_refs = [ref for ref in refs if "services.your_ext" in ref.get("uri", "")]
        assert len(services_refs) > 0, "Should find User class references in services file"
```

#### Advanced Test Implementation

For more comprehensive testing, add additional test files:

**`test/solidlsp/your_language/test_your_language_integration.py`:**

```python
"""
Integration tests for Your Language server advanced functionality.
"""

import os
import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language


@pytest.mark.your_language
class TestYourLanguageIntegration:
    """Advanced integration tests."""

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_workspace_symbols(self, language_server: SolidLanguageServer) -> None:
        """Test workspace-wide symbol search."""
        symbols = language_server.request_workspace_symbols("User")
        
        # Should find User class across the workspace
        user_symbols = [s for s in symbols if s.get("name") == "User"]
        assert len(user_symbols) > 0, "Should find User class in workspace symbols"

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_definition_lookup(self, language_server: SolidLanguageServer) -> None:
        """Test go-to-definition functionality."""
        services_file = os.path.join("src", "services.your_ext")
        
        # Find a line that references the User class
        # This depends on your test repository structure
        definitions = language_server.request_definition(services_file, 5, 20)  # Adjust line/column
        
        assert len(definitions) > 0, "Should find definition for referenced symbol"
        
        # Should point to models file
        definition_uris = [d.get("uri", "") for d in definitions]
        assert any("models.your_ext" in uri for uri in definition_uris), "Definition should be in models file"

    @pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
    def test_hover_information(self, language_server: SolidLanguageServer) -> None:
        """Test hover information (if supported by your language server)."""
        main_file = os.path.join("src", "main.your_ext")
        
        try:
            hover_info = language_server.request_hover(main_file, 10, 15)  # Adjust position
            
            if hover_info:
                assert "contents" in hover_info, "Hover should contain contents"
                assert len(hover_info["contents"]) > 0, "Hover contents should not be empty"
        except Exception:
            # Some language servers might not support hover
            pytest.skip("Hover not supported by this language server")
```

#### Language-Specific Test Configuration

If your language requires special setup, create `conftest.py`:

**`test/solidlsp/your_language/conftest.py`:**

```python
"""
Your Language specific test configuration and fixtures.
"""

import os
import subprocess
from pathlib import Path
import pytest


def ensure_your_language_environment(repo_path: str) -> None:
    """Ensure Your Language environment is set up for testing."""
    project_file = os.path.join(repo_path, "your_project_file")
    if not os.path.exists(project_file):
        return
    
    try:
        # Install dependencies
        subprocess.run(["your-package-manager", "install"], cwd=repo_path, check=True, timeout=180)
        
        # Build project if needed
        subprocess.run(["your-build-tool", "build"], cwd=repo_path, check=True, timeout=180)
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: Your Language setup failed: {e}")
    except FileNotFoundError:
        print("Warning: Your Language tools not found")


@pytest.fixture(scope="session", autouse=True)
def setup_your_language_test_environment():
    """Automatically prepare Your Language test environment."""
    test_repo_path = Path(__file__).parent.parent.parent / "resources" / "repos" / "your_language" / "test_repo"
    ensure_your_language_environment(str(test_repo_path))
    return str(test_repo_path)
```

#### Availability Checking

Create `__init__.py` with availability checking:

**`test/solidlsp/your_language/__init__.py`:**

```python
import platform
import subprocess


def _test_your_language_available() -> str:
    """Test if Your Language tools are available."""
    
    # Check platform compatibility if needed
    if platform.system() == "SomeUnsupportedPlatform":
        return "Your Language not supported on this platform"
    
    # Check if language tools are installed
    try:
        result = subprocess.run(["your-language-command", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return "Your Language tools not working properly"
        
        # Check language server availability
        result = subprocess.run(["your-language-server", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return "Your Language server not available"
        
        return ""  # No error
        
    except FileNotFoundError:
        return "Your Language tools not installed"
    except subprocess.TimeoutExpired:
        return "Your Language tools timeout"
    except Exception as e:
        return f"Error checking Your Language availability: {e}"


YOUR_LANGUAGE_UNAVAILABLE_REASON = _test_your_language_available()
YOUR_LANGUAGE_UNAVAILABLE = bool(YOUR_LANGUAGE_UNAVAILABLE_REASON)
```

Then use it in your test files:

```python
from . import YOUR_LANGUAGE_UNAVAILABLE, YOUR_LANGUAGE_UNAVAILABLE_REASON

pytestmark = [
    pytest.mark.your_language, 
    pytest.mark.skipif(YOUR_LANGUAGE_UNAVAILABLE, reason=f"Your Language not available: {YOUR_LANGUAGE_UNAVAILABLE_REASON}")
]
```

### Step 6: Configure Test Markers

Add your language marker to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    # ... existing markers ...
    "your_language: marks tests as Your Language language server tests",
]
```

### Step 7: Testing Your Implementation

Run your tests with various configurations:

```bash
# Test your specific language
uv run pytest test/solidlsp/your_language/ -v

# Test with markers
uv run pytest -m "your_language" -v

# Test specific functionality
uv run pytest test/solidlsp/your_language/test_your_language_basic.py::TestYourLanguageBasic::test_find_symbol -v

# Run all language server tests to ensure no regressions
uv run pytest test/solidlsp/ -v
```

### Step 8: Error Handling and Edge Cases

Add comprehensive error handling:

```python
@pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
def test_error_handling(self, language_server: SolidLanguageServer) -> None:
    """Test error handling for invalid inputs."""
    
    # Test with non-existent file
    try:
        symbols = language_server.request_document_symbols("non_existent_file.your_ext")
        # Some servers return empty, others raise exceptions
        assert symbols == [] or symbols is None
    except Exception:
        # Exception is acceptable for non-existent files
        pass
    
    # Test with invalid position
    try:
        refs = language_server.request_references("src/main.your_ext", 999999, 999999)
        assert refs == [] or refs is None
    except Exception:
        # Exception is acceptable for invalid positions
        pass
```

### Step 9: Performance and Timeout Tests

```python
@pytest.mark.parametrize("language_server", [Language.YOUR_LANGUAGE], indirect=True)
def test_performance_and_timeouts(self, language_server: SolidLanguageServer) -> None:
    """Test that operations complete within reasonable time."""
    import time
    
    start_time = time.time()
    symbols = language_server.request_full_symbol_tree()
    duration = time.time() - start_time
    
    assert duration < 30.0, f"Full symbol tree took too long: {duration}s"
    assert len(symbols) > 0, "Should find symbols in reasonable time"
```

### Step 10: Documentation and Examples

Create documentation for your language support:

1. Add entry to README.md
2. Create usage examples
3. Document any special requirements or limitations
4. Add to the Language enum documentation

## Testing Best Practices

### 1. Test Repository Design
- Include common language constructs (classes, functions, variables)
- Create cross-file references for testing navigation
- Include both simple and complex scenarios
- Use realistic code patterns from your language

### 2. Test Coverage
- **Symbol Discovery**: Full symbol tree, document symbols, workspace symbols
- **Navigation**: Go-to-definition, find references, find implementations
- **Cross-file Operations**: Multi-file references, imports/modules
- **Error Handling**: Invalid files, positions, timeouts
- **Performance**: Reasonable response times

### 3. Test Organization
- Use descriptive test names that indicate what's being tested
- Group related tests in classes
- Use parametrized tests for testing multiple scenarios
- Include both positive and negative test cases

### 4. CI/CD Considerations
- Use availability checking to skip tests when tools aren't installed
- Set appropriate timeouts for language server startup
- Handle platform-specific differences
- Cache dependencies when possible

## Common Patterns and Troubleshooting

### Language Server Won't Start
- Check that the language server binary is in PATH
- Verify command-line arguments are correct
- Check for missing dependencies
- Review initialization parameters

### Symbols Not Found
- Ensure project is properly compiled/indexed
- Check file paths are correct
- Verify the language server supports the LSP features you're using
- Check that ignore patterns aren't excluding your files

### Tests Timing Out
- Increase timeout values for language server startup
- Ensure test repository is minimal but functional
- Check for infinite loops in language server initialization
- Consider pre-compiling test repositories in CI

### Platform Issues
- Use platform detection for unsupported systems
- Handle different binary names/paths per platform
- Test on multiple operating systems if possible

## Example Implementation Reference

Study existing implementations for patterns:

- **Simple**: `pyright_server.py` - Minimal setup, command-based
- **Complex**: `csharp_language_server.py` - Runtime dependencies, binary management
- **Project Setup**: `elixir_tools/` - Compilation requirements, project preparation

Each pattern handles different complexity levels and can be adapted to your language's needs.

## Final Steps

1. Run the full test suite to ensure no regressions
2. Update documentation and README
3. Consider adding CI/CD pipeline tests for your language
4. Submit pull request with comprehensive tests and documentation

This comprehensive guide should enable you to successfully add support for any programming language to Serena while maintaining the high quality and reliability standards of the existing codebase.