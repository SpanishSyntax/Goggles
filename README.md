<p align="center">
  <img src="assets/banner.png" alt="Traditional carved Inuit snow goggles designed to reduce polar glare" width="100%" />
</p>

# Goggles 🥽

Instant GitHub-Flavored Markdown (GFM) native desktop document viewer.

Goggles is a dedicated, zero-clutter native desktop viewer for GitHub-Flavored Markdown (GFM). Built for the Frost ecosystem alongside Flaker, Borealis, Glaze, Folio, and Sled, it pairs `grip` (rendering via GitHub's official Markdown API and Primer CSS) with an ephemeral local `pywebview` / WebKit2GTK window that terminates the background server the moment the window closes.

---

> [!TIP]
> **Documentation Site**: Comprehensive architecture notes, complete CLI references, and configuration options are available on the **[Documentation Site](https://spanishsyntax.github.io/Goggles)**.

---

## Why "Goggles"? (The Lore)

> **snow goggles** (`/ˈɡɒɡ.əlz/`) — *noun:* Slotted, glare-resistant eyewear carved from caribou antler or driftwood by inuit hunters, shielding vision from blinding arctic blizzard whiteouts and high-albedo snowfield reflections.

Stepping out onto an open arctic icefield without eye protection causes blinding snow glare. Similarly, reading technical markdown through heavy web browsers or bloated editors introduces visual clutter, distracting toolbars, and sluggish render latency.

**Goggles provides slotted, glare-free clarity:**

- **Focused Reading**: Launches an instantaneous, zero-clutter native desktop window rendering GitHub Flavored Markdown (GFM) with official Primer CSS typography.
- **Ephemeral Lifecycle**: Spawns directly from the terminal and terminates all background processes the millisecond the window closes—leaving zero background battery or memory footprint.

---

## Features

- **GitHub Rendering Parity**:
  - **GitHub Alerts / Callouts**: Native rendering for `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]`.
  - **Diagrams & Flowcharts**: Client-side **Mermaid.js** diagram rendering for ```` ```mermaid ```` code blocks.
  - **Mathematical Typesetting**: Inline (`$...$`) and display (`$$...$$`) LaTeX math powered by **KaTeX**.
  - **GFM Tables, Task Lists & Syntax Highlighting**: Exact GitHub Primer typography and code highlighting.
- **Isolated Native Desktop Frame**: Renders inside a lightweight `pywebview` (GTK3 / WebKit2GTK) window on Wayland and X11 without browser tab clutter.
- **Ephemeral Loopback & Strict Teardown**: Binds an ephemeral unprivileged localhost port, spawns `grip` in an isolated process group with Linux `PR_SET_PDEATHSIG`, and guarantees daemon teardown on window exit or signal (`SIGINT`, `SIGTERM`, `SIGHUP`).
- **Token Discovery Hierarchy**: Bypasses GitHub's 60 req/hr anonymous rate limit by checking `GITHUB_TOKEN` / `GRIP_TOKEN` / `GH_TOKEN` / `GOGGLES_GITHUB_TOKEN`, `~/.config/goggles/token`, Unix `pass` (`password-store`) paths (`github/token`, `github/pat`), or `gh auth token`.
- **Adaptive Dark & Light Modes**: Follows system color scheme (`--theme auto`), forces GitHub Dark (`--dark`) or Light (`--light`), or toggles live with `t`.
- **Model Context Protocol (MCP)**: Native stdio MCP server for agentic markdown document discovery and previewing.

---

## Quick Start

Run Goggles directly via Nix without installing:

```bash
# Launch interactive dashboard & Quick Actions start menu
nix run github:SpanishSyntax/Goggles

# Render README.md in an isolated native desktop window
nix run github:SpanishSyntax/Goggles -- README.md

# Force GitHub Dark mode in a wide layout
nix run github:SpanishSyntax/Goggles -- README.md --dark --wide

# Launch in a minimal frameless window
nix run github:SpanishSyntax/Goggles -- docs/spec.md --frameless

# Interactively pick a Markdown file from a directory
nix run github:SpanishSyntax/Goggles -- docs/
```

---

## CLI Reference

```text
Usage: goggles                                Open interactive dashboard & document picker
       goggles <path-to-markdown> [options]   Directly preview Markdown document
       goggles <directory> [options]          Select *.md interactively within directory
       goggles mcp                            Start Model Context Protocol stdio server

Options:
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
  -A, --agent            Compact machine-friendly output mode
  --json                 Structured JSON output mode
  --color MODE           Color output mode: auto, always, never (default: auto)
  --no-color             Disable colored terminal output
  -h, --help             Show this help message and exit
  -V, -v, --version      Show version information and exit
```

---

## Window Keyboard Shortcuts

| Keybinding | Action |
| :--- | :--- |
| `q` / `Esc` / `Ctrl + W` | Close window & terminate ephemeral `grip` daemon |
| `t` | Toggle between GitHub Dark and Light themes |
| `g` | Toggle between Clean Document Mode and GitHub Box Layout |
| `r` / `F5` / `Ctrl + R` | Reload Markdown document |
| `Ctrl + +` / `Ctrl + -` | Zoom in / Zoom out |
| `Ctrl + 0` | Reset zoom level to 100% |

---

## Configuration

Goggles optionally reads default preferences from `~/.config/goggles/goggles.toml`:

```toml
[general]
theme = "auto"
width = 980
height = 860
wide = false
pass_path = "github/token"
```

---

## Home Manager Configuration

Add Goggles to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    goggles = {
      url = "github:SpanishSyntax/Goggles";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, goggles, ... }: {
    homeConfigurations.user = home-manager.lib.homeManagerConfiguration {
      modules = [
        goggles.homeManagerModules.default
        {
          programs.goggles.enable = true;
        }
      ];
    };
  };
}
```

---

## License

MIT © SpanishSyntax
