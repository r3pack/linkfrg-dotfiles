from ignis import widgets
from ignis.services.hyprland import HyprlandService

hyprland = HyprlandService.get_default()


class WinTitle(widgets.Box):
    def __init__(self) -> None:
        super().__init__(
            css_classes=["wintitle", "unset"],
            child=[widgets.Label(
                ellipsize="end",
                max_width_chars=40,
                label=hyprland.active_window.bind("title"),
            )]
        )