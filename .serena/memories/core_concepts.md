# Serena Core Concepts

This document explains the fundamental concepts and architectural principles that make Serena a powerful coding agent toolkit.

## Overview

Serena transforms Large Language Models (LLMs) into sophisticated coding agents by providing semantic code understanding and precise editing capabilities. Unlike text-based approaches, Serena leverages Language Server Protocol (LSP) to understand code at the symbol level.

## Core Architectural Concepts

### 1. Semantic Code Understanding

**Traditional Text-Based Approach:**
- Treats code as plain text
- Uses regex and string matching
- Limited understanding of code structure
- Prone to context misunderstanding

**Serena's Semantic Approach:**
- Uses Language Server Protocol (LSP)
- Understands symbols, types, and relationships
- Provides precise navigation and refactoring
- Maintains code integrity during edits

```python
# Traditional: "Find all uses of 'User'"
# Problem: Matches User class, user variable, username, etc.

# Serena: "Find all references to User class symbol"
# Solution: Only matches actual references to the specific User class
```

### 2. Language Server Protocol (LSP) Integration

LSP provides the foundation for semantic understanding:

**Core LSP Operations:**
- **Symbol Resolution** - Find definition of symbols
- **Reference Finding** - Locate all uses of a symbol
- **Type Information** - Understand symbol types and relationships
- **Document Symbols** - Get structured view of code
- **Diagnostics** - Real-time error detection

**Serena's LSP Wrapper:**
```python
# High-level semantic operations
language_server.request_document_symbols("src/models.py")
language_server.request_references("src/models.py", line=10, character=5)
language_server.request_definition("src/controllers.py", line=25, character=12)
```

### 3. Multi-Language Support Architecture

Serena supports 14+ programming languages through a unified interface:

**Language Server Implementations:**
- **C#** - Microsoft.CodeAnalysis.LanguageServer (Roslyn)
- **Python** - Pyright (with Jedi fallback)
- **TypeScript/JavaScript** - TypeScript Language Server
- **Rust** - Rust Analyzer
- **Java** - Eclipse JDT Language Server
- **Go** - Gopls
- **Ruby** - Solargraph
- **Elixir** - Next LS
- **C/C++** - Clangd
- **PHP** - Intelephense
- **Clojure** - Clojure LSP
- **Dart** - Dart Language Server
- **Kotlin** - Kotlin Language Server
- **Terraform** - Terraform LS

**Unified Interface:**
```python
# Same API works across all languages
for language in [Language.PYTHON, Language.RUST, Language.TYPESCRIPT]:
    ls = SolidLanguageServer.create(config, logger, repo_path)
    symbols = ls.request_full_symbol_tree()
    # Language-specific optimizations handled internally
```

### 4. Agent Framework Integration

Serena provides multiple integration patterns:

#### A. Model Context Protocol (MCP) Server
Primary integration for Claude Desktop and other MCP clients:

```python
# Entry point: src/serena/mcp.py
# Tools automatically exposed to LLM
tools = [
    "find_symbol",
    "replace_symbol_body", 
    "search_for_pattern",
    "create_file",
    "edit_file"
]
```

#### B. Agno Framework Integration
Model-agnostic agent framework with GUI support:

```python
# Entry point: src/serena/agno.py
# Works with any LLM (OpenAI, Anthropic, local models)
# Provides GUI interface for agent interaction
```

#### C. Custom Framework Adapter
Adaptable to any agent framework:

```python
# Example: Custom integration
from serena.agent import SerenaAgent
from serena.tools.symbol_tools import SymbolTools

class CustomAgent:
    def __init__(self):
        self.serena = SerenaAgent(project_path)
        self.tools = SymbolTools(self.serena)
    
    def process_request(self, request):
        # Use Serena tools in custom framework
        return self.tools.find_symbol(request.symbol_name)
```

### 5. Configuration and Mode System

Serena uses a sophisticated configuration system with four layers:

#### Configuration Hierarchy (highest to lowest priority):
1. **Runtime Mode Configuration** - Active during operation
2. **CLI Arguments** - Command-line overrides
3. **Project Configuration** (`.serena/project.yml`) - Project-specific
4. **Global Configuration** (`serena_config.yml`) - System-wide defaults

#### Context System
Defines the environment where Serena operates:

**Available Contexts:**
- **`agent`** - Autonomous agent behavior
- **`desktop-app`** - Claude Desktop integration
- **`ide-assistant`** - IDE plugin integration

**Context Configuration Example:**
```yaml
# contexts/agent.yml
name: "Serena Agent"
description: "Autonomous coding agent with full capabilities"
enabled_tools:
  - symbol_tools
  - file_tools
  - memory_tools
  - workflow_tools
memory_enabled: true
auto_commit: false
```

#### Mode System
Controls runtime behavior:

**Available Modes:**
- **`editing`** - Code editing and refactoring
- **`interactive`** - Interactive development
- **`planning`** - Task planning and analysis
- **`one-shot`** - Single operation execution

**Mode Configuration Example:**
```yaml
# modes/editing.yml
name: "Editing Mode"
description: "Optimized for code editing tasks"
symbol_editing_enabled: true
backup_on_edit: true
verify_syntax: true
```

### 6. Symbol-Based Operations

Core concept: Work with code symbols rather than text:

#### Symbol Types
```python
class SymbolKind:
    FILE = 1
    MODULE = 2
    NAMESPACE = 3
    PACKAGE = 4
    CLASS = 5
    METHOD = 6
    PROPERTY = 7
    FIELD = 8
    CONSTRUCTOR = 9
    ENUM = 10
    INTERFACE = 11
    FUNCTION = 12
    VARIABLE = 13
    # ... more types
```

#### Symbol Operations
```python
# Find symbol by name across entire codebase
symbols = agent.find_symbol("UserService")

# Get symbol definition and implementation
definition = agent.get_symbol_definition("UserService.create_user")

# Replace symbol implementation while preserving signature
agent.replace_symbol_body(
    symbol_name="UserService.create_user",
    new_implementation="// New implementation here"
)

# Find all references to a symbol
references = agent.find_symbol_references("User.email")
```

### 7. Tool System Architecture

Serena's tools are organized into categories:

#### Symbol Tools (`symbol_tools.py`)
- `find_symbol` - Locate symbols by name/pattern
- `replace_symbol_body` - Edit symbol implementations
- `get_symbol_definition` - Get symbol details
- `find_referencing_symbols` - Find symbols that reference others

#### File Tools (`file_tools.py`)
- `create_file` - Create new files
- `edit_file` - Edit existing files
- `read_file` - Read file contents
- `delete_file` - Remove files

#### Memory Tools (`memory_tools.py`)
- `store_memory` - Store information for later use
- `recall_memory` - Retrieve stored information
- `list_memories` - Browse stored memories

#### Workflow Tools (`workflow_tools.py`)
- `plan_implementation` - Break down complex tasks
- `execute_workflow` - Run multi-step operations
- `validate_changes` - Verify modifications

### 8. Error Handling and Reliability

#### Language Server Reliability
```python
# Automatic retry on LSP failures
@retry_on_failure(max_attempts=3)
def request_with_fallback(self, operation):
    try:
        return self.primary_operation(operation)
    except LSPException:
        return self.fallback_operation(operation)
```

#### Graceful Degradation
```python
# If semantic analysis fails, fall back to text-based operations
if not language_server.is_available():
    logger.warning("LSP unavailable, using text-based fallback")
    return text_based_search(pattern)
```

#### State Management
```python
# Track changes for rollback capability
class EditTracker:
    def __init__(self):
        self.changes = []
        self.checkpoints = []
    
    def create_checkpoint(self):
        self.checkpoints.append(self.get_current_state())
    
    def rollback_to_checkpoint(self):
        if self.checkpoints:
            self.restore_state(self.checkpoints.pop())
```

### 9. Performance Optimizations

#### LSP Connection Pooling
```python
# Reuse language server connections
class LSPPool:
    def __init__(self):
        self.connections = {}
    
    def get_server(self, language, repo_path):
        key = (language, repo_path)
        if key not in self.connections:
            self.connections[key] = create_language_server(language, repo_path)
        return self.connections[key]
```

#### Caching Strategy
```python
# Cache symbol trees and references
@lru_cache(maxsize=128)
def get_symbol_tree(self, file_path):
    return self.language_server.request_document_symbols(file_path)
```

#### Batch Operations
```python
# Batch multiple LSP requests
async def batch_symbol_requests(self, requests):
    tasks = [self.request_symbol(req) for req in requests]
    return await asyncio.gather(*tasks)
```

### 10. Testing Philosophy

#### Language Server Testing
```python
@pytest.mark.parametrize("language_server", [Language.CSHARP], indirect=True)
def test_find_symbol(self, language_server: SolidLanguageServer):
    """Test semantic symbol finding"""
    symbols = language_server.request_full_symbol_tree()
    assert SymbolUtils.symbol_tree_contains_name(symbols, "Calculator")
```

#### Integration Testing
```python
# Test actual agent workflows
def test_symbol_replacement_workflow():
    agent = SerenaAgent(test_repo_path)
    original = agent.get_symbol_definition("Calculator.add")
    
    agent.replace_symbol_body("Calculator.add", new_implementation)
    
    modified = agent.get_symbol_definition("Calculator.add")
    assert modified != original
    assert agent.verify_syntax()
```

## Design Principles

### 1. Semantic First
Always prefer semantic operations over text-based when possible.

### 2. Language Agnostic
Provide consistent APIs across all supported languages.

### 3. Graceful Degradation
Fall back to simpler methods when advanced features aren't available.

### 4. Configurable Behavior
Allow customization through contexts, modes, and configuration.

### 5. Tool Composability
Design tools that can be combined for complex workflows.

### 6. Reliable State Management
Track changes and provide rollback capabilities.

These core concepts enable Serena to provide sophisticated code manipulation capabilities while maintaining reliability, performance, and ease of use across multiple programming languages and integration scenarios.