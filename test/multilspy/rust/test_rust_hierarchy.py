import os

import pytest

from multilspy import SyncLanguageServer
from multilspy.multilspy_config import Language


@pytest.mark.rust
class TestRustTypeHierarchy:
    @pytest.mark.parametrize("language_server", [Language.RUST], indirect=True)
    def test_request_type_hierarchy(self, language_server: SyncLanguageServer) -> None:
        # Test trait implementation: ChildStruct implements Processable
        child_file_path = os.path.join("src", "child.rs")
        symbols = language_server.request_document_symbols(child_file_path)
        child_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "ChildStruct" and sym.get("kind") == 23:  # 23 = Struct
                child_struct_symbol = sym
                break
        assert child_struct_symbol is not None, "Could not find 'ChildStruct' symbol"

        # Test trait implementation for ChildStruct -> Processable
        hierarchy_result = language_server.request_type_hierarchy(
            child_file_path,
            child_struct_symbol["location"]["range"]["start"]["line"],
            child_struct_symbol["location"]["range"]["start"]["character"],
            "Processable",
        )
        assert hierarchy_result is True, "ChildStruct should implement Processable trait"

        # Test trait implementation: ChildStruct implements Worker
        hierarchy_result = language_server.request_type_hierarchy(
            child_file_path,
            child_struct_symbol["location"]["range"]["start"]["line"],
            child_struct_symbol["location"]["range"]["start"]["character"],
            "Worker",
        )
        assert hierarchy_result is True, "ChildStruct should implement Worker trait"

        # Test trait implementation: ConcreteProcessor implements Processable
        processor_file_path = os.path.join("src", "processor.rs")
        symbols = language_server.request_document_symbols(processor_file_path)
        processor_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "ConcreteProcessor" and sym.get("kind") == 23:  # 23 = Struct
                processor_struct_symbol = sym
                break
        assert processor_struct_symbol is not None, "Could not find 'ConcreteProcessor' symbol"

        # Test trait implementation
        hierarchy_result = language_server.request_type_hierarchy(
            processor_file_path,
            processor_struct_symbol["location"]["range"]["start"]["line"],
            processor_struct_symbol["location"]["range"]["start"]["character"],
            "Processable",
        )
        assert hierarchy_result is True, "ConcreteProcessor should implement Processable trait"

        # Test multiple trait implementation: MultipleInterfaces implements multiple traits
        multi_struct_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "MultipleInterfaces" and sym.get("kind") == 23:  # 23 = Struct
                multi_struct_symbol = sym
                break
        assert multi_struct_symbol is not None, "Could not find 'MultipleInterfaces' symbol"

        # Test each trait implementation
        for trait_name in ["Readable", "Writable", "Processable"]:
            hierarchy_result = language_server.request_type_hierarchy(
                processor_file_path,
                multi_struct_symbol["location"]["range"]["start"]["line"],
                multi_struct_symbol["location"]["range"]["start"]["character"],
                trait_name,
            )
            assert hierarchy_result is True, f"MultipleInterfaces should implement {trait_name} trait"

        # Test negative case: Processable trait should not implement ChildStruct
        base_file_path = os.path.join("src", "base.rs")
        symbols = language_server.request_document_symbols(base_file_path)
        processable_trait_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "Processable" and sym.get("kind") == 11:  # 11 = Interface/Trait
                processable_trait_symbol = sym
                break
        assert processable_trait_symbol is not None, "Could not find 'Processable' trait"

        hierarchy_result = language_server.request_type_hierarchy(
            base_file_path,
            processable_trait_symbol["location"]["range"]["start"]["line"],
            processable_trait_symbol["location"]["range"]["start"]["character"],
            "ChildStruct",
        )
        assert hierarchy_result is False, "Processable trait should not implement ChildStruct"

    @pytest.mark.parametrize("language_server", [Language.RUST], indirect=True)
    def test_request_type_hierarchy_symbols(self, language_server: SyncLanguageServer) -> None:
        """Test the type hierarchy symbols method that returns actual hierarchy information."""
        base_file_path = os.path.join("src", "base.rs")
        symbols = language_server.request_document_symbols(base_file_path)
        processable_trait_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "Processable" and sym.get("kind") == 11:  # 11 = Interface/Trait
                processable_trait_symbol = sym
                break
        assert processable_trait_symbol is not None, "Could not find 'Processable' trait"

        # Test type hierarchy symbols
        supertypes, subtypes = language_server.request_type_hierarchy_symbols(
            base_file_path,
            processable_trait_symbol["location"]["range"]["start"]["line"],
            processable_trait_symbol["location"]["range"]["start"]["character"],
        )

        # Our fallback implementation should find structs that implement Processable
        subtype_names = {sub["name"] for sub in subtypes}
        expected_subtypes = {"ChildStruct", "ConcreteProcessor", "MultipleInterfaces"}

        # At least some of the expected subtypes should be found
        assert (
            len(subtype_names.intersection(expected_subtypes)) > 0
        ), f"Expected to find some of {expected_subtypes}, but got {subtype_names}"
