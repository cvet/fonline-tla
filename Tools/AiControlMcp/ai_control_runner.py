#!/usr/bin/env python3
"""Shared MCP client library and helpers for the smoke test and live playtest runners.

This module owns the low-level client primitive (`McpProcess`) and the JSON-RPC/observation
helpers used to drive the `ai_control_mcp.py` adapter. The smoke test and every `*_playtest.py`
runner are clients of this library; they must not redefine the primitive themselves.
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

MCP_VERSION = "2025-11-25"
ADAPTER_PATH = Path(__file__).with_name("ai_control_mcp.py")


def configure_stdio() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


class SmokeError(RuntimeError):
    pass


class McpProcess:
    def __init__(self, command: list[str], request_timeout: float = 180.0) -> None:
        self._next_id = 1
        self._request_timeout = request_timeout
        self._process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self._stdout_lines: queue.Queue[str | None] = queue.Queue()
        self._stderr_lines: queue.Queue[str | None] = queue.Queue()
        self._stdout_thread = threading.Thread(target=self._read_pipe, args=(self._process.stdout, self._stdout_lines), daemon=True)
        self._stderr_thread = threading.Thread(target=self._read_pipe, args=(self._process.stderr, self._stderr_lines), daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        self._write(request)
        request_timeout = getattr(self, "_request_timeout", 180.0)
        deadline = time.monotonic() + request_timeout

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0.0:
                if self._process.poll() is not None:
                    raise SmokeError(f"Adapter exited with code {self._process.returncode} while waiting for {method}")
                raise SmokeError(f"Adapter response timeout after {request_timeout:.1f}s for {method}")

            if hasattr(self, "_stdout_lines"):
                try:
                    line = self._stdout_lines.get(timeout=remaining)
                except queue.Empty:
                    if self._process.poll() is not None:
                        raise SmokeError(f"Adapter exited with code {self._process.returncode} while waiting for {method}")
                    raise SmokeError(f"Adapter response timeout after {request_timeout:.1f}s for {method}")
            else:
                if self._process.stdout is None:
                    raise SmokeError("Adapter stdout is closed")
                line = self._process.stdout.readline()

            if line is None:
                raise SmokeError("Adapter closed stdout before returning a response")
            if not line:
                raise SmokeError("Adapter closed stdout before returning a response")

            response = json.loads(line)
            response_id = response.get("id")
            if response_id is None:
                continue
            if response_id != request_id:
                raise SmokeError(f"Unexpected MCP response id: {response_id} != {request_id}")
            return response

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        self._write({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def close(self) -> None:
        if self._process.stdin is not None:
            self._process.stdin.close()

        try:
            self._process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            self._process.terminate()
            try:
                self._process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2.0)

    def _write(self, request: dict[str, Any]) -> None:
        if self._process.poll() is not None:
            raise SmokeError(f"Adapter exited with code {self._process.returncode}")
        if self._process.stdin is None:
            raise SmokeError("Adapter stdin is closed")

        self._process.stdin.write(json.dumps(request, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._process.stdin.flush()

    @staticmethod
    def _read_pipe(pipe: Any, lines: queue.Queue[str | None]) -> None:
        if pipe is None:
            lines.put(None)
            return

        try:
            for line in pipe:
                lines.put(line)
        finally:
            lines.put(None)


def require_result(response: dict[str, Any], label: str) -> dict[str, Any]:
    if "error" in response:
        raise SmokeError(f"{label} failed: {json.dumps(response['error'], ensure_ascii=False)}")
    result = response.get("result")
    if not isinstance(result, dict):
        raise SmokeError(f"{label} returned no result object")
    return result


def tool_payload(client: McpProcess, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    result = require_result(client.request("tools/call", {"name": name, "arguments": arguments or {}}), name)
    content = result.get("content")
    if not isinstance(content, list) or not content:
        raise SmokeError(f"{name} returned no text content")

    text = content[0].get("text")
    if not isinstance(text, str):
        raise SmokeError(f"{name} returned non-text content")

    payload = json.loads(text)
    if result.get("isError"):
        raise SmokeError(f"{name} bridge error: {json.dumps(payload, ensure_ascii=False)}")
    if not isinstance(payload, dict):
        raise SmokeError(f"{name} returned non-object payload")
    return payload


def unwrap_observation_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        observation = payload.get("observation")
        if isinstance(observation, dict):
            return unwrap_observation_payload(observation)
        return payload
    return {}


def wait_observation_snapshot(client: McpProcess, timeout: float, poll_interval: float = 0.1) -> dict[str, Any]:
    deadline = time.monotonic() + max(timeout, 0.0)
    last_payload: dict[str, Any] = {}

    while True:
        last_payload = tool_payload(client, "tla_observe")
        snapshot = unwrap_observation_payload(last_payload)
        if "schemaVersion" in snapshot:
            return snapshot
        if time.monotonic() >= deadline:
            break
        time.sleep(max(poll_interval, 0.01))

    raise SmokeError(f"tla_observe did not return an observation schema version before timeout; last payload: {json.dumps(last_payload, ensure_ascii=False)}")


def build_adapter_command(adapter_path: Path, host: str, port: int, timeout: int | float | str, token: str | None = None) -> list[str]:
    command = [sys.executable, str(adapter_path), "--host", host, "--port", str(port), "--timeout", str(timeout)]
    if token:
        command.extend(["--token", token])
    return command


def initialize_client(client: McpProcess, client_name: str, version: str = "0.1.0") -> None:
    require_result(
        client.request(
            "initialize",
            {
                "protocolVersion": MCP_VERSION,
                "capabilities": {},
                "clientInfo": {"name": client_name, "version": version},
            },
        ),
        "initialize",
    )
    client.notify("notifications/initialized")


def call_tool(client: McpProcess, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    return tool_payload(client, name, arguments or {})


def endpoint_args(endpoint: dict[str, Any]) -> dict[str, Any]:
    return {"endpointId": str(endpoint["endpointId"])}


def observe(client: McpProcess, endpoint: dict[str, Any] | None = None) -> dict[str, Any]:
    return unwrap_observation_payload(call_tool(client, "tla_observe", endpoint or {}))


def read_log_text(client: McpProcess, process_id: int, lines: int) -> str:
    payload = call_tool(client, "tla_logs", {"processId": process_id, "lines": lines})
    return str(payload.get("text", ""))


def stripped_log_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def matching_log_lines(lines: list[str], markers: tuple[str, ...], limit: int | None = None, tail: bool = False) -> list[str]:
    matches = [line for line in lines if any(marker in line for marker in markers)]
    if limit is None:
        return matches
    return matches[-limit:] if tail else matches[:limit]


def wait_ready(
    client: McpProcess,
    endpoint: dict[str, Any],
    timeout_ms: int,
    require_map: bool = False,
    require_chosen: bool = False,
    poll_interval_ms: int = 250,
) -> None:
    ready = call_tool(
        client,
        "tla_wait_ready",
        {
            **endpoint,
            "requireMap": require_map,
            "requireChosen": require_chosen,
            "timeoutMs": timeout_ms,
            "pollIntervalMs": poll_interval_ms,
        },
    )
    if not ready.get("ready"):
        raise SmokeError(f"endpoint not ready: {ready.get('missing')}")


def command_args(
    endpoint: dict[str, Any],
    arguments: dict[str, Any] | None = None,
    wait: bool = True,
    timeout_ms: int = 20000,
    poll_interval_ms: int = 150,
    sync_after_completion: bool | None = None,
    include_observation: bool = False,
) -> dict[str, Any]:
    result = dict(arguments or {})
    result.update(endpoint)
    result.setdefault("waitForCompletion", wait)
    result.setdefault("timeoutMs", timeout_ms)
    result.setdefault("pollIntervalMs", poll_interval_ms)
    result.setdefault("syncAfterCompletion", wait if sync_after_completion is None else sync_after_completion)
    result.setdefault("includeObservation", include_observation)
    return result


def verify_command_payload(payload: dict[str, Any], label: str, rejected_text: str = "rejected", failed_text: str = "failed") -> None:
    if payload.get("success") is False:
        raise SmokeError(f"{label} {rejected_text}: {payload.get('message')}")

    completion = payload.get("completion")
    if isinstance(completion, dict) and completion.get("completed") is False:
        raise SmokeError(f"{label} did not complete before timeout")

    event = completion.get("event") if isinstance(completion, dict) else {}
    if isinstance(event, dict) and event.get("success") is False:
        raise SmokeError(f"{label} {failed_text}: {event.get('message')}")


def run_command(
    client: McpProcess,
    tool: str,
    endpoint: dict[str, Any],
    arguments: dict[str, Any] | None = None,
    wait: bool = True,
    timeout_ms: int = 20000,
    poll_interval_ms: int = 150,
    sync_after_completion: bool | None = None,
    include_observation: bool = False,
    label: str | None = None,
    rejected_text: str = "rejected",
    failed_text: str = "failed",
) -> dict[str, Any]:
    payload = call_tool(
        client,
        tool,
        command_args(
            endpoint,
            arguments,
            wait,
            timeout_ms,
            poll_interval_ms,
            sync_after_completion,
            include_observation,
        ),
    )
    verify_command_payload(payload, label or tool, rejected_text, failed_text)
    return payload


def active_modal(observation: dict[str, Any]) -> bool:
    screen = observation.get("screen") if isinstance(observation.get("screen"), dict) else {}
    return bool(screen.get("modalActive"))


def active_screen_name(observation: dict[str, Any]) -> str:
    screen = observation.get("screen") if isinstance(observation.get("screen"), dict) else {}
    return str(screen.get("activeModal") or screen.get("active") or "")


def write_json_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_markdown_lines(path: Path, lines: list[str]) -> None:
    write_text_report(path, "\n".join(lines) + "\n")
