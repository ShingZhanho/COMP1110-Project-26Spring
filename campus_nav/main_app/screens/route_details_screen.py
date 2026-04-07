from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from ..route_engine import Route, format_time


class RouteDetailsScreen(Screen):
    """Displays step-by-step details of a single route."""

    CSS_PATH = "route_details_screen.tcss"

    def __init__(self, route: Route) -> None:
        super().__init__()
        self._route = route

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="details_container"):
            yield Button("← Back", id="btn_back", variant="default")
            badges = ", ".join(self._route.labels) if self._route.labels else ""
            yield Static(f"[b]Route Details[/b]   {badges}", id="details_title")
            yield Static(
                f"Total time: {format_time(self._route.total_cost)}  •  "
                f"Stops: {self._route.num_stops}  •  "
                f"Edges: {len(self._route.steps)}",
                id="details_summary",
            )
            with VerticalScroll(id="steps_scroll"):
                for i, step in enumerate(self._route.steps):
                    if i == 0:
                        yield Static(
                            f"● {step.from_node.node_id}"
                            + (f"  [dim]{step.from_node.description}[/dim]" if step.from_node.description else ""),
                            classes="step-node",
                        )
                    yield Static(
                        f"  │  {step.edge.edge_type.value} · {format_time(step.adjusted_cost)}"
                        f" (base {step.edge.time_cost}s)",
                        classes="step-edge",
                    )
                    yield Static(
                        f"● {step.to_node.node_id}"
                        + (f"  [dim]{step.to_node.description}[/dim]" if step.to_node.description else ""),
                        classes="step-node",
                    )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back":
            self.app.pop_screen()
