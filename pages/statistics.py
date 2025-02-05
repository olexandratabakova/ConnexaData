import os
from collections import Counter
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import networkx as nx
from config import FILTERED_OUTPUT_DIR

from styles import common_styles, h1_style, button_style_backtohome, description_style

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
        width=1200,
        height=600,
    )

    return fig

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'padding': '0px', 'position': 'relative'},
    children=[
        html.H1("ConnexaData", style=h1_style),
        html.Div(
            style={'position': 'fixed', 'top': '20px', 'right': '20px'},
            children=[
                html.A("Back to Home", href="/", style=button_style_backtohome)
            ]
        ),
        html.Div(
            style={'marginTop': '0px', 'textAlign': 'center'},
            children=[
                html.P(
                    "This is a page with statistics about your texts (degree, mention of words in the text).",
                    style=description_style
                ),
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

        counts = count_occurrences(file_path)
        influence = calculate_influence(file_path)

        fig_counts = create_bar_chart(counts, "Most Frequent Objects", color="#FCE7AB")
        fig_degree = create_bar_chart(influence, "Node Degrees", color="#CEFCFF")

        return html.Div(
            style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '20px'},
            children=[
                dcc.Graph(figure=fig_counts),
                dcc.Graph(figure=fig_degree)
            ]
        )