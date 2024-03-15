{
  description = "Animeted Cursors on Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
    devshell.url = "github:numtide/devshell";
  };

  outputs = {
    self,
    pre-commit-hooks-nix,
    ...
  } @ inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux"];
      imports = [inputs.flake-parts.flakeModules.easyOverlay];
      flake.nixosModules = let
        inherit (inputs.nixpkgs) lib;
      in {
        default = throw (lib.mdDoc ''
          default is deprecated
          ${builtins.concatStringsSep "\n" (lib.filter (name: name != "default") (lib.attrNames self.nixosModules))}
        '');
      };
      perSystem = {
        config,
        system,
        pkgs,
        ...
      }: {
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            allowBroken = true;
            packageOverrides = pkgs: {
              gimp-python = pkgs.gimp.override {withPython = true;};
              win2xcur = config.packages.cursorgen;
            };
            permittedInsecurePackages = [
              "python-2.7.18.7"
              "python-2.7.18.7-env"
            ];
          };
          overlays = [
            inputs.devshell.overlays.default
          ];
        };
        checks = {
          pre-commit-check = pre-commit-hooks-nix.lib.${system}.run {
            src = ./.;
            hooks = {
              alejandra.enable = true; # enable pre-commit formatter
              black.enable = true;
              flake8.enable = true;
              isort.enable = true;
              mypy.enable = true;
            };
            settings = {
              alejandra = {
                package = config.formatter;
                check = true;
                threads = 4;
              };
              isort = {
                profile = "black";
              };
            };
          };
        };
        devShells.default = let
          inherit (config.checks.pre-commit-check) shellHook;
        in
          pkgs.devshell.mkShell {
            imports = [(pkgs.devshell.importTOML ./devshell.toml)];
            git.hooks = {
              enable = true;
              pre-commit.text = shellHook;
            };
            packages = with pkgs;
              [
                (python3.withPackages (p:
                  with p; [
                    win2xcur
                  ]))
              ]
              ++ (with config.packages; [xcursor-viewer]);
          };
        formatter = pkgs.alejandra;

        packages = with pkgs; {
          win2xcur-git = callPackage ./pkgs/python/win2xcur {};
          cursorgen = callPackage ./pkgs/python/cursorgen {};
          clickgen = callPackage ./pkgs/python/clickgen {};
          xcursor-viewer = libsForQt5.callPackage ./pkgs/utils/xcursor-viewer {};
        };
      };
    };
}
