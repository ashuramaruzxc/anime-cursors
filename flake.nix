{
  description = "Animated cursor themes for Linux";

  inputs = {
    nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    cursorgen = {
      url = "github:meanvoid/cursorgen";
      flake = false;
    };
  };

  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      flake.overlays.default = final: _prev: {
        anime-cursors-packages = final.callPackage ./pkgs { cursorgenSrc = inputs.cursorgen; };
        anime-cursors = final.anime-cursors-packages.cursors;
      };
      flake = {
        nixosModules.default = import ./modules/nixos.nix { overlay = inputs.self.overlays.default; };
        homeManagerModules.default = import ./modules/home-manager.nix {
          overlay = inputs.self.overlays.default;
        };
      };
      perSystem =
        {
          config,
          pkgs,
          system,
          ...
        }:
        {
          _module.args.pkgs = import inputs.nixpkgs {
            inherit system;
            overlays = [ inputs.self.overlays.default ];
            config.allowUnfreePredicate =
              pkg: inputs.nixpkgs.lib.strings.hasPrefix "anime-cursors" (inputs.nixpkgs.lib.strings.getName pkg);
          };
          packages = {
            inherit (pkgs.anime-cursors-packages) cursorgen converter;
            inherit (pkgs) anime-cursors xcursor-viewer;
            cursors = pkgs.anime-cursors;
            default = pkgs.anime-cursors;
          }
          // pkgs.lib.attrsets.mapAttrs' (
            name: _:
            pkgs.lib.attrsets.nameValuePair "anime-${name}"
              (pkgs.anime-cursors.override {
                themes = [ name ];
              }).variants.${name}
          ) pkgs.anime-cursors.variants;
          checks = {
            inherit (config.packages) converter cursorgen cursors;
          };
          formatter = pkgs.nixfmt;
          devShells.default =
            let
              cursorPython = config.packages.converter.pythonModule.withPackages (
                _: pkgs.lib.attrsets.attrValues { inherit (config.packages) converter; }
              );
            in
            pkgs.mkShell {
              packages = pkgs.lib.attrsets.attrValues {
                inherit cursorPython;
                inherit (pkgs)
                  uv
                  nixfmt
                  actionlint
                  pre-commit
                  imagemagick
                  ffmpeg
                  ;
                build-cursors = pkgs.writeShellApplication {
                  name = "build-cursors";
                  text = ''${cursorPython.interpreter} process_cursors.py "$@"'';
                };
                audit-cursors = pkgs.writeShellApplication {
                  name = "audit-cursors";
                  text = ''${cursorPython.interpreter} parse_directories.py "$@"'';
                };
              };
            };
        };
    };
}
