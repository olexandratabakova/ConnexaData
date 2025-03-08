import os
import pandas as pd
from dash import html, dash_table
from dash.dependencies import Input, Output
from styles import (
    table_style,
    table_style_text,
    cell_style,
    header_style,
    data_style,
    button_style,
    button_style_backtohome,
    layout_style,
    h1_style,
    description_style
)
from config import FILTERED_OUTPUT_DIR
from components.dropdown import create_dropdown
def load_data(file_name):
    input_file = os.path.join(FILTERED_OUTPUT_DIR, file_name)
    df = pd.read_csv(input_file, sep=';', header=None, encoding='utf-8', on_bad_lines='skip').fillna('')
    df.rename(columns={0: "object_1", 1: "object_2"}, inplace=True)
    return df

def create_layout(file_list):
    return html.Div(
        style=table_style_text,
        children=[
            html.Div(
                style={
                    'position': 'fixed',
                    'top': '10px',
                    'right': '10px',
                    'zIndex': '1000'
                },
                children=[html.A("Back to Home", href="/", style=button_style_backtohome)]
            ),
            html.H1("ConnexaData", style=h1_style),
            html.P("This page allows you to see tables. Select a file to view its data.", style=description_style),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'},
                children=[
                    create_dropdown(),
                    html.A("Go to Table Influence", href="/table_influence", style=button_style)
                ]
            ),
            html.Div(
                dash_table.DataTable(
                    id='table-content',
                    columns=[
                        {"name": "№", "id": "Row Number"},
                        {"name": "Object 1", "id": "object_1"},
                        {"name": "Object 2", "id": "object_2"}
                    ],
                    data=[],
                    style_table=table_style,
                    style_cell=cell_style,
                    style_header=header_style,
                    style_data=data_style,
                    style_data_conditional=[
                        {
                            'if': {'column_id': 'Row Number'},
                            'width': '70px',
                            'textAlign': 'center',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'whiteSpace': 'nowrap',
                        },
                        {
                            'if': {'column_id': 'object_1'},
                            'width': '200px',
                            'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'whiteSpace': 'nowrap',
                        },
                        {
                            'if': {'column_id': 'object_2'},
                            'width': '200px',
                            'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'whiteSpace': 'nowrap',
                        }
                    ]
                ),
                style={'marginTop': '20px'}
            )
        ]
    )

def get_file_list(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

file_list = get_file_list(FILTERED_OUTPUT_DIR)

layout = html.Div(
    style=layout_style,
    children=[
        create_layout(file_list) if file_list else html.Div("No files available.", style={'color': 'red', 'fontSize': '16px', 'textAlign': 'center'})
    ]
)

def register_callbacks(app):
    @app.callback(
        Output('table-content', 'data'),
        Input('file-dropdown', 'value')
    )
    def update_table_content(selected_file):
        if selected_file:
            df = load_data(selected_file)
            df.insert(0, 'Row Number', range(1, len(df) + 1))
            return df.to_dict('records')
        return []