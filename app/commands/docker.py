import asyncio
import shutil


class DockerCommands:
    async def status(self) -> dict[str, str]:
        if not shutil.which("docker"):
            return {"message": "Docker CLI is not installed."}
        code, output = await self._run(["docker", "compose", "ps"])
        if code != 0:
            return {"message": f"docker compose ps failed: {output}"}
        return {"message": output}

    async def logs(self, service: str = "", tail: int = 100) -> dict[str, str]:
        if not shutil.which("docker"):
            return {"message": "Docker CLI is not installed."}

        cmd = ["docker", "logs", f"--tail={tail}"]
        if service:
            cmd.append(service)
        else:
            return {"message": "Please provide container/service name for docker logs."}

        code, output = await self._run(cmd)
        if code != 0:
            return {"message": f"docker logs failed: {output}"}
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
