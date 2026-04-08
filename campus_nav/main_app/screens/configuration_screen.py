from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from ..route_engine import Preferences, find_candidate_routes


class ConfigurationScreen(Screen):
    """First screen: configure waypoints, preferences and speed multiplier."""

    CSS_PATH = "configuration_screen.tcss"
    BINDINGS = [
        ("ctrl+g", "continue", "Go"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="config_panels"):
            # Left panel – waypoints
            with Vertical(id="waypoints_panel"):
                yield Static("Waypoints", classes="panel-title")
                yield ListView(id="waypoints_list")
                with Horizontal(classes="button-row"):
                    yield Button("Add", id="btn_add_wp", variant="default")
                    yield Button("Remove", id="btn_remove_wp", variant="default")
                with Horizontal(classes="button-row"):
                    yield Button("Edit", id="btn_edit_wp", variant="default")
                with Horizontal(classes="button-row"):
                    yield Button("▲ Up", id="btn_move_up", variant="default")
                    yield Button("▼ Down", id="btn_move_down", variant="default")

            # Middle panel – preferences
            with Vertical(id="preferences_panel"):
                yield Static("Preferences", classes="panel-title")
                yield Checkbox("Avoid Stairs", id="chk_avoid_stairs")
                yield Checkbox("Prioritise Stairs", id="chk_prioritise_stairs")
                yield Checkbox("Avoid Escalators", id="chk_avoid_escalators")
                yield Checkbox("Prefer Lifts", id="chk_prefer_lifts")
                yield Checkbox("Accessible Route", id="chk_accessible")

            # Right panel – configuration
            with Vertical(id="config_panel"):
                yield Static("Configuration", classes="panel-title")
                yield Label("Speed Multiplier:")
                with Horizontal(id="speed_row"):
                    yield Button("-", id="btn_speed_down", variant="default")
                    yield Input(value="1.0", id="input_speed")
                    yield Button("+", id="btn_speed_up", variant="default")
                yield Static("", id="lbl_speed_hint")

        yield Button("Go", id="btn_go", variant="primary", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_waypoint_list()
        self._update_speed_hint()

    # ── Waypoint list ──────────────────────────────────────────────

    def _refresh_waypoint_list(self) -> None:
        lv = self.query_one("#waypoints_list", ListView)
        lv.clear()
        total = len(self.app.waypoints)
        for i, wp in enumerate(self.app.waypoints):
            role = "Start" if i == 0 else ("End" if i == total - 1 else f"Via {i}")
            name = wp if wp else "(not set)"
            lv.append(ListItem(Label(f"[b]{role}:[/b] {name}")))
        self._update_go_button()

    def _open_waypoint_selection(self, index: int) -> None:
        excluded = {w for j, w in enumerate(self.app.waypoints) if w is not None and j != index}
        from .waypoint_selection_screen import WaypointSelectionScreen

        def callback(result: str | None) -> None:
            if result is not None:
                self.app.waypoints[index] = result
                self._refresh_waypoint_list()

        self.app.push_screen(WaypointSelectionScreen(excluded), callback=callback)

    # ── Preference handling ────────────────────────────────────────

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        avoid = self.query_one("#chk_avoid_stairs", Checkbox)
        prioritise = self.query_one("#chk_prioritise_stairs", Checkbox)
        lifts = self.query_one("#chk_prefer_lifts", Checkbox)
        escalators = self.query_one("#chk_avoid_escalators", Checkbox)

        if event.checkbox.id == "chk_accessible":
            if event.value:
                avoid.value = True
                avoid.disabled = True
                prioritise.value = False
                prioritise.disabled = True
                escalators.value = True
                escalators.disabled = True
                lifts.value = True
                lifts.disabled = True
            else:
                avoid.disabled = False
                prioritise.disabled = False
                escalators.disabled = False
                lifts.disabled = False
        elif event.checkbox.id == "chk_avoid_stairs" and event.value:
            prioritise.value = False
        elif event.checkbox.id == "chk_prioritise_stairs" and event.value:
            avoid.value = False
        self._sync_preferences()
        self._update_go_button()

    def _sync_preferences(self) -> None:
        self.app.preferences = Preferences(
            avoid_stairs=self.query_one("#chk_avoid_stairs", Checkbox).value,
            avoid_escalators=self.query_one("#chk_avoid_escalators", Checkbox).value,
            prefer_lifts=self.query_one("#chk_prefer_lifts", Checkbox).value,
            prioritise_stairs=self.query_one("#chk_prioritise_stairs", Checkbox).value,
            accessible=self.query_one("#chk_accessible", Checkbox).value,
        )

    # ── Speed multiplier ──────────────────────────────────────────

    def _current_speed(self) -> float | None:
        try:
            val = float(self.query_one("#input_speed", Input).value)
            return val if val > 0 else None
        except ValueError:
            return None

    def _update_speed_hint(self) -> None:
        speed = self._current_speed()
        hint = self.query_one("#lbl_speed_hint", Static)
        if speed is None:
            hint.update("[red]Invalid speed[/red]")
        elif speed > 1:
            hint.update(f"Walking {speed:.1f}× faster")
        elif speed < 1:
            hint.update(f"Walking {speed:.1f}× slower")
        else:
            hint.update("Normal walking speed")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "input_speed":
            speed = self._current_speed()
            if speed is not None:
                self.app.speed_multiplier = speed
            self._update_speed_hint()
            self._update_go_button()

    def _adjust_speed(self, delta: float) -> None:
        speed = self._current_speed()
        if speed is None:
            speed = 1.0
        speed = max(0.1, round(speed + delta, 1))
        self.query_one("#input_speed", Input).value = str(speed)

    # ── Go button ─────────────────────────────────────────────────

    def _is_config_valid(self) -> bool:
        wps = self.app.waypoints
        if len(wps) < 2:
            return False
        if any(w is None for w in wps):
            return False
        if len(set(wps)) != len(wps):
            return False
        if self._current_speed() is None:
            return False
        return True

    def _update_go_button(self) -> None:
        self.query_one("#btn_go", Button).disabled = not self._is_config_valid()

    # ── Button handlers ───────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn_add_wp":
            if len(self.app.waypoints) < 5:
                self.app.waypoints.insert(len(self.app.waypoints) - 1, None)
                self._refresh_waypoint_list()
                new_index = len(self.app.waypoints) - 2
                self._open_waypoint_selection(new_index)
        elif bid == "btn_edit_wp":
            lv = self.query_one("#waypoints_list", ListView)
            if lv.index is not None:
                self._open_waypoint_selection(lv.index)
        elif bid == "btn_remove_wp":
            lv = self.query_one("#waypoints_list", ListView)
            if lv.index is not None and len(self.app.waypoints) > 2:
                self.app.waypoints.pop(lv.index)
                self._refresh_waypoint_list()
        elif bid == "btn_move_up":
            lv = self.query_one("#waypoints_list", ListView)
            if lv.index is not None and lv.index > 0:
                idx = lv.index
                self.app.waypoints[idx], self.app.waypoints[idx - 1] = (
                    self.app.waypoints[idx - 1],
                    self.app.waypoints[idx],
                )
                self._refresh_waypoint_list()
                lv.index = idx - 1
        elif bid == "btn_move_down":
            lv = self.query_one("#waypoints_list", ListView)
            if lv.index is not None and lv.index < len(self.app.waypoints) - 1:
                idx = lv.index
                self.app.waypoints[idx], self.app.waypoints[idx + 1] = (
                    self.app.waypoints[idx + 1],
                    self.app.waypoints[idx],
                )
                self._refresh_waypoint_list()
                lv.index = idx + 1
        elif bid == "btn_speed_down":
            self._adjust_speed(-0.1)
        elif bid == "btn_speed_up":
            self._adjust_speed(0.1)
        elif bid == "btn_go":
            self._sync_preferences()
            routes = find_candidate_routes(
                self.app.campus_map,
                self.app.waypoints,
                self.app.preferences,
                self.app.speed_multiplier,
            )
            from .solutions_screen import SolutionsScreen

            self.app.push_screen(SolutionsScreen(routes))

    # ── Keyboard bindings ───────────────────────────────────────────────
    
    def action_continue(self) -> None:
        if not self.query_one("#btn_go", Button).disabled:
            self.on_button_pressed(Button.Pressed(self.query_one("#btn_go", Button)))
