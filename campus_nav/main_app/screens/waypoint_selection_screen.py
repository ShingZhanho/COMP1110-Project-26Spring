from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static


class WaypointSelectionScreen(Screen):
    """Screen for selecting a waypoint from the available nodes."""

    CSS_PATH = "waypoint_selection_screen.tcss"

    def __init__(self, excluded_ids: set[str]) -> None:
        super().__init__()
        self._excluded_ids = excluded_ids
        self._all_nodes: list[tuple[str, str]] = []  # (node_id, description)
        self._selected_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="wp_sel_container"):
            yield Input(placeholder="Search waypoints...", id="search_input")
            yield ListView(id="wp_list")
            with Horizontal(id="wp_sel_buttons"):
                yield Button("Confirm", id="btn_confirm", variant="primary", disabled=True)
                yield Button("Cancel", id="btn_cancel")
        yield Footer()

    def on_mount(self) -> None:
        nodes = sorted(self.app.campus_map.get_nodes(), key=lambda n: n.node_id)
        self._all_nodes = [
            (n.node_id, n.description)
            for n in nodes
            if n.node_id not in self._excluded_ids
        ]
        self._populate_list()

    def _populate_list(self, filter_text: str = "") -> None:
        lv = self.query_one("#wp_list", ListView)
        lv.clear()
        ft = filter_text.lower()
        for node_id, desc in self._all_nodes:
            if ft and ft not in node_id.lower() and ft not in desc.lower():
                continue
            display = node_id
            if desc:
                display += f" ({desc})"
            lv.append(ListItem(Label(display), id=f"wps_{node_id}"))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search_input":
            self._populate_list(event.value)
            self._selected_id = None
            self.query_one("#btn_confirm", Button).disabled = True

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id and event.item.id.startswith("wps_"):
            self._selected_id = event.item.id[4:]
            self.query_one("#btn_confirm", Button).disabled = False

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id and event.item.id.startswith("wps_"):
            self.dismiss(event.item.id[4:])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_confirm":
            if self._selected_id is not None:
                self.dismiss(self._selected_id)
        elif event.button.id == "btn_cancel":
            self.dismiss(None)
