import os
from ignis import utils
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
from ignis.css_manager import CssManager, CssInfoPath
from ignis.icon_manager import IconManager
from user_options import user_options

icon_manager = IconManager.get_default()
css_manager = CssManager.get_default()
WallpaperService.get_default()


def format_scss_var(name: str, val: str) -> str:
    return f"${name}: {val};\n"


def patch_style_scss(path: str) -> str:
    with open(path) as file:
        contents = file.read()

    scss_colors = ""

    for key, value in user_options.material.colors.items():
        scss_colors += format_scss_var(key, value)

    string = (
        format_scss_var("darkmode", str(user_options.material.dark_mode).lower())
        + scss_colors
        + contents
    )

    return utils.sass_compile(
        string=string, extra_args=["--load-path", utils.get_current_dir()]
    )


css_manager.apply_css(
    CssInfoPath(
        name="main",
        path=os.path.join(utils.get_current_dir(), "style.scss"),
        compiler_function=patch_style_scss,
    )
)

icon_manager.add_icons(os.path.join(utils.get_current_dir(), "icons"))

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
