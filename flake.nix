{
  description = "Animeted Cursors on Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
    devenv.url = "github:cachix/devenv";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
    nixpkgs-python.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    { self, pre-commit-hooks-nix, ... }@inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      imports = [
        inputs.flake-parts.flakeModules.easyOverlay
        inputs.devenv.flakeModule
      ];
      flake.nixosModules =
        let
          inherit (inputs.nixpkgs) lib;
        in
        {
          default = throw (
            lib.mdDoc ''
              default is deprecated
              ${builtins.concatStringsSep "\n" (
                lib.filter (name: name != "default") (lib.attrNames self.nixosModules)
              )}
            ''
          );
        };
      perSystem =
        {
          config,
          system,
          pkgs,
          ...
        }:
        {
          _module.args.pkgs = import inputs.nixpkgs {
            inherit system;
            config = {
              allowUnfree = true;
              packageOverrides = pkgs: {
                gimp-python = pkgs.gimp.override { withPython = true; };
                win2xcur = config.packages.cursorgen;
              };
              permittedInsecurePackages = [
                "python-2.7.18.7"
                "python-2.7.18.7-env"
              ];
            };
          };
          devenv.shells.default = {
            name = "anime-cursors env";
            languages = {
              nix.enable = true;
              shell.enable = true;
              python = {
                enable = true;
                venv = {
                    enable = true;
                    requirements = ''
                        cursorgen
                        pillow
                        numpy
                        black
                        isort
                        mypy
                        flake8
                    '';
                };
                version = "3.11.2";
              };
            };
            packages = [
              pkgs.ffmpeg
              pkgs.imagemagick
              pkgs.zlib
              pkgs.git
              pkgs.pre-commit
              pkgs.nix-index
              pkgs.nix-prefetch-github
              pkgs.nix-prefetch-scripts
              config.packages.xcursor-viewer
            ];
          };
          formatter = pkgs.nixfmt-rfc-style;

          packages = with pkgs; {
            win2xcur-git = callPackage ./pkgs/python/win2xcur { };
            cursorgen = callPackage ./pkgs/python/cursorgen { };
            clickgen = callPackage ./pkgs/python/clickgen { };
            xcursor-viewer = libsForQt5.callPackage ./pkgs/utils/xcursor-viewer { };
          };
        };
    };
}
