{
  description = "Goggles - Instant GitHub-Flavored Markdown (GFM) Native Desktop Viewer";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    prism = {
      url = "github:SpanishSyntax/Prism";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    prism,
  }: let
    systems = flake-utils.lib.defaultSystems;
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [prism.overlays.default];
      };
      gogglesPackage = pkgs.callPackage ./default.nix {};
    in {
      packages = {
        default = gogglesPackage;
        goggles = gogglesPackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${gogglesPackage}/bin/goggles";
        };
        goggles = {
          type = "app";
          program = "${gogglesPackage}/bin/goggles";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3Packages.setuptools
          python3Packages.pytest
          python3Packages.prism
          python3Packages.grip
          python3Packages.pywebview
          python3Packages.pygobject3
          gobject-introspection
          gtk3
          webkitgtk_4_1
          glib-networking
          gsettings-desktop-schemas
        ];

        shellHook = ''
          export GI_TYPELIB_PATH="${pkgs.lib.makeSearchPath "lib/girepository-1.0" [
            pkgs.gtk3
            pkgs.webkitgtk_4_1
            pkgs.gobject-introspection
            pkgs.pango
            pkgs.gdk-pixbuf
            pkgs.atk
            pkgs.harfbuzz
          ]}''${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}"
          export GIO_EXTRA_MODULES="${pkgs.glib-networking}/lib/gio/modules''${GIO_EXTRA_MODULES:+:$GIO_EXTRA_MODULES}"
          export PYWEBVIEW_GUI="gtk"
        '';
      };
    })
    // {
      overlays = {
        default = final: prev: {
          goggles = final.callPackage ./default.nix {};
        };
        goggles = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.goggles;
        goggles = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.goggles;
          system = pkgs.stdenv.hostPlatform.system;
          defaultGoggles = self.packages.${system}.default;
        in {
          options.programs.goggles = {
            enable = lib.mkEnableOption "Goggles - Instant GitHub-Flavored Markdown (GFM) native desktop viewer";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultGoggles;
              description = "The Goggles package to use.";
            };
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
      };

      homeManagerModules = {
        default = self.homeManagerModules.goggles;
        goggles = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.goggles;
          tomlFormat = pkgs.formats.toml {};
          system = pkgs.stdenv.hostPlatform.system;
          defaultGoggles = self.packages.${system}.default;
        in {
          options.programs.goggles = {
            enable = lib.mkEnableOption "Goggles - Instant GitHub-Flavored Markdown (GFM) native desktop viewer";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultGoggles;
              description = "The Goggles package to use.";
            };

            settings = lib.mkOption {
              type = tomlFormat.type;
              default = {};
              description = "Configuration written to ~/.config/goggles/goggles.toml.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];

            xdg.configFile."goggles/goggles.toml" = lib.mkIf (cfg.settings != {}) {
              source = tomlFormat.generate "goggles.toml" cfg.settings;
            };
          };
        };
      };
    };
}
