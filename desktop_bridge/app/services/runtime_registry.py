import os

from app.runtime.base import AgentRuntimeAdapter
from app.runtime.antigravity_cli import AntigravityCliAdapter, AntigravityCliConfig
from app.runtime.official_sdk import OfficialSdkAdapter, OfficialSdkConfig
from app.runtime.stub import StubRuntimeAdapter

runtime_name = os.getenv("ANTIGRAVITY_RUNTIME", "").strip().lower()
cli_config = AntigravityCliConfig.from_env()
sdk_config = OfficialSdkConfig.from_env()


def _build_runtime_adapter() -> AgentRuntimeAdapter:
    if runtime_name == "official_sdk":
        if sdk_config is not None:
            return OfficialSdkAdapter(sdk_config)
        return StubRuntimeAdapter()
    if runtime_name == "antigravity_cli":
        if cli_config is not None:
            return AntigravityCliAdapter(cli_config)
        return StubRuntimeAdapter()
    if cli_config is not None:
        return AntigravityCliAdapter(cli_config)
    if sdk_config is not None:
        return OfficialSdkAdapter(sdk_config)
    return StubRuntimeAdapter()


_runtime_adapter: AgentRuntimeAdapter = _build_runtime_adapter()


def get_runtime_adapter() -> AgentRuntimeAdapter:
    return _runtime_adapter


def get_runtime_status() -> dict[str, str | bool]:
    if isinstance(_runtime_adapter, AntigravityCliAdapter) and cli_config is not None:
        return {
            "adapter": "antigravity_cli",
            "configured": True,
            "lsAddress": cli_config.ls_address,
            "hasDefaultConversation": bool(cli_config.default_conversation_id),
            "runtimePreference": runtime_name or "auto",
        }
    if isinstance(_runtime_adapter, OfficialSdkAdapter) and sdk_config is not None:
        return {
            "adapter": "official_sdk",
            "configured": True,
            "lsAddress": "",
            "hasDefaultConversation": bool(sdk_config.default_conversation_id),
            "runtimePreference": runtime_name or "auto",
            "vertexProject": sdk_config.project,
            "vertexLocation": sdk_config.location,
            "sdkInstalled": OfficialSdkAdapter.sdk_installed(),
        }
    return {
        "adapter": "stub",
        "configured": False,
        "lsAddress": "",
        "hasDefaultConversation": False,
        "runtimePreference": runtime_name or "auto",
        "sdkInstalled": OfficialSdkAdapter.sdk_installed(),
    }
