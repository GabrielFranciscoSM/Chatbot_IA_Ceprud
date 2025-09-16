"""
Módulo para manejo de ChromaDB y búsquedas RAG
"""
import os
import shutil
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .embeddings import get_embedding_function

# Configuración de rutas
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "/app/data/chroma")

class RAGManager:
    """Clase para manejar operaciones de ChromaDB"""
    
    def __init__(self):
        self.embedding_function = get_embedding_function()
        
    def _get_chroma_path(self, subject: str) -> str:
        """Obtiene la ruta de ChromaDB para una asignatura"""
        return os.path.join(BASE_CHROMA_PATH, subject)
    
    def search_documents(
        self, 
        query: str, 
        subject: str, 
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> tuple[List[Document], List[str]]:
        """
        Buscar documentos relevantes en ChromaDB
        
        Args:
            query: Consulta de búsqueda
            subject: Asignatura
            k: Número de documentos a recuperar
            filter_metadata: Filtros adicionales
            
        Returns:
            Tupla con (documentos, fuentes)
        """
        chroma_path = self._get_chroma_path(subject)
        
        if not os.path.exists(chroma_path):
            return [], []
        
        try:
            # Crear conexión a ChromaDB
            db = Chroma(
                persist_directory=chroma_path,
                embedding_function=self.embedding_function
            )
            
            # Realizar búsqueda por similaridad
            docs = db.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_metadata
            )
            
            # Extraer documentos y fuentes
            documents = [doc for doc, score in docs]
            sources = [doc.metadata.get("source", "N/A") for doc in documents]
            
            return documents, sources
            
        except Exception as e:
            print(f"Error en búsqueda RAG: {str(e)}")
            return [], []
    
    def list_subjects(self) -> List[str]:
        """Lista las asignaturas disponibles en ChromaDB"""
        if not os.path.exists(BASE_CHROMA_PATH):
            return []
        
        try:
            subjects = []
            for item in os.listdir(BASE_CHROMA_PATH):
                item_path = os.path.join(BASE_CHROMA_PATH, item)
                if os.path.isdir(item_path):
                    subjects.append(item)
            return subjects
        except Exception as e:
            print(f"Error listando asignaturas: {str(e)}")
            return []
    
    def check_subject_exists(self, subject: str) -> bool:
        """Verifica si existe la base de datos para una asignatura"""
        chroma_path = self._get_chroma_path(subject)
        return os.path.exists(chroma_path)
    
    def clear_subject_database(self, subject: str) -> bool:
        """Limpia la base de datos de una asignatura"""
        chroma_path = self._get_chroma_path(subject)
        
        try:
            if os.path.exists(chroma_path):
                shutil.rmtree(chroma_path)
                print(f"🗑️ Base de datos eliminada: {chroma_path}")
                return True
            return False
        except Exception as e:
            print(f"Error eliminando base de datos: {str(e)}")
            return False
    
    def populate_subject_with_sample_data(self, subject: str) -> bool:
        """
        Poblar una asignatura con datos de ejemplo para testing
        """
        try:
            chroma_path = self._get_chroma_path(subject)
            
            # Crear documentos de ejemplo
            sample_docs = [
                Document(
                    page_content="""
                    Un algoritmo greedy es un paradigma algorítmico que sigue la heurística de resolver problemas 
                    haciendo la elección localmente óptima en cada etapa. Es decir, en cada paso, el algoritmo 
                    selecciona la opción que parece la mejor en ese momento, sin considerar las consecuencias futuras.
                    
                    Características principales:
                    - Hace elecciones localmente óptimas
                    - No reconsidera decisiones anteriores
                    - Es eficiente computacionalmente
                    - No siempre encuentra la solución global óptima
                    """,
                    metadata={"source": "algoritmos_greedy.pdf", "page": 1, "topic": "algoritmos"}
                ),
                Document(
                    page_content="""
                    Ejemplos clásicos de algoritmos greedy:
                    
                    1. Algoritmo de Dijkstra para caminos más cortos
                    2. Algoritmo de Kruskal para árbol de expansión mínima
                    3. Planificación de trabajos (Job Scheduling)
                    4. Problema de la mochila fraccionaria
                    5. Codificación de Huffman
                    
                    El algoritmo greedy funciona bien cuando el problema tiene la propiedad 
                    de subestructura óptima y la propiedad greedy.
                    """,
                    metadata={"source": "ejemplos_greedy.pdf", "page": 2, "topic": "ejemplos"}
                ),
                Document(
                    page_content="""
                    Metaheurísticas: son estrategias de alto nivel para resolver problemas de optimización 
                    difíciles. Se utilizan cuando los métodos exactos no son eficientes debido al 
                    tamaño del problema o su complejidad.
                    
                    Tipos principales:
                    - Algoritmos evolutivos (genéticos, evolución diferencial)
                    - Búsqueda local (simulated annealing, búsqueda tabú)
                    - Inteligencia de enjambres (PSO, colonias de hormigas)
                    - Algoritmos basados en poblaciones
                    """,
                    metadata={"source": "metaheuristicas_intro.pdf", "page": 1, "topic": "metaheuristicas"}
                )
            ]
            
            # Crear la base de datos ChromaDB
            db = Chroma(
                persist_directory=chroma_path,
                embedding_function=self.embedding_function
            )
            
            # Añadir documentos
            db.add_documents(sample_docs)
            
            print(f"✅ Poblada asignatura '{subject}' con {len(sample_docs)} documentos de ejemplo")
            return True
            
        except Exception as e:
            print(f"Error poblando asignatura {subject}: {str(e)}")
            return False

# Instancia global del manager
rag_manager = RAGManager()
