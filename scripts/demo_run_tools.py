"""
This script demonstrates how to use Serena's tools locally, useful
for testing or development. Here the tools will be operation the serena repo itself.
"""

from pprint import pprint

from serena.agent import *
from serena.constants import REPO_ROOT


@dataclass
class InMemorySerenaConfig(SerenaConfigBase):
    """
    In-memory implementation of Serena configuration with the GUI disabled.
    """

    gui_log_window_enabled: bool = False
    web_dashboard: bool = False


if __name__ == "__main__":
    # project_path = str(Path("test") / "resources" / "repos" / "python" / "test_repo")
    agent = SerenaAgent(project=REPO_ROOT)

    # apply a tool
    find_refs_tool = agent.get_tool(FindReferencingSymbolsTool)
    find_symbol_tool = agent.get_tool(FindSymbolTool)
    print("Finding the symbol 'SyncLanguageServer'\n")
    pprint(
        json.loads(
            find_symbol_tool.apply(name_path="test_request_type_hierarchy", relative_path="test/multilspy/python/test_symbol_retrieval.py")
        )
    )
