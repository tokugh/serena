import os
import pytest
from multilspy import SyncLanguageServer
from multilspy.multilspy_config import Language


@pytest.mark.typescript
class TestTypeScriptTypeHierarchy:
    @pytest.mark.parametrize("language_server", [Language.TYPESCRIPT], indirect=True)
    def test_request_type_hierarchy(self, language_server: SyncLanguageServer) -> None:
        # Test class inheritance: ChildClass extends BaseClass
        child_file_path = "ChildClass.ts"
        symbols = language_server.request_document_symbols(child_file_path)
        child_class_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "ChildClass" and sym.get("kind") == 5:  # 5 = Class
                child_class_symbol = sym
                break
        assert child_class_symbol is not None, "Could not find 'ChildClass' symbol"

        # Test type hierarchy for ChildClass -> BaseClass
        hierarchy_result = language_server.request_type_hierarchy(
            child_file_path, 
            child_class_symbol["range"]["start"]["line"], 
            child_class_symbol["range"]["start"]["character"], 
            "BaseClass"
        )
        assert hierarchy_result is True, "ChildClass should extend BaseClass"

        # Test interface implementation: ConcreteProcessor implements Processable
        concrete_file_path = "ConcreteProcessor.ts"
        symbols = language_server.request_document_symbols(concrete_file_path)
        concrete_class_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "ConcreteProcessor" and sym.get("kind") == 5:  # 5 = Class
                concrete_class_symbol = sym
                break
        assert concrete_class_symbol is not None, "Could not find 'ConcreteProcessor' symbol"

        # Test interface implementation
        hierarchy_result = language_server.request_type_hierarchy(
            concrete_file_path,
            concrete_class_symbol["range"]["start"]["line"],
            concrete_class_symbol["range"]["start"]["character"],
            "Processable",
        )
        assert hierarchy_result is True, "ConcreteProcessor should implement Processable"

        # Test inheritance chain: ConcreteProcessor extends BaseClass
        hierarchy_result = language_server.request_type_hierarchy(
            concrete_file_path,
            concrete_class_symbol["range"]["start"]["line"],
            concrete_class_symbol["range"]["start"]["character"],
            "BaseClass",
        )
        assert hierarchy_result is True, "ConcreteProcessor should extend BaseClass"

        # Test multiple interfaces: MultipleInterfaces implements Readable, Writable, Processable
        multi_file_path = "MultipleInterfaces.ts"
        symbols = language_server.request_document_symbols(multi_file_path)
        multi_class_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "MultipleInterfaces" and sym.get("kind") == 5:  # 5 = Class
                multi_class_symbol = sym
                break
        assert multi_class_symbol is not None, "Could not find 'MultipleInterfaces' symbol"

        # Test each interface implementation
        for interface_name in ["Readable", "Writable", "Processable"]:
            hierarchy_result = language_server.request_type_hierarchy(
                multi_file_path,
                multi_class_symbol["range"]["start"]["line"],
                multi_class_symbol["range"]["start"]["character"],
                interface_name,
            )
            assert hierarchy_result is True, f"MultipleInterfaces should implement {interface_name}"

        # Test negative case: BaseClass should not inherit from ChildClass
        base_file_path = "BaseClass.ts"
        symbols = language_server.request_document_symbols(base_file_path)
        base_class_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "BaseClass" and sym.get("kind") == 5:  # 5 = Class
                base_class_symbol = sym
                break
        assert base_class_symbol is not None, "Could not find 'BaseClass' symbol"

        hierarchy_result = language_server.request_type_hierarchy(
            base_file_path, 
            base_class_symbol["range"]["start"]["line"], 
            base_class_symbol["range"]["start"]["character"], 
            "ChildClass"
        )
        assert hierarchy_result is False, "BaseClass should not inherit from ChildClass"

    @pytest.mark.parametrize("language_server", [Language.TYPESCRIPT], indirect=True)  
    def test_request_type_hierarchy_symbols(self, language_server: SyncLanguageServer) -> None:
        """Test the type hierarchy symbols method that returns actual hierarchy information."""
        base_file_path = "BaseClass.ts"
        symbols = language_server.request_document_symbols(base_file_path)
        base_class_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "BaseClass" and sym.get("kind") == 5:  # 5 = Class
                base_class_symbol = sym
                break
        assert base_class_symbol is not None, "Could not find 'BaseClass' symbol"

        # Test type hierarchy symbols
        supertypes, subtypes = language_server.request_type_hierarchy_symbols(
            base_file_path,
            base_class_symbol["range"]["start"]["line"],
            base_class_symbol["range"]["start"]["character"]
        )

        # Our fallback implementation should find subclasses
        subtype_names = {sub["name"] for sub in subtypes}
        expected_subtypes = {"ChildClass", "ConcreteProcessor"}
        
        # At least some of the expected subtypes should be found
        assert len(subtype_names.intersection(expected_subtypes)) > 0, f"Expected to find some of {expected_subtypes}, but got {subtype_names}"