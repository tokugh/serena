"""
Provides Julia specific instantiation of the LanguageServer class using LanguageServer.jl.
"""

import logging
import os
import pathlib
import subprocess
import threading

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


class JuliaLanguageServer(SolidLanguageServer):
    """Julia Language Server implementation using LanguageServer.jl."""

    @override
    def _get_wait_time_for_cross_file_referencing(self) -> float:
        return 5.0  # Julia language server needs extra time for workspace indexing

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # For Julia projects, ignore common directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "Manifest.toml",  # Not a directory but commonly excluded
            ".julia",  # Julia package cache
            "docs",  # Documentation
        ]

    @staticmethod
    def _check_julia_installation():
        """Check if Julia and LanguageServer.jl are available."""
        try:
            # Check Julia installation
            result = subprocess.run(["julia", "--version"], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                raise RuntimeError("Julia is not installed or not in PATH")

            # Check LanguageServer.jl package
            result = subprocess.run(
                [
                    "julia",
                    "--startup-file=no",
                    "--history-file=no",
                    "-e",
                    'using Pkg; if !haskey(Pkg.project().dependencies, "LanguageServer") && !haskey(Pkg.dependencies(), "LanguageServer") exit(1) end',
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    'Julia LanguageServer.jl package is not installed.\nInstall it with: julia -e \'using Pkg; Pkg.add("LanguageServer")\''
                )

        except FileNotFoundError:
            raise RuntimeError("Julia is not installed. Please install Julia from https://julialang.org/downloads/")

    def __init__(
        self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str, solidlsp_settings: SolidLSPSettings
    ):
        # Check Julia installation
        self._check_julia_installation()

        # Julia command to start language server
        # Use string command like R language server does
        julia_cmd = 'julia --startup-file=no --history-file=no -e "using LanguageServer; server = LanguageServer.LanguageServerInstance(stdin, stdout, pwd()); run(server);"'

        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=julia_cmd, cwd=repository_root_path),
            "julia",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """Initialize params for Julia Language Server."""
        root_uri = pathlib.Path(repository_absolute_path).as_uri()
        initialize_params = {
            "locale": "en",
            "capabilities": {
                "textDocument": {
                    "synchronization": {"didSave": True, "dynamicRegistration": True},
                    "completion": {
                        "dynamicRegistration": True,
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": ["markdown", "plaintext"],
                            "deprecatedSupport": True,
                            "preselectSupport": True,
                        },
                    },
                    "hover": {"dynamicRegistration": True, "contentFormat": ["markdown", "plaintext"]},
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "hierarchicalDocumentSymbolSupport": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "formatting": {"dynamicRegistration": True},
                    "rangeFormatting": {"dynamicRegistration": True},
                },
                "workspace": {
                    "workspaceFolders": True,
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "symbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                },
            },
            "processId": os.getpid(),
            "rootPath": repository_absolute_path,
            "rootUri": root_uri,
            "workspaceFolders": [
                {
                    "uri": root_uri,
                    "name": os.path.basename(repository_absolute_path),
                }
            ],
        }
        return initialize_params

    def _start_server(self):
        """Start Julia Language Server process."""

        def window_log_message(msg):
            self.logger.log(f"Julia LSP: window/logMessage: {msg}", logging.INFO)

        def do_nothing(params):
            return

        def register_capability_handler(params):
            return

        # Register LSP message handlers
        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        self.logger.log("Starting Julia Language Server process", logging.INFO)
        self.server.start()

        initialize_params = self._get_initialize_params(self.repository_root_path)
        self.logger.log(
            "Sending initialize request to Julia Language Server",
            logging.INFO,
        )

        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities
        capabilities = init_response.get("capabilities", {})
        assert "textDocumentSync" in capabilities
        if "completionProvider" in capabilities:
            self.logger.log("Julia LSP completion provider available", logging.INFO)
        if "definitionProvider" in capabilities:
            self.logger.log("Julia LSP definition provider available", logging.INFO)

        self.server.notify.initialized({})
        self.completions_available.set()

        # Julia Language Server is ready after initialization
        self.server_ready.set()
