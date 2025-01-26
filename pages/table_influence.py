import os
import pandas as pd
import networkx as nx
from dash import html, dash_table, dcc
from dash.dependencies import Input, Output
from styles import (
    button_style,
    error_message_style,
    layout_style,
    table_style,
    cell_style,
    header_style,
    data_style,
    h1_style,
    button_style_backtohome
)
from config import FILTERED_OUTPUT_DIR

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, sep=';', header=None, encoding='utf-8', on_bad_lines='skip')
            df = df.rename(columns={0: "object_1", 1: "object_2"})
            df = df[df["object_1"] != df["object_2"]]
            G = nx.Graph()
            for _, row in df.iterrows():
                G.add_edge(row["object_1"], row["object_2"])

            degrees = dict(G.degree())

            degrees_df = pd.DataFrame(list(degrees.items()), columns=["object", "degree"])

            return degrees_df
        except Exception as e:
            return html.Div(f"Error loading table: {str(e)}", style=error_message_style)
    else:
        return html.Div("File not found!", style=error_message_style)

def create_layout():
    tables_filtered_dir = FILTERED_OUTPUT_DIR
    files = sorted([f for f in os.listdir(tables_filtered_dir) if f.endswith('.txt')])
    default_file_path = os.path.join(tables_filtered_dir, files[0]) if files else None
    result = load_data(default_file_path) if default_file_path else html.Div("No files found in tables_filtered directory!", style=error_message_style)

    if isinstance(result, html.Div):
        return result

    degrees_df = result

    table_content = dash_table.DataTable(
        id='influence-table',
        columns=[
            {"name": "Object", "id": "object"},
            {"name": "Degree", "id": "degree", "type": "numeric"}
        ],
        data=degrees_df.to_dict('records'),
        style_table=table_style,
        style_cell=cell_style,
        style_header=header_style,
        style_data=data_style,
        sort_action="native"
    )

    return html.Div(
        style=layout_style,
        children=[
            html.H1("ConnexaData", style=h1_style),
            html.A("Back to Main Table", href="/table", style=button_style_backtohome),
            dcc.Dropdown(
                id='file-dropdown',
                options=[{'label': f, 'value': os.path.join(tables_filtered_dir, f)} for f in files],
                value=default_file_path,
                style={'width': '50%', 'marginBottom': '20px'}
            ),
            html.Div(table_content, style={'marginTop': '20px'})
        ]
    )

layout = create_layout()

def register_callbacks(app):
    @app.callback(
        Output('influence-table', 'data'),
        [Input('file-dropdown', 'value')]
    )
    def update_table(file_path):
        result = load_data(file_path)
        if isinstance(result, html.Div):
            return []
        return result.to_dict('records')