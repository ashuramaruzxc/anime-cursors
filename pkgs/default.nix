{
  inputs,
  self,
  ...
}: {
  systems = ["x86_64-linux" "aarch64-linux"];

  imports = [inputs.flake-parts.flakeModules.easyOverlay];

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
          win2xcur = config.packages.win2xcur-custom;
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
    formatter = pkgs.alejandra;
    packages = with pkgs; {
      win2xcur-git = callPackage ./python/win2xcur/win2xcur-git.nix {};
      win2xcur-custom = callPackage ./python/win2xcur/win2xcur-custom.nix {};
      clickgen = callPackage ./python/clickgen {};
      xcursor-viewer = libsForQt5.callPackage ./utils/xcursor-viewer {};
    };
    devShells.default = pkgs.devshell.mkShell {
      imports = [(pkgs.devshell.importTOML ./devshell.toml)];
      packages = with pkgs;
        [
          (python3.withPackages (p:
            with p; [
              requests
              black
              pillow
              numpy
              pyyaml
              attrs
              wand
              toml
              win2xcur
            ]))
        ]
        ++ (with config.packages; [xcursor-viewer]);
    };
  };
}
