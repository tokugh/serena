import asyncio
import json
import logging
import os
import pathlib
import re
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from overrides import override

from multilspy import multilspy_types
from multilspy.lsp_protocol_handler import lsp_types
from multilspy.multilspy_exceptions import MultilspyException
from multilspy.multilspy_logger import MultilspyLogger
from multilspy.language_server import LanguageServer
from multilspy.lsp_protocol_handler.server import Error, ProcessLaunchInfo
from multilspy.lsp_protocol_handler.lsp_types import InitializeParams
from multilspy.multilspy_config import MultilspyConfig


class Gopls(LanguageServer):
    """
    Provides Go specific instantiation of the LanguageServer class using gopls.
    """
    
    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # For Go projects, we should ignore:
        # - vendor: third-party dependencies vendored into the project
        # - node_modules: if the project has JavaScript components
        # - dist/build: common output directories
        return super().is_ignored_dirname(dirname) or dirname in ["vendor", "node_modules", "dist", "build"]

    @staticmethod
    def _get_go_version():
        """Get the installed Go version or None if not found."""
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @staticmethod
    def _get_gopls_version():
        """Get the installed gopls version or None if not found."""
        try:
            result = subprocess.run(['gopls', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @classmethod
    def setup_runtime_dependency(cls):
        """
        Check if required Go runtime dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        go_version = cls._get_go_version()
        if not go_version:
            raise RuntimeError("Go is not installed. Please install Go from https://golang.org/doc/install and make sure it is added to your PATH.")
        
        gopls_version = cls._get_gopls_version()
        if not gopls_version:
            raise RuntimeError(
                "Found a Go version but gopls is not installed.\n"
                "Please install gopls as described in https://pkg.go.dev/golang.org/x/tools/gopls#section-readme\n\n"
                "After installation, make sure it is added to your PATH (it might be installed in a different location than Go)."
            )
        
        return True

    def __init__(self, config: MultilspyConfig, logger: MultilspyLogger, repository_root_path: str):
        self.setup_runtime_dependency()
        
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd="gopls", cwd=repository_root_path),
            "go",
        )
        self.server_ready = asyncio.Event()
        self.request_id = 0

    def _get_initialize_params(self, repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the TypeScript Language Server.
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
    async def start_server(self) -> AsyncIterator["Gopls"]:
        """Start gopls server process"""
        async def register_capability_handler(params):
            return

        async def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        async def do_nothing(params):
            return

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        async with super().start_server():
            self.logger.log("Starting gopls server process", logging.INFO)
            await self.server.start()
            initialize_params = self._get_initialize_params(self.repository_root_path)

            self.logger.log(
                "Sending initialize request from LSP client to LSP server and awaiting response",
                logging.INFO,
            )
            init_response = await self.server.send.initialize(initialize_params)
            
            # Verify server capabilities
            assert "textDocumentSync" in init_response["capabilities"]
            assert "completionProvider" in init_response["capabilities"]
            assert "definitionProvider" in init_response["capabilities"]

            self.server.notify.initialized({})
            self.completions_available.set()

            # gopls server is typically ready immediately after initialization
            self.server_ready.set()
            await self.server_ready.wait()

            yield self

    @override
    def _supports_lsp_type_hierarchy(self) -> bool:
        """
        Gopls claims to support LSP 3.17 type hierarchy methods but Go struct embedding
        is not traditional inheritance and may not work reliably with LSP type hierarchy.
        Use fallback approach instead.
        """
        return False


    @override
    def _is_inheriting_from(self, file_path: str, class_symbol: dict, target_class_name: str) -> bool:
            """
            For Go, inheritance detection via heuristics.
            Go uses embedding rather than traditional inheritance, so this checks for struct embedding.
            """
            try:
                # Read the line where the struct is defined
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
                
                # Use regex to find struct definition and check for embedded fields
                import re
                
                # Find the struct definition starting from start_line
                struct_content = ""
                found_opening_brace = False
                brace_count = 0
                
                for i in range(start_line, min(start_line + 50, len(lines))):
                    line = lines[i]
                    struct_content += line + "\n"
                    
                    # Find opening brace
                    if '{' in line:
                        found_opening_brace = True
                        brace_count += line.count('{')
                    
                    if found_opening_brace:
                        brace_count -= line.count('}')
                        # Stop when we've closed all braces
                        if brace_count <= 0:
                            break
                
                if not found_opening_brace:
                    return False
                
                # Use regex to find embedded fields in the struct
                # Pattern matches: BaseStruct, *BaseStruct, pkg.BaseStruct, *pkg.BaseStruct
                # With optional struct tags and comments
                patterns = [
                    # Direct embedding: BaseStruct
                    rf'\b{re.escape(target_class_name)}\b\s*(?://.*)?(?:`[^`]*`)?\s*$',
                    # Pointer embedding: *BaseStruct  
                    rf'\*{re.escape(target_class_name)}\b\s*(?://.*)?(?:`[^`]*`)?\s*$',
                    # Qualified embedding: pkg.BaseStruct
                    rf'\w+\.{re.escape(target_class_name)}\b\s*(?://.*)?(?:`[^`]*`)?\s*$',
                    # Qualified pointer embedding: *pkg.BaseStruct
                    rf'\*\w+\.{re.escape(target_class_name)}\b\s*(?://.*)?(?:`[^`]*`)?\s*$'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, struct_content, re.MULTILINE):
                        return True
                        
                return False
                
            except Exception as e:
                self.logger.log(f"Error checking Go struct embedding in {file_path}: {e}", logging.DEBUG)
                return False


