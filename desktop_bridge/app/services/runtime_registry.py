from app.runtime.base import AgentRuntimeAdapter
from app.runtime.antigravity_cli import AntigravityCliAdapter, AntigravityCliConfig
from app.runtime.stub import StubRuntimeAdapter

runtime_config = AntigravityCliConfig.from_env()
_runtime_adapter: AgentRuntimeAdapter = (
    AntigravityCliAdapter(runtime_config) if runtime_config is not None else StubRuntimeAdapter()
)


def get_runtime_adapter() -> AgentRuntimeAdapter:
    return _runtime_adapter


def get_runtime_status() -> dict[str, str | bool]:
    if runtime_config is not None:
        return {
            "adapter": "antigravity_cli",
            "configured": True,
            "lsAddress": runtime_config.ls_address,
            "hasDefaultConversation": bool(runtime_config.default_conversation_id),
        }
    return {
        "adapter": "stub",
        "configured": False,
        "lsAddress": "",
        "hasDefaultConversation": False,
    }
