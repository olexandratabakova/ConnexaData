from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import pandas as pd
import os
from styles import (
    visualization_layout_style,
    visualization_cytoscape_style,
    button_style,
    error_message_style,
    button_style_backtohome,
    button_style2,
    sidebar_style,
    main_content_style,
    width_slider_style
)
import networkx as nx
import community as community_louvain
import dash_daq as daq
from config import FILTERED_OUTPUT_DIR

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb).upper()

IMAGES_DIR = os.path.join(FILTERED_OUTPUT_DIR, "images")
CSV_DIR = os.path.join(FILTERED_OUTPUT_DIR, "tables_filtered_csv")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

def get_filtered_files():
    return [f for f in os.listdir(FILTERED_OUTPUT_DIR) if f.endswith('.txt')]

def normalize_text(text):
    return str(text).strip().lower()

def interpolate_color(min_color, max_color, normalized_value):
    min_r, min_g, min_b = hex_to_rgb(min_color)
    max_r, max_g, max_b = hex_to_rgb(max_color)
    r = min_r + (max_r - min_r) * normalized_value
    g = min_g + (max_g - min_g) * normalized_value
    b = min_b + (max_b - min_b) * normalized_value
    return rgb_to_hex((int(r), int(g), int(b)))

def calculate_node_style(degree, min_degree, max_degree, min_color, max_color, avg_size):
    normalized_degree = (degree - min_degree) / (max_degree - min_degree) if max_degree > min_degree else 0
    size = avg_size * (1 + normalized_degree)
    color = interpolate_color(min_color, max_color, normalized_degree)
    border_color = interpolate_color(min_color, max_color, normalized_degree * 0.8)
    return size, color, border_color

def calculate_edge_style(source_degree, target_degree, min_degree, max_degree, min_color, max_color):
    avg_degree = (source_degree + target_degree) / 2
    normalized_degree = (avg_degree - min_degree) / (max_degree - min_degree) if max_degree > min_degree else 0
    color = interpolate_color(min_color, max_color, normalized_degree)
    return color

def cluster_data(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from([node['data']['id'] for node in nodes])
    G.add_edges_from([(edge['data']['source'], edge['data']['target']) for edge in edges])

    partition = community_louvain.best_partition(G)
    for node in nodes:
        node_id = node['data']['id']
        node['data']['cluster'] = partition.get(node_id, 0)

    return nodes, edges

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
                    node_dict[node] = {'data': {'id': node, 'label': node.title()}}
                    degree_dict[node] = 0

            if source != target:
                edges.append({'data': {'source': source, 'target': target}})
                degree_dict[source] += 1
                degree_dict[target] += 1

        sorted_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
        top_nodes = [node[0] for node in sorted_nodes[:max_objects]]

        filtered_nodes = [node_dict[node] for node in top_nodes]
        filtered_edges = [edge for edge in edges if edge['data']['source'] in top_nodes and edge['data']['target'] in top_nodes]

        min_degree, max_degree = min(degree_dict.values()), max(degree_dict.values())

        for node in filtered_nodes:
            node_id = node['data']['id']
            degree = degree_dict[node_id]
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

def create_layout(file_name, min_color, max_color, max_objects, avg_size):
    nodes, edges, error_message = load_data(file_name, min_color, max_color, max_objects, avg_size)
    if error_message:
        return error_message

    return html.Div(
        style=visualization_layout_style,
        children=[
            cyto.Cytoscape(
                id='cytoscape-graph',
                elements=nodes + edges,
                layout={'name': 'preset'},
                style=visualization_cytoscape_style,
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'content': 'data(label)',
                            'background-color': 'data(color)',
                            'width': 'data(size)',
                            'height': 'data(size)',
                            'border-color': 'data(border_color)',
                            'border-width': '2px',
                            'text-halign': 'center',
                            'text-valign': 'center',
                            'font-family': 'Helvetica'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'line-color': 'data(color)',
                            'target-arrow-shape': 'triangle',
                            'target-arrow-color': 'data(color)',
                            'font-family': 'Helvetica'
                        }
                    }
                ]
            ),
            html.Div(
                html.A("Back to Home", href="/", style={**button_style, **button_style_backtohome}),
                style={'textAlign': 'center', 'marginTop': '20px'}
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        Output('visualization-content', 'children'),
        Input('apply-button', 'n_clicks'),
        State('file-dropdown', 'value'),
        State('min-color-picker', 'value'),
        State('max-color-picker', 'value'),
        State('max-objects-slider', 'value'),
        State('avg-size-slider', 'value')
    )
    def update_visualization(n_clicks, selected_file, min_color, max_color, max_objects, avg_size):
        if n_clicks is None or not selected_file:
            return html.Div("Please select a file and click 'Apply' to visualize.", style=error_message_style)
        return create_layout(selected_file, min_color['hex'], max_color['hex'], max_objects, avg_size)

    @app.callback(
        Output('cytoscape-graph', 'stylesheet'),
        Input('apply-button', 'n_clicks'),
        State('text-size-slider', 'value'),
        State('node-size-slider', 'value'),
        State('edge-thickness-slider', 'value')
    )
    def update_stylesheet(n_clicks, text_size, node_size, edge_thickness):
        if n_clicks is None:
            return []

        return [
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'font-size': f"{text_size}px",
                    'background-color': 'data(color)',
                    'width': 'data(size)',
                    'height': 'data(size)',
                    'border-color': 'data(border_color)',
                    'border-width': '2px',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    'font-family': 'Helvetica'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': 'data(color)',
                    'width': f'{edge_thickness}',
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': 'data(color)',
                    'font-family': 'Helvetica'
                }
            }
        ]

    @app.callback(
        Output('cytoscape-graph', 'layout'),
        Input('layout-dropdown', 'value')
    )
    def update_layout(selected_layout):
        return {'name': selected_layout}

    @app.callback(
        Output('sidebar', 'style'),
        Input('width-slider', 'value')
    )
    def update_sidebar_width(width):
        return {**sidebar_style, 'width': f'{width}%'}

layout = html.Div(
    style={
        'display': 'flex',
        'flexDirection': 'row',
        'height': '100vh',
        'fontFamily': 'Helvetica',
        'background': 'linear-gradient(180deg, #E2F9FB, #ffffff)',
    },
    children=[
        # Бічна панель
        html.Div(
            id='sidebar',
            style=sidebar_style,
            children=[
                html.H3("ConnexaData", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginBottom': '20px'}),

                html.Label("Sidebar Width", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='width-slider',
                        min=20,
                        max=50,
                        step=5,
                        value=40,
                        marks={i: f'{i}%' for i in range(20, 51, 5)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style=width_slider_style
                ),

                dcc.Dropdown(
                    id='file-dropdown',
                    options=[{'label': f, 'value': f} for f in get_filtered_files()],
                    placeholder="Select a file",
                    style={
                        'width': '100%',
                        'marginBottom': '20px',
                        'fontFamily': 'Helvetica',
                        'whiteSpace': 'normal',
                    },
                    clearable=False,
                ),

                dcc.Dropdown(
                    id='layout-dropdown',
                    options=[
                        {'label': 'Random', 'value': 'random'},
                        {'label': 'Preset', 'value': 'preset'},
                        {'label': 'Grid', 'value': 'grid'},
                        {'label': 'Circle', 'value': 'circle'},
                        {'label': 'Concentric', 'value': 'concentric'},
                        {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                        {'label': 'Cose', 'value': 'cose'}
                    ],
                    value='random',
                    placeholder="Select a layout",
                    style={
                        'width': '100%',
                        'marginBottom': '20px',
                        'fontFamily': 'Helvetica',
                        'whiteSpace': 'normal',
                    },
                    clearable=False,
                ),

                html.Label("Text Size", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='text-size-slider',
                        min=10,
                        max=30,
                        step=1,
                        value=12,
                        marks={i: str(i) for i in range(10, 31, 5)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Node Size", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='node-size-slider',
                        min=10,
                        max=150,
                        step=10,
                        value=50,
                        marks={i: str(i) for i in range(10, 151, 20)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Edge Thickness", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='edge-thickness-slider',
                        min=1,
                        max=10,
                        step=1,
                        value=2,
                        marks={i: str(i) for i in range(1, 11, 1)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px', 'width': '100%'},
                    children=[
                        html.Label("Min Color", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginRight': '10px'}),
                        daq.ColorPicker(
                            id='min-color-picker',
                            value=dict(hex='#FF69B4'),
                            style={'marginBottom': '20px', 'width': '100%'}
                        )
                    ]
                ),
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px', 'width': '100%'},
                    children=[
                        html.Label("Max Color", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginRight': '10px'}),
                        daq.ColorPicker(
                            id='max-color-picker',
                            value=dict(hex='#1E90FF'),
                            style={'marginBottom': '20px', 'width': '100%'}
                        )
                    ]
                ),

                html.Label("Max Objects", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='max-objects-slider',
                        min=10,
                        max=500,
                        step=10,
                        value=50,
                        marks={i: str(i) for i in range(10, 501, 50)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Average Node Size", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='avg-size-slider',
                        min=10,
                        max=100,
                        step=5,
                        value=30,
                        marks={i: str(i) for i in range(10, 101, 10)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Div(
                    style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%'},
                    children=[
                        html.Button("Apply", id='apply-button', style={**button_style2, 'marginTop': '20px', 'width': '100%'}),
                        html.Button("Save as table (.csv)", id='save-table-button', style={**button_style2, 'marginTop': '10px', 'width': '100%'}),
                    ]
                ),
            ]
        ),

        html.Div(
            id='main-content',
            style=main_content_style,
            children=[
                html.Div(id='visualization-content')
            ]
        )
    ]
)