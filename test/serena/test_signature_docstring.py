"""Tests for signature and docstring retrieval functionality."""

from unittest.mock import Mock

import pytest

from src.multilspy import multilspy_types
from src.serena.symbol import Symbol, SymbolManager


class TestSignatureAndDocstring:
    """Test suite for signature and docstring functionality."""

    @pytest.fixture
    def mock_lang_server(self):
        """Create a mock language server for testing."""
        mock_server = Mock()
        mock_server.request_signature_help = Mock()
        mock_server.request_hover = Mock()
        return mock_server

    @pytest.fixture
    def symbol_manager(self, mock_lang_server):
        """Create a SymbolManager with mocked language server."""
        manager = SymbolManager(None)
        manager._lang_server = mock_lang_server
        return manager

    @pytest.fixture
    def sample_symbol(self):
        """Create a sample symbol for testing."""
        symbol_info = multilspy_types.UnifiedSymbolInformation(
            name="test_function",
            kind=multilspy_types.SymbolKind.Function,
            location=multilspy_types.Location(
                uri="file:///test.py",
                range=multilspy_types.Range(
                    start=multilspy_types.Position(line=10, character=4), end=multilspy_types.Position(line=15, character=10)
                ),
                absolutePath="/test.py",
                relativePath="test.py",
            ),
            selectionRange=multilspy_types.Range(
                start=multilspy_types.Position(line=10, character=4), end=multilspy_types.Position(line=10, character=17)
            ),
            children=[],
        )
        return Symbol(symbol_info)

    def test_symbol_signature_property(self, sample_symbol):
        """Test signature property getter and setter."""
        # Initially should be None
        assert sample_symbol.signature is None

        # Set signature
        sample_symbol.signature = "def test_function(param1: str, param2: int) -> bool"
        assert sample_symbol.signature == "def test_function(param1: str, param2: int) -> bool"

        # Set to None
        sample_symbol.signature = None
        assert sample_symbol.signature is None

    def test_symbol_docstring_property(self, sample_symbol):
        """Test docstring property getter and setter."""
        # Initially should be None
        assert sample_symbol.docstring is None

        # Set docstring
        sample_symbol.docstring = "This is a test function that does something useful."
        assert sample_symbol.docstring == "This is a test function that does something useful."

        # Set to None
        sample_symbol.docstring = None
        assert sample_symbol.docstring is None

    def test_symbol_to_dict_with_signature_and_docstring(self, sample_symbol):
        """Test to_dict method includes signature and docstring when requested."""
        sample_symbol.signature = "def test_function() -> None"
        sample_symbol.docstring = "Test docstring"

        # Test without signature/docstring
        result = sample_symbol.to_dict()
        assert "signature" not in result
        assert "docstring" not in result

        # Test with signature only
        result = sample_symbol.to_dict(include_signature=True)
        assert result["signature"] == "def test_function() -> None"
        assert "docstring" not in result

        # Test with docstring only
        result = sample_symbol.to_dict(include_docstring=True)
        assert "signature" not in result
        assert result["docstring"] == "Test docstring"

        # Test with both
        result = sample_symbol.to_dict(include_signature=True, include_docstring=True)
        assert result["signature"] == "def test_function() -> None"
        assert result["docstring"] == "Test docstring"

    def test_get_signature_and_docstring_with_signature_help(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test signature and docstring retrieval from signatureHelp."""
        # Mock signature help response
        mock_lang_server.request_signature_help.return_value = {
            "signatures": [
                {
                    "label": "def test_function(param: str) -> bool",
                    "documentation": "This function tests something important.",
                    "parameters": [{"label": "param", "documentation": "The parameter to test"}],
                }
            ],
            "activeSignature": 0,
        }

        # Mock hover not called since signature help provides sufficient info
        mock_lang_server.request_hover.return_value = None

        signature, docstring = symbol_manager.get_signature_and_docstring(sample_symbol)

        assert signature == "def test_function(param: str) -> bool"
        assert docstring == "This function tests something important."

        # Verify calls
        mock_lang_server.request_signature_help.assert_called_once_with("test.py", 10, 4)

    def test_get_signature_and_docstring_with_hover_fallback(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test fallback to hover when signature help lacks documentation."""
        # Mock signature help with no documentation
        mock_lang_server.request_signature_help.return_value = {
            "signatures": [
                {
                    "label": "def test_function(param: str) -> bool"
                    # No documentation field
                }
            ],
            "activeSignature": 0,
        }

        # Mock hover response
        mock_lang_server.request_hover.return_value = {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef test_function(param: str) -> bool\n```\n\nThis function performs comprehensive testing of the given parameter.",
            }
        }

        signature, docstring = symbol_manager.get_signature_and_docstring(sample_symbol)

        assert signature == "def test_function(param: str) -> bool"
        assert docstring == "This function performs comprehensive testing of the given parameter."

        # Verify both calls were made
        mock_lang_server.request_signature_help.assert_called_once()
        mock_lang_server.request_hover.assert_called_once()

    def test_get_signature_and_docstring_no_results(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test when neither signature help nor hover return useful information."""
        # Mock empty responses
        mock_lang_server.request_signature_help.return_value = None
        mock_lang_server.request_hover.return_value = None

        signature, docstring = symbol_manager.get_signature_and_docstring(sample_symbol)

        assert signature is None
        assert docstring is None

    def test_get_signature_and_docstring_exception_handling(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test exception handling in signature/docstring retrieval."""
        # Mock exception
        mock_lang_server.request_signature_help.side_effect = Exception("LSP error")

        signature, docstring = symbol_manager.get_signature_and_docstring(sample_symbol)

        assert signature is None
        assert docstring is None

    def test_enrich_symbol_with_signature_and_docstring(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test enriching a symbol with signature and docstring."""
        # Mock successful responses
        mock_lang_server.request_signature_help.return_value = {
            "signatures": [{"label": "def enriched_function() -> str", "documentation": "An enriched function."}],
            "activeSignature": 0,
        }

        # Initially no signature/docstring
        assert sample_symbol.signature is None
        assert sample_symbol.docstring is None

        # Enrich the symbol
        symbol_manager.enrich_symbol_with_signature_and_docstring(sample_symbol)

        # Check that properties were set
        assert sample_symbol.signature == "def enriched_function() -> str"
        assert sample_symbol.docstring == "An enriched function."

    def test_hover_content_parsing_markdown(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test parsing different formats of hover content."""
        # Mock signature help with no docs
        mock_lang_server.request_signature_help.return_value = {"signatures": [{"label": "def test() -> None"}], "activeSignature": 0}

        # Mock hover with markdown content
        mock_lang_server.request_hover.return_value = {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef test() -> None\n```\n\nThis is the actual docstring content.\nIt spans multiple lines.",
            }
        }

        signature, docstring = symbol_manager.get_signature_and_docstring(sample_symbol)

        assert signature == "def test() -> None"
        assert "This is the actual docstring content.\nIt spans multiple lines." in docstring

    def test_hover_content_parsing_string_list(self, symbol_manager, mock_lang_server, sample_symbol):
        """Test parsing hover content when it's a list of strings."""
        # Mock signature help with no docs
        mock_lang_server.request_signature_help.return_value = {"signatures": [{"label": "def test() -> None"}], "activeSignature": 0}

        # Mock hover with list content
        mock_lang_server.request_hover.return_value = {
            "contents": [{"value": "```python\ndef test() -> None\n```"}, {"value": "Documentation for the test function."}]
        }

        signature, docstring = symbol_manager.get_signature_and_docstring(sample_symbol)

        assert signature == "def test() -> None"
        assert "Documentation for the test function." in docstring
