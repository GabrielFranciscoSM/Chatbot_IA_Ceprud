"""
RAG Service - Servicio independiente para manejo de ChromaDB y documentos RAG
"""
import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from .rag_manager import rag_manager
from .document_processor import document_processor

app = FastAPI(
    title="RAG Service",
    description="Servicio para manejo de ChromaDB y búsquedas RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELOS PYDANTIC =====

class SearchRequest(BaseModel):
    query: str
    subject: str
    k: int = 5  # Número de documentos a recuperar
    filter_metadata: Optional[dict] = None

class SearchResponse(BaseModel):
    documents: List[dict]
    sources: List[str]

class PopulateRequest(BaseModel):
    subject: str
    documents_path: str
    clear_existing: bool = False

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class GuiaDocenteRequest(BaseModel):
    subject: str
    section: Optional[str] = None  # Si no se especifica, devuelve toda la guía

class GuiaDocenteResponse(BaseModel):
    success: bool
    data: dict
    subject: str
    section: Optional[str] = None

# ===== ENDPOINTS =====

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="rag-service",
        version="1.0.0"
    )

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Buscar documentos en ChromaDB para una asignatura específica
    """
    try:
        documents, sources = rag_manager.search_documents(
            query=request.query,
            subject=request.subject,
            k=request.k,
            filter_metadata=request.filter_metadata
        )
        
        # Convertir documentos a diccionarios
        docs_dict = []
        for doc in documents:
            docs_dict.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return SearchResponse(
            documents=docs_dict,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@app.post("/populate")
async def populate_with_files(
    subject: str = Form(...),
    reset: bool = Form(False),
    files: List[UploadFile] = File(...)
):
    """
    Poblar la base de datos ChromaDB con archivos reales (PDF/TXT)
    """
    try:
        # Validar archivos
        supported_extensions = ['.pdf', '.txt']
        for file in files:
            if not any(file.filename.lower().endswith(ext) for ext in supported_extensions):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Archivo no soportado: {file.filename}. Solo se permiten: {', '.join(supported_extensions)}"
                )
        
        # Procesar archivos
        result = await document_processor.populate_subject_from_files(
            files=files,
            subject=subject,
            reset=reset
        )
        
        if result["success"]:
            return {
                "message": result["message"],
                "subject": result["subject"],
                "processed_files": result["processed_files"],
                "failed_files": result["failed_files"],
                "documents_processed": result["documents_processed"],
                "chunks_added": result.get("chunks_added", 0),
                "existing_chunks": result.get("existing_chunks", 0)
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al poblar: {str(e)}")

@app.post("/populate/legacy")
async def populate_database_legacy(request: PopulateRequest):
    """
    Poblar la base de datos ChromaDB con documentos (endpoint legacy)
    """
    try:
        # Por ahora, poblar con datos de ejemplo
        success = rag_manager.populate_subject_with_sample_data(request.subject)
        
        if success:
            return {"message": f"Base de datos poblada para {request.subject} con datos de ejemplo"}
        else:
            raise HTTPException(status_code=500, detail="Error al poblar la base de datos")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al poblar: {str(e)}")

@app.post("/populate/sample/{subject}")
async def populate_sample_data(subject: str):
    """
    Poblar una asignatura con datos de ejemplo (endpoint simplificado)
    """
    try:
        success = rag_manager.populate_subject_with_sample_data(subject)
        
        if success:
            return {"message": f"Asignatura '{subject}' poblada con datos de ejemplo", "subject": subject}
        else:
            raise HTTPException(status_code=500, detail="Error al poblar la base de datos")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al poblar: {str(e)}")

@app.get("/subjects")
async def list_subjects():
    """
    Listar asignaturas disponibles en ChromaDB
    """
    try:
        subjects = rag_manager.list_subjects()
        return {"subjects": subjects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar: {str(e)}")

@app.delete("/subjects/{subject}")
async def clear_subject_database(subject: str):
    """
    Limpiar la base de datos de una asignatura específica
    """
    try:
        result = document_processor.clear_database(subject)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar: {str(e)}")

@app.get("/guia-docente/{subject}")
async def get_guia_docente(subject: str, section: Optional[str] = None):
    """
    Obtener información de la guía docente de una asignatura
    
    Args:
        subject: Nombre de la asignatura
        section: Sección específica (opcional). Si no se especifica, devuelve toda la guía.
                Secciones disponibles: profesorado, evaluacion, temario, metodologia, 
                bibliografia, prerrequisitos, competencias, enlaces, informacion_adicional
    """
    try:
        import json
        
        # Buscar el archivo de guía docente
        possible_paths = [
            f"/app/data/{subject}/guía_docente.json",
            f"/app/data/{subject}/guia_docente.json"
        ]
        
        guia_path = None
        for path in possible_paths:
            if os.path.exists(path):
                guia_path = path
                break
        
        if not guia_path:
            raise HTTPException(
                status_code=404, 
                detail=f"Guía docente no encontrada para la asignatura: {subject}"
            )
        
        # Cargar el JSON
        with open(guia_path, 'r', encoding='utf-8') as f:
            guia_data = json.load(f)
        
        # Si se especifica una sección, extraerla
        if section:
            # Mapeo de secciones (igual que en graph.py)
            section_mapping = {
                "profesorado": "profesorado_y_tutorias",
                "profesores": "profesorado_y_tutorias", 
                "tutorias": "profesorado_y_tutorias",
                "evaluacion": "evaluación",
                "evaluación": "evaluación",
                "temario": "programa_de_contenidos_teóricos_y_prácticos",
                "programa": "programa_de_contenidos_teóricos_y_prácticos",
                "metodologia": "metodología_docente",
                "metodología": "metodología_docente",
                "bibliografia": "bibliografía",
                "bibliografía": "bibliografía",
                "prerrequisitos": "prerrequisitos_o_recomendaciones",
                "competencias": "resultados_del_proceso_de_formación_y_de_aprendizaje",
                "resultados": "resultados_de_aprendizaje",
                "enlaces": "enlaces_recomendados",
                "informacion_adicional": "información_adicional",
                "información_adicional": "información_adicional"
            }
            
            section_key = section_mapping.get(section.lower(), section)
            section_data = guia_data.get(section_key)
            
            if section_data is None:
                available_sections = list(guia_data.keys())
                raise HTTPException(
                    status_code=404,
                    detail=f"Sección '{section}' no encontrada. Secciones disponibles: {available_sections}"
                )
            
            return GuiaDocenteResponse(
                success=True,
                data={section_key: section_data},
                subject=subject,
                section=section
            )
        else:
            # Devolver toda la guía
            return GuiaDocenteResponse(
                success=True,
                data=guia_data,
                subject=subject,
                section=None
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer guía docente: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8082, 
        reload=True
    )
