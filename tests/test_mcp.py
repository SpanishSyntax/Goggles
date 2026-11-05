"""Unit tests for Goggles Model Context Protocol (MCP) server."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from goggles.mcp import StdioMCPServer, TOOL_DEFINITIONS, execute_tool


def test_mcp_initialize() -> None:
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-agent", "version": "1.0"},
        },
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "goggles"
    assert resp["result"]["protocolVersion"] == "2024-11-05"


def test_mcp_tools_list() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = server.handle_request(req)
    assert resp is not None
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "goggles_view" in tool_names

    tool = next(t for t in tools if t["name"] == "goggles_view")
    props = tool["inputSchema"]["properties"]
    assert "path" in props
    assert "port" in props
    assert "github_mode" in props
    assert "theme" in props
    assert "path" in tool["inputSchema"]["required"]


def test_mcp_ping() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 3, "method": "ping"}
    resp = server.handle_request(req)
    assert resp == {"jsonrpc": "2.0", "id": 3, "result": {}}


def test_mcp_unknown_method() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 4, "method": "unknown/method"}
    resp = server.handle_request(req)
    assert resp is not None
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_execute_goggles_view_missing_path() -> None:
    res = execute_tool("goggles_view", {})
    assert res["status"] == "error"
    assert "Missing required argument" in res["error"]


def test_execute_goggles_view_nonexistent_file() -> None:
    res = execute_tool("goggles_view", {"path": "/nonexistent/path/readme.md"})
    assert res["status"] == "error"
    assert "not found" in res["error"]


def test_execute_goggles_view_success(tmp_path: Path) -> None:
    doc = tmp_path / "test.md"
    doc.write_text("# Hello Markdown")

    mock_proc = MagicMock()
    mock_proc.pid = 99999

    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
        res = execute_tool(
            "goggles_view",
            {
                "path": str(doc),
                "port": 5000,
                "github_mode": True,
                "theme": "dark",
            },
        )
        assert res["status"] == "ok"
        assert res["pid"] == 99999
        assert res["port"] == 5000
        assert res["github_mode"] is True
        assert res["theme"] == "dark"
        assert res["document"] == str(doc.resolve())

        mock_popen.assert_called_once()
        cmd = mock_popen.call_args[0][0]
        assert str(doc.resolve()) in cmd
        assert "-p" in cmd
        assert "5000" in cmd
        assert "-g" in cmd
        assert "--theme" in cmd
        assert "dark" in cmd


def test_execute_unknown_tool() -> None:
    res = execute_tool("nonexistent_tool", {})
    assert res["status"] == "error"
    assert "Unknown tool" in res["error"]


def test_mcp_tools_call_handler(tmp_path: Path) -> None:
    doc = tmp_path / "notes.md"
    doc.write_text("Notes")

    mock_proc = MagicMock()
    mock_proc.pid = 12345

    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "goggles_view",
            "arguments": {
                "path": str(doc),
            },
        },
    }

    with patch("subprocess.Popen", return_value=mock_proc):
        resp = server.handle_request(req)
        assert resp is not None
        assert resp["id"] == 10
        content = resp["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        parsed = json.loads(content[0]["text"])
        assert parsed["status"] == "ok"
        assert parsed["pid"] == 12345
