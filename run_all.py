#!/usr/bin/env python3
"""Unified launcher for Majestic RP legal portal services."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class ProcessGroup:
    def __init__(self) -> None:
        self.processes: list[subprocess.Popen] = []

    def start(self, cmd: list[str], name: str) -> None:
        process = subprocess.Popen(cmd, cwd=ROOT)
        self.processes.append(process)
        print(f"[STARTED] {name} (pid={process.pid})")

    def stop_all(self) -> None:
        for process in self.processes:
            if process.poll() is None:
                process.terminate()

        deadline = time.time() + 5
        for process in self.processes:
            while process.poll() is None and time.time() < deadline:
                time.sleep(0.1)

        for process in self.processes:
            if process.poll() is None:
                process.kill()

    def wait(self) -> int:
        while True:
            for process in self.processes:
                code = process.poll()
                if code is not None:
                    return code
            time.sleep(0.2)


def require_file(path: Path, message: str) -> None:
    if not path.exists():
        print(f"[ERROR] {message}: {path}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Majestic RP web server and Telegram bot from one Python file."
    )
    parser.add_argument(
        "--mode",
        choices=["all", "web", "bot"],
        default="all",
        help="What to run: website only, bot only, or both (default: all).",
    )
    args = parser.parse_args()

    require_file(ROOT / "web_server.py", "Missing Python web server file")
    require_file(ROOT / "bot" / "bot.py", "Missing Telegram bot file")

    if args.mode in {"all", "bot"} and not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("[WARNING] TELEGRAM_BOT_TOKEN is empty. Bot will fail until token is set.")

    procs = ProcessGroup()

    def handle_signal(signum: int, _frame: object) -> None:
        print(f"\n[INFO] Received signal {signum}. Stopping services...")
        procs.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if args.mode in {"all", "web"}:
        procs.start([sys.executable, "web_server.py"], "Web server")

    if args.mode in {"all", "bot"}:
        procs.start([sys.executable, "bot/bot.py"], "Telegram bot")

    if not procs.processes:
        print("[ERROR] Nothing to run.")
        sys.exit(1)

    print(f"[INFO] Launcher mode: {args.mode}. Press Ctrl+C to stop.")

    exit_code = procs.wait()
    print(f"[INFO] A child process exited with code {exit_code}. Stopping all...")
    procs.stop_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
