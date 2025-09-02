#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
from ignis import widgets
from ignis.app import IgnisApp
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace

hyprland = HyprlandService.get_default()
ignis_app = IgnisApp.get_initialized()


def is_main_desktop_file(desktop_file):
    name = desktop_file.stem.lower()
    return not any(x in name for x in ['url-handler', 'handler', 'wayland', 'wrapper'])


def get_best_desktop_match(search_term):
    # XDG base dirs
    data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")

    desktop_dirs = {Path(os.path.join(data_home, "applications"))}
    for d in data_dirs:
        desktop_dirs.add(Path(os.path.join(d, "applications")))

    all_matches = []
    for desktop_dir in desktop_dirs:
        if not desktop_dir.exists():
            continue
            
        for desktop_file in desktop_dir.glob("*.desktop"):
            try:
                content = desktop_file.read_text()
                if (f"Exec={search_term}" in content or 
                    f"StartupWMClass={search_term}" in content or
                    search_term.lower() in desktop_file.stem.lower()):
                    
                    info = {
                        "path": str(desktop_file),
                        "is_main": is_main_desktop_file(desktop_file),
                        "score": 0
                    }
                    
                    # Score matches (higher is better)
                    if f"StartupWMClass={search_term}" in content:
                        info["score"] += 3
                    if f"Exec={search_term}" in content:
                        info["score"] += 2
                    if search_term.lower() == desktop_file.stem.lower():
                        info["score"] += 4
                        
                    all_matches.append(info)
                    
            except (UnicodeDecodeError, PermissionError):
                continue
                
    if not all_matches:
        return None
        
    # Sort by: main entries first, then by score, then by path length
    all_matches.sort(key=lambda x: (
        -x['is_main'], 
        -x['score'],
        len(x['path'])
        )
    )
    
    return all_matches[0]


def get_desktop_info(desktop_path):
    info = {"icon": ""}
    try:
        with open(desktop_path, 'r') as f:
            for line in f:
                if line.startswith("Icon="):
                    info["icon"] = line.split("=", 1)[1].strip()
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        pass
    return info


def find_app_data_best_match(class_name):
    # Basic cache
    if class_name in TaskList.class_to_app_data:
        return TaskList.class_to_app_data[class_name]
    desktop = get_best_desktop_match(class_name)
    if desktop:
        desktop_info = get_desktop_info(desktop['path'])
        return {'icon': desktop_info['icon']}
    return None


def create_app_button(app, win_id):
    return widgets.Button(
                child=widgets.Icon(image=app['icon'], pixel_size=32),
                css_classes=["tasklist-item", "unset"],
                on_click=lambda self: focus_window(win_id)
            )


def focus_window(win_id):
    subprocess.run(
        ["hyprctl", "dispatch", "focuswindow", "address:" + win_id]
    )


def get_windows_from_workspace(workspace_id):
    return [window for window in hyprland.windows
            if window.workspace_id == workspace_id or not window.title]


class TaskListWorkspace(widgets.Box):
    def __init__(self, workspace: HyprlandWorkspace):
        super().__init__()

        self.workspace = workspace
        TaskList.workspace_tasklists[workspace.id] = self

        if workspace.id == hyprland.active_workspace.id:
            self.on_init()
    
    def on_init(self) -> None:
        windows_from_workspace = get_windows_from_workspace(self.workspace.id)

        if windows_from_workspace:
            for window in windows_from_workspace:
                class_name = window.class_name
                app_info = find_app_data_best_match(class_name)
                if app_info:
                    TaskList.running_apps[window.address] = app_info
                    TaskList.bind_win_close_event(window)

            self.sync()
    
    def sync(self):
        app_buttons = []

        for win_id, app in TaskList.running_apps.items():
            window = hyprland.get_window_by_address(win_id)
            if window and window.workspace_id == self.workspace.id:
                app_buttons.append(create_app_button(app, win_id))

        self.child = app_buttons


class TaskList(widgets.Box):
    running_apps = {}
    class_to_app_data = {}
    workspace_tasklists = {}

    @classmethod
    def bind_win_close_event(cls, window):
        window.connect('closed', lambda win: cls.on_win_closed(win))

    @classmethod
    def on_win_closed(cls, window):
        cls.running_apps.pop(window.address, None)
        workspace_id = window.workspace_id
        if workspace_id in cls.workspace_tasklists:
            cls.workspace_tasklists[workspace_id].sync()

    def on_win_add(self, window) -> None:
        # Skip windows without titles (they are temporary)
        if not window.title:
            return

        workspace_id = window.workspace_id
        class_name = window.class_name
        app_info = find_app_data_best_match(class_name)
        if app_info:
            self.running_apps[window.address] = app_info
            self.bind_win_close_event(window)
            if workspace_id in self.workspace_tasklists:
                self.workspace_tasklists[workspace_id].sync()

    def __init__(self):
        if hyprland.is_available:
            hyprland.connect("window_added", lambda x, window: self.on_win_add(window))

            child = [
                widgets.EventBox(
                    child=hyprland.bind_many(
                        ["workspaces", "active_workspace"],
                        transform=lambda workspaces, *_: [
                            TaskListWorkspace(i) for i in workspaces
                        ],
                    ),
                )
            ]
        else:
            child = []
        super().__init__(child=child)
