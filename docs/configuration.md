# Configuration & Advanced Options

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Configuration File

Goggles optionally reads default user preferences from `~/.config/goggles/goggles.toml` (or `$XDG_CONFIG_HOME/goggles/goggles.toml`).

### Specification (`goggles.toml`)

```toml
[general]
# Default color theme: auto, dark, or light
theme = "auto"

# Default window dimensions in pixels
width = 980
height = 860

# Default layout flags
wide = false
github_mode = false
frameless = false

# Custom pass entry for token retrieval
pass_path = "github/token"

# Bind address and port (0 for ephemeral)
host = "127.0.0.1"
port = 0

# Terminal color mode: auto, always, or never
color = "auto"
```

Command-line flags always take precedence over values defined in `goggles.toml`.

---

## Password-Store Integration

Goggles automatically queries the standard Unix password manager (`pass`) for GitHub Personal Access Tokens. By default, it searches the following paths:

- `github/token`
- `github/pat`
- `github/api-token`
- `github/personal-access-token`
- `dev/github/token`

You can override the target entry by either:
1. Setting `--pass-path <entry>` on the CLI.
2. Setting `pass_path = "<entry>"` in `goggles.toml`.
3. Exporting `GOGGLES_PASS_PATH="<entry>"` in your shell environment.

---

## NixOS and Home Manager

### NixOS System Module

```nix
# flake.nix or configuration.nix
{
  programs.goggles = {
    enable = true;
    package = inputs.goggles.packages.${pkgs.system}.default;
  };
}
```

### Home Manager Module

```nix
{
  programs.goggles = {
    enable = true;
    settings = {
      general = {
        theme = "dark";
        width = 1100;
        height = 900;
        wide = true;
      };
    };
  };
}
```

### Frost Iceberg Module

In the **Frost** ecosystem, Goggles is enabled via the iceberg app module:

```nix
frost.home.apps.icebergs.goggles.enable = true;
```
