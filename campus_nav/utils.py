import csv
from pathlib import Path

from .models import *

NODES_CSV_PATH = "data/NODES.csv"
EDGES_CSV_PATH = "data/EDGES.csv"

def construct_map_from_csv(nodes_file: str = None, edges_file: str = None) -> CampusMap:
    """
    Constructs a CampusMap object from the given CSV files containing nodes and edges information.
    :param nodes_file: The path to the CSV file containing nodes information. If None, it defaults to NODES_CSV_PATH.
    :param edges_file: The path to the CSV file containing edges information. If None, it defaults to EDGES_CSV_PATH.
    :return: The constructed CampusMap object.
    """
    if nodes_file is None: nodes_file = Path(__file__).resolve().parent / NODES_CSV_PATH
    if edges_file is None: edges_file = Path(__file__).resolve().parent / EDGES_CSV_PATH

    campus_map: CampusMap = CampusMap()

    # Read nodes
    nodes_col_keys = ["node_id", "node_description"]
    with open(str(nodes_file), mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            node_id, node_description = (row[key] for key in nodes_col_keys)
            campus_map.add_node(Node(node_id, node_description))

    # Read edges
    edges_col_keys = ["node_1_id", "node_2_id", "edge_type", "time_cost"]
    with open(str(edges_file), mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            node1_id, node2_id, edge_type, edge_time_cost = (row[key] for key in edges_col_keys)
            edge_type = EdgeType(edge_type)
            edge_time_cost = int(edge_time_cost)
            campus_map.add_edge(node1_id, node2_id, edge_type, edge_time_cost)

    return campus_map