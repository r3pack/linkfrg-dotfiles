{
  pkgs,
  config,
  lib,
  ...
}: let
  cfg = config.linkfrg-dotfiles.iconTheme;
in {
  options.linkfrg-dotfiles.iconTheme = {
    enable = lib.mkEnableOption "Enable Papirus icon theme";
  };

  config = lib.mkIf cfg.enable {
    gtk.enable = true;
    gtk.iconTheme = {
      name = "Papirus";
      package = pkgs.papirus-icon-theme;
    };
  };
}
