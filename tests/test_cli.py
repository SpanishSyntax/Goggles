"""Tests for Goggles CLI argument parsing and flags."""

from goggles import __version__
from goggles.cli import main, run_interactive_hub
from goggles.ui import ui


def test_cli_version(capsys):
    ret = main(["--version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert f"v{__version__}" in captured.out


def test_cli_help(capsys):
    ret = main(["--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Instant GitHub-Flavored Markdown" in captured.out


def test_cli_raw_no_args(capsys):
    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Instant GitHub-Flavored Markdown" in captured.out
    assert "Usage:" in captured.out


def test_cli_flags_without_path(capsys):
    ret = main(["--dark"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "No Markdown document specified" in captured.err


def test_interactive_hub_exit(monkeypatch):
    monkeypatch.setattr(ui, "select", lambda prompt, options: "exit")
    ret = run_interactive_hub([], {})
    assert ret == 0


def test_interactive_hub_help(monkeypatch, capsys):
    monkeypatch.setattr(ui, "select", lambda prompt, options: "help")
    ret = run_interactive_hub([], {})
    assert ret == 0
    captured = capsys.readouterr()
    assert "Instant GitHub-Flavored Markdown" in captured.out


def test_interactive_hub_prompt_nonexistent(monkeypatch, capsys):
    monkeypatch.setattr(ui, "select", lambda prompt, options: "prompt")
    monkeypatch.setattr(ui, "prompt", lambda msg: "nonexistent_file.md")
    ret = run_interactive_hub([], {})
    assert ret == 1
    captured = capsys.readouterr()
    assert "File 'nonexistent_file.md' not found." in captured.err


def test_interactive_hub_prompt_empty(monkeypatch):
    monkeypatch.setattr(ui, "select", lambda prompt, options: "prompt")
    monkeypatch.setattr(ui, "prompt", lambda msg: "   ")
    ret = run_interactive_hub([], {})
    assert ret == 0

