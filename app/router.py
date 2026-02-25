import logging
from typing import Any

from app.commands.devops import DevOpsCommands
from app.commands.docker import DockerCommands
from app.commands.system import SystemCommands

logger = logging.getLogger("jarvis.router")


class CommandRouter:
    def __init__(self) -> None:
        self.plugins: dict[str, Any] = {}

    async def initialize(self) -> None:
        self.plugins = {
            "system": SystemCommands(),
            "docker": DockerCommands(),
            "devops": DevOpsCommands(),
            "chat": None,
        }

    async def dispatch(self, command: dict[str, Any]) -> dict[str, str]:
        plugin_name = command.get("command", "chat")
        action = command.get("action", "answer")
        args = command.get("args", {})

        if plugin_name == "chat":
            return {"message": command.get("say") or command.get("text", "")}

        plugin = self.plugins.get(plugin_name)
        if plugin is None:
            return {"message": f"Unknown plugin: {plugin_name}"}

        handler = getattr(plugin, action, None)
        if not handler:
            return {"message": f"Unknown action: {plugin_name}.{action}"}

        try:
            result = await handler(**args)
            if isinstance(result, dict):
                return result
            return {"message": str(result)}
        except TypeError:
            logger.exception("Invalid args for %s.%s", plugin_name, action)
            return {"message": f"Invalid arguments for {plugin_name}.{action}"}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Command execution failed")
            return {"message": f"Execution failed: {exc}"}
