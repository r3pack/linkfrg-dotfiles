from ignis import utils
from ignis.app import IgnisApp
from ignis.services.wallpaper import WallpaperService
from modules import (
    Bar,
    ControlCenter,
    Launcher,
    NotificationPopup,
    OSD,
    Powermenu,
    Settings,
)

app = IgnisApp.get_default()
WallpaperService.get_default()

app.add_icons(f"{utils.get_current_dir()}/icons")
app.apply_css(utils.get_current_dir() + "/style.scss")

utils.exec_sh("gsettings set org.gnome.desktop.interface gtk-theme Material")
utils.exec_sh("gsettings set org.gnome.desktop.interface icon-theme s4bba7")
utils.exec_sh(
    'gsettings set org.gnome.desktop.interface font-name "Noto Sans Regular 11"'
)
utils.exec_sh("hyprctl reload")

ControlCenter()

added_on_external_monitor = False
for i, monitor in enumerate(utils.get_monitors()):
    connector = monitor.get_property('connector')
    if any(x in connector for x in ('HDMI-', 'DVI-', 'USB-', 'DL-')):
        Bar(i)
        NotificationPopup(i)
        added_on_external_monitor = True

if added_on_external_monitor is False:
    Bar(0)
    NotificationPopup(0)

Launcher()
Powermenu()
OSD()
Settings()
