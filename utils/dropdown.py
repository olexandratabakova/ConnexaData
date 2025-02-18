import os
from dash import dcc
from config import FILTERED_OUTPUT_DIR

REMOVE_PATTERNS = [
    "filtered_output_request_",
    "filtered_output_request_",
    "filtered_output_request_"
]

def get_file_list(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

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
        value=None,
        placeholder="Select a file...",
        style={'width': '50%'}
    )
