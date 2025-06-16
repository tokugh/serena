"""
Provides Python specific instantiation of the LanguageServer class. Contains various configurations and settings specific to Python.
"""

import json
import logging
import os
import pathlib
from contextlib import asynccontextmanager
from typing import AsyncIterator, Tuple

from overrides import override

from multilspy.multilspy_logger import MultilspyLogger
from multilspy.language_server import LanguageServer
from multilspy.lsp_protocol_handler.server import ProcessLaunchInfo
from multilspy.lsp_protocol_handler.lsp_types import InitializeParams
from multilspy.multilspy_config import MultilspyConfig


class JediServer(LanguageServer):
    """
    Provides Python specific instantiation of the LanguageServer class. Contains various configurations and settings specific to Python.
    """

    def __init__(self, config: MultilspyConfig, logger: MultilspyLogger, repository_root_path: str):
        """
        Creates a JediServer instance. This class is not meant to be instantiated directly. Use LanguageServer.create() instead.
        """
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd="jedi-language-server", cwd=repository_root_path),
            "python",
        )
        
    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        return super().is_ignored_dirname(dirname) or dirname in ["venv", "__pycache__"]

    def _get_initialize_params(self, repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Jedi Language Server.
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
    async def start_server(self) -> AsyncIterator["JediServer"]:
        """
        Starts the JEDI Language Server, waits for the server to be ready and yields the LanguageServer instance.

        Usage:
        ```
        async with lsp.start_server():
            # LanguageServer has been initialized and ready to serve requests
            await lsp.request_definition(...)
            await lsp.request_references(...)
            # Shutdown the LanguageServer on exit from scope
        # LanguageServer has been shutdown
        ```
        """

        async def execute_client_command_handler(params):
            return []

        async def do_nothing(params):
            return

        async def check_experimental_status(params):
            if params["quiescent"] == True:
                self.completions_available.set()

        async def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        self.server.on_request("client/registerCapability", do_nothing)
        self.server.on_notification("language/status", do_nothing)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request("workspace/executeClientCommand", execute_client_command_handler)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)
        self.server.on_notification("language/actionableNotification", do_nothing)
        self.server.on_notification("experimental/serverStatus", check_experimental_status)

        async with super().start_server():
            self.logger.log("Starting jedi-language-server server process", logging.INFO)
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
                "triggerCharacters": [".", "'", '"'],
                "resolveProvider": True,
            }

            self.server.notify.initialized({})

            yield self

    @override
    def _supports_lsp_type_hierarchy(self) -> bool:
        """Jedi does not support LSP 3.17 type hierarchy methods."""
        return False

    @override
    def _is_inheriting_from(self, file_path: str, class_symbol: dict, target_class_name: str) -> bool:
        """
        Check if a Python class symbol is inheriting from the target class.
        Same heuristic as PyrightServer since both handle Python.
        """
        try:
            # Read the line where the class is defined
            abs_path = os.path.join(self.repository_root_path, file_path)
            if not os.path.exists(abs_path):
                return False
                
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            class_range = class_symbol.get("range", {})
            start_line = class_range.get("start", {}).get("line", -1)
            
            if start_line < 0 or start_line >= len(lines):
                return False
            
            # Check the class definition line for inheritance
            class_line = lines[start_line].strip()
            
            # Look for patterns like "class Child(Parent):" or "class Child(Base, Parent):"
            if f"({target_class_name}" in class_line or f", {target_class_name}" in class_line or f"{target_class_name})" in class_line:
                return True
                
            # Also check a few lines after in case the inheritance spans multiple lines
            for i in range(start_line + 1, min(start_line + 3, len(lines))):
                line = lines[i].strip()
                if line.endswith("):") or line.endswith(","):
                    if target_class_name in line:
                        return True
                else:
                    break  # Stop if we hit a line that doesn't look like continuation
                    
            return False
            
        except Exception as e:
            self.logger.log(f"Error checking inheritance in {file_path}: {e}", logging.DEBUG)
            return False
