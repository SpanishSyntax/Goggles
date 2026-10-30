"""CLI router, argument parser, and desktop application launcher for Goggles."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import traceback
from typing import Any, Sequence

from goggles import __version__
from goggles.config import load_user_config
from goggles.core import (
    GripOrchestrator,
    GripStartupError,
    RenderConfig,
    find_ephemeral_port,
    resolve_github_token,
)
from goggles.discovery import (
    discover_markdown_target,
    print_status_dashboard,
    scan_recursive_markdown,
)
from goggles.ui import add_color_args, handle_color_args, ui
from goggles.viewer import launch_viewer

__all__ = [
    "main",
    "discover_markdown_target",
    "scan_recursive_markdown",
    "print_status_dashboard",
    "run_interactive_hub",
    "launch_document_viewer",
    "clear_grip_cache",
    "load_user_config",
    "find_ephemeral_port",
    "resolve_github_token",
    "RenderConfig",
    "GripOrchestrator",
    "launch_viewer",
]


def clear_grip_cache() -> int:
    """Invokes grip to clear locally cached GitHub styling assets."""
    with ui.spinner("Clearing local grip cached assets...") as sp:
        try:
            res = subprocess.run(
                ["grip", "--clear"],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                sp.stop("Successfully cleared grip cached styles.", ok=True)
                return 0
            else:
                sp.stop("Failed to clear grip cache.", ok=False)
                ui.error_panel(
                    "Failed to Clear Cache",
                    res.stderr.strip() or "Unknown grip error.",
                )
                return 1
        except Exception as exc:
            sp.stop("Error executing grip.", ok=False)
            ui.error(f"Cannot run grip: {exc}")
            return 1


def print_help() -> None:
    """Prints colored usage instructions matching Flaker, Glaze, Folio, and Borealis."""
    if ui.is_agent:
        print(f"""Goggles v{__version__} - Instant GFM Native Desktop Markdown Viewer
Usage: goggles <path-to-markdown> [options]
       goggles [options]

Options:
  -A, --agent            Compact machine/agent friendly output mode
  --json                 Structured JSON output mode
  -p, --port PORT        Bind specific localhost port
  --host HOST            Bind address for grip daemon
  -g, --github-mode      Render with GitHub repository Box chrome & page layout
  -w, --wide             Render wide GitHub document container
  -u, --user-content     Render as GitHub user-content
  -c, --context REPO     Repository context for autolinks
  -t, --title TITLE      Override window title
  --theme MODE           Viewer color theme: auto, dark, light
  --frameless            Launch in a frameless minimal native window
  --width PX             Initial window width in pixels
  --height PX            Initial window height in pixels
  --clear-cache          Clear cached GitHub CSS assets via `grip --clear`
  --color MODE           Color output mode: auto, always, never
  --no-color             Disable colored output
  -h, --help             Show this help message and exit
  -V, -v, --version      Show version information and exit
""")
        return

    print(f"""{ui.badge()} {ui.bold("Instant GitHub-Flavored Markdown (GFM) Native Desktop Viewer")}

{ui.blue("Usage:")}
  goggles                                Open interactive dashboard & document picker
  goggles <path-to-markdown> [options]   Directly preview Markdown document
  goggles <directory> [options]          Select *.md interactively within directory

{ui.blue("Options:")}
  -p, --port PORT        Bind specific localhost port (default: random ephemeral port)
  --host HOST            Bind address for grip daemon (default: 127.0.0.1)
  -g, --github-mode      Render with GitHub repository Box chrome & page layout
  -w, --wide             Render wide GitHub document container (--wide)
  -u, --user-content     Render as GitHub user-content (issues/comments mode)
  -c, --context REPO     Repository context (e.g. SpanishSyntax/Goggles) for autolinks
  -t, --title TITLE      Override window title (default: "Goggles: <filename>")
  --theme MODE           Viewer color theme: auto, dark, light (default: auto)
  --dark / --light       Shortcut for --theme=dark / --theme=light
  --frameless            Launch in a frameless minimal native window
  --width PX             Initial window width in pixels (default: 980)
  --height PX            Initial window height in pixels (default: 860)
  --token TOKEN          Explicit GitHub Personal Access Token (or set GITHUB_TOKEN)
  --pass-path ENTRY      Password-store (`pass`) entry for GitHub token
  --api-url URL          Custom GitHub API base URL
  --inline               Inline CSS styles instead of passing --no-inline to grip
  --clear-cache          Clear cached GitHub CSS assets via `grip --clear` and exit
  --debug                Enable WebKit inspector / developer tools in viewer window
  --color MODE           Color output mode: auto, always, never (default: auto)
  --no-color             Disable colored terminal output
  -h, --help             Show this help message and exit
  -V, -v, --version      Show version information and exit

{ui.blue("Examples:")}
  goggles                                # Launch interactive dashboard & document picker
  goggles README.md                      # Open README.md in native WebKitGTK window
  goggles README.md -g                   # Open with full GitHub repository Box layout
  goggles docs/architecture.md --dark    # Render in GitHub Dark mode
  goggles SPEC.md --frameless --wide     # Frameless wide native window
  goggles docs/                          # Interactively select Markdown file in directory
""")


def _build_parser(user_cfg: dict[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="goggles", add_help=False)
    parser.add_argument("path", nargs="?", default=None, help="Path to Markdown document to preview.")
    parser.add_argument("-p", "--port", type=int, default=int(user_cfg.get("port", 0)), help="Local port.")
    parser.add_argument("--host", default=str(user_cfg.get("host", "127.0.0.1")), help="Local host.")
    parser.add_argument("-g", "--github-mode", "--github", dest="github_mode", action="store_true", default=bool(user_cfg.get("github_mode", False)))
    parser.add_argument("-w", "--wide", action="store_true", default=bool(user_cfg.get("wide", False)))
    parser.add_argument("-u", "--user-content", action="store_true", default=bool(user_cfg.get("user_content", False)))
    parser.add_argument("-c", "--context", default=user_cfg.get("context"))
    parser.add_argument("-t", "--title", default=user_cfg.get("title"))
    parser.add_argument("--theme", choices=["auto", "dark", "light"], default=str(user_cfg.get("theme", "auto")))
    parser.add_argument("--dark", dest="theme", action="store_const", const="dark")
    parser.add_argument("--light", dest="theme", action="store_const", const="light")
    parser.add_argument("--frameless", action="store_true", default=bool(user_cfg.get("frameless", False)))
    parser.add_argument("--width", type=int, default=int(user_cfg.get("width", 980)))
    parser.add_argument("--height", type=int, default=int(user_cfg.get("height", 860)))
    parser.add_argument("--token", default=user_cfg.get("token"))
    parser.add_argument("--pass-path", default=user_cfg.get("pass_path"))
    parser.add_argument("--api-url", default=user_cfg.get("api_url"))
    parser.add_argument("--inline", dest="no_inline", action="store_false", default=bool(user_cfg.get("no_inline", True)))
    parser.add_argument("--no-inline", dest="no_inline", action="store_true")
    parser.add_argument("--clear-cache", action="store_true")
    parser.add_argument("--debug", action="store_true", default=bool(user_cfg.get("debug", False)))
    add_color_args(parser)
    return parser


def _build_render_config(
    target_md: Path,
    user_cfg: dict[str, Any],
    args: argparse.Namespace | None = None,
) -> RenderConfig:
    """Builds a RenderConfig dataclass from CLI arguments or configuration defaults."""
    return RenderConfig(
        target_path=target_md,
        host=args.host if args else str(user_cfg.get("host", "127.0.0.1")),
        port=args.port if args else int(user_cfg.get("port", 0)),
        wide=args.wide if args else bool(user_cfg.get("wide", False)),
        user_content=args.user_content if args else bool(user_cfg.get("user_content", False)),
        context=args.context if args else user_cfg.get("context"),
        title=args.title if args else user_cfg.get("title"),
        api_url=args.api_url if args else user_cfg.get("api_url"),
        token=args.token if args else user_cfg.get("token"),
        pass_path=args.pass_path if args else user_cfg.get("pass_path"),
        no_inline=args.no_inline if args else bool(user_cfg.get("no_inline", True)),
        frameless=args.frameless if args else bool(user_cfg.get("frameless", False)),
        github_mode=args.github_mode if args else bool(user_cfg.get("github_mode", False)),
        theme=args.theme if args else str(user_cfg.get("theme", "auto")),
        width=args.width if args else int(user_cfg.get("width", 980)),
        height=args.height if args else int(user_cfg.get("height", 860)),
        debug=args.debug if args else bool(user_cfg.get("debug", False)),
    )


def launch_document_viewer(target_md: Path, config: RenderConfig) -> int:
    """Spawns the local Grip daemon and launches the native WebKitGTK viewer window."""
    mode_str = "GitHub Box" if config.github_mode else "GFM Standard"
    theme_str = config.theme.capitalize()
    frame_str = "Frameless" if config.frameless else f"{config.width}x{config.height}"
    lines = [
        f"{ui.bold('Target Document:')}  {ui.cyan(str(target_md))} ({target_md.stat().st_size:,} bytes)",
        f"{ui.bold('Viewer Mode:')}      {ui.green(mode_str)} | Theme: {ui.magenta(theme_str)} | Window: {frame_str}",
        f"{ui.bold('Rendering Engine:')} Grip (Local WebKit / PyWebView runtime)",
    ]
    ui.panel("GOGGLES GFM DOCUMENT VIEWER", lines)

    orchestrator = GripOrchestrator(config)
    try:
        orchestrator.start()
        launch_viewer(orchestrator, config)
    except GripStartupError as exc:
        ui.error_panel(
            "Grip Engine Failed to Start",
            [
                *str(exc).splitlines(),
                "",
                "Tip: Set GITHUB_TOKEN or store a token in `pass` (github/token) to avoid rate limits.",
            ],
        )
        return 1
    except KeyboardInterrupt:
        print()
        orchestrator.stop()
        return 0
    except SystemExit as exc:
        orchestrator.stop()
        return exc.code if isinstance(exc.code, int) else 0
    except Exception as exc:
        orchestrator.stop()
        exc_type = type(exc).__name__
        err_msg = str(exc)
        panel_lines = [
            f"{ui.bold('Exception:')} {ui.red(exc_type)}",
            f"{err_msg}",
        ]
        if os.environ.get("LD_LIBRARY_PATH"):
            panel_lines.append("")
            panel_lines.append(
                f"{ui.yellow('Warning:')} LD_LIBRARY_PATH is active in your environment, which can cause GLib/GTK symbol collisions."
            )
        if not config.debug:
            panel_lines.append("")
            panel_lines.append(
                f"Tip: Run with {ui.cyan('--debug')} to display the full Python stack trace."
            )
        ui.error_panel("Viewer Runtime Error", panel_lines)
        if config.debug:
            sys.stderr.write(f"\n{ui.bold('Traceback (most recent call last):')}\n")
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
        return 1
    return 0


def run_interactive_hub(
    docs: list[Path],
    user_cfg: dict[str, Any],
    args: argparse.Namespace | None = None,
) -> int:
    """Interactive Quick Actions menu matching Snowpack, Borealis, and Barograph."""
    actions: list[tuple[str, str, str]] = []

    if docs:
        actions.append(
            (
                "select",
                "Select Discovered Document to Preview...",
                f"Choose from {len(docs)} Markdown file(s) in active workspace",
            )
        )

    actions.append(
        (
            "scan",
            "Search Workspace Subdirectories Recursively (*.md)...",
            "Scan workspace tree for nested Markdown documents",
        )
    )
    actions.append(
        (
            "prompt",
            "Open Document by Custom Path...",
            "Prompt for explicit relative or absolute file path",
        )
    )
    actions.append(
        (
            "cache",
            "Clear Grip Cached Primer CSS Assets",
            "Invoke `grip --clear` to refresh local GitHub asset cache",
        )
    )
    actions.append(
        (
            "help",
            "Open Help",
            "Print comprehensive CLI usage guide and viewer keybindings",
        )
    )
    actions.append(("exit", "Exit", "Close Goggles"))

    choice = ui.select("Goggles Quick Actions:", actions)

    if choice == "exit":
        return 0
    elif choice == "help":
        print_help()
        return 0
    elif choice == "cache":
        return clear_grip_cache()
    elif choice == "select" and docs:
        options = [
            (str(f.resolve()), f"📄 {f.name}", f"{f.stat().st_size:,} bytes")
            for f in docs
        ]
        chosen = ui.select("Select Markdown document to open:", options)
        target = Path(chosen).resolve()
        config = _build_render_config(target, user_cfg, args)
        return launch_document_viewer(target, config)
    elif choice == "scan":
        nested = scan_recursive_markdown(Path(".").resolve())
        if not nested:
            ui.error("No Markdown files found in workspace subdirectories.")
            return 1
        options = [
            (
                str(f.resolve()),
                f"📄 {f.relative_to(Path('.').resolve())}",
                f"{f.stat().st_size:,} bytes",
            )
            for f in nested
        ]
        chosen = ui.select("Select nested Markdown document to open:", options)
        target = Path(chosen).resolve()
        config = _build_render_config(target, user_cfg, args)
        return launch_document_viewer(target, config)
    elif choice == "prompt":
        entered = ui.prompt("Enter Markdown file path to open")
        if not entered or not entered.strip():
            return 0
        target = Path(entered.strip()).resolve()
        if not target.is_file():
            ui.error(f"File '{entered}' not found.")
            return 1
        config = _build_render_config(target, user_cfg, args)
        return launch_document_viewer(target, config)

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    handle_color_args(raw_args)

    if any(a in ("-h", "--help", "help") for a in raw_args):
        print_help()
        return 0

    if any(a in ("-V", "-v", "--version", "version") for a in raw_args):
        if ui.is_json:
            import json

            print(json.dumps({"app": "goggles", "version": __version__}))
            return 0
        if ui.is_agent:
            print(f"goggles {__version__}")
            return 0
        print(f"{ui.badge()} {ui.bold(f'v{__version__}')}")
        return 0

    user_cfg = load_user_config()

    parser = _build_parser(user_cfg)
    args = parser.parse_args(raw_args)

    if args.clear_cache:
        return clear_grip_cache()

    if not args.path:
        docs = print_status_dashboard()
        if ui.is_json:
            import json

            print(
                json.dumps(
                    {
                        "status": "ok",
                        "documents_count": len(docs),
                        "documents": [str(d) for d in docs],
                    },
                    indent=2,
                )
            )
            return 0
        if sys.stdin.isatty() and not ui.is_agent:
            return run_interactive_hub(docs, user_cfg, args)
        if not raw_args or ui.is_agent:
            print_help()
            return 0
        ui.error("No Markdown document specified. Specify a file: goggles <file.md>")
        print()
        print_help()
        return 1

    target_md = discover_markdown_target(args.path)
    config = _build_render_config(target_md, user_cfg, args)
    return launch_document_viewer(target_md, config)


if __name__ == "__main__":
    sys.exit(main())
