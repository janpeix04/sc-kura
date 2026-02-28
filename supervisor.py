#!/usr/bin/env python3
"""
Manages lifecycle of:
- FastAPI (uvicorn)
- Celery (worker + beat)
- SvelteKit (node build)

Features:
- Single source of truth for process specs
- Automatic restart with exponential backoff
- HTTP healthcheck to detect hangs (including C code)
- Special handling for exit code 137 (SIGKILL from watchdog)
- Clean shutdown on SIGTERM/SIGINT
"""

import asyncio
import logging
import os
import signal
import sys
import aiohttp
from dataclasses import dataclass, field

from typing import List

logging.basicConfig(
    level=logging.INFO, format="[supervisor] %(levelname)s: %(message)s"
)
logger = logging.getLogger("supervisor")

HEALTHCHECK_URL = "http://localhost:8000/healthcheck/"


@dataclass
class ProcessSpec:
    name: str
    cmd: list[str]
    cwd: str
    run_once: bool = False
    healthcheck: bool = False


@dataclass
class ManagedProcess:
    spec: ProcessSpec
    process: asyncio.subprocess.Process | None = None
    consecutive_failures: int = 0
    restart_task: asyncio.Task | None = field(default=None, repr=False)


class Supervisor:
    def __init__(
        self,
        shutdown_timeout: float = 10.0,
        max_backoff: float = 60.0,
        healthcheck_interval: float = 5.0,
        healthcheck_timeout: float = 30.0,
    ):
        self.shutdown_timeout = shutdown_timeout
        self.max_backoff = max_backoff
        self.healthcheck_interval = healthcheck_interval
        self.healthcheck_timeout = healthcheck_timeout

        self.managed: dict[str, ManagedProcess] = {}
        self._shutting_down = False

    async def run_once(self, spec: ProcessSpec) -> bool:
        """
        Run a process once and wait for completion.
        Return:
            - True if successful, otherwise, False
        """
        logger.info(f"Running {spec.name}: {' '.join(spec.cmd)}")
        proc = await asyncio.create_subprocess_exec(*spec.cmd, cwd=spec.cwd)
        exit_code = await proc.wait()
        if exit_code != 0:
            logger.critical(f"{spec.name} failed with exit code {exit_code}")
            return False
        logger.info(f"{spec.name} completed successfullt")
        return True

    async def spawn(self, spec: ProcessSpec) -> ManagedProcess:
        """
        Spawn a long-running process.
        """
        logger.info(f"Starting {spec.name}: {' '.join(spec.cmd)}")
        proc = await asyncio.create_subprocess_exec(*spec.cmd, cwd=spec.cwd)
        managed = ManagedProcess(spec=spec, process=proc)
        self.managed[spec.name] = managed
        logger.info(f"{spec.name} started (PID {proc.pid})")
        return managed

    async def watch(self, managed: ManagedProcess):
        """
        Watch a process and restart on unexpecte exit.
        """
        spec = managed.spec
        while not self._shutting_down and managed.process is not None:
            exit_code = await managed.process.wait()
            if self._shutting_down:
                return logger.info(f"{spec.name} exited during shutdown")
            if exit_code == 0:
                return logger.info(f"{spec.name} exited cleanly, not restarting")
            logger.warning(f"{spec.name} exited with code {exit_code}")
            await self._restart_with_backoff(managed, exit_code)

    async def _restart_with_backoff(self, managed: ManagedProcess, exit_code: int):
        """
        Apply exponential backoff and restart process
        """
        spec = managed.spec
        if exit_code == 137:
            managed.consecutive_failures = 0
            logger.info(f"{spec.name} killed (137), restarting immediately")
        else:
            managed.consecutive_failures += 1
            delay = min(pow(2, managed.consecutive_failures - 1), self.max_backoff)
            level = (
                logging.CRITICAL
                if managed.consecutive_failures >= 5
                else logging.WARNING
            )
            logger.log(
                level,
                f"{spec.name} failed {managed.consecutive_failures} times, "
                f"restarting in {delay:.1f}s",
            )
            await asyncio.sleep(delay)

        if self._shutting_down:
            return

        proc = await asyncio.create_subprocess_exec(*spec.cmd, cwd=spec.cwd)
        managed.process = proc
        logger.info(f"{spec.name} restarted (PID {proc.pid})")

    async def healthcheck_loop(self):
        """
        Periodically check FastAPI health, kill if unresponsive.
        """
        await asyncio.sleep(self.healthcheck_interval)

        async with aiohttp.ClientSession() as session:
            while not self._shutting_down:
                await self._do_healthcheck(session)
                await asyncio.sleep(self.healthcheck_interval)

    async def _do_healthcheck(self, session: aiohttp.ClientSession):
        """
        Single healthcheck iteration. Only timeout trigger kill.
        """
        try:
            async with session.get(
                HEALTHCHECK_URL,
                timeout=aiohttp.ClientTimeout(total=self.healthcheck_timeout),
            ) as response:
                if response.status != 200:
                    logger.warning(f"Healthcheck returned {response.status}")
        except asyncio.TimeoutError:
            logger.critical(
                f"Healthcheck timeout ({self.healthcheck_timeout}s), killing FastAPI"
            )
            await self._kill_process("fastapi")
        except aiohttp.ClientError:
            # Connection refused/reset - FastAPI is restarting, ignore
            pass
        except Exception as e:
            logger.error(f"Healthcheck error: {e}")

    async def _kill_process(self, name: str):
        """
        Send SIGKILL to a managed process
        """
        managed = self.managed.get(name)
        if not managed or not managed.process or managed.process.returncode is not None:
            return
        logger.warning(f"Sending SIGKILL to {name} (PID {managed.process.pid})")
        managed.process.kill()

    async def shutdown(self):
        """
        Gracefully shutdown all processes.
        """
        if self._shutting_down:
            return
        self._shutting_down = True
        logger.info("Shutting down all processes...")

        # Send SIGTERM to all runnning processes
        for name, managed in self.managed.items():
            if not managed.process or managed.process.returncode is not None:
                continue
            logger.info(f"Sending SIGTERM to {name} (PID {managed.process.pid})")
            managed.process.terminate()

        # Wait with timeout, then SIGKILL
        await asyncio.gather(
            *[
                self._wait_or_kill(name, managed)
                for name, managed in self.managed.items()
            ]
        )
        logger.info("All processes stopped")

    async def _wait_or_kill(self, name: str, managed: ManagedProcess):
        """
        Wait for process to exit, kill if timeout
        """
        if not managed.process:
            return
        try:
            await asyncio.wait_for(
                managed.process.wait(), timeout=self.shutdown_timeout
            )
            logger.info(f"{name} exited gracefully")
        except asyncio.TimeoutError:
            logger.warning(f"{name} didn't exit in time, sending SIGKILL")
            managed.process.kill()
            await managed.process.wait()


def get_process_specs() -> List[ProcessSpec]:
    """
    Process specifications (single source of truth)
    """
    return [
        ProcessSpec(
            name="alembic",
            cmd=["uv", "run", "--no-dev", "alembic", "upgrade", "head"],
            cwd="/workspace",
            run_once=True,
        ),
        ProcessSpec(
            name="celery-worker",
            cmd=[
                "uv",
                "run",
                "--no-dev",
                "celery",
                "-A",
                "app.celery:app",
                "worker",
                "--concurrency=4",
                "--loglevel=INFO",
            ],
            cwd="/workspace",
        ),
        ProcessSpec(
            name="celery-beat",
            cmd=[
                "uv",
                "run",
                "--no-dev",
                "celery",
                "-A",
                "app.celery:app",
                "beat",
                "--loglevel=INFO",
            ],
            cwd="/workspace",
        ),
        ProcessSpec(
            name="fastapi",
            cmd=[
                "uv",
                "run",
                "--no-dev",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--workers",
                "1",
            ],
            cwd="/workspace",
            healthcheck=True,
        ),
        ProcessSpec(name="node", cmd=["node", "build"], cwd="/workspace/frontend"),
    ]


async def main():
    shutdown_timeout = float(os.getenv("SUPERVISOR_SHUTDOWN_TIMEOUT", "10.0"))
    max_backoff = float(os.getenv("SUPERVISOR_MAX_BACKOFF", "60.0"))
    healthcheck_interval = float(os.getenv("SUPERVISOR_HEALTHCHECK_INTERVAL", "5.0"))
    healthcheck_timeout = float(os.getenv("SUPERVISOR_HEALTHCHECK_TIMEOUT", "30.0"))

    logger.info(
        f"Starting supervisor (shutdown={shutdown_timeout}s, "
        f"healthcheck_interval={healthcheck_interval}s, "
        f"healthcheck_timeout={healthcheck_timeout}s)"
    )

    supervisor = Supervisor(
        shutdown_timeout=shutdown_timeout,
        max_backoff=max_backoff,
        healthcheck_interval=healthcheck_interval,
        healthcheck_timeout=healthcheck_timeout,
    )

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(supervisor.shutdown()))

    specs = get_process_specs()

    # Run setup tasks (alembic)
    for spec in specs:
        if spec.run_once:
            if not await supervisor.run_once(spec):
                sys.exit(1)

    # Spawn long-running processes
    watch_tasks = []
    for spec in specs:
        if not spec.run_once:
            managed = await supervisor.spawn(spec)
            watch_tasks.append(asyncio.create_task(supervisor.watch(managed)))

    # Start healthcheck
    healthcheck_task = asyncio.create_task(supervisor.healthcheck_loop())

    # Wait for shutdown
    await asyncio.gather(*watch_tasks, healthcheck_task, return_exceptions=True)

    logger.info("Supervisor exited")


if __name__ == "__main__":
    asyncio.run(main())
