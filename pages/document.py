from dash import dcc, html, dash, callback_context
from dash.dependencies import Input, Output, State
from styles import common_styles, h1_style, description_style, button_style, button_style2, text_content_style, button_style_backtohome
from config import TEXT_FILE_PATH, OUTPUT_DIR, FILTERED_OUTPUT_DIR, UPLOAD_DIR
import os
import base64
from groq import Groq
import PyPDF2
from docx import Document
import threading
import re
from config import api_key

client = Groq(api_key=api_key)

analysis_running = False
analysis_stop_event = threading.Event()
progress = 0
model = "llama-3.3-70b-versatile"
languages = "Ukrainian"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FILTERED_OUTPUT_DIR, exist_ok=True)

def request_related_concepts(client, text_chunk):
    prompt = (
        f"Extract pairs of most related conspiracy-related concepts from the text. "
        f"Each concept should be described in no more than 3 words. Format: 'Concept 1; Concept 2'. "
        f"Each pair on a new line. Provide the answer in {languages}. "
        f"Text: {text_chunk}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        temperature=0,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()

def request_related_people(client, text_chunk):
    prompt = (
        f"Extract pairs of most related people with specific surnames from the text. "
        f"Each person should be described in no more than 3 words. Format: 'Surname 1; Surname 2'. "
        f"Each pair on a new line. Give the answer on {languages} if there is person. Text: {text_chunk}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        temperature=0,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()


def request_the_most_influential_people(client, text_chunk):
    prompt = (
        f"Analyze the given text and identify the most influential individuals mentioned in it. "
        f"Start with the person who acts as the initiator of actions or appears to give commands, if applicable. "
        f"Each person should be described in no more than three words. Format: 'Surname 1; Surname 2', no more than two individuals per line. "
        f"Provide the answer in {languages} if there is a person. "
        f"Text: {text_chunk}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        temperature=0,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()
def filter_row(row):
    cleaned_row = re.sub(r'^\d+\.\s*', '', row)
    cleaned_row = re.sub(r'^-\s*', '', cleaned_row)
    cleaned_row = re.sub(r'[^a-zA-Zа-яА-Я\s;]', '', cleaned_row)
    cleaned_row = cleaned_row.strip()
    if ';' not in cleaned_row:
        return False
    parts = cleaned_row.split(';')
    if len(parts) != 2:
        return False
    for part in parts:
        part = part.strip()
        if not part or len(part.split()) > 3:
            return False
    return True

def process_text_chunks(file_path, output_dir, client, request_function, chunk_size=2400):
    global analysis_running, analysis_stop_event, progress
    analysis_running = True
    progress = 0
    original_filename = os.path.basename(file_path)
    output_filename = f"output_{request_function.__name__}_{original_filename}"
    output_file = os.path.join(output_dir, output_filename)
    filtered_output_filename = f"filtered_{output_filename}"
    filtered_output_file = os.path.join(FILTERED_OUTPUT_DIR, filtered_output_filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().replace('\n', ' ')
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(FILTERED_OUTPUT_DIR):
        os.makedirs(FILTERED_OUTPUT_DIR)
    with open(output_file, "w", encoding='utf-8') as output_file, open(filtered_output_file, "w", encoding='utf-8') as filtered_file:
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            if analysis_stop_event.is_set():
                break
            result = request_function(client, chunk)
            output_file.write(result + "\n")
            filtered_result = "\n".join([line for line in result.split("\n") if filter_row(line)])
            filtered_file.write(filtered_result + "\n")
            progress = int((i + 1) / total_chunks * 100)
    analysis_running = False
    analysis_stop_event.clear()
    return output_file

def read_text_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return "File not found."

def get_file_list(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def save_uploaded_file(contents, filename, upload_dir):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    upload_path = os.path.join(upload_dir, filename)
    with open(upload_path, 'wb') as f:
        f.write(decoded)

    return upload_path

def process_uploaded_file(file_path):
    if file_path.endswith('.txt'):
        return read_text_file(file_path)
    elif file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format."

def convert_to_txt(file_path, upload_dir):
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return file_path
    else:
        return None

    txt_filename = os.path.splitext(os.path.basename(file_path))[0] + '.txt'
    txt_file_path = os.path.join(upload_dir, txt_filename)

    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    if os.path.exists(file_path):
        os.remove(file_path)

    return txt_file_path

file_list = get_file_list(os.path.dirname(TEXT_FILE_PATH))

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'display': 'flex', 'flexDirection': 'column'},
    children=[
        html.H1("ConnexaData", style={**h1_style, 'textAlign': 'center'}),
        html.Div(children=["This is the document page."], style=description_style),

        html.Div(
            style={'display': 'flex', 'flexDirection': 'row', 'marginTop': '20px', 'flex': '1'},
            children=[
                html.Div(
                    style={
                        'flex': '0.7',
                        'padding': '10px',
                        'borderRight': '1px solid #ccc',
                        'backgroundColor': '#f9f9f9'
                    },
                    children=[
                        dcc.Dropdown(
                            id='file-dropdown',
                            options=[{'label': file, 'value': file} for file in file_list],
                            value=file_list[0] if file_list else None,
                            style={'width': '100%', 'marginBottom': '20px', 'fontSize': '14px'}
                        ),
                        dcc.Upload(
                            id='upload-file',
                            children=html.Div([
                                "Drag and Drop or ",
                                html.A("Select Files", style={'color': '#007acc', 'textDecoration': 'underline'})
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0',
                                'backgroundColor': 'white',
                                'color': 'black'
                            },
                            multiple=False
                        ),
                        html.Div(
                            style={'display': 'flex', 'flexDirection': 'column', 'marginTop': '10px'},
                            children=[
                                html.Button("Find connections between", id="run-analysis-related-button",
                                            style={**button_style, 'border': 'none', 'marginBottom': '10px'}),
                                html.Div("Discover related people by name", style={'marginBottom': '20px'}),
                                html.Button("Discover influential", id="run-analysis-influential-button",
                                            style={**button_style, 'border': 'none', 'marginBottom': '10px'}),
                                html.Div("Identify the most influential individuals", style={'marginBottom': '20px'}),
                                html.Button("Find related concepts", id="run-analysis-related-concepts-button",
                                            style={**button_style, 'border': 'none', 'marginBottom': '10px'}),
                                html.Div("Discover related concepts", style={'marginBottom': '20px'}),
                                html.Button("Stop Analysis", id="stop-analysis-button",
                                            style={**button_style2, 'border': 'none', 'display': 'none',
                                                   'marginLeft': '10px'})
                            ]
                        ),
                    ]
                ),

                html.Div(
                    style={
                        'flex': '2.3',
                        'padding': '10px',
                        'backgroundColor': 'white'
                    },
                    children=[
                        html.Div(
                            style={
                                'border': '1px solid #ccc',
                                'padding': '10px',
                                'overflow': 'auto',
                                'maxHeight': '500px',
                                'backgroundColor': 'white'
                            },
                            children=[
                                html.Div(id='text-content', style=text_content_style)
                            ]
                        )
                    ]
                ),

            ]
        ),

        html.Div(
            id='progress-container',
            style={'display': 'none', 'marginTop': '20px'},
            children=[
                html.Div("Progress:", style={'fontWeight': 'bold'}),
                html.Div(id='progress-bar', style={'width': '0%', 'height': '20px', 'backgroundColor': '#007acc'}),
                html.Div(id='progress-text', style={'marginTop': '10px'})
            ]
        ),

        dcc.Interval(
            id='progress-interval',
            interval=1000,
            n_intervals=0,
            disabled=True
        ),

        html.A("Back to home", href="/",
               style={**button_style_backtohome, 'marginTop': '20px', 'marginBottom': '20px', 'alignSelf': 'center'}),
    ]
)

def register_callbacks(app):
    @app.callback(
        [Output('file-dropdown', 'options'),
         Output('file-dropdown', 'value')],
        [Input('upload-file', 'contents')],
        State('upload-file', 'filename'),
        State('upload-file', 'last_modified')
    )
    def upload_and_convert_file(contents, filename, last_modified):
        if contents is not None:
            upload_dir = os.path.dirname(TEXT_FILE_PATH)
            upload_path = save_uploaded_file(contents, filename, upload_dir)
            converted_file_path = convert_to_txt(upload_path, upload_dir)

            file_list = get_file_list(upload_dir)
            return [{'label': file, 'value': file} for file in file_list], os.path.basename(converted_file_path)

        upload_dir = os.path.dirname(TEXT_FILE_PATH)
        file_list = get_file_list(upload_dir)
        return [{'label': file, 'value': file} for file in file_list], None

    @app.callback(
        Output('text-content', 'children'),
        [Input('file-dropdown', 'value')]
    )
    def display_selected_file_content(selected_file):
        if not selected_file:
            return "No file selected."

        file_path = os.path.join(os.path.dirname(TEXT_FILE_PATH), selected_file)
        content = read_text_file(file_path)
        return content

    @app.callback(
        [Output('progress-container', 'style'),
         Output('progress-bar', 'style'),
         Output('progress-text', 'children'),
         Output('progress-interval', 'disabled'),
         Output('stop-analysis-button', 'style')],
        [Input('run-analysis-related-button', 'n_clicks'),
         Input('run-analysis-influential-button', 'n_clicks'),
         Input('run-analysis-related-concepts-button', 'n_clicks'),
         Input('stop-analysis-button', 'n_clicks'),
         Input('progress-interval', 'n_intervals')],
        State('file-dropdown', 'value')
    )
    def update_progress(related_clicks, influential_clicks, related_concepts_clicks, stop_clicks, n_intervals, selected_file):
        global analysis_running, progress

        ctx = callback_context
        if not ctx.triggered:
            return {'display': 'none'}, {'width': '0%'}, "0%", True, {'display': 'none'}

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id in ['run-analysis-related-button', 'run-analysis-influential-button', 'run-analysis-related-concepts-button']:
            if not selected_file:
                return {'display': 'none'}, {'width': '0%'}, "Please select a file first.", True, {'display': 'none'}

            file_path = os.path.join(os.path.dirname(TEXT_FILE_PATH), selected_file)
            if trigger_id == 'run-analysis-related-button':
                analysis_thread = threading.Thread(target=process_text_chunks, args=(file_path, OUTPUT_DIR, client, request_related_people))
            elif trigger_id == 'run-analysis-influential-button':
                analysis_thread = threading.Thread(target=process_text_chunks, args=(file_path, OUTPUT_DIR, client, request_the_most_influential_people))
            elif trigger_id == 'run-analysis-related-concepts-button':
                analysis_thread = threading.Thread(target=process_text_chunks, args=(file_path, OUTPUT_DIR, client, request_related_concepts))

            analysis_thread.start()

            return {'display': 'block'}, {'width': '0%'}, "0%", False, {'display': 'block', **button_style2}

        elif trigger_id == 'stop-analysis-button':
            if analysis_running:
                analysis_stop_event.set()
                return {'display': 'block'}, {'width': '100%',
                                              'backgroundColor': '#ff4d4d'}, "Analysis stopped by user.", True, {
                    'display': 'none'}
            else:
                return {'display': 'none'}, {'width': '0%'}, "No analysis is running.", True, {'display': 'none'}

        elif trigger_id == 'progress-interval':
            if analysis_running:
                return {'display': 'block'}, {'width': f'{progress}%',
                                              'backgroundColor': '#007acc'}, f"{progress}%", False, {'display': 'block',
                                                                                                     **button_style2}
            else:
                return {'display': 'none'}, {'width': '0%'}, "", True, {'display': 'none'}

        return {'display': 'none'}, {'width': '0%'}, "", True, {'display': 'none'}

    return app