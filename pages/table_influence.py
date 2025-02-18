import os
import pandas as pd
import networkx as nx
from dash import html, dash_table, dcc
from dash.dependencies import Input, Output
from styles import (
    error_message_style,
    layout_style,
    table_style,
    cell_style,
    header_style,
    data_style,
    h1_style,
    description_style,
    button_style_backtohome
)
from config import FILTERED_OUTPUT_DIR
from utils.dropdown import create_dropdown


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
            degrees_df = degrees_df.groupby("object", as_index=False).sum()

            return degrees_df
        except Exception as e:
            return html.Div(f"Error loading table: {str(e)}", style=error_message_style)
    else:
        return html.Div(f"File not found: {file_path}", style=error_message_style)


def create_layout():
    tables_filtered_dir = FILTERED_OUTPUT_DIR
    files = sorted([f for f in os.listdir(tables_filtered_dir) if f.endswith('.txt')])
    default_file = files[0] if files else None
    default_file_path = os.path.join(tables_filtered_dir, default_file) if default_file else None

    result = load_data(default_file_path) if default_file_path else html.Div(
        "No files found in tables_filtered directory!", style=error_message_style)

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
            html.Div(
                style={
                    'position': 'fixed',
                    'top': '10px',
                    'right': '10px',
                    'zIndex': '1000'
                },
                children=[html.A("Back to Main Table", href="/table", style=button_style_backtohome)]
            ),
            html.H1("ConnexaData", style=h1_style),
            html.P("This page allows you to see degree of objects. Select a file to view.", style=description_style),
            create_dropdown("file-dropdown"),
            html.Div(id='table-container', style={'marginTop': '20px'}, children=table_content)
        ]
    )


layout = create_layout()


def register_callbacks(app):
    @app.callback(
        Output('table-container', 'children'),
        [Input('file-dropdown', 'value')]
    )
    def update_table(selected_filename):
        if not selected_filename:
            return html.Div("Please select a file to view the data.", style=description_style)


        full_path = os.path.join(FILTERED_OUTPUT_DIR, selected_filename)

        result = load_data(full_path)
        if isinstance(result, html.Div):
            return result

        degrees_df = result

        return dash_table.DataTable(
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