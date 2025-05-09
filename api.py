# api.py (servIA)
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from query_logic import (
    initialize_models,
    query_rag,
    get_base_model_response,
)

app = FastAPI()

# Configuración CORS para permitir llamadas desde servWEB
origins = ["http://<IP_servWEB>:puerto"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Inicialización de modelos
@app.on_event("startup")
async def on_startup():
    initialize_models()

@app.post("/chat", response_model=dict)
async def chat(
    message: str = Form(...),
    subject: str = Form("default"),
    email: str = Form("anonimo"),
    mode: str = Form("rag"),
):
    """
    Endpoint para procesar consultas del chatbot.
    """
    if not message.strip():
        return {"response": "❌ Por favor, escribe una pregunta."}

    # Determinar el modo de respuesta
    if mode in ["rag", "rag_lora"]:
        result = query_rag(
            message,
            chroma_path=f"./chroma/{subject.lower()}",
            use_finetuned=(mode == "rag_lora"),
        )
    elif mode == "base":
        result = get_base_model_response(message)
    else:
        return {"response": "❌ Modo no válido."}

    # Devolver respuesta al frontend
    return {
        "response": f"🤖: {result['response']}",
        "sources": result.get("sources", []),
        "model_used": result.get("model_used", ""),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)