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


def test_cli_debug_flag_config(tmp_path):
    from goggles.cli import _build_parser, _build_render_config

    test_file = tmp_path / "doc.md"
    test_file.write_text("# Hello")

    parser = _build_parser({})
    args_default = parser.parse_args([str(test_file)])
    cfg_default = _build_render_config(test_file, {}, args_default)
    assert cfg_default.debug is False

    args_debug = parser.parse_args([str(test_file), "--debug"])
    cfg_debug = _build_render_config(test_file, {}, args_debug)
    assert cfg_debug.debug is True


def test_launch_viewer_exception_formatting(tmp_path, monkeypatch, capsys):
    from goggles.cli import launch_document_viewer
    from goggles.core import RenderConfig
    import goggles.cli as cli_mod

    test_file = tmp_path / "doc.md"
    test_file.write_text("# Test")

    def mock_fail(*args, **kwargs):
        raise RuntimeError("Simulated GTK failure")

    monkeypatch.setattr(cli_mod, "launch_viewer", mock_fail)

    # 1. Without debug
    cfg_normal = RenderConfig(target_path=test_file, debug=False)
    ret = launch_document_viewer(test_file, cfg_normal)
    assert ret == 1
    err_normal = capsys.readouterr().err
    assert "Simulated GTK failure" in err_normal
    assert "Tip: Run with" in err_normal
    assert "--debug" in err_normal
    assert "Traceback (most recent call last):" not in err_normal

    # 2. With debug
    cfg_debug = RenderConfig(target_path=test_file, debug=True)
    ret = launch_document_viewer(test_file, cfg_debug)
    assert ret == 1
    err_debug = capsys.readouterr().err
    assert "Simulated GTK failure" in err_debug
    assert "Traceback (most recent call last):" in err_debug


