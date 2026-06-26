#!/usr/bin/env python3
"""Small MCP/JSON-RPC response helpers for the AI-control adapter."""

from __future__ import annotations

import json
from typing import Any


def mcp_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def mcp_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def bridge_text_result(response: dict[str, Any]) -> dict[str, Any]:
    is_error = "error" in response
    payload = response.get("error") if is_error else response.get("result", response)
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ],
        "isError": is_error,
    }

