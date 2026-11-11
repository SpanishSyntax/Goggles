<p align="center">
  <img src="assets/banner.png" alt="Traditional carved Inuit snow goggles designed to reduce polar glare" width="100%" />
</p>

# Goggles 🥽

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

> Instant GitHub-Flavored Markdown (GFM) native desktop document viewer.

Goggles is a dedicated, zero-clutter native desktop viewer for GitHub-Flavored Markdown (GFM). It pairs `grip` (rendering via GitHub's official Markdown API and Primer CSS) with an ephemeral local `pywebview` / WebKit2GTK window that automatically terminates the background server the instant the window closes.

---

## Why "Goggles"? (The Lore)

> **snow goggles** (`/ˈɡɒɡ.əlz/`) — *noun:* Slotted, glare-resistant eyewear carved from caribou antler or driftwood by inuit hunters, shielding vision from blinding arctic blizzard whiteouts and high-albedo snowfield reflections.

Stepping out onto an open arctic icefield without eye protection causes blinding snow glare. Similarly, reading technical markdown through heavy web browsers or resource-intensive editors introduces visual clutter, unwanted browser tabs, and sluggish render latency.

**Goggles provides slotted, glare-free clarity:**

- **Focused Reading**: Launches an instantaneous, zero-clutter native desktop window rendering Markdown with official Primer CSS typography.
- **Ephemeral Lifecycle**: Spawns directly from the terminal and terminates all background processes the millisecond the window closes—leaving zero lingering memory or battery consumption.

---

## Architecture at a Glance

Goggles coordinates three primary subsystems:

1. **Grip Process Orchestrator (`goggles.core.GripOrchestrator`)**: Binds an unprivileged ephemeral port (port 0), injects discovered GitHub tokens, launches the local Grip daemon in an isolated process group, and guarantees clean teardown via signal trapping and Linux `PR_SET_PDEATHSIG`.
2. **Desktop WebKit Runtime (`goggles.viewer`)**: Creates a native GTK3 / WebKit2GTK window via `pywebview` with custom hotkeys, adaptive light/dark theming, and zoom controls.
3. **Document Discovery Hub (`goggles.discovery`)**: Discovers Markdown files in active workspaces, displays workspace dashboards, and provides interactive file pickers.

---

## Rendering Features

- **GitHub Primer Typography**: Official styles for headings, code blocks, tables, task lists, and blockquotes.
- **GitHub Alerts / Callouts**: Native rendering for `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]`.
- **Mermaid.js Diagrams**: Automatic client-side rendering for ```` ```mermaid ```` flowchart and sequence diagram fences.
- **KaTeX Mathematical Typesetting**: Inline (`$...$`) and display (`$$...$$`) LaTeX math formulas rendered crisply.
- **Light & Dark Theme Switching**: Live theme toggling via `t` key or `--dark` / `--light` flags.

---

## Documentation Navigation

- [Installation & Quick Start](getting-started.md): Installation via Nix, Home Manager, or pip, and first-time usage.
- [Architecture & Design Philosophy](architecture.md): WebKit runtime, ephemeral process lifecycle, signal trapping, and token discovery hierarchy.
- [CLI Reference & Command Guide](usage.md): Full flag specifications, keyboard shortcuts, MCP tools, and recipes.
- [Configuration & Advanced Options](configuration.md): Declarative options via `goggles.toml`, password-store integration, and NixOS/Home Manager modules.
