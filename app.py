import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

# Cargar variables de entorno (como la API KEY)
load_dotenv()

app = Flask(__name__)

# Configuración de OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/")
def index():
    """Sirve la página HTML principal."""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Este es nuestro propio endpoint (Backend API).
    Recibe el mensaje del cliente (frontend HTML/JS),
    hace la petición a OpenRouter, y devuelve la respuesta.
    """
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "No se ha configurado la API Key de OpenRouter."}), 400

    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "El mensaje no puede estar vacío."}), 400

    # Preparamos la petición para OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000", # Recomendado por OpenRouter
        "X-Title": "Ejemplo Basico API", # Recomendado por OpenRouter
        "Content-Type": "application/json"
    }
    
    payload = {
         # Usamos un modelo gratuito para el ejemplo
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    try:
        # Hacemos la petición HTTP POST a la API de OpenRouter
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status() # Lanza un error si la respuesta no es 200 OK
        
        # Parseamos la respuesta JSON de OpenRouter
        api_response = response.json()
        
        # Extraemos solo el texto del mensaje generado
        reply_text = api_response["choices"][0]["message"]["content"]
        
        # Devolvemos la respuesta a nuestro frontend
        return jsonify({"reply": reply_text})

    except requests.exceptions.RequestException as e:
        # Si hay un error al conectar con OpenRouter
        print(f"Error llamando a OpenRouter: {e}")
        return jsonify({"error": "Error al comunicarse con el proveedor de IA."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
