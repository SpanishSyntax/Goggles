"""Tests for Goggles document discovery and recursive search."""

from pathlib import Path
from goggles.discovery import (
    discover_markdown_target,
    print_status_dashboard,
    scan_recursive_markdown,
)


import pytest


def test_print_status_dashboard(tmp_path: Path, capsys):
    (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
    (tmp_path / "notes.md").write_text("# Notes", encoding="utf-8")
    docs = print_status_dashboard(tmp_path)
    assert len(docs) == 2
    assert docs[0].name == "README.md"
    assert docs[1].name == "notes.md"
    captured = capsys.readouterr()
    assert "GOGGLES GFM DOCUMENT VIEWER" in captured.out
    assert "Active Workspace:" in captured.out


def test_discover_markdown_target_explicit(tmp_path: Path):
    doc = tmp_path / "custom.md"
    doc.write_text("# Custom", encoding="utf-8")
    found = discover_markdown_target(str(doc), base_dir=tmp_path)
    assert found == doc


def test_discover_markdown_target_no_path_exits(tmp_path: Path):
    (tmp_path / "other.md").write_text("# Other", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        discover_markdown_target(None, base_dir=tmp_path)
    assert exc_info.value.code == 1


def test_discover_markdown_target_directory_non_interactive_exits(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        discover_markdown_target(str(tmp_path), base_dir=tmp_path)
    assert exc_info.value.code == 1


def test_scan_recursive_markdown(tmp_path: Path):
    (tmp_path / "doc1.md").write_text("1", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "doc2.markdown").write_text("2", encoding="utf-8")
    node_mod = tmp_path / "node_modules"
    node_mod.mkdir()
    (node_mod / "ignored.md").write_text("3", encoding="utf-8")

    results = scan_recursive_markdown(tmp_path)
    names = [r.name for r in results]
    assert "doc1.md" in names
    assert "doc2.markdown" in names
    assert "ignored.md" not in names
