"""
Cliente HTTP para comunicarse con el RAG Service
"""
import os
import requests
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class RAGServiceClient:
    """Cliente para comunicarse con el RAG Service"""
    
    def __init__(self):
        self.base_url = os.getenv("RAG_SERVICE_URL", "http://rag-service:8082")
        
    def search_documents(
        self, 
        query: str, 
        subject: str, 
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Tuple[List[Document], List[str]]:
        """
        Buscar documentos en el RAG Service
        
        Args:
            query: Consulta de búsqueda
            subject: Asignatura
            k: Número de documentos a recuperar
            filter_metadata: Filtros adicionales
            
        Returns:
            Tupla con (documentos, fuentes)
        """
        try:
            payload = {
                "query": query,
                "subject": subject,
                "k": k,
                "filter_metadata": filter_metadata
            }
            
            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Convertir documentos de vuelta a objetos Document
                documents = []
                for doc_data in data["documents"]:
                    doc = Document(
                        page_content=doc_data["content"],
                        metadata=doc_data["metadata"]
                    )
                    documents.append(doc)
                
                return documents, data["sources"]
            else:
                print(f"Error en RAG Service: {response.status_code} - {response.text}")
                return [], []
                
        except requests.exceptions.RequestException as e:
            print(f"Error conectando con RAG Service: {str(e)}")
            return [], []
        except Exception as e:
            print(f"Error inesperado en RAG Service: {str(e)}")
            return [], []
    
    def list_subjects(self) -> List[str]:
        """Lista las asignaturas disponibles"""
        try:
            response = requests.get(
                f"{self.base_url}/subjects",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["subjects"]
            else:
                print(f"Error listando asignaturas: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error listando asignaturas: {str(e)}")
            return []
    
    def health_check(self) -> bool:
        """Verifica si el RAG Service está disponible"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# Instancia global del cliente
rag_client = RAGServiceClient()
