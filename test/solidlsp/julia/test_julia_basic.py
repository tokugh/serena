"""
Basic tests for Julia Language Server integration
"""

import os
from pathlib import Path

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language


@pytest.mark.julia
class TestJuliaLanguageServer:
    """Test basic functionality of the Julia language server."""

    @pytest.mark.parametrize("language_server", [Language.JULIA], indirect=True)
    @pytest.mark.parametrize("repo_path", [Language.JULIA], indirect=True)
    def test_server_initialization(self, language_server: SolidLanguageServer, repo_path: Path):
        """Test that the Julia language server initializes properly."""
        assert language_server is not None
        assert language_server.language_id == "julia"
        assert language_server.is_running()
        assert Path(language_server.language_server.repository_root_path).resolve() == repo_path.resolve()

    @pytest.mark.parametrize("language_server", [Language.JULIA], indirect=True)
    def test_symbol_retrieval(self, language_server: SolidLanguageServer):
        """Test Julia document symbol extraction."""
        all_symbols, root_symbols = language_server.request_document_symbols(os.path.join("src", "calculator.jl"))

        # Should find the exported functions
        function_symbols = [s for s in all_symbols if s.get("kind") == 12]  # Function kind
        assert len(function_symbols) >= 4

        # Check that we found the expected functions
        function_names = {s.get("name") for s in function_symbols}
        expected_functions = {"add", "subtract", "multiply", "divide"}
        assert expected_functions.issubset(function_names), f"Expected functions {expected_functions} but found {function_names}"

    @pytest.mark.parametrize("language_server", [Language.JULIA], indirect=True)
    def test_find_definition_across_files(self, language_server: SolidLanguageServer):
        """Test finding function definitions across files."""
        main_file = "main.jl"

        # In main.jl, there is a call to Calculator.add
        # Find definition of add function
        definition_location_list = language_server.request_definition(main_file, 17, 23)  # cursor on 'add'

        assert definition_location_list, f"Expected non-empty definition_location_list but got {definition_location_list=}"
        assert len(definition_location_list) >= 1
        definition_location = definition_location_list[0]
        assert definition_location["uri"].endswith("calculator.jl")

    @pytest.mark.parametrize("language_server", [Language.JULIA], indirect=True)
    def test_find_references_across_files(self, language_server: SolidLanguageServer):
        """Test finding function references across files."""
        calculator_file = os.path.join("src", "calculator.jl")

        # Test from definition side: find references to add function defined in calculator.jl
        references = language_server.request_references(calculator_file, 9, 10)  # cursor on 'add' function definition

        assert references, f"Expected non-empty references for add function but got {references=}"

        # Must find usage in main.jl (cross-file reference)
        reference_files = [ref["uri"] for ref in references]
        assert any(uri.endswith("main.jl") for uri in reference_files), "Cross-file reference to usage in main.jl not found"

    def test_file_matching(self):
        """Test that Julia files are properly matched."""
        from solidlsp.ls_config import Language

        matcher = Language.JULIA.get_source_fn_matcher()

        assert matcher.is_relevant_filename("script.jl")
        assert matcher.is_relevant_filename("Main.jl")
        assert not matcher.is_relevant_filename("script.py")
        assert not matcher.is_relevant_filename("README.md")

    def test_julia_language_enum(self):
        """Test Julia language enum value."""
        assert Language.JULIA == "julia"
        assert str(Language.JULIA) == "julia"
