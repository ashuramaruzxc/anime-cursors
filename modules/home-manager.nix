{ overlay }:
{ config, lib, ... }:
let
  cfg = config.programs.anime-cursors;
in
{
  imports = [ (import ./options.nix { inherit overlay; }) ];
  config = lib.modules.mkIf cfg.enable {
    home.pointerCursor = {
      enable = true;
      inherit (cfg) package size;
      name = "anime-${cfg.theme}";
      gtk.enable = lib.modules.mkDefault true;
      x11.enable = lib.modules.mkDefault true;
    };
  };
}
