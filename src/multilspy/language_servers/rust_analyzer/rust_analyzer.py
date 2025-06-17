"""
Provides Rust specific instantiation of the LanguageServer class. Contains various configurations and settings specific to Rust.
"""

import asyncio
import json
import logging
import os
import re
import stat
import pathlib
from contextlib import asynccontextmanager
from typing import AsyncIterator

from overrides import override

from multilspy.multilspy_logger import MultilspyLogger
from multilspy.language_server import LanguageServer
from multilspy.lsp_protocol_handler.server import ProcessLaunchInfo
from multilspy.lsp_protocol_handler.lsp_types import InitializeParams
from multilspy.multilspy_config import MultilspyConfig
from multilspy.multilspy_utils import FileUtils
from multilspy.multilspy_utils import PlatformUtils


class RustAnalyzer(LanguageServer):
    """
    Provides Rust specific instantiation of the LanguageServer class. Contains various configurations and settings specific to Rust.
    """

    def __init__(self, config: MultilspyConfig, logger: MultilspyLogger, repository_root_path: str):
        """
        Creates a RustAnalyzer instance. This class is not meant to be instantiated directly. Use LanguageServer.create() instead.
        """
        rustanalyzer_executable_path = self.setup_runtime_dependencies(logger, config)
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=rustanalyzer_executable_path, cwd=repository_root_path),
            "rust",
        )
        self.server_ready = asyncio.Event()
    
    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        return super().is_ignored_dirname(dirname) or dirname in ["target"]

    def setup_runtime_dependencies(self, logger: MultilspyLogger, config: MultilspyConfig) -> str:
        """
        Setup runtime dependencies for rust_analyzer.
        """
        platform_id = PlatformUtils.get_platform_id()

        with open(os.path.join(os.path.dirname(__file__), "runtime_dependencies.json"), "r", encoding="utf-8") as f:
            d = json.load(f)
            del d["_description"]

        # assert platform_id.value in [
        #     "linux-x64",
        #     "win-x64",
        # ], "Only linux-x64 and win-x64 platform is supported for in multilspy at the moment"

        runtime_dependencies = d["runtimeDependencies"]
        runtime_dependencies = [
            dependency for dependency in runtime_dependencies if dependency["platformId"] == platform_id.value
        ]
        assert len(runtime_dependencies) == 1
        dependency = runtime_dependencies[0]

        rustanalyzer_ls_dir = os.path.join(os.path.dirname(__file__), "static", "RustAnalyzer")
        rustanalyzer_executable_path = os.path.join(rustanalyzer_ls_dir, dependency["binaryName"])
        if not os.path.exists(rustanalyzer_ls_dir):
            os.makedirs(rustanalyzer_ls_dir)
            if dependency["archiveType"] == "gz":
                FileUtils.download_and_extract_archive(
                    logger, dependency["url"], rustanalyzer_executable_path, dependency["archiveType"]
                )
            else:
                FileUtils.download_and_extract_archive(
                    logger, dependency["url"], rustanalyzer_ls_dir, dependency["archiveType"]
                )
        assert os.path.exists(rustanalyzer_executable_path)
        os.chmod(rustanalyzer_executable_path, stat.S_IEXEC)

        return rustanalyzer_executable_path

    def _get_initialize_params(self, repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Rust Analyzer Language Server.
        """
        with open(os.path.join(os.path.dirname(__file__), "initialize_params.json"), "r", encoding="utf-8") as f:
            d = json.load(f)

        del d["_description"]

        d["processId"] = os.getpid()
        assert d["rootPath"] == "$rootPath"
        d["rootPath"] = repository_absolute_path

        assert d["rootUri"] == "$rootUri"
        d["rootUri"] = pathlib.Path(repository_absolute_path).as_uri()

        assert d["workspaceFolders"][0]["uri"] == "$uri"
        d["workspaceFolders"][0]["uri"] = pathlib.Path(repository_absolute_path).as_uri()

        assert d["workspaceFolders"][0]["name"] == "$name"
        d["workspaceFolders"][0]["name"] = os.path.basename(repository_absolute_path)

        return d

    @asynccontextmanager
    async def start_server(self) -> AsyncIterator["RustAnalyzer"]:
        """
        Starts the Rust Analyzer Language Server, waits for the server to be ready and yields the LanguageServer instance.

        Usage:
        ```
        async with lsp.start_server():
            # LanguageServer has been initialized and ready to serve requests
            await lsp.request_definition(...)
            await lsp.request_references(...)
            # Shutdown the LanguageServer on exit from scope
        # LanguageServer has been shutdown
        """

        async def register_capability_handler(params):
            assert "registrations" in params
            for registration in params["registrations"]:
                if registration["method"] == "workspace/executeCommand":
                    self.initialize_searcher_command_available.set()
                    self.resolve_main_method_available.set()
            return

        async def lang_status_handler(params):
            # TODO: Should we wait for
            # server -> client: {'jsonrpc': '2.0', 'method': 'language/status', 'params': {'type': 'ProjectStatus', 'message': 'OK'}}
            # Before proceeding?
            if params["type"] == "ServiceReady" and params["message"] == "ServiceReady":
                self.service_ready_event.set()

        async def execute_client_command_handler(params):
            return []

        async def do_nothing(params):
            return

        async def check_experimental_status(params):
            if params["quiescent"] == True:
                self.server_ready.set()

        async def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("language/status", lang_status_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request("workspace/executeClientCommand", execute_client_command_handler)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)
        self.server.on_notification("language/actionableNotification", do_nothing)
        self.server.on_notification("experimental/serverStatus", check_experimental_status)

        async with super().start_server():
            self.logger.log("Starting RustAnalyzer server process", logging.INFO)
            await self.server.start()
            initialize_params = self._get_initialize_params(self.repository_root_path)

            self.logger.log(
                "Sending initialize request from LSP client to LSP server and awaiting response",
                logging.INFO,
            )
            init_response = await self.server.send.initialize(initialize_params)
            assert init_response["capabilities"]["textDocumentSync"]["change"] == 2
            assert "completionProvider" in init_response["capabilities"]
            assert init_response["capabilities"]["completionProvider"] == {
                "resolveProvider": True,
                "triggerCharacters": [":", ".", "'", "("],
                "completionItem": {"labelDetailsSupport": True},
            }
            self.server.notify.initialized({})
            self.completions_available.set()

            await self.server_ready.wait()

            yield self

    @override
    def _supports_lsp_type_hierarchy(self) -> bool:
        """
        Rust Analyzer claims to support LSP 3.17 type hierarchy methods but returns 
        'unknown request' error in practice. Use fallback approach instead.
        """
        return False


    @override
    def _is_inheriting_from(self, file_path: str, class_symbol: dict, target_class_name: str) -> bool:
            """
            Check if a Rust struct/enum/trait is implementing/deriving from the target.
            Checks for trait implementations and derive macros, searching across files if needed.
            """
            try:
                struct_name = class_symbol.get("name", "")
                if not struct_name:
                    return False
                

                
                # First check the current file for derive macros and local impl blocks
                abs_path = os.path.join(self.repository_root_path, file_path)
                if not os.path.exists(abs_path):
                    return False
                    
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Handle both range formats - direct range and location.range
                if "range" in class_symbol:
                    class_range = class_symbol.get("range", {})
                elif "location" in class_symbol and "range" in class_symbol["location"]:
                    class_range = class_symbol["location"]["range"]
                else:
                    return False
                start_line = class_range.get("start", {}).get("line", -1)
                
                lines = content.split('\n')
                if start_line < 0 or start_line >= len(lines):
                    return False
                
                import re
                
                # Check for derive macros above the struct definition
                for i in range(max(0, start_line - 10), start_line + 1):
                    if i < len(lines):
                        line = lines[i].strip()
                        if line.startswith("#[derive("):
                            # Parse derive attributes more carefully
                            derive_content = line
                            # Handle multi-line derive attributes
                            j = i
                            while j < len(lines) and ')]' not in derive_content:
                                j += 1
                                if j < len(lines):
                                    derive_content += lines[j].strip()
                            
                            if target_class_name in derive_content:
                                return True
                
                # Search for impl blocks in current file and workspace
                self.logger.log(f"Checking Rust trait implementation for struct '{struct_name}' implementing trait '{target_class_name}'", logging.DEBUG)
                
                impl_patterns = [
                    # Direct impl: impl TraitName for StructName
                    rf'impl\s+{re.escape(target_class_name)}\s+for\s+{re.escape(struct_name)}\b',
                    # Generic impl: impl<T> TraitName for StructName<T>
                    rf'impl\s*<[^>]*>\s*{re.escape(target_class_name)}\s+for\s+{re.escape(struct_name)}\b',
                    # Qualified impl: impl path::TraitName for StructName
                    rf'impl\s+\w+::{re.escape(target_class_name)}\s+for\s+{re.escape(struct_name)}\b',
                    # Self impl: impl TraitName for Self (when inside impl block)
                    rf'impl\s+{re.escape(target_class_name)}\s+for\s+Self\b'
                ]
                
                # Check current file first
                for pattern in impl_patterns:
                    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                        return True
                
                # Search across workspace for impl blocks (common in Rust)
                try:
                    
                    # Find all .rs files in the workspace
                    workspace_root = self.repository_root_path
                    rust_files = []
                    for root, dirs, files in os.walk(workspace_root):
                        # Skip target directory and other build artifacts
                        dirs[:] = [d for d in dirs if d not in ['target', 'node_modules', '.git']]
                        for file in files:
                            if file.endswith('.rs'):
                                rust_files.append(os.path.join(root, file))
                    
                    # Limit search to avoid performance issues
                    for rust_file in rust_files[:50]:  # Limit to first 50 files
                        try:
                            with open(rust_file, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            
                            # Check for impl blocks referencing our struct
                            for pattern in impl_patterns:
                                if re.search(pattern, file_content, re.MULTILINE | re.IGNORECASE):
                                    return True
                                    
                        except (UnicodeDecodeError, PermissionError):
                            continue
                            
                except Exception as workspace_error:
                    # If workspace search fails, continue with local file search only
                    self.logger.log(f"Workspace search failed: {workspace_error}", logging.DEBUG)
                
                return False
                
            except Exception as e:
                self.logger.log(f"Error checking Rust trait implementation in {file_path}: {e}", logging.DEBUG)
                return False

