import os
from collections import Counter
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import networkx as nx
from networkx.algorithms import community
from config import FILTERED_OUTPUT_DIR

from styles import common_styles, h1_style, button_style_backtohome

def count_occurrences(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().splitlines()
        objects = []
        for line in data:
            node1, node2 = map(str.strip, line.split(';'))
            if node1 and node2:
                objects.append(node1)
                objects.append(node2)
        return Counter(objects)

def calculate_influence(file_path):
    G = nx.Graph()
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().splitlines()
        for line in data:
            node1, node2 = map(str.strip, line.split(';'))
            if node1 and node2:
                G.add_edge(node1, node2)
    G.remove_nodes_from(list(nx.isolates(G)))
    degree_dict = dict(G.degree())
    return degree_dict

def calculate_clusters(file_path):
    G = nx.Graph()
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().splitlines()
        for line in data:
            node1, node2 = map(str.strip, line.split(';'))
            if node1 and node2:
                G.add_edge(node1, node2)
    G.remove_nodes_from(list(nx.isolates(G)))

    clusters = community.greedy_modularity_communities(G)
    return clusters

def create_bar_chart(data, title, top_n=50, color="#FCE7AB"):
    filtered_data = {k: v for k, v in data.items() if v > 3}

    if not filtered_data:
        return "No objects with more than 3 occurrences found."

    df = pd.DataFrame(list(filtered_data.items()), columns=["Object", "Count"])
    df = df.sort_values(by="Count", ascending=False).head(top_n)

    fig = px.bar(
        df,
        x="Object",
        y="Count",
        title=title,
        labels={"Object": "Object", "Count": "Count"},
        text_auto=True,
        hover_data={"Object": True, "Count": True},
        color_discrete_sequence=[color],
    )

    fig.update_layout(
        xaxis_title="Object",
        yaxis_title="Count",
        xaxis_tickangle=-45,
        template="plotly_white",
        width=1920,
        height=800,
    )

    return fig

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'padding': '0px', },
    children=[
        html.H1("ConnexaData", style=h1_style),
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'gap': '30px'},
            children=[
                html.Div(style={'textAlign': 'center', 'marginTop': '10px'}, children=[
                    html.A("Back to Home", href="/", style=button_style_backtohome)
                ])
            ]
        ),
        html.Div(
            style={'marginTop': '20px', 'textAlign': 'center'},
            children=[
                dcc.Dropdown(
                    id='file-selector',
                    options=[
                        {'label': file, 'value': os.path.join(FILTERED_OUTPUT_DIR, file)}
                        for file in os.listdir(FILTERED_OUTPUT_DIR)
                        if file.endswith('.txt')
                    ],
                    placeholder="Select a file",
                    style={'width': '50%', 'margin': 'auto'}
                ),
                html.Div(id='output-container', style={'marginTop': '20px'})
            ]
        )
    ]
)

def register_callbacks(app):
    @app.callback(
        Output('output-container', 'children'),
        Input('file-selector', 'value')
    )
    def update_output(file_path):
        if file_path is None:
            return "Please select a file."

        influence = calculate_influence(file_path)
        fig_degree = create_bar_chart(influence, "Node Degrees", color="#CEFCFF")

        if 'related' in file_path.lower():
            counts = count_occurrences(file_path)
            fig_counts = create_bar_chart(counts, "Most Frequent Objects", color="#FCE7AB")
            return html.Div([
                dcc.Graph(figure=fig_counts),
                dcc.Graph(figure=fig_degree)
            ])
        elif 'influential' in file_path.lower():
            return dcc.Graph(figure=fig_degree)
        elif 'clusters' in file_path.lower():
            clusters = calculate_clusters(file_path)
            return html.Div([
                html.H3("Clusters:"),
                html.Ul([html.Li(", ".join(cluster)) for cluster in clusters]),
                dcc.Graph(figure=fig_degree)
            ])
        else:
            return dcc.Graph(figure=fig_degree)