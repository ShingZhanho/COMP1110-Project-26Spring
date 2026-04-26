## How to run

You should have Python installed on your device.
The program is tested on Python 3.14.
Other versions may work but not guaranteed.

1. **Clone the repository**
   ```shell
   git clone https://github.com/ShingZhanho/COMP1110-Project-26Spring.git
   cd COMP1110-Project-26Spring
   ```
2. **Install Python dependencies** (installing packages in a virtual environment is recommended)
   ```shell
   pip install -r requirements.txt
   ```
3. **Start the program**
   ```shell
   python -m campus_nav
   ```

## How to use

The campus navigator app is built with the library Textual, supporting both keyboard and mouse interaction.
Upon launching the app, you should see the following screen:

![App selector screenshot](images/screenshot_AppSelector.svg)

Click "continue" to access to the navigator

You can set your waypoints, preferences and configuration in this interface

For the "waypoints" part, you can use "Edit" to set the start point and end point. And you can use "ADD" and "Remove" to add and remove passing points.

For the "Preferences" part, you can choose your prederence here. After you choose the preference, the "X" will turn to green.

For the "Configuration" part, you can set your set your relative walking speed here.

After setting all the things here, you can click "go" in the bottom.

Then, you can get all the routes that meet your requirements.

You can click" "Details" to view the detail of the route.

## Each File Purpose

#### Root Directory
- **pyproject.toml / requirements.txt / requirements-dev.txt**: Define project metadata, build systems, and Python dependencies required to run and develop the application.
- **.gitignore**: Specifies intentionally untracked files to ignore (e.g., compiled Python files, virtual environments).
- **.github/workflows/**: Contains CI/CD pipelines for automating Python code checks, fetching data, and compiling LaTeX PDFs.

#### campus_nav/
- **__main__.py**: The global entry point of the project. It launches the `AppSelector` to let the user choose between the navigator and the data visualiser.
- **app_selector.py**: Provides the initial startup UI that allows users to select which sub-application to launch.
- **app_selector.tcss**: The Textual stylesheet defining the layout and styling for the app selector screen.
- **constants.py**: Stores global constants and configuration paths used throughout the application.
- **utils.py**: Contains shared utility and helper functions.

#### campus_nav/data/
- The two files under this route are datas for the navigator.

#### campus_nav/data_visualiser/
- **__init__.py**: Initializes the data visualiser submodule.
- **data_visualiser_app.py**: The main application class for the map data visualiser tool.
- **data_visualiser_app.tcss**: The stylesheet for arranging widgets in the visualiser application.
- **data_store.py**: Manages and processes the graph data specifically for visualization purposes.
- **gui_window.py**: Handles the graphical user interface window for the graph rendering.
- **web_assets/**: Contains the HTML template and bundled JavaScript libraries (e.g., Sigma.js) required to render the graph visually.

#### campus_nav/main_app/
- **__init__.py**: Imports MainApp from the submodule .main_app.
- **__main__.py**: Entry point of the application.
- **main_app.py**: The main window class of the navigator.
- **main_app.tcss**: Arrange the widgets in the Screen container.
- **route_engine.py**: The routing engine of the navigator. Compute optimal campus navigation routes based on user's requirements.

#### campus_nav/main_app/screens/
- **waypoint_selection_screen.py & .tcss**: The interface for users to specify their start point, end point, and any intermediate passing points.
- **configuration_screen.py & .tcss**: The interface for users to adjust walking speed and select path preferences (e.g., avoiding stairs, preferring lifts).
- **solutions_screen.py & .tcss**: Displays the list of calculated candidate routes that satisfy the user's criteria.
- **route_details_screen.py & .tcss**: Shows the step-by-step navigation details and cost breakdown of a selected route.

#### campus_nav/models/
- **__init__.py**: Import core classes.
- **campus_map.py**: Define the CampusMap class to represent and manage an undirected multigraph structure of the campus map.
- **edge.py**: Define the edge class, representing the connections between two nodes in the campus.
- **edge_type.py**: Define the edge type class, representing the type of edge between two nodes.
- **node.py**: Define the node class, storing the information related to the nodes.

#### Documentation & Reports
- **project_plan/**: Contains the LaTeX source code and settings for the project plan document.
- **project_report/**: Contains the LaTeX source code, output figures (`figs/`), and shell scripts (`pre_build.sh`) used to compile the final project report.
- **images/**: Stores image assets like screenshots used in this README.

## Sample Test Cases

### Basic Path Planning

| ID | Description | Input | Expected Output | Actual Result | Status |
|----|-------------|-------|------------------|---------------|--------|
| TC-01 | Normal shortest path | Start: CYMAmenitiesCtr_CYMCanteen, End: LawLibrary A, Preferences: avoid stairs, Configuration: speed multiplier: 1.0 | Returns path, stops, edges and time (without) | Three routes are output, each with a "no stairs" tag. When entering Details, the complete path can be seen, which matches reality. | ✅ Pass |
| TC-02 | Adding passing points | Start: CYMAmenitiesCtr_CYMCanteen, passing point: KKLeung_Building_LG2F, End: Swire_Building | The output route must pass through the point KKLeung_Building_LG2F | Two routes are output. In the details, the three locations CYMAmenitiesCtr_CYMCanteen, KKLeung_Building_LG2F, and Swire_Building all appear and are marked in green. | ✅ Pass |
| TC-03 | Start = End | Start: Bookstore, End: Bookstore | Users cannot select the same point for Start and End in the waypoint interface. | Same as expected | ✅ Pass |



### Preferences and Configuration

| ID | Description | Input | Expected Output | Actual Result | Status |
|----|-------------|-------|------------------|---------------|--------|
| TC-04 | Modify the walking speed multiplier| Start: Library_Extension, End: ChiWah_1F_North, Speed Multiplier = 1.5 | Estimated time = normal time/1.5 | When the speed multiplier is 1 (default state), the time is 1 minute and 41 seconds; when the speed multiplier is 1.5, the time is 1 minute and 7 seconds. | ✅ Pass |
| TC-05 | Select one preference| Start: Library_Extension, End: ChiWah_1F_North, Choose "Avoid Stairs" in the preference interface | No stairs in the output routes | Output three routes. None of the three routes have stairs, and the route 1 is the fastest. | ✅ Pass |
| TC-06 | Select more than one preference| Start: Library_Extension, End: ChiWah_1F_North, Choose "Prioritise Stair" and "Avoid Escalators"| Return routes without escalators and with stairs | Output four routes. The first route has stairs and no escalators. The other three routes also have no escalators, but due to constraints, they have no stairs either. The route 2 is the fastest.| ✅ Pass |

### Boundary & Exception Handling

| ID | Description | Input | Expected Output | Actual Result | Status |
|----|-------------|-------|------------------|---------------|--------|

