import os
import logging
from collections import Counter
from dash import html, dcc, Input, Output, no_update
import plotly.express as px
import pandas as pd
import networkx as nx
from config import FILTERED_OUTPUT_DIR
from styles import common_styles, h1_style, button_style_backtohome, description_style


logging.basicConfig(level=logging.ERROR)


def safe_file_operation(func):
    def wrapper(file_path, *args, **kwargs):
        try:
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return func(file, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            return None

    return wrapper


@safe_file_operation
def count_occurrences(file):
    counter = Counter()
    for line in file:
        line = line.strip()
        if not line:
            continue
        parts = line.split(';')
        if len(parts) != 2:
            continue
        node1, node2 = map(str.strip, parts)
        if node1:
            counter[node1] += 1
        if node2:
            counter[node2] += 1
    return counter or None


@safe_file_operation
def calculate_influence(file):
    G = nx.Graph()
    for line in file:
        line = line.strip()
        if not line:
            continue
        parts = line.split(';')
        if len(parts) != 2:
            continue
        node1, node2 = map(str.strip, parts)
        if node1 and node2:
            G.add_edge(node1, node2)

    if G.number_of_nodes() == 0:
        return None

    isolates = list(nx.isolates(G))
    if isolates:
        G.remove_nodes_from(isolates)

    return dict(G.degree()) if G else None


def create_visualization(data, title, color):
    if not data:
        return html.Div(f"No data available for {title}", style={'color': 'gray'})

    try:
        filtered_data = {k: v for k, v in data.items() if v > 3}
        if not filtered_data:
            return html.Div(f"No significant data for {title} (all values ≤3)", style={'color': 'gray'})

        df = pd.DataFrame(filtered_data.items(), columns=["Object", "Count"])
        df = df.sort_values("Count", ascending=False).head(50)

        fig = px.bar(
            df,
            x="Object",
            y="Count",
            title=title,
            labels={"Object": "Object", "Count": "Count"},
            text_auto=True,
            color_discrete_sequence=[color],
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            template="plotly_white",
            margin=dict(l=40, r=40, t=40, b=40),
            height=400
        )
        return dcc.Graph(figure=fig)

    except Exception as e:
        logging.error(f"Visualization error: {str(e)}")
        return html.Div(f"Error creating {title} visualization", style={'color': 'red'})


layout = html.Div(
    style={**common_styles, 'padding': '0px', 'position': 'relative'},
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
                        for file in sorted(os.listdir(FILTERED_OUTPUT_DIR))
                        if file.endswith('.txt')
                    ],
                    placeholder="Select a file",
                    style={'width': '50%', 'margin': 'auto'},
                    clearable=False
                ),
                html.Div(
                    id='output-container',
                    style={
                        'marginTop': '20px',
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'justifyContent': 'center',
                        'gap': '20px'
                    }
                )
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
        if not file_path or not os.path.exists(file_path):
            return html.Div("Please select a valid file.", style={'color': 'gray'})

        try:
            counts = count_occurrences(file_path)
            influence = calculate_influence(file_path)

            visualizations = []
            if counts:
                visualizations.append(create_visualization(counts, "Most Frequent Objects", "#FCE7AB"))
            if influence:
                visualizations.append(create_visualization(influence, "Node Degrees", "#CEFCFF"))

            return visualizations or html.Div("No valid data found in selected file", style={'color': 'gray'})

        except Exception as e:
            logging.error(f"Callback error: {str(e)}")
            return html.Div("Error processing selected file", style={'color': 'red'})