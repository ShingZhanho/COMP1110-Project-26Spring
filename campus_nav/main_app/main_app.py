from textual.app import App

from ..utils import construct_map_from_csv
from .route_engine import Preferences
from .screens import ConfigurationScreen


class MainApp(App):
    """Campus navigation application."""

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]
    CSS_PATH = "main_app.tcss"

    def __init__(self) -> None:
        super().__init__()
        self.campus_map = construct_map_from_csv()
        self.waypoints: list[str | None] = [None, None]
        self.preferences = Preferences()
        self.speed_multiplier: float = 1.0

    def on_mount(self) -> None:
        self.theme = "textual-dark"
        self.title = "Campus Navigator"
        self.sub_title = "Route Planner"
        self.push_screen(ConfigurationScreen())

    def action_quit(self) -> None:
        self.exit()
