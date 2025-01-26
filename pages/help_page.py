from dash import html
from styles import common_styles, h1_style, h2_style, description_style, ul_style, button_style_backtohome

layout = html.Div(
    style={**common_styles, 'height': '100vh'},
    children=[
        html.H1("ConnexaData - Help", style=h1_style),
        html.Div(
            "This is the help page. Below are some instructions and definitions to help you navigate and understand the features of ConnexaData.",
            style=description_style
        ),
        html.Div(
            [
                html.H2("Glossary", style=h2_style),
                html.Ul(
                    children=[
                        html.Li([
                            html.B("ConnexaData: "),
                            "a service for visualizing tables that allows users to identify and analyze connections within data using clusters and graphs."
                        ]),
                        html.Li([
                            html.B("Graph: "),
                            "a data structure consisting of nodes (vertices) and the connections between them (edges). Used to visualize relationships between objects within the data."
                        ]),
                        html.Li([
                            html.B("Cluster: "),
                            "a group of interrelated objects or nodes in a graph. Clusters represent tightly connected groups of data, making it easier to understand the structure and interactions within the table."
                        ]),
                        html.Li([
                            html.B("\"Table\" Tab: "),
                            "a section that contains the uploaded table, where data is presented in rows and columns for easy viewing and preliminary analysis."
                        ]),
                    ],
                    style=ul_style
                ),
            ]
        ),
        html.Div(
            html.A("Back to Home", href="/", style=button_style_backtohome),
            style={'textAlign': 'center', 'marginTop': '20px'}
        )
    ]
)