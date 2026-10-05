{ overlay }:
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.programs.anime-cursors;
  catalog = lib.trivial.importJSON ../CursorConverter/config/cursor_data.json;
  themes = builtins.attrNames (
    lib.attrsets.filterAttrs (_: theme: theme.missing_roles == [ ]) catalog
  );
in
{
  options.programs.anime-cursors = {
    enable = lib.options.mkEnableOption "an animated anime cursor theme";
    theme = lib.options.mkOption {
      type = lib.types.enum themes;
      default = "hakurei-reimu";
      description = "Complete theme ID from the anime-cursors catalog";
    };
    size = lib.options.mkOption {
      type = lib.types.ints.positive;
      default = 32;
      description = "Requested cursor size in pixels";
    };
    package =
      lib.options.mkPackageOption pkgs "anime-cursors" {
        default = null;
        extraDescription = ''
          The package must provide `share/icons/anime-<theme>`; its unfree
          license must be allowed in nixpkgs
        '';
      }
      // {
        default = (pkgs.anime-cursors or (pkgs.extend overlay).anime-cursors).override {
          themes = [ cfg.theme ];
        };
        defaultText = lib.options.literalExpression ''
          pkgs.anime-cursors.override { themes = [ config.programs.anime-cursors.theme ]; }
        '';
      };
  };
}
