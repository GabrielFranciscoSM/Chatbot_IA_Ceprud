import os
import csv
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from query_logic import query_rag, get_base_model_response

# Configuración de Flask
app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://150.214.205.61:8080"}})
app.secret_key = 'clave_secreta_para_sesion'

# Configuración de Chroma
BASE_CHROMA_PATH = "chroma"

# Ruta principal para servir la interfaz web
@app.route('/')
def index():
    """
    Renderiza la página principal del chatbot.
    """
    return render_template('index.html')

# Función para guardar logs de mensajes del usuario en un archivo CSV
def log_user_message(email, message, subject, response, sources):
    """
    Guarda los mensajes del usuario y las respuestas en un archivo CSV para auditoría.
    
    Args:
        email (str): Correo electrónico del usuario.
        message (str): Mensaje enviado por el usuario.
        subject (str): Asignatura seleccionada.
        response (str): Respuesta generada por el modelo.
        sources (list): Fuentes utilizadas para generar la respuesta.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "chat_logs.csv")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    file_exists = os.path.isfile(log_file)

    # Convertir las fuentes a una cadena separada por comas
    sources_str = ",".join(sources) if sources else "N/A"

    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user", "message", "time", "date", "subject", "sources"])
        writer.writerow([email, message, time, date, subject, sources_str])

# Ruta para manejar mensajes de texto
@app.route('/chat', methods=['POST'])
def chat():
    """
    Procesa las solicitudes de chat enviadas desde el frontend.
    """
    try:
        # Obtener los datos enviados desde el frontend
        user_message = request.form.get('message', '').strip()
        selected_subject = request.form.get('subject', 'default').lower()
        user_email = request.form.get('email', 'anonimo')
        selected_mode = request.form.get('mode', 'rag').lower()

        print(f"DEBUG: Modo={selected_mode}, Asignatura={selected_subject}, Usuario={user_email}")

        # Validar que el mensaje no esté vacío
        if not user_message:
            return jsonify({"response": "❌ Por favor, escribe una pregunta."})

        # Determinar la ruta de la base de datos Chroma para la asignatura
        chroma_path = os.path.join(BASE_CHROMA_PATH, selected_subject)
        if not os.path.exists(chroma_path) and selected_mode != "base":
            return jsonify({"response": f"❌ No hay datos disponibles para la asignatura '{selected_subject}'."})

        # Llamar al modelo según el modo seleccionado
        if selected_mode == "rag":
            result = query_rag(user_message, chroma_path, use_finetuned=False)
        elif selected_mode == "rag_lora":
            result = query_rag(user_message, chroma_path, subject=selected_subject, use_finetuned=True)
        elif selected_mode == "base":
            print(f"DEBUG: Usando modelo base para {selected_subject}")
            result = get_base_model_response(user_message)
        else:
            return jsonify({"response": "❌ Modo no válido."})

        # Extraer la respuesta y las fuentes
        if selected_mode == "base":
            response_text = result
            sources = []
        else:
            response_text = result.get("response", "No se pudo generar una respuesta.")
            sources = result.get("sources", [])

        # Guardar el mensaje y la respuesta en los logs
        log_user_message(
            email=user_email,
            message=user_message,
            subject=selected_subject,
            response=response_text,
            sources=sources
        )

        # Devolver la respuesta al frontend
        return jsonify({
            "response": f"🤖: {response_text}",
            "sources": sources,
            "model_used": result.get("model_used", "Base")
        })

    except Exception as e:
        print(f"Error durante el procesamiento: {str(e)}")
        return jsonify({"response": "❌ Ocurrió un error al procesar tu solicitud."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=False)
