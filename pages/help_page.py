from dash import html
from styles import common_styles, h1_style, h2_style, description_style, button_style_backtohome

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'},
    children=[
        html.Div(
            style={'width': '60%', 'maxWidth': '700px', 'paddingLeft': '40px', 'paddingRight': '40px'},
            children=[
                html.H1("ConnexaData - Help", style=h1_style),
                html.Div(
                    "This is the help page. Below are some instructions and definitions to help you navigate and understand the features of ConnexaData.",
                    style={**description_style, 'textAlign': 'left'}
                ),

                html.H2("Document", style={**h2_style, 'textAlign': 'left'}),
                html.P(
                    children=[
                        "You can upload your document in ",
                        html.I("txt"), ", ",
                        html.I("pdf"), ", or ",
                        html.I("docx"),
                        " format and analyse it to determine the influence of related people or objects. "
                        "The percentage displayed shows how much of the document has been analysed. You can stop the process at any time, and the analysis completed up to that point will be saved."
                    ],
                    style={**description_style, 'textAlign': 'left'}
                ),

                html.H2("Table", style={**h2_style, 'textAlign': 'left'}),
                html.P(
                    children=[
                        "Here, you can view the intermediate results of the analysis between your text and the visualisation. On this page, you can also access the ",
                        html.B("\"Table Influence\""),
                        " section, where you can see the degree of influence for each object."
                    ],
                    style={**description_style, 'textAlign': 'left'}
                ),
                html.P(
                    children=[
                        "The ",
                        html.B("Object Degree"),
                        " is calculated as the degree of each ",
                        html.I("node"),
                        " in the graph, reflecting how much influence an object or person has within the dataset."
                    ],
                    style={**description_style, 'textAlign': 'left'}
                ),

                html.H2("Statistics", style={**h2_style, 'textAlign': 'left'}),
                html.P(
                    children=[
                        "This section provides insights into the frequency of mentions of specific ",
                        html.I("objects"),
                        " within your document. It also shows the influence these objects hold within the visualisation."
                    ],
                    style={**description_style, 'textAlign': 'left'}
                ),

                html.H2("Visualisation", style={**h2_style, 'textAlign': 'left'}),
                html.P(
                    children=[
                        "The ",
                        html.B("semantic maps"),
                        " visualise the relationships between the entities in your document. You can adjust the parameters for better viewing, such as choosing the maximum number of ",
                        html.I("objects"),
                        " to display. This helps with readability and focuses the view on the most important data."
                    ],
                    style={**description_style, 'textAlign': 'left'}
                ),

                html.Div(
                    html.A("Back to Home", href="/", style=button_style_backtohome),
                    style={'textAlign': 'center', 'marginTop': '20px'}
                )
            ]
        )
    ]
)
