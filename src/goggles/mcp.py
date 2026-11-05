"""Model Context Protocol (MCP) stdio server for Goggles."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from goggles import __version__

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "goggles_view",
        "description": "Opens a GitHub-Flavored Markdown (GFM) document in an isolated native desktop viewer window via Goggles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the Markdown document to preview.",
                },
                "port": {
                    "type": "integer",
                    "description": "Explicit localhost port to bind (default: 0 for auto ephemeral port).",
                    "default": 0,
                },
                "github_mode": {
                    "type": "boolean",
                    "description": "Render with full GitHub repository Box chrome (default: true).",
                    "default": True,
                },
                "theme": {
                    "type": "string",
                    "description": "Viewer color theme: 'auto', 'dark', 'light' (default: 'auto').",
                    "default": "auto",
                },
            },
            "required": ["path"],
        },
    }
]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Goggles MCP tool call and return JSON-serializable results."""
    try:
        if name == "goggles_view":
            raw_path = arguments.get("path")
            if not raw_path or not str(raw_path).strip():
                return {"status": "error", "error": "Missing required argument 'path'."}

            port = int(arguments.get("port", 0))
            github_mode = bool(arguments.get("github_mode", True))
            theme = str(arguments.get("theme", "auto")).strip().lower()
            if theme not in ("auto", "dark", "light"):
                theme = "auto"

            target = Path(raw_path).expanduser().resolve()
            if not target.is_file():
                if target.is_dir():
                    try:
                        from goggles.discovery import discover_markdown_target

                        target = discover_markdown_target(raw_path)
                    except (Exception, SystemExit):
                        return {
                            "status": "error",
                            "error": f"Markdown document not found in directory: {raw_path}",
                        }
                else:
                    return {
                        "status": "error",
                        "error": f"Markdown document not found: {raw_path}",
                    }

            if not target.is_file():
                return {
                    "status": "error",
                    "error": f"Markdown document not found: {target}",
                }

            cmd = [sys.executable, "-m", "goggles", str(target), "--no-color"]
            if port > 0:
                cmd.extend(["-p", str(port)])
            if github_mode:
                cmd.append("-g")
            if theme in ("dark", "light"):
                cmd.extend(["--theme", theme])

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            return {
                "status": "ok",
                "pid": proc.pid,
                "document": str(target),
                "port": port,
                "github_mode": github_mode,
                "theme": theme,
            }
        else:
            return {"status": "error", "error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


class StdioMCPServer:
    """JSON-RPC 2.0 stdio server implementing the Model Context Protocol."""

    def __init__(self) -> None:
        self.server_info = {"name": "goggles", "version": __version__}

    def handle_request(self, req: dict[str, Any]) -> dict[str, Any] | None:
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {"tools": {}},
                },
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOL_DEFINITIONS},
            }

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name", "")
            args = params.get("arguments", {})
            res = execute_tool(name, args)
            is_error = res.get("status") == "error"

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": is_error,
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    def run(self) -> None:
        """Run JSON-RPC event loop reading lines from sys.stdin."""
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
