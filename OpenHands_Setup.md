# Making OpenHands Run

Instructions or running Serena locally inside OpenHands. The MCP support there
was [merged just on 10.04.2025](https://github.com/All-Hands-AI/OpenHands/pull/7637) 
and is not part of the official documentation or the
last released docker image at the time of writing. Nevertheless, it works!

## Config

After cloning with

```shell
git clone git@github.com:All-Hands-AI/OpenHands.git
```

we need to configure OpenHands before we begin.

```shell
cp config.template.toml config.toml
```

There add mcp config

```toml
[mcp]
mcp_servers = ["http://localhost:8000/sse"]
```

Disable all `codeact_*` settings.

Unfortunately, this is not enough - the `CodeActAgent` always has some default tools that can't be disabled.
They are created in the constructor of that class as:

```python
        built_in_tools = codeact_function_calling.get_tools(
            codeact_enable_browsing=self.config.codeact_enable_browsing,
            codeact_enable_jupyter=self.config.codeact_enable_jupyter,
            codeact_enable_llm_editor=self.config.codeact_enable_llm_editor,
            llm=self.llm,
        )

        self.tools = built_in_tools
```

with `get_tools` implemented as

```python
def get_tools(
    codeact_enable_browsing: bool = False,
    codeact_enable_llm_editor: bool = False,
    codeact_enable_jupyter: bool = False,
    llm: LLM | None = None,
) -> list[ChatCompletionToolParam]:
    SIMPLIFIED_TOOL_DESCRIPTION_LLM_SUBSTRS = ['gpt-', 'o3', 'o1']

    use_simplified_tool_desc = False
    if llm is not None:
        use_simplified_tool_desc = any(
            model_substr in llm.config.model
            for model_substr in SIMPLIFIED_TOOL_DESCRIPTION_LLM_SUBSTRS
        )

    tools = [
        create_cmd_run_tool(use_simplified_description=use_simplified_tool_desc),
        ThinkTool,
        FinishTool,
    ]
    if codeact_enable_browsing:
        tools.append(WebReadTool)
        tools.append(BrowserTool)
    if codeact_enable_jupyter:
        tools.append(IPythonTool)
    if codeact_enable_llm_editor:
        tools.append(LLMBasedFileEditTool)
    else:
        tools.append(
            create_str_replace_editor_tool(
                use_simplified_description=use_simplified_tool_desc
            )
        )
    return tools
```

So you will always get the bash tool, the thinking tool, and the finish tool. They can only 
be disabled by editing openhands source code (e.g., in a fork). But probably a better strategy
is to disable Serena's shell tool and the tools related to finishing. It may make sense to disable
some of Serena's thinking tools, though I would rather disable openhands' generic thinking tool instead...


## Installation

```shell
cd frontend
npm install
npm run build
```

```shell
mamba create -n openhands python=3.12
mamba activate openhands   
mamba install conda-forge::nodejs    
mamba install conda-forge::poetry
poetry env use $(which python)
poetry install
```

## Start Backend

The docs from the readme don't exactly work, but you can start the backend
and frontend separately.

For the backend, you can do

```shell
make start-backend
```

which is equivalent to 

```shell
poetry run uvicorn openhands.server.listen:app --host "127.0.0.1" --port 3000 --reload --reload-exclude "./workspace"
```

Since this is not debuggable, you may prefer to start it through a python script. 
You might need to install uvicorn for that (e.g. `mamba install uvicorn`). Here a script version:

```python
import uvicorn

# Global variables for host and port
HOST = "127.0.0.1"
PORT = 3000

if __name__ == "__main__":
    print(f"Starting server on {HOST}:{PORT} with reload enabled.")
    uvicorn.run(
        "openhands.server.listen:app", 
        host=HOST, 
        port=PORT, 
        reload=True,
        reload_excludes=["./workspace"]
    ) 
```

For some unholy reason, the frontend needs to be built for the backend to startup,
see installation section

## Start Frontend

The make command works

```shell
make start-frontend
```

which is the same as 

```shell
cd frontend
export VITE_BACKEND_HOST="127.0.0.1:3000" 
export VITE_FRONTEND_PORT=3001
npm run dev -- --port 3001 --host "127.0.0.1"
```

When the frontend opens, go to settings, select your model and enter your api key.

> IMPORTANT: the pro version of Gemini may cost far more than the experimental one, 
> make sure to not accidentally select it!

## First Conversation

On your first conversation, OpenHands will build a docker image and start a container.
**This is very slow!** You will see the message 

`================ DOCKER BUILD STARTED ================`

in the backend logs, just be patient. Eventually, you will get a response.

Ask the LLM to list the available tools, you will see Serena mcp tools (the names are postfixed with `_mcp_tool_call`).
