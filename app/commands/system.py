import asyncio
import platform
import shutil
import subprocess
import psutil


class SystemCommands:
    async def open_application(self, app_name: str) -> dict[str, str]:
        command = self._resolve_app_command(app_name)
        if command is None:
            return {"message": f"Application '{app_name}' not found."}

        await asyncio.to_thread(subprocess.Popen, command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"message": f"Opening {app_name}."}

    async def cpu_usage(self) -> dict[str, str]:
        cpu = psutil.cpu_percent(interval=0.5)
        return {"message": f"CPU usage is {cpu:.1f} percent."}

    async def ram_usage(self) -> dict[str, str]:
        mem = psutil.virtual_memory()
        return {"message": f"RAM usage is {mem.percent:.1f} percent."}

    async def disk_usage(self, path: str = "/") -> dict[str, str]:
        usage = psutil.disk_usage(path)
        return {"message": f"Disk usage for {path} is {usage.percent:.1f} percent."}

    def _resolve_app_command(self, app_name: str) -> list[str] | None:
        app = app_name.lower().strip()
        if app in {"vscode", "code", "visual studio code"} and shutil.which("code"):
            return ["code"]

        if platform.system().lower().startswith("win"):
            return ["cmd", "/c", "start", "", app_name]

        if shutil.which(app):
            return [app]
        return None
