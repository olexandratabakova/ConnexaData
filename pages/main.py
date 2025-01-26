from dash import html
from styles import common_styles, h1_style, description_style_main, button_style_main

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'padding': '0px',},
    children=[
        html.H1("ConnexaData", style=h1_style),
        html.Div("What will you do today?", style=description_style_main),
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'gap': '30px'},
            children=[
                html.A("My document", href="/document", style=button_style_main),
                html.A("Table", href="/table", style=button_style_main),
                html.A("Statistics", href="/statistics", style=button_style_main),
                html.A("Visualisation", href="/visualization", style=button_style_main),
                html.A("Help", href="/help", style=button_style_main)
            ]
        )
    ]
)