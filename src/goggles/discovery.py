"""Document discovery and search utilities for Goggles."""

from __future__ import annotations

import sys
from pathlib import Path

from goggles.ui import ui


def print_status_dashboard(base_dir: Path | str = ".") -> list[Path]:
    """Renders the standard Frost bounding box status dashboard panel for Goggles."""
    from goggles import __version__
    from goggles.core import resolve_github_token

    search_dir = Path(base_dir).resolve()
    docs = sorted(
        [
            p
            for p in search_dir.iterdir()
            if p.is_file() and p.suffix.lower() in (".md", ".markdown", ".mdown")
        ],
        key=lambda p: (0 if p.name.lower() == "readme.md" else 1, p.name.lower()),
    )

    token, source = resolve_github_token()
    token_str = (
        f"{ui.bold_green('✔ Active')} ({source})"
        if token
        else f"{ui.dim('Anonymous (60 req/hr rate limit)')}"
    )

    if docs:
        doc_names = ", ".join(f"{d.name} ({d.stat().st_size:,}B)" for d in docs[:3])
        if len(docs) > 3:
            doc_names += f" and {len(docs) - 3} more"
        docs_display = doc_names
    else:
        docs_display = ui.dim("no markdown files in root directory")

    lines = [
        f"{ui.bold('Goggles Version:')}   {ui.bold_cyan(f'v{__version__}')} (Engines: Grip GFM + WebKitGTK / PyWebView)",
        f"{ui.bold('Active Workspace:')}  {search_dir}",
        f"{ui.bold('GitHub Token:')}      {token_str}",
        f"{ui.bold('Discovered Files:')}  {docs_display}",
    ]
    ui.panel("GOGGLES GFM DOCUMENT VIEWER", lines)
    return docs


def scan_recursive_markdown(root: Path) -> list[Path]:
    """Recursively discovers all Markdown documents excluding hidden dirs, node_modules, and git."""
    results: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".md", ".markdown", ".mdown"):
            parts = p.parts
            if any(
                part.startswith(".")
                or part in ("node_modules", "target", "result", "dist")
                for part in parts
            ):
                continue
            results.append(p)
    return sorted(results, key=lambda p: (len(p.parts), p.name.lower()))


def discover_markdown_target(raw_path: str | Path | None = None, base_dir: Path | str = ".") -> Path:
    """Resolves a target Markdown document or interactively prompts if a directory is given."""
    search_dir = Path(base_dir).resolve()

    if not raw_path:
        ui.error("No Markdown document specified. Specify a file: goggles <file.md>")
        sys.exit(1)

    target = search_dir / raw_path if not Path(raw_path).is_absolute() else Path(raw_path)
    if target.is_file():
        return target
    elif target.is_dir():
        search_dir = target
    else:
        ui.error(f"File '{raw_path}' not found.")
        sys.exit(1)

    md_files = sorted(
        [
            p
            for p in search_dir.iterdir()
            if p.is_file() and p.suffix.lower() in (".md", ".markdown", ".mdown")
        ],
        key=lambda p: (0 if p.name.lower() == "readme.md" else 1, p.name.lower()),
    )

    if not md_files:
        if sys.stdin.isatty():
            lines = [
                f"{ui.bold('Active Directory:')} {search_dir}",
                f"{ui.bold('Target Document:')}  {ui.dim('No markdown documents (*.md) found in directory')}",
            ]
            ui.panel("GOGGLES GFM DOCUMENT VIEWER", lines)
            action = ui.select(
                f"No Markdown document found in '{search_dir.name}'. What would you like to do?",
                [
                    ("scan", "Search subdirectories recursively for *.md files"),
                    ("help", "Show help and command usage"),
                    ("exit", "Exit"),
                ],
            )
            if action == "scan":
                nested = scan_recursive_markdown(search_dir)
                if not nested:
                    ui.error(f"No Markdown files found under '{search_dir}'.")
                    sys.exit(1)
                options = [
                    (
                        str(f),
                        f"📄 {f.relative_to(search_dir)}",
                        f"{f.stat().st_size:,} bytes",
                    )
                    for f in nested
                ]
                chosen = ui.select("Select a Markdown document to open:", options)
                return Path(chosen).resolve()
            else:
                sys.exit(0)

        ui.error(f"No Markdown files found in '{search_dir}'. Specify one: goggles <file.md>")
        sys.exit(1)

    if sys.stdin.isatty():
        options = [
            (str(f.resolve()), f"📄 {f.name}", f"{f.stat().st_size:,} bytes")
            for f in md_files
        ]
        chosen = ui.select(
            f"Select a Markdown document in '{search_dir.name}' to open:", options
        )
        return Path(chosen).resolve()

    ui.error(
        f"'{raw_path}' is a directory containing {len(md_files)} markdown files. "
        f"Specify a document explicitly: goggles {Path(raw_path) / md_files[0].name}"
    )
    sys.exit(1)
