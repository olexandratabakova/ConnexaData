import pandas as pd
from dash import html
import networkx as nx
from styles import error_message_style
from config import *
from utils_viz.nodes_color import *
import community as community_louvain
import os

def normalize_text(text):
    return str(text).strip().lower()

def capitalize_first_letter(text):
    return text[0].upper() + text[1:] if text else text

def calculate_node_positions(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from([node['data']['id'] for node in nodes])
    G.add_edges_from([(edge['data']['source'], edge['data']['target']) for edge in edges])

    num_nodes = len(nodes)
    k = 10 + (num_nodes / 10)
    iterations = 100 + (num_nodes * 2)

    pos = nx.spring_layout(G, k=k, iterations=iterations, seed=42)

    for node in nodes:
        node_id = node['data']['id']
        node['position'] = {'x': pos[node_id][0] * 1000, 'y': pos[node_id][1] * 1000}

    return nodes

def cluster_data(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from([node['data']['id'] for node in nodes])
    G.add_edges_from([(edge['data']['source'], edge['data']['target']) for edge in edges])

    partition = community_louvain.best_partition(G)
    for node in nodes:
        node_id = node['data']['id']
        node['data']['cluster'] = partition.get(node_id, 0)

    return nodes, edges

def load_data(file_name, min_color, max_color, max_objects, avg_size):
    file_path = os.path.join(FILTERED_OUTPUT_DIR, file_name)

    if not os.path.exists(file_path):
        return [], [], html.Div(f"File {file_name} not found!", style=error_message_style)

    try:
        data = pd.read_csv(file_path, sep=';', header=None, encoding='utf-8', on_bad_lines='skip')
        data.columns = ["object_1", "object_2"]

        node_dict = {}
        edges = []
        degree_dict = {}

        for _, row in data.iterrows():
            source, target = map(normalize_text, [row["object_1"], row["object_2"]])

            for node in [source, target]:
                if node not in node_dict:
                    capitalized_label = capitalize_first_letter(node)
                    node_dict[node] = {'data': {'id': node, 'label': capitalized_label, 'merged_parts': [capitalized_label]}}
                    degree_dict[node] = 0

            if source != target:
                edges.append({'data': {'source': source, 'target': target}})
                degree_dict[source] += 1
                degree_dict[target] += 1

        existing_nodes = list(node_dict.keys())
        if existing_nodes:
            sorted_nodes = sorted(existing_nodes, key=lambda x: -len(x))
            merged_mapping = {}

            for node in sorted_nodes:
                for existing in sorted_nodes:
                    if existing == node or existing in merged_mapping:
                        continue
                    if existing in node:
                        merged_mapping[existing] = node

            new_node_dict = {}
            new_degree_dict = {}

            for original, merged in merged_mapping.items():
                if merged not in new_node_dict:
                    capitalized_label = capitalize_first_letter(merged)
                    new_node_dict[merged] = node_dict.get(merged, {'data': {'id': merged, 'label': capitalized_label, 'merged_parts': []}})
                    new_degree_dict[merged] = 0

                new_node_dict[merged]['data']['merged_parts'].extend(node_dict[original]['data']['merged_parts'])

            for node in existing_nodes:
                if node not in merged_mapping and node not in new_node_dict:
                    new_node_dict[node] = node_dict[node]
                    new_degree_dict[node] = 0

            node_dict = new_node_dict
            degree_dict = new_degree_dict

            edge_set = set()
            new_edges = []
            for edge in edges:
                source = edge['data']['source']
                target = edge['data']['target']
                new_source = merged_mapping.get(source, source)
                new_target = merged_mapping.get(target, target)
                if new_source == new_target:
                    continue
                if new_source > new_target:
                    new_source, new_target = new_target, new_source
                if (new_source, new_target) not in edge_set:
                    edge_set.add((new_source, new_target))
                    new_edges.append({'data': {'source': new_source, 'target': new_target}})
            edges = new_edges

            degree_dict = {node: 0 for node in node_dict}
            for edge in edges:
                source = edge['data']['source']
                target = edge['data']['target']
                degree_dict[source] += 1
                degree_dict[target] += 1

        sorted_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
        top_nodes = [node[0] for node in sorted_nodes[:max_objects]]

        filtered_nodes = [node_dict[node] for node in top_nodes if node in node_dict]
        filtered_edges = [edge for edge in edges if edge['data']['source'] in top_nodes and edge['data']['target'] in top_nodes]

        min_degree, max_degree = min(degree_dict.values(), default=0), max(degree_dict.values(), default=0)

        for node in filtered_nodes:
            node_id = node['data']['id']
            degree = degree_dict.get(node_id, 0)
            size, color, border_color = calculate_node_style(degree, min_degree, max_degree, min_color, max_color, avg_size)
            node['data'].update({
                'size': size,
                'color': color,
                'border_color': border_color
            })

        for edge in filtered_edges:
            source, target = edge['data']['source'], edge['data']['target']
            edge['data']['color'] = calculate_edge_style(degree_dict[source], degree_dict[target], min_degree, max_degree, min_color, max_color)

        filtered_nodes = calculate_node_positions(filtered_nodes, filtered_edges)
        nodes, edges = cluster_data(filtered_nodes, filtered_edges)

        for node in nodes:
            node['data']['color'] = str(node['data']['color'])
            node['data']['cluster'] = str(node['data']['cluster'])

        return nodes, edges, None

    except Exception as e:
        return [], [], html.Div(f"Error loading data: {e}", style=error_message_style)