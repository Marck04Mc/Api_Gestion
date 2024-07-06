from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__, template_folder='../html', static_folder='../css')
CORS(app)  # Esta línea permite todas las solicitudes CORS

# Configurar la API de Generative AI
genai.configure(api_key="AIzaSyA_fPnKEozH3ufteVusyv8x9Xv2VVN7KFk")

# Crear la instancia del modelo generativo
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel(
    model_name="gemini-1.0-pro", safety_settings=safety_settings, generation_config=generation_config
)
chat_session = model.start_chat(history=[])

@app.route('/consulta', methods=['POST'])
def consulta():
    try:
        data = request.get_json()
        messages = data["messages"]
        responses = []
        for message in messages:
            response = chat_session.send_message(message)
            cleaned_response = clean_response(response.text, message)
            responses.append(cleaned_response)
        return jsonify({"responses": responses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import re

def clean_response(response_text, message):
    if response_text.startswith(message):
        response_text = response_text[len(message):].strip()
        if response_text.startswith(','):
            response_text = response_text[1:].strip()

    # Convertir asteriscos para títulos y negrita
    response_text = re.sub(r'\*\*(.*?)\*\*', r'<h2>\1</h2>', response_text)  # Títulos en h2
    response_text = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', response_text)  # Texto en negrita
    
    # Convertir incisos marcados con asteriscos en listas
    lines = response_text.split('\n')
    for i in range(len(lines)):
        if lines[i].strip().startswith('* '):
            lines[i] = '<ul><li>' + lines[i].strip()[2:] + '</li>'
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('* '):
                    lines[j] = '<li>' + lines[j].strip()[2:] + '</li>'
                else:
                    lines[j - 1] = lines[j - 1] + '</ul>'
                    break
            else:
                lines[-1] = lines[-1] + '</ul>'
    
    response_text = '\n'.join(lines)
    return response_text



@app.route('/', methods=['GET'])
def inicio():
    return render_template('bienvenida.html')

@app.route('/test', methods=['GET'])
def prueba():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)