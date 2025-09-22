"""
Módulo para manejo de ChromaDB y búsquedas RAG
"""
import os
import shutil
import re
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
        # Simple Spanish stop words for better keyword matching
        self.stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son',
            'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'me', 'hasta', 'hay', 'donde',
            'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso'
        }
        
    def _clean_query(self, query: str) -> List[str]:
        """Extract meaningful words from query"""
        # Remove punctuation and convert to lowercase
        clean_query = re.sub(r'[^\w\s]', ' ', query.lower())
        words = clean_query.split()
        # Keep only meaningful words (longer than 2 chars, not stop words)
        meaningful_words = [word for word in words if len(word) > 2 and word not in self.stop_words]
        return meaningful_words
        
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
            
            # Optional: Use expanded query for better results
            # expanded_query = self._expand_query(query)
            # For now, let's keep it simple and use original query
            search_query = query
            
            # Realizar búsqueda por similaridad
            docs = db.similarity_search_with_score(
                query=search_query,
                k=k*2,
                filter=filter_metadata
            )
            
            # 1. Better adaptive threshold
            scores = [score for _, score in docs]
            if not scores:
                print(f"⚠️  No documents found for query: '{query}' in {subject}")
                return [], []
                
            if len(scores) == 1:
                # If only one document, use it
                adaptive_threshold = scores[0] + 0.1
            else:
                avg_score = sum(scores) / len(scores)
                std_score = (sum((s - avg_score) ** 2 for s in scores) / len(scores)) ** 0.5
                # More lenient threshold for better recall
                adaptive_threshold = max(avg_score - 0.3 * std_score, 0.6)

            filtered_docs = [(doc, score) for doc, score in docs if score < adaptive_threshold]
            
            # Ensure we have at least some documents
            if not filtered_docs and docs:
                # If threshold is too strict, take the best 2 documents
                sorted_docs = sorted(docs, key=lambda x: x[1])
                filtered_docs = sorted_docs[:2]
                print(f"⚠️  Threshold too strict, using top 2 documents")
            elif not filtered_docs:
                print(f"❌ No documents pass the threshold for: '{query}'")
                return [], []

            # 2. Improved reranking with better keyword matching
            query_keywords = self._clean_query(query)
            reranked_docs = []
            
            for doc, original_score in filtered_docs:
                content_lower = doc.page_content.lower()
                
                # Better keyword overlap score
                keyword_overlap = 0
                for keyword in query_keywords:
                    if keyword in content_lower:
                        # Count how many times the keyword appears
                        count = content_lower.count(keyword)
                        keyword_overlap += count
                
                # Content quality score (prefer medium-length, structured content)
                content_length = len(doc.page_content)
                if 200 <= content_length <= 1500:
                    length_score = 1.0
                elif 100 <= content_length < 200:
                    length_score = 0.8
                else:
                    length_score = 0.6
                
                # Structure score (lists, headings, etc.)
                structure_indicators = [':', '•', '-', '1.', '2.', '3.', '\n-', '\n*']
                structure_score = 1.0 + sum(0.1 for indicator in structure_indicators if indicator in content_lower)
                
                # Combined score (lower is better, so we subtract bonuses)
                bonus = (keyword_overlap * 0.15) + (length_score * 0.1) + (structure_score * 0.05)
                rerank_score = original_score - bonus
                
                reranked_docs.append((doc, rerank_score, original_score, keyword_overlap))

            # Sort by reranked score and take top results
            reranked_docs.sort(key=lambda x: x[1])
            final_docs = reranked_docs[:k]  # Use k instead of hardcoded 4

            # Simple logging for debugging
            print(f"🔍 RAG Search for '{query}' in {subject}:")
            print(f"  Found {len(docs)} initial docs, filtered to {len(filtered_docs)}, final: {len(final_docs)}")
            for i, (doc, rerank_score, original_score, keyword_matches) in enumerate(final_docs):
                source = doc.metadata.get("source", "Unknown")
                print(f"  {i+1}. {source} - Score: {rerank_score:.3f} (Keywords: {keyword_matches})")

            # Extract documents and sources
            documents = [doc for doc, _, _, _ in final_docs]
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
    
    def _expand_query(self, query: str) -> str:
        """Simple query expansion with common synonyms and related terms"""
        # Basic synonym mapping for academic terms
        synonyms = {
            'algoritmo': ['algoritmos', 'método', 'procedimiento', 'técnica'],
            'optimización': ['optimizar', 'mejorar', 'eficiencia'],
            'problema': ['problemas', 'ejercicio', 'cuestión'],
            'función': ['funciones', 'operación'],
            'estructura': ['estructuras', 'organización'],
            'datos': ['información', 'data'],
            'búsqueda': ['buscar', 'encontrar', 'localizar'],
            'análisis': ['analizar', 'estudiar', 'examinar'],
            'ejemplo': ['ejemplos', 'caso', 'instancia'],
            'definición': ['definir', 'concepto', 'significado']
        }
        
        expanded_terms = [query]  # Start with original query
        query_lower = query.lower()
        
        # Add synonyms for words found in the query
        for term, term_synonyms in synonyms.items():
            if term in query_lower:
                expanded_terms.extend(term_synonyms)
        
        # Return expanded query (limit to avoid too long queries)
        return ' '.join(expanded_terms[:10])

# Instancia global del manager
rag_manager = RAGManager()
