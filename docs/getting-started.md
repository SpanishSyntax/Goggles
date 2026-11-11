# Getting Started with Goggles

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Installation

### Running Directly via Nix (Recommended)

Run Goggles directly on any Markdown document:

```bash
# Preview README.md
nix run github:SpanishSyntax/Goggles -- README.md

# Open interactive dashboard in current repository
nix run github:SpanishSyntax/Goggles
```

### Home Manager

Add Goggles to your flake inputs and include its Home Manager module:

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
          programs.goggles.settings = {
            general = {
              theme = "dark";
              width = 1100;
              height = 900;
            };
          };
        }
      ];
    };
  };
}
```

### NixOS System Configuration

```nix
{
  programs.goggles.enable = true;
  programs.goggles.package = inputs.goggles.packages.${pkgs.system}.default;
}
```

### Installing via Pip / Uv

When installing via pip or uv on Linux, ensure GTK3, WebKit2GTK (`webkit2gtk-4.1`), and GObject Introspection development libraries are present on the host:

```bash
# Using uv
uv tool install git+https://github.com/SpanishSyntax/Goggles.git

# Using pip
pip install git+https://github.com/SpanishSyntax/Goggles.git
```

---

## Quick Start

### 1. Preview a Specific Document

```bash
goggles README.md
```

This starts an ephemeral background server, queries GitHub's Markdown API for Primer HTML, and opens a clean desktop window. When you close the window (or press `q` / `Esc`), the background server is terminated immediately.

### 2. Force Dark Mode & Wide Layout

For wide documentation tables or code blocks:

```bash
goggles docs/architecture.md --dark --wide
```

### 3. Open in Frameless Minimal Window

For reading without standard window titlebars:

```bash
goggles SPEC.md --frameless
```

### 4. Interactive File Selection

If no file argument is provided, Goggles displays discovered Markdown documents in the current directory and opens an interactive selector:

```bash
goggles
```
