{
  description = "Animeted Cursors on Linux";

  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [ inputs.devenv.flakeModule ];
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      perSystem =
        { pkgs, system, ... }:
        {
          _module.args.pkgs = inputs.nixpkgs.legacyPackages.${system};
          checks = {
            pre-commit-check =
              let
                excludes = [
                  ".direnv"
                  ".devenv"
                ];
              in
              inputs.pre-commit-hooks.lib.${system}.run {
                src = ./.;
                hooks.shellcheck.enable = true;
                hooks.nixfmt-rfc-style = {
                  enable = true;
                  packages = pkgs.nixfmt-rfc-style;
                  inherit excludes;
                };
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
                    black
                    cursorgen
                    flake8
                    isort
                    mypy
                    numpy
                    pillow
                    pylint
                  '';
                };
                version = "3.12.9";
              };
            };
            pre-commit =
              let
                excludes = [
                  ".direnv"
                  ".devenv"
                ];
              in
              {
                hooks.nixfmt-rfc-style = {
                  enable = true;
                  inherit excludes;
                  package = pkgs.nixfmt-rfc-style;
                };
                hooks.shellcheck.enable = true;
              };
            packages = builtins.attrValues {
              inherit (pkgs) zlib pylint;
              inherit (pkgs) git pre-commit;
              inherit (pkgs) nix-index nix-prefetch-github nix-prefetch-scripts;
              inherit (pkgs) ffmpeg-full imagemagick;
              xcursor-viewer = pkgs.libsForQt5.callPackage ./pkgs/xcursor-viewer.nix { };
              cursorgen = pkgs.callPackage ./pkgs/cursorrgen.nix { };
            };
          };
          formatter = pkgs.nixfmt-rfc-style;
          packages = {
            # debug packages outputs
            cursorgen = pkgs.callPackage ./pkgs/cursorrgen.nix { };
            xcursor-viewer = pkgs.libsForQt5.callPackage ./pkgs/xcursor-viewer.nix { };
          };
        };
    };

  inputs = {
    # Flake-Parts and Devenv
    # --------------------------------------------------
    flake-parts.url = "github:hercules-ci/flake-parts";
    devenv.url = "github:cachix/devenv";
    devenv.inputs.nixpkgs.follows = "nixpkgs";
    nix2container.url = "github:nlewo/nix2container";
    nix2container.inputs.nixpkgs.follows = "nixpkgs";
    mk-shell-bin.url = "github:rrbutani/nix-mk-shell-bin";
    pre-commit-hooks.url = "github:cachix/git-hooks.nix";
    pre-commit-hooks.inputs.nixpkgs.follows = "nixpkgs";
    pre-commit-hooks.inputs.flake-compat.follows = "";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
    nixpkgs-python.inputs.nixpkgs.follows = "nixpkgs";
    # --------------------------------------------------
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
}
