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
#### campus_nav/data 
- The two files under this route are datas for the navigator

#### campus_nav/main_app/__init__.py 
- Imports MainApp from the submodule .main_app 
#### campus_nav/main_app/__main__.py 
- Entry point of the application
#### campus_nav/main_app/main_app.py 
- The main window class of the navigator
#### campus_nav/main_app/main_app.tcss 
- Arrange the widgets in the Screen container
#### campus_nav/main_app/route_engine.py 
- The routing engine of the navigator. Compute optimal campus navigation routes based on user's requirements.


#### campus_nav/models/__init__.py 
- Import core classes
#### campus_nav/models/campus_map.py 
- Define the CampusMap class to represent and manage an undirected multigraph structure of the campus map
#### campus_nav/models/edge.py
- Define the edge class, representing the connections between two nodes in the campus.
#### campus_nav/models/edge_type.py
- Define the edge type class, representing the type of edge between two nodes.
#### campus_nav/models/node.py
- Define the node class, storing the information related to the nodes.


## Sample Test Cases
