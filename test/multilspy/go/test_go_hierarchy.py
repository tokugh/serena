import os
import pytest
from multilspy import SyncLanguageServer
from multilspy.multilspy_config import Language


@pytest.mark.go
class TestGoTypeHierarchy:
    @pytest.mark.parametrize("language_server", [Language.GO], indirect=True)
    def test_request_type_hierarchy(self, language_server: SyncLanguageServer) -> None:
        # Test struct embedding: ChildStruct embeds BaseStruct
        child_file_path = "child.go"
        symbols = language_server.request_document_symbols(child_file_path)
        child_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "ChildStruct" and sym.get("kind") == 23:  # 23 = Struct
                child_struct_symbol = sym
                break
        assert child_struct_symbol is not None, "Could not find 'ChildStruct' symbol"

        # Test struct embedding for ChildStruct -> BaseStruct
        hierarchy_result = language_server.request_type_hierarchy(
            child_file_path, 
            child_struct_symbol["range"]["start"]["line"], 
            child_struct_symbol["range"]["start"]["character"], 
            "BaseStruct"
        )
        assert hierarchy_result is True, "ChildStruct should embed BaseStruct"

        # Test struct embedding: ConcreteProcessor embeds BaseStruct
        processor_file_path = "processor.go"
        symbols = language_server.request_document_symbols(processor_file_path)
        processor_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "ConcreteProcessor" and sym.get("kind") == 23:  # 23 = Struct
                processor_struct_symbol = sym
                break
        assert processor_struct_symbol is not None, "Could not find 'ConcreteProcessor' symbol"

        # Test struct embedding
        hierarchy_result = language_server.request_type_hierarchy(
            processor_file_path,
            processor_struct_symbol["range"]["start"]["line"],
            processor_struct_symbol["range"]["start"]["character"],
            "BaseStruct",
        )
        assert hierarchy_result is True, "ConcreteProcessor should embed BaseStruct"

        # Test negative case: BaseStruct should not embed ChildStruct
        base_file_path = "base.go"
        symbols = language_server.request_document_symbols(base_file_path)
        base_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "BaseStruct" and sym.get("kind") == 23:  # 23 = Struct
                base_struct_symbol = sym
                break
        assert base_struct_symbol is not None, "Could not find 'BaseStruct' symbol"

        hierarchy_result = language_server.request_type_hierarchy(
            base_file_path, 
            base_struct_symbol["range"]["start"]["line"], 
            base_struct_symbol["range"]["start"]["character"], 
            "ChildStruct"
        )
        assert hierarchy_result is False, "BaseStruct should not embed ChildStruct"

    @pytest.mark.parametrize("language_server", [Language.GO], indirect=True)  
    def test_request_type_hierarchy_symbols(self, language_server: SyncLanguageServer) -> None:
        """Test the type hierarchy symbols method that returns actual hierarchy information."""
        base_file_path = "base.go"
        symbols = language_server.request_document_symbols(base_file_path)
        base_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "BaseStruct" and sym.get("kind") == 23:  # 23 = Struct
                base_struct_symbol = sym
                break
        assert base_struct_symbol is not None, "Could not find 'BaseStruct' symbol"

        # Test type hierarchy symbols
        supertypes, subtypes = language_server.request_type_hierarchy_symbols(
            base_file_path,
            base_struct_symbol["range"]["start"]["line"],
            base_struct_symbol["range"]["start"]["character"]
        )

        # Our fallback implementation should find structs that embed BaseStruct
        subtype_names = {sub["name"] for sub in subtypes}
        expected_subtypes = {"ChildStruct", "ConcreteProcessor"}
        
        # At least some of the expected subtypes should be found
        assert len(subtype_names.intersection(expected_subtypes)) > 0, f"Expected to find some of {expected_subtypes}, but got {subtype_names}"