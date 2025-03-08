from dash import html, dcc


def create_rename_panel(merged_parts, current_label):
    return [
        html.Div(
            [
                html.Strong("Objects in the node", style={
                    'color': '#1B5E67',
                    'fontSize': '14px',
                    'marginBottom': '10px',
                    'display': 'block',
                }),
                html.Ul(
                    [
                        html.Li(
                            part,
                            style={
                                'margin': '8px 0',
                                'padding': '8px',
                                'backgroundColor': '#f8f9fa',
                                'borderRadius': '4px',
                                'transition': '0.3s',
                                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                            }
                        ) for part in merged_parts
                    ],
                    style={
                        'listStyleType': 'none',
                        'padding': '0',
                        'margin': '0'
                    }
                )
            ],
            style={'maxHeight': '400px', 'overflowY': 'auto'}
        ),
        html.Div(
            [
                html.Strong("Select the label to display", style={
                    'color': '#1B5E67',
                    'fontSize': '14px',
                    'marginBottom': '10px',
                    'display': 'block'
                }),
                dcc.RadioItems(
                    id='label-radio',
                    options=[{'label': part, 'value': part} for part in merged_parts],
                    value=current_label,
                    labelStyle={'display': 'block', 'margin': '5px 0'}
                )
            ],
            style={'marginTop': '20px'}
        )
    ]