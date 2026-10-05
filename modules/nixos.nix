{ overlay }:
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.programs.anime-cursors;
  name = "anime-${cfg.theme}";
in
{
  imports = [ (import ./options.nix { inherit overlay; }) ];
  config = lib.modules.mkIf cfg.enable {
    environment = {
      systemPackages = [ cfg.package ];
      pathsToLink = [ "/share/icons" ];
      sessionVariables = {
        XCURSOR_THEME = lib.modules.mkDefault name;
        XCURSOR_SIZE = lib.modules.mkDefault (toString cfg.size);
      };
    };
    xdg.icons.enable = lib.modules.mkDefault true;
    xdg.icons.fallbackCursorThemes = lib.modules.mkDefault [ name ];
    services.displayManager.sddm.settings.Theme =
      lib.modules.mkIf config.services.displayManager.sddm.enable
        {
          CursorTheme = lib.modules.mkDefault name;
          CursorSize = lib.modules.mkDefault cfg.size;
        };
    assertions = [
      {
        assertion = pkgs.stdenv.hostPlatform.isLinux;
        message = "programs.anime-cursors requires Linux";
      }
    ];
  };
}
