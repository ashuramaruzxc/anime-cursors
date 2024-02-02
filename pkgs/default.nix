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
  } @ args: let
    overlayAttrs = config.packages;
  in {
    _module.args.pkgs = import inputs.nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };

    overlayAttrs = config.packages;
    packages = with pkgs; {
      win2xcur = callPackage ./python/win2xcur {};    
    };
  };
}
