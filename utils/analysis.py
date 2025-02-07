# f"Extract pairs of most related people with specific surnames from the text. "
# f"Each person should be described in no more than 3 words. Format: 'Surname 1; Surname 2'. "
# f"Each pair on a new line. Give the answer on {languages} if there is person. Text: {text_chunk}"
from config_keys import api_groq_key, api_openai_key
from groq import Groq
from openai import OpenAI
client_groq = Groq(api_key=api_groq_key)
client_openai = OpenAI(api_key=api_openai_key)
model = "gpt-4o-mini"
# model = "llama-3.3-70b-versatile"
languages = "Ukrainian"
def request_related_concepts(client_openai, text_chunk):
    prompt = (
        f"Extract pairs of most related concepts from the text. "
        f"Each concept should be described in no more than 3 words. "
        f"Additionally, include related organizations and speakers involved in the conspiracy. "
        f"Return the concepts, speakers in pairs where possible."
        f"Text: {text_chunk}"
    )

    chat_completion = client_openai.chat.completions.create(
        messages=[
            {"role": "system", "content": f"Format: 'Concept 1; Concept 2' Each pair on a new line. Provide the answer in {languages}."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        temperature=0,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()

def request_related_people(client_openai, text_chunk):
    prompt = (
        f"Extract pairs of most related people with specific surnames from the text. "
        f"Each person should be described in no more than 3 words. Text: {text_chunk}"
    )

    chat_completion = client_openai.chat.completions.create(
        messages=[
            {"role": "system", "content": f"Format: 'Surname 1; Surname 2'. Each pair on a new line. Provide the answer in {languages}."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        temperature=0,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()


def request_the_most_influential_people(client_openai, text_chunk): #related_objects
    prompt = (
        f"Analyze the provided data and identify related entities, such as companies, speakers, or competitors."
        f"For each pair of related objects, display the connection in a row, with two objects per row." 
        f"Text: {text_chunk}"
    )

    chat_completion = client_openai.chat.completions.create(
        messages=[
            {"role": "system", "content": f"Format: 'Object 1; Object 2'. Result in {languages}"},
            {"role": "user", "content": prompt}
        ],
        model=model,
        temperature=0,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()