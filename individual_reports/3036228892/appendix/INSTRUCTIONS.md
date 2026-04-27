# LLM Instructions

This document provides instructions for an LLM agent to build an application.
The agent should follow these instructions to finish the implementation.

## General Guidelines

1. Read the entire instructions carefully before starting the implementation.
2. Read the entire codebase to understand the existing structure and how the new feature should fit in.
3. Follow the coding style and conventions (including commit message format) used in this repository.
4. Write clean, modular code. Documentation should be only at an appropriate level and should be concise. No verbose comments.
5. As you build, make incremental commits. Before committing, ensure that the code is working but no unit tests are required. Do not make big commits that include multiple features or refactors. Each commit should be focused on a single change or addition.
6. When implementing, if you encounter any ambiguities or uncertainties in the instructions, ask for clarification before proceeding. Do not make assumptions that are not stated in the instructions.

## Task Overview

You will be writing a Python app with the module name `campus_nav.main_app`.
The app's class name should be `MainApp`.
This app will be similar to Google Maps but for a campus.
Users can select start and end points on the campus map, and toggle on/off different preferences (e.g. avoid stairs, etc.), and optionally add intermediate points.
The app will then calculate several candidate routes and display them as a list.
The app should be implemented using Textual and completely text-based (no graphical map rendering is required).
The app should have several screens.
The details of the implementation and features are described below.

### Architecture

1. Create a self-contained module named `campus_nav.main_app` and expose necessary classes and functions in its `__init__.py`.
2. The app will depend on Textual. Data for the campus map and data classes are already defined in the `campus_nav.models` module. Use those, and extend them INTERNALLY as needed, but do not modify the existing data classes, unless they have bugs.
3. The app should be structured with a main `MainApp` class that manages the overall application flow and state, and separate screen classes for each distinct screen in the app (e.g. `RouteSelectionScreen`, `RouteDisplayScreen`, etc.).
4. The app should not be built with GUI frameworks. It should be entirely text-based using Textual's widgets and layout system. Custom widgets can be created.
5. Arrange files in submodules as needed for better organization, but keep the overall structure simple and intuitive. For example, you might have a `screens` submodule for the different screen classes, and a `widgets` submodule for any custom widgets you create. `.tcss` files should live within the same directory as the `.py` files that use them, with the same base name (e.g. `main_app.py` and `main_app.tcss`).
6. Business logic need to be separated from UI code as much as possible. The screen classes should primarily handle rendering and user interaction, while the route calculation logic should be in separate functions or classes.

### Screens

Name the screens as appropriate, but they must all be suffixed with `Screen`.

1. **Configuration Screen**: This is the first screen that the app launches into. It will have three sections, arranged horizontally:
    - Waypoint selection: A list of waypoints (start, intermediate, end) that the user can edit. The user can have at most 5 points (including start and end). Points must be distinct. There should be buttons at the bottom to add/remove points, and buttons to move points up/down the list. Each point in the list can be focused to highlight and modified using the buttons. No edit button is needed, just select the point and use the add/remove/move buttons.
    - Preferences: A list of toggleable preferences (e.g. avoid stairs, prefer lifts, accessible route, etc.).
    The app should handle preferences that are mutually exclusive automatically if any.
    - Configuration: A customisable "speed multiplier" set at 1.0 by default, that the user can adjust to simulate faster or slower walking speeds. A larger multiplier means faster walking, so the time cost for each edge will be adjusted accordingly in the route calculations. Also, different edge types should receive different intensity of the multiplier adjustment (e.g. stairs might be more affected by the speed multiplier than flat paths and lifts are not affected at all).
    - A "Go" button at the bottom that becomes enabled when the configuration is valid (e.g. at least start and end points are set, preferences are consistent, etc.). The button spans the entire width of the screen and is centered horizontally.

2. **Waypoint Selection Screen**: This screen presents a list of all available waypoints, sorted alphabetically, with a search input at the top to filter the list. The list items are selectable, and can be confirmed with a "Confirm" button at the bottom. When a waypoint is selected and confirmed, the app should return to the Configuration Screen and update the selected waypoint. Only those waypoints that are not already selected in the Configuration Screen should be selectable in this screen.

3. **Solutions Screen**: This screen displays the calculated routes based on the user's configuration.
On top-left there should be a "Back" button to return to the Configuration Screen.
The main area of the screen should be a scrollable list of route options, each showing a summary of the route (e.g. total time, number of stops, etc.) and some labels or badges indicating the features of the route (e.g. has stairs, no stairs, fastest, least stops, etc.).
There is a "Details" button for each route that the user can select to view more detailed information about the route.

4. **Route Details Screen**: This screen shows the details of a selected route from the Solutions Screen. It should include a top-down list of waypoints in the route, with edge information between them (e.g. time cost, edge type, etc.). There should be a "Back" button to return to the Solutions Screen.