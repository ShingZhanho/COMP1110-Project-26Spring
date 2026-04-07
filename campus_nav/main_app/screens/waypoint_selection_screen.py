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
        self._filtered_nodes: list[tuple[str, str]] = []
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
        self._filtered_nodes = [
            (nid, desc) for nid, desc in self._all_nodes
            if not ft or ft in nid.lower() or ft in desc.lower()
        ]
        for node_id, desc in self._filtered_nodes:
            display = node_id
            if desc:
                display += f" ({desc})"
            lv.append(ListItem(Label(display)))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search_input":
            self._populate_list(event.value)
            self._selected_id = None
            self.query_one("#btn_confirm", Button).disabled = True

    def _node_id_at(self, index: int) -> str | None:
        if 0 <= index < len(self._filtered_nodes):
            return self._filtered_nodes[index][0]
        return None

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        lv = self.query_one("#wp_list", ListView)
        nid = self._node_id_at(lv.index) if lv.index is not None else None
        if nid is not None:
            self._selected_id = nid
            self.query_one("#btn_confirm", Button).disabled = False

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        lv = self.query_one("#wp_list", ListView)
        nid = self._node_id_at(lv.index) if lv.index is not None else None
        if nid is not None:
            self.dismiss(nid)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_confirm":
            if self._selected_id is not None:
                self.dismiss(self._selected_id)
        elif event.button.id == "btn_cancel":
            self.dismiss(None)
