# Architecture & Design Philosophy

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Design Philosophy

Goggles is designed around three architectural invariants:

1. **Zero Lingering State**: No daemon processes or orphan servers should persist after the viewer window closes. Process lifecycle is strictly bounded by the window lifecycle.
2. **Official Rendering Parity**: Document styling should match GitHub exactly, including Primer typography, alerts (`[!NOTE]`), tables, and syntax themes.
3. **Transparent Rate Limit Bypass**: The user should never collide with GitHub's anonymous 60 requests/hour limit; authentication tokens are resolved automatically from existing credentials.

---

## The Lore

> **snow goggles** (`/ˈɡɒɡ.əlz/`) — *noun:* Slotted, glare-resistant eyewear carved from caribou antler or driftwood by inuit hunters, shielding vision from blinding arctic blizzard whiteouts and high-albedo snowfield reflections.

Stepping out onto an open arctic icefield without eye protection causes blinding snow glare. Similarly, reading technical markdown through heavy web browsers or resource-intensive editors introduces visual clutter, unwanted browser tabs, and sluggish render latency.

Goggles provides slotted, glare-free clarity by stripping away browser chrome and window clutter, presenting Markdown in a dedicated, high-contrast desktop viewport.

---

## Desktop WebKit Runtime

Goggles utilizes `pywebview` paired with Linux WebKit2GTK (`webkit2gtk-4.1` on GTK3):

- **Wayland and X11 Native**: Directly renders using native system graphics contexts without requiring Chromium or Electron runtimes.
- **Dynamic JavaScript Injection**: Custom keyboard shortcuts, theme toggle hooks, and zoom controllers are injected into the page DOM post-load.
- **Client-Side Asset Enhancements**: Automatically injects KaTeX CDN assets for LaTeX math rendering and Mermaid.js runtime scripts for client-side diagram generation.

---

## Ephemeral Process Lifecycle

Goggles employs multi-layered teardown mechanisms to guarantee zero orphan background processes:

```
[goggles CLI]
     │
     ├── 1. Bind port 0 -> Kernel returns ephemeral port
     ├── 2. Resolve GitHub API token
     ├── 3. Spawn child grip subprocess:
     │        ├── Linux `PR_SET_PDEATHSIG` (SIGTERM if parent dies)
     │        └── `os.setsid()` (isolated process group)
     ├── 4. Polling loop awaits socket availability on localhost:port
     │
[pywebview Desktop Window]
     │
     ├── User closes window or presses `q` / `Esc`
     │
[Cleanup Traps]
     ├── Python `atexit` hook invoked
     ├── OS Signal handlers: SIGINT, SIGTERM, SIGHUP, SIGQUIT
     └── `os.killpg(pgid, SIGTERM)` followed by SIGKILL if timeout expires
```

### Linux `PR_SET_PDEATHSIG`

On Linux systems, the child process sets `prctl(PR_SET_PDEATHSIG, SIGTERM)`. If the parent Goggles Python process crashes or is killed with `SIGKILL`, the Linux kernel immediately sends `SIGTERM` to the child grip process, preventing zombie daemons.

---

## Token Discovery Hierarchy

To unlock GitHub's 5,000 requests/hour authenticated rate limit without requiring manual configuration, Goggles scans existing system credentials in descending priority order:

1. Explicit CLI argument: `--token <TOKEN>`
2. Environment variables: `GITHUB_TOKEN`, `GRIP_TOKEN`, `GH_TOKEN`, `GOGGLES_GITHUB_TOKEN`
3. Configuration file: `~/.config/goggles/token`
4. Standard Unix Password Store (`pass`):
   - `--pass-path <path>` (CLI argument)
   - `GOGGLES_PASS_PATH` (Environment variable)
   - `github/token`, `github/pat`, `github/api-token`, `github/personal-access-token`, `dev/github/token`
5. GitHub CLI: `gh auth token`
6. Unauthenticated Fallback: Anonymous mode (60 requests/hour)

---

## GitHub Rendering Parity

Goggles achieves exact GitHub rendering parity by delegating Markdown processing directly to GitHub's `/markdown` REST API via `grip`:

- **Primer CSS**: Loads official GitHub Primer styles and typography rules.
- **GFM Alerts**: Blocks with `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, and `> [!CAUTION]` render with official icons and color themes.
- **KaTeX Integration**: Mathematical formulas wrapped in single (`$...$`) or double (`$$...$$`) dollar signs render into crisp vector math.
- **Mermaid Diagrams**: Client-side JavaScript detects ```` ```mermaid ```` code blocks and parses them into interactive vector diagrams.
