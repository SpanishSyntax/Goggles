# CLI Reference & Command Guide

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Command Overview

```text
Usage: goggles                                Open interactive dashboard & document picker
       goggles <path-to-markdown> [options]   Directly preview Markdown document
       goggles <directory> [options]          Select *.md interactively within directory
       goggles mcp                            Start Model Context Protocol stdio server
```

| Invocation | Description |
| :--- | :--- |
| `goggles <file.md>` | Directly preview the specified Markdown document. |
| `goggles <directory>` | Interactively choose a Markdown file from the target folder. |
| `goggles` | Open interactive workspace dashboard and Quick Actions start menu. |
| `goggles mcp` | Launch standard I/O Model Context Protocol (MCP) server. |

---

## Interactive Document Hub

When launched without arguments in an interactive terminal, Goggles displays a workspace dashboard:

- **Workspace File Discovery**: Detects all root and nested Markdown documents.
- **Quick Actions Menu**:
  - `Select Discovered Document`: Browse list of detected `.md` files.
  - `Search Workspace Subdirectories`: Recursively locate documents in child folders.
  - `Open Document by Custom Path`: Type an explicit relative or absolute file path.
  - `Clear Grip Cached Primer CSS Assets`: Refresh local GitHub stylesheet caches.

---

## Options and Flags

| Flag | Long Option | Description | Default |
| :--- | :--- | :--- | :--- |
| `-p` | `--port PORT` | Bind specific localhost port. | Ephemeral port (`0`) |
| | `--host HOST` | Bind address for local daemon. | `127.0.0.1` |
| `-g` | `--github-mode` | Render with GitHub repository Box chrome and page margins. | `false` |
| `-w` | `--wide` | Render wide GitHub document container. | `false` |
| `-u` | `--user-content` | Render in GitHub user-content mode (issues/comments). | `false` |
| `-c` | `--context REPO` | GitHub repository context (`Owner/Repo`) for autolinks. | `None` |
| `-t` | `--title TITLE` | Override window title. | `Goggles: <filename>` |
| | `--theme MODE` | Viewer color theme: `auto`, `dark`, or `light`. | `auto` |
| | `--dark` / `--light`| Shortcuts for `--theme=dark` / `--theme=light`. | - |
| | `--frameless` | Launch in a frameless minimal window without titlebars. | `false` |
| | `--width PX` | Initial window width in pixels. | `980` |
| | `--height PX` | Initial window height in pixels. | `860` |
| | `--token TOKEN` | Explicit GitHub Personal Access Token. | Auto-discovered |
| | `--pass-path ENTRY`| Password-store (`pass`) entry for GitHub token. | Auto-discovered |
| | `--api-url URL` | Custom GitHub API base URL (for GitHub Enterprise). | GitHub API |
| | `--inline` | Inline CSS styles into HTML instead of linking. | `false` |
| | `--clear-cache` | Clear cached GitHub CSS assets via `grip --clear` and exit.| `false` |
| | `--debug` | Enable WebKit inspector / developer tools in viewer window. | `false` |
| `-A` | `--agent` | Compact machine-friendly output mode. | `false` |
| | `--json` | Output document list in structured JSON. | `false` |
| | `--color MODE` | Terminal color mode: `auto`, `always`, or `never`. | `auto` |
| | `--no-color` | Disable colored terminal output. | `false` |
| `-h` | `--help` | Show command-line help text. | - |
| `-V` | `--version` | Display version information. | - |

---

## Keyboard Shortcuts

When the native desktop viewer window is focused, the following hotkeys are available:

| Keybinding | Action |
| :--- | :--- |
| `q` / `Esc` / `Ctrl + W` | Close viewer window and terminate ephemeral background daemon. |
| `t` | Toggle between GitHub Dark and Light themes. |
| `g` | Toggle between Clean Document Mode and GitHub Box Layout. |
| `r` / `F5` / `Ctrl + R` | Reload Markdown document from disk. |
| `Ctrl + +` | Zoom in. |
| `Ctrl + -` | Zoom out. |
| `Ctrl + 0` | Reset zoom level to 100%. |

---

## Model Context Protocol Server

Goggles exposes a native Model Context Protocol (MCP) server over standard I/O:

```bash
goggles mcp
```

### MCP Tools Exposed

1. **`goggles_preview`**: Launch desktop viewer for a specified file path.
2. **`goggles_list_documents`**: Discover and list all Markdown files in a target workspace.
3. **`goggles_clear_cache`**: Invoke cache purge on local grip stylesheets.

---

## Practical Recipes

### Recipe 1: Inspecting an Architectural Specification

Open a document in wide dark mode for reviewing wide tables and code blocks:

```bash
goggles docs/architecture.md --dark --wide
```

### Recipe 2: Presentation or Reading Mode

Open in a frameless window with a custom geometry:

```bash
goggles README.md --frameless --width 1200 --height 900
```

### Recipe 3: Authenticating with a Custom Pass Entry

If your GitHub token is stored in password-store under `work/github/token`:

```bash
goggles README.md --pass-path work/github/token
```
