import os
from flask import Flask, render_template, request, session
from dotenv import load_dotenv
from openai import OpenAI

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configurar la clave secreta para las sesiones
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')

# Crear una instancia del cliente OpenAI usando la clave de API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/', methods=['GET', 'POST'])
def home():
    # Inicializar el historial de la conversación si no existe
    if 'conversation' not in session:
        session['conversation'] = []

    if request.method == 'POST':
        texto = request.form['textarea']

        # Enviar el texto a la API de ChatGPT y obtener la respuesta
        respuesta = chatgpt_response(texto)
        
        # Almacenar la entrada del usuario y la respuesta en el historial
        session['conversation'].append({"role": "user", "content": texto})
        session['conversation'].append({"role": "assistant", "content": respuesta})
        session.modified = True  # Asegurar que la sesión se actualiza
    
    return render_template('index.html', conversation=session['conversation'])

def chatgpt_response(texto):
    try:
        # Realiza la solicitud a la API de OpenAI con el historial de la conversación
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session['conversation'] + [{"role": "user", "content": texto}]
        )
        # Devuelve la respuesta del modelo
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/reset', methods=['POST'])
def reset_conversation():
    # Reiniciar la conversación
    session.pop('conversation', None)
    return render_template('index.html', conversation=[])

if __name__ == '__main__':
    app.run(debug=True)