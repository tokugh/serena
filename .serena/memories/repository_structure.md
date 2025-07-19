# Serena Repository Structure

This document provides a comprehensive overview of the Serena repository structure, explaining the organization and purpose of each major component.

## Overview

Serena is a powerful coding agent toolkit that turns LLMs into fully-featured agents working directly on codebases through semantic code retrieval and editing tools. The repository is organized into several key directories:

## Top-Level Structure

```
serena/
├── src/                    # Main source code
├── test/                   # Test suite
├── scripts/                # Utility scripts
├── resources/              # Static resources
├── public/                 # Public assets
├── node_modules/           # Node.js dependencies
├── temp/                   # Temporary files
├── uploads/                # Upload directory
├── .serena/                # Project configuration
├── pyproject.toml          # Python project configuration
├── uv.lock                 # UV dependency lock file
└── compose.yaml            # Docker composition
```

## Source Code (`src/`)

The source code is organized into three main packages:

### 1. `src/serena/` - Core Agent Framework

The main Serena package containing the core agent implementation:

- **`agent.py`** - Core agent implementation with semantic tools
- **`agno.py`** - Agno framework integration for model-agnostic agents
- **`mcp.py`** - Model Context Protocol server implementation
- **`cli.py`** - Command-line interface
- **`project.py`** - Project management and configuration
- **`symbol.py`** - Symbol representation and manipulation
- **`code_editor.py`** - Code editing capabilities

#### Configuration System (`config/`)
- **`serena_config.py`** - Global configuration management
- **`context_mode.py`** - Context and mode system implementation

#### Tool System (`tools/`)
- **`symbol_tools.py`** - Semantic symbol manipulation tools
- **`file_tools.py`** - File system operations
- **`memory_tools.py`** - Agent memory management
- **`workflow_tools.py`** - Workflow automation tools
- **`jetbrains_tools.py`** - JetBrains IDE integration

#### Utilities (`util/`)
- **`file_system.py`** - File system utilities
- **`git.py`** - Git integration
- **`shell.py`** - Shell command execution
- **`thread.py`** - Threading utilities

#### Resources (`resources/`)
Configuration templates and assets:
- **`config/contexts/`** - Context definitions (agent, desktop-app, ide-assistant)
- **`config/modes/`** - Mode definitions (editing, interactive, planning)
- **`config/prompt_templates/`** - System prompt templates
- **`dashboard/`** - Web dashboard assets

### 2. `src/solidlsp/` - Language Server Integration

Provides semantic code analysis through Language Server Protocol (LSP):

- **`ls.py`** - Core language server abstraction
- **`ls_config.py`** - Language server configuration (Language enum, FilenameMatcher)
- **`ls_handler.py`** - Request/response handling
- **`ls_logger.py`** - Logging infrastructure
- **`ls_types.py`** - Type definitions
- **`ls_utils.py`** - Utility functions

#### Language Server Implementations (`language_servers/`)

Each language has its own implementation:

- **`csharp_language_server.py`** - Microsoft.CodeAnalysis.LanguageServer (Roslyn)
- **`pyright_server.py`** - Python (Pyright)
- **`typescript_language_server.py`** - TypeScript/JavaScript
- **`rust_analyzer.py`** - Rust
- **`eclipse_jdtls.py`** - Java (Eclipse JDT)
- **`gopls.py`** - Go
- **`solargraph.py`** - Ruby
- **`clojure_lsp.py`** - Clojure
- **`elixir_tools/`** - Elixir (Next LS)
- **`intelephense.py`** - PHP
- **`clangd_language_server.py`** - C/C++
- **`dart_language_server.py`** - Dart
- **`kotlin_language_server.py`** - Kotlin
- **`terraform_ls.py`** - Terraform

#### Static Resources (`static/`)
Pre-built language server binaries and dependencies for offline operation:
- **`CSharpLanguageServer/`** - Microsoft.CodeAnalysis.LanguageServer binaries
- **`EclipseJDTLS/`** - Eclipse JDT Language Server
- **`OmniSharp/`** - OmniSharp server (alternative C# server)
- **`RustAnalyzer/`** - Rust Analyzer binary
- **`TypeScriptLanguageServer/`** - TypeScript language server
- **`clojure-lsp/`** - Clojure LSP binary

#### LSP Protocol Handler (`lsp_protocol_handler/`)
- **`server.py`** - LSP server communication
- **`lsp_requests.py`** - LSP request implementations
- **`lsp_types.py`** - LSP type definitions
- **`lsp_constants.py`** - LSP constants

### 3. `src/interprompt/` - Template System

Prompt and template management:

- **`prompt_factory.py`** - Prompt generation and management
- **`jinja_template.py`** - Jinja2 template integration
- **`multilang_prompt.py`** - Multi-language prompt support

## Test Suite (`test/`)

Comprehensive test coverage organized by component:

### Test Structure
```
test/
├── conftest.py                 # Pytest configuration and fixtures
├── serena/                     # Serena core tests
│   ├── test_mcp.py            # MCP server tests
│   ├── test_serena_agent.py   # Agent functionality tests
│   ├── test_symbol.py         # Symbol manipulation tests
│   └── config/                # Configuration tests
└── solidlsp/                  # Language server tests
    ├── csharp/                # C# language server tests
    ├── python/                # Python language server tests
    ├── typescript/            # TypeScript language server tests
    ├── rust/                  # Rust language server tests
    ├── java/                  # Java language server tests
    ├── go/                    # Go language server tests
    ├── elixir/                # Elixir language server tests
    └── ...                    # Other language tests
```

### Test Resources (`test/resources/repos/`)
Language-specific test repositories:
```
repos/
├── csharp/test_repo/          # C# test project
├── python/test_repo/          # Python test project
├── typescript/test_repo/      # TypeScript test project
├── rust/test_repo/            # Rust test project
└── ...                        # Other language test repos
```

## Scripts (`scripts/`)

Utility and demonstration scripts:
- **`mcp_server.py`** - MCP server runner
- **`agno_agent.py`** - Agno agent runner
- **`demo_run_tools.py`** - Tool demonstration script
- **`print_tool_overview.py`** - Tool documentation generator

## Configuration System

Serena uses a four-layer configuration hierarchy:

1. **Global Configuration** (`serena_config.yml`)
2. **CLI Arguments** - Client-specific overrides
3. **Project Configuration** (`.serena/project.yml`)
4. **Active Modes** - Runtime behavior modification

### Key Configuration Files
- **`serena_config.yml`** - Global settings
- **`.serena/project.yml`** - Project-specific settings
- **`pyproject.toml`** - Python package configuration
- **`uv.lock`** - Dependency lock file

## Key Design Principles

### 1. Language Agnostic Architecture
- Supports 14+ programming languages through LSP adapters
- Consistent API across all languages
- Language-specific optimizations where needed

### 2. Multiple Integration Methods
- **MCP Server** - Primary integration for Claude Desktop
- **Agno Agent** - Model-agnostic framework with GUI
- **Framework Adapter** - Can be adapted to any agent framework

### 3. Semantic Code Understanding
- Uses Language Server Protocol for symbol-level analysis
- Goes beyond text-based approaches
- Provides precise code navigation and editing

### 4. Modular Design
- Clear separation between agent logic and language server integration
- Pluggable tool system
- Configurable behavior through modes and contexts

## Integration Patterns

### MCP Server Integration
```python
# Entry point: src/serena/mcp.py
# Configuration: contexts/desktop-app.yml
# Tools: symbol_tools.py, file_tools.py, memory_tools.py
```

### Agno Agent Integration
```python
# Entry point: src/serena/agno.py
# Configuration: contexts/agent.yml
# GUI: Available through Agno framework
```

### Custom Framework Integration
```python
# Base: src/serena/agent.py
# Tools: Available through SerenaAgnoToolkit pattern
# Adaptation: tools/tools_base.py provides base classes
```

## Development Workflow

### Adding New Languages
1. Implement language server in `src/solidlsp/language_servers/`
2. Add language to `Language` enum in `ls_config.py`
3. Create test repository in `test/resources/repos/`
4. Add test suite in `test/solidlsp/{language}/`
5. Update file pattern matching in `get_source_fn_matcher()`

### Adding New Tools
1. Create tool class inheriting from appropriate base in `tools_base.py`
2. Add tool to relevant tool modules
3. Register tool in agent configuration
4. Add tests in `test/serena/`

### Testing
```bash
# Run all tests
uv run poe test

# Run language-specific tests
uv run pytest test/solidlsp/csharp/

# Run with specific markers
uv run pytest -m "csharp and not slow"
```

This structure enables Serena to provide sophisticated semantic code operations while maintaining a clean, modular architecture that can be adapted to various use cases and integration patterns.