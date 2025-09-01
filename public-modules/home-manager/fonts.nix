{
  pkgs,
  config,
  lib,
  ...
}: let
  cfg = config.linkfrg-dotfiles.fonts;
in {
  options.linkfrg-dotfiles.fonts = {
    enable = lib.mkEnableOption "Enable Adwaita fonts";
  };

  config = lib.mkIf cfg.enable {
    fonts.fontconfig.enable = true;

     home.packages = with pkgs; [
      adwaita-fonts
    ];

    gtk.font.name = "Adwaita Sans";
  };
}
