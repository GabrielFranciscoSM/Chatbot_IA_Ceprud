import os
import csv
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_cors import CORS
from query_logic import query_rag, get_base_model_response
from langchain_chroma import Chroma 

# Configuración de Flask
app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://150.214.205.61:8080"}})
app.secret_key = 'clave_secreta_para_sesion'

# Configuración de Chroma
BASE_CHROMA_PATH = "chroma"

# Diccionario para almacenar historiales de chat por usuario
# La estructura será: {email: [(pregunta1, respuesta1), (pregunta2, respuesta2), ...]}
chat_histories = {}

# Máximo número de mensajes a guardar en el historial
MAX_HISTORY_LENGTH = 5

# Ruta principal para servir la interfaz web
@app.route('/')
def index():
    """
    Renderiza la página principal del chatbot.
    """
    return render_template('index.html')

# Ruta para listar gráficas generales
@app.route('/graphs', methods=['GET'])
def list_graphs():
    graphs_dir = "graphs"
    if not os.path.exists(graphs_dir):
        return jsonify([])
    
    # Filtrar solo las gráficas específicas
    specific_graphs = ["calendar.png", "hours.png", "subjects.png", "users.png"]
    graphs = [f for f in os.listdir(graphs_dir) if f in specific_graphs]
    
    return jsonify(graphs)

# Ruta para servir las imágenes
@app.route('/graphs/<filename>', methods=['GET'])
def serve_graph(filename):
    return send_from_directory("graphs", filename)

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

# Función para obtener el historial de chat del usuario
def get_user_history(email):
    """
    Obtiene el historial de chat para un usuario específico.
    Si no existe, crea un historial vacío.
    
    Args:
        email (str): Correo electrónico del usuario.
        
    Returns:
        list: Lista de tuplas (pregunta, respuesta)
    """
    if email not in chat_histories:
        chat_histories[email] = []
    return chat_histories[email]

# Función para actualizar el historial de chat del usuario
def update_user_history(email, question, answer):
    """
    Actualiza el historial de chat del usuario con una nueva pregunta y respuesta.
    Mantiene solo las MAX_HISTORY_LENGTH más recientes.
    
    Args:
        email (str): Correo electrónico del usuario.
        question (str): Pregunta del usuario.
        answer (str): Respuesta generada.
    """
    if email not in chat_histories:
        chat_histories[email] = []
    
    # Añadir nueva conversación
    chat_histories[email].append((question, answer))
    
    # Limitar el tamaño del historial (FIFO)
    if len(chat_histories[email]) > MAX_HISTORY_LENGTH:
        chat_histories[email].pop(0)  # Eliminar el elemento más antiguo

# Función para construir el prompt con historial
def build_prompt_with_history(user_message, history, context_text=None):
    """
    Construye un prompt que incluye el historial de conversaciones recientes.
    
    Args:
        user_message (str): Mensaje actual del usuario.
        history (list): Historial de conversaciones [(pregunta1, respuesta1), ...].
        context_text (str, optional): Contexto RAG si está disponible.
        
    Returns:
        str: Prompt completo con historial
    """
    prompt = "RESPONDE A LAS SIGUIENTES PREGUNTAS CON EL CONTEXTO PROPORCIONADO, ERES UN BOT DE LA UGR EXPERTO EN LA MATERIA:\n\n"
    
    # Añadir contexto RAG si está disponible
    if context_text:
        prompt += f"{context_text}\n\n"
    
    # Añadir historial de conversaciones
    if history:
        prompt += "HISTORIAL DE CONVERSACIÓN RECIENTE:\n"
        for i, (q, a) in enumerate(history):
            prompt += f"Usuario: {q}\n"
            prompt += f"Bot: {a}\n\n"
    
    # Añadir la pregunta actual
    prompt += f"LA PREGUNTA ACTUAL A RESPONDER ES:\n{user_message}\n\n### RESPUESTA:"
    
    return prompt

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

        # Obtener el historial de chat del usuario
        user_history = get_user_history(user_email)

        # Determinar la ruta de la base de datos Chroma para la asignatura
        chroma_path = os.path.join(BASE_CHROMA_PATH, selected_subject)
        if not os.path.exists(chroma_path) and selected_mode != "base":
            return jsonify({"response": f"❌ No hay datos disponibles para la asignatura '{selected_subject}'."})

        # Llamar al modelo según el modo seleccionado, incluyendo el historial
        if selected_mode == "rag":
            # Primero recuperamos el contexto
            db = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())
            results = db.similarity_search_with_score(user_message, k=5)
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            
            # Construimos el prompt con historial
            from query_logic import load_base_model, generate_response
            tokenizer, base_model = load_base_model()
            prompt = build_prompt_with_history(user_message, user_history, context_text)
            response_text = generate_response(base_model, tokenizer, prompt)
            sources = [doc.metadata.get("id", "N/A") for doc, _score in results]
            result = {
                "response": response_text,
                "sources": sources,
                "model_used": "RAG base"
            }
            
        elif selected_mode == "rag_lora":
            # Similar al anterior pero usando el modelo fine-tuned
            db = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())
            results = db.similarity_search_with_score(user_message, k=5)
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            
            from query_logic import load_base_model, load_finetuned_model, generate_response
            tokenizer, base_model = load_base_model()
            model = load_finetuned_model(base_model, selected_subject)
            prompt = build_prompt_with_history(user_message, user_history, context_text)
            response_text = generate_response(model, tokenizer, prompt)
            sources = [doc.metadata.get("id", "N/A") for doc, _score in results]
            result = {
                "response": response_text,
                "sources": sources,
                "model_used": "RAG+LoRA"
            }
            
        elif selected_mode == "base":
            # Modelo base con historial pero sin contexto RAG
            from query_logic import load_base_model, generate_response
            tokenizer, model = load_base_model()
            prompt = build_prompt_with_history(user_message, user_history)
            response_text = generate_response(model, tokenizer, prompt)
            result = {
                "response": response_text,
                "sources": [],
                "model_used": "Base"
            }
        else:
            return jsonify({"response": "❌ Modo no válido."})

        response_text = result.get("response", "No se pudo generar una respuesta.")
        sources = result.get("sources", [])

        # Actualizar el historial del usuario
        clean_response = response_text.replace('🤖: ', '')  # Quitar el prefijo si existe
        update_user_history(user_email, user_message, clean_response)

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