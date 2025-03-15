import os
from dash import dcc
from config import FILTERED_OUTPUT_DIR

REMOVE_PATTERNS = [
    "filtered_output_request_",
    "filtered_output_request_",
    "filtered_output_request_"
]

def get_file_list(FILTERED_OUTPUT_DIR):
    return [f for f in os.listdir(FILTERED_OUTPUT_DIR) if os.path.isfile(os.path.join(FILTERED_OUTPUT_DIR, f))]

def clean_filename(filename):
    cleaned_name = filename
    for pattern in REMOVE_PATTERNS:
        cleaned_name = cleaned_name.replace(pattern, "")
    return cleaned_name.lstrip("_").strip()

def create_dropdown(dropdown_id="file-dropdown"):
    file_list = get_file_list(FILTERED_OUTPUT_DIR)
    return dcc.Dropdown(
        id=dropdown_id,
        options=[{'label': clean_filename(file), 'value': file} for file in file_list],
        placeholder="Select a file...",
        style={'width': '100%', 'marginBottom': '10px', 'fontFamily': 'Helvetica'},
        clearable=False,
    )