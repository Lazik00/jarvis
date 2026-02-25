import asyncio
import platform
import shutil


class DevOpsCommands:
    async def restart_service(self, service_name: str) -> dict[str, str]:
        if platform.system().lower().startswith("win"):
            cmd = ["powershell", "-Command", f"Restart-Service -Name {service_name} -Force"]
        else:
            if not shutil.which("systemctl"):
                return {"message": "systemctl not available on this host."}
            cmd = ["systemctl", "restart", service_name]

        code, output = await self._run(cmd)
        if code != 0:
            return {"message": f"Failed to restart {service_name}: {output}"}
        return {"message": f"Service {service_name} restarted."}

    async def check_logs(self, service_name: str = "", lines: int = 100) -> dict[str, str]:
        if platform.system().lower().startswith("win"):
            if not service_name:
                return {"message": "Provide service_name for Windows event logs lookup."}
            cmd = [
                "powershell",
                "-Command",
                f"Get-EventLog -LogName Application -Newest {lines} | Where-Object {{$_.Source -like '*{service_name}*'}}",
            ]
        else:
            if not shutil.which("journalctl"):
                return {"message": "journalctl not available on this host."}
            if not service_name:
                return {"message": "Please provide a service_name."}
            cmd = ["journalctl", "-u", service_name, "-n", str(lines), "--no-pager"]

        code, output = await self._run(cmd)
        if code != 0:
            return {"message": f"Log check failed: {output}"}
        return {"message": output}

    async def _run(self, cmd: list[str]) -> tuple[int, str]:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        output = (stdout + stderr).decode("utf-8", errors="ignore").strip()
        return process.returncode, output
