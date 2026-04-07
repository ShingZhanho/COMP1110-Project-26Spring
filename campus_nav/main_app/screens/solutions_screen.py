from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

from ..route_engine import Route, format_time


class SolutionsScreen(Screen):
    """Displays the computed candidate routes."""

    CSS_PATH = "solutions_screen.tcss"

    def __init__(self, routes: list[Route]) -> None:
        super().__init__()
        self._routes = routes

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="solutions_container"):
            yield Button("← Back", id="btn_back", variant="default")
            if not self._routes:
                yield Static("[b]No routes found.[/b]\nTry adjusting your preferences.", id="no_routes")
            else:
                with VerticalScroll(id="routes_scroll"):
                    for i, route in enumerate(self._routes):
                        with Vertical(classes="route-card", id=f"route_card_{i}"):
                            yield Static(f"[b]Route {i + 1}[/b]", classes="route-title")
                            time_str = format_time(route.total_cost)
                            orig_str = format_time(route.total_original_cost)
                            yield Label(
                                f"Time: {time_str} (base: {orig_str})  •  "
                                f"Stops: {route.num_stops}  •  "
                                f"Edges: {len(route.steps)}"
                            )
                            with Horizontal(classes="badges-row"):
                                for lbl in route.labels:
                                    css_class = _badge_class(lbl)
                                    yield Static(lbl, classes=f"badge {css_class}")
                            yield Button("Details ▶", id=f"btn_detail_{i}", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn_back":
            self.app.pop_screen()
        elif bid and bid.startswith("btn_detail_"):
            idx = int(bid.split("_")[-1])
            from .route_details_screen import RouteDetailsScreen

            self.app.push_screen(RouteDetailsScreen(self._routes[idx]))


def _badge_class(label: str) -> str:
    mapping = {
        "Fastest": "badge-fastest",
        "Fewest Stops": "badge-fewest",
        "No Stairs": "badge-no-stairs",
        "Has Stairs": "badge-has-stairs",
        "Uses Lifts": "badge-uses-lifts",
        "Uses Escalators": "badge-uses-escalators",
    }
    return mapping.get(label, "badge-default")
