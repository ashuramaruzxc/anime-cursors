{
  description = "Animeted Cursors on Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
    devshell.url = "github:numtide/devshell";
  };

  outputs = {self, ...} @ inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      flake.nixosModules = let
        inherit (inputs.nixpkgs) lib;
      in {
        default = throw (lib.mdDoc ''
          default is deprecated
          ${builtins.concatStringsSep "\n" (lib.filter (name: name != "default") (lib.attrNames self.nixosModules))}
        '');
      };
      imports = [
        inputs.pre-commit-hooks-nix.flakeModule
        inputs.devshell.flakeModule
        ./pkgs
      ];
    };
}
