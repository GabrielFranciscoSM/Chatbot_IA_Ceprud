# Documentación de API - Chatbot IA CEPRUD

## 🌟 Descripción General

La API del Chatbot IA CEPRUD está construida con FastAPI y sigue los principios REST. Proporciona endpoints para interacciones de chat, gestión de sesiones, y operaciones administrativas. La API está distribuida en múltiples microservicios especializados.

## 🔗 URLs Base

- **Backend Principal**: `http://localhost:8080`
- **RAG Service**: `http://localhost:8082`
- **Logging Service**: `http://localhost:8002`
- **Frontend**: `http://localhost:8090`

## 📚 Documentación Interactiva

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI JSON**: `http://localhost:8080/openapi.json`

## 🔐 Autenticación

Actualmente la API no requiere autenticación, pero implementa rate limiting por IP:
- **Límite**: 20 requests por minuto por IP
- **Headers de respuesta**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## 📋 Backend Service API (Puerto 8080)

### **Sistema y Salud**

#### `GET /`
Información básica de la API.

**Respuesta:**
```json
{
  "message": "Chatbot UGR API",
  "version": "2.0",
  "frontend_url": "http://localhost:3000",
  "docs": "/docs"
}
```

#### `GET /health`
Health check del servicio.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "backend",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Chat y Conversaciones**

#### `POST /chat`
Procesa un mensaje del usuario y devuelve la respuesta del chatbot.

**Request Body:**
```json
{
  "message": "¿Qué es la programación orientada a objetos?",
  "subject": "Programacion_I",
  "session_id": "user_123_session_456",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "response": "La programación orientada a objetos es un paradigma...",
  "subject": "Programacion_I",
  "session_id": "user_123_session_456",
  "timestamp": "2024-01-15T10:30:00Z",
  "sources": [
    {
      "document": "POO_conceptos.pdf",
      "page": 15,
      "relevance": 0.92
    }
  ],
  "processing_time": 1.24
}
```

**Códigos de Estado:**
- `200`: Respuesta exitosa
- `400`: Request inválido
- `429`: Rate limit excedido
- `500`: Error interno

### **Asignaturas**

#### `GET /subjects`
Lista todas las asignaturas disponibles.

**Response:**
```json
{
  "subjects": [
    {
      "id": "Programacion_I",
      "name": "Programación I",
      "description": "Fundamentos de programación",
      "document_count": 25,
      "last_updated": "2024-01-10T15:20:00Z"
    },
    {
      "id": "Estructuras_Datos",
      "name": "Estructuras de Datos",
      "description": "Algoritmos y estructuras de datos",
      "document_count": 18,
      "last_updated": "2024-01-12T09:15:00Z"
    }
  ]
}
```

#### `GET /subjects/{subject_id}/info`
Información detallada de una asignatura específica.

**Parámetros:**
- `subject_id`: ID de la asignatura

**Response:**
```json
{
  "id": "Programacion_I",
  "name": "Programación I",
  "description": "Fundamentos de programación",
  "document_count": 25,
  "topics": ["Variables", "Funciones", "POO", "Algoritmos"],
  "last_updated": "2024-01-10T15:20:00Z",
  "statistics": {
    "total_queries": 1250,
    "avg_response_time": 1.8,
    "satisfaction_rate": 0.87
  }
}
```

### **Sesiones**

#### `POST /sessions`
Crea una nueva sesión de usuario.

**Request Body:**
```json
{
  "user_id": "user_123",
  "subject": "Programacion_I"
}
```

**Response:**
```json
{
  "session_id": "user_123_session_456",
  "user_id": "user_123",
  "subject": "Programacion_I",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T18:30:00Z"
}
```

#### `GET /sessions/{session_id}`
Obtiene información de una sesión específica.

**Response:**
```json
{
  "session_id": "user_123_session_456",
  "user_id": "user_123",
  "subject": "Programacion_I",
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T11:45:00Z",
  "message_count": 8,
  "status": "active"
}
```

#### `DELETE /sessions/{session_id}`
Finaliza una sesión específica.

**Response:**
```json
{
  "message": "Session ended successfully",
  "session_id": "user_123_session_456"
}
```

### **Rate Limiting**

#### `GET /rate-limit/status`
Consulta el estado actual del rate limiting para la IP.

**Response:**
```json
{
  "ip": "192.168.1.100",
  "requests_remaining": 15,
  "reset_time": "2024-01-15T10:31:00Z",
  "window_seconds": 60
}
```

## 🔍 RAG Service API (Puerto 8082)

### **Búsqueda Semántica**

#### `POST /search`
Realiza búsqueda semántica en la base de conocimiento.

**Request Body:**
```json
{
  "query": "programación orientada a objetos",
  "subject": "Programacion_I",
  "k": 5,
  "filter_metadata": {
    "document_type": "teoria"
  }
}
```

**Response:**
```json
{
  "documents": [
    {
      "content": "La programación orientada a objetos...",
      "metadata": {
        "source": "POO_conceptos.pdf",
        "page": 15,
        "document_type": "teoria"
      },
      "score": 0.92
    }
  ],
  "sources": ["POO_conceptos.pdf", "OOP_examples.pdf"],
  "total_found": 5,
  "processing_time": 0.34
}
```

### **Gestión de Documentos**

#### `POST /upload`
Sube y procesa nuevos documentos.

**Request (multipart/form-data):**
- `file`: Archivo PDF/TXT
- `subject`: Asignatura
- `document_type`: Tipo de documento (teoria, practica, examen)

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document_id": "doc_456",
  "subject": "Programacion_I",
  "chunks_created": 25,
  "processing_time": 3.45
}
```

#### `POST /populate`
Pobla la base de datos con documentos de un directorio.

**Request Body:**
```json
{
  "subject": "Programacion_I",
  "documents_path": "/app/data/documents/programacion",
  "clear_existing": false
}
```

**Response:**
```json
{
  "message": "Database populated successfully",
  "subject": "Programacion_I",
  "documents_processed": 15,
  "chunks_created": 342,
  "processing_time": 45.67
}
```

### **Administración**

#### `GET /subjects`
Lista asignaturas disponibles en el RAG.

**Response:**
```json
{
  "subjects": [
    {
      "name": "Programacion_I",
      "document_count": 15,
      "chunk_count": 342,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `DELETE /subjects/{subject}`
Elimina todos los documentos de una asignatura.

**Response:**
```json
{
  "message": "Subject documents deleted successfully",
  "subject": "Programacion_I",
  "documents_deleted": 15,
  "chunks_deleted": 342
}
```

### **Guías Docentes**

#### `POST /scrape-guia`
Extrae información de una guía docente desde URL.

**Request Body:**
```json
{
  "url": "https://grados.ugr.es/informatica/programacion-1",
  "subject": "Programacion_I"
}
```

**Response:**
```json
{
  "message": "Guía docente scraped successfully",
  "subject": "Programacion_I",
  "data_extracted": {
    "objetivos": "Aprender fundamentos...",
    "contenidos": "1. Variables, 2. Funciones...",
    "metodologia": "Clases teóricas y prácticas...",
    "evaluacion": "Exámenes y prácticas..."
  }
}
```

## 📊 Logging Service API (Puerto 8002)

### **Registro de Eventos**

#### `POST /log/interaction`
Registra una interacción de chat.

**Request Body:**
```json
{
  "session_id": "user_123_session_456",
  "user_id": "user_123",
  "subject": "Programacion_I",
  "query": "¿Qué es una variable?",
  "response": "Una variable es un espacio de memoria...",
  "response_time": 1.24,
  "sources_used": ["variables.pdf"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "message": "Interaction logged successfully",
  "log_id": "log_789"
}
```

#### `POST /log/session`
Registra eventos de sesión.

**Request Body:**
```json
{
  "session_id": "user_123_session_456",
  "user_id": "user_123",
  "event_type": "session_start",
  "subject": "Programacion_I",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "ip": "192.168.1.100"
  }
}
```

### **Analytics**

#### `GET /analytics/summary`
Resumen de analytics del sistema.

**Query Parameters:**
- `start_date`: Fecha inicio (YYYY-MM-DD)
- `end_date`: Fecha fin (YYYY-MM-DD)
- `subject`: Filtrar por asignatura (opcional)

**Response:**
```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-15"
  },
  "total_interactions": 2547,
  "unique_users": 234,
  "avg_response_time": 1.67,
  "subjects": {
    "Programacion_I": {
      "interactions": 1200,
      "users": 150,
      "avg_response_time": 1.45
    }
  },
  "top_queries": [
    {
      "query": "¿Qué es una variable?",
      "count": 67
    }
  ]
}
```

#### `GET /analytics/performance`
Métricas de rendimiento del sistema.

**Response:**
```json
{
  "response_times": {
    "avg": 1.67,
    "p50": 1.2,
    "p95": 3.4,
    "p99": 5.8
  },
  "throughput": {
    "requests_per_hour": 125,
    "peak_hour": "14:00-15:00"
  },
  "error_rates": {
    "total_errors": 23,
    "error_rate": 0.009
  }
}
```

#### `GET /analytics/learning`
Analytics de aprendizaje y patrones de uso.

**Response:**
```json
{
  "learning_patterns": {
    "peak_hours": ["10:00-12:00", "16:00-18:00"],
    "popular_subjects": [
      {
        "subject": "Programacion_I",
        "percentage": 35.2
      }
    ],
    "query_categories": {
      "conceptos_basicos": 45,
      "ejercicios": 30,
      "dudas_especificas": 25
    }
  },
  "user_behavior": {
    "avg_session_duration": 18.5,
    "avg_messages_per_session": 6.2,
    "return_rate": 0.68
  }
}
```

## 📤 Modelos de Datos

### **ChatRequest**
```typescript
interface ChatRequest {
  message: string;          // Mensaje del usuario (max 1000 chars)
  subject: string;          // ID de la asignatura
  session_id?: string;      // ID de sesión (opcional, se genera si no se proporciona)
  user_id?: string;         // ID del usuario (opcional)
}
```

### **ChatResponse**
```typescript
interface ChatResponse {
  response: string;         // Respuesta del chatbot
  subject: string;          // Asignatura utilizada
  session_id: string;       // ID de la sesión
  timestamp: string;        // ISO 8601 timestamp
  sources: Source[];        // Fuentes utilizadas
  processing_time: number;  // Tiempo de procesamiento en segundos
}
```

### **Source**
```typescript
interface Source {
  document: string;         // Nombre del documento
  page?: number;           // Página (si aplica)
  relevance: number;       // Puntuación de relevancia (0-1)
  chunk_id?: string;       // ID del chunk específico
}
```

### **Subject**
```typescript
interface Subject {
  id: string;              // ID único de la asignatura
  name: string;            // Nombre completo
  description: string;     // Descripción breve
  document_count: number;  // Número de documentos
  last_updated: string;    // Última actualización (ISO 8601)
}
```

### **Session**
```typescript
interface Session {
  session_id: string;      // ID único de la sesión
  user_id: string;         // ID del usuario
  subject: string;         // Asignatura de la sesión
  created_at: string;      // Timestamp de creación
  last_activity: string;   // Última actividad
  message_count: number;   // Número de mensajes
  status: 'active' | 'ended';  // Estado de la sesión
}
```

## ⚠️ Códigos de Error

### **Códigos HTTP Estándar**
- `200`: Éxito
- `201`: Creado exitosamente
- `400`: Request inválido
- `404`: Recurso no encontrado
- `429`: Rate limit excedido
- `500`: Error interno del servidor
- `503`: Servicio no disponible

### **Errores Específicos**

#### **Error 400 - Request Inválido**
```json
{
  "error": "validation_error",
  "message": "Invalid request format",
  "details": {
    "field": "message",
    "issue": "Message cannot be empty"
  }
}
```

#### **Error 429 - Rate Limit**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "retry_after": 45,
  "limit": 20,
  "window": 60
}
```

#### **Error 500 - Error Interno**
```json
{
  "error": "internal_error",
  "message": "An internal error occurred",
  "request_id": "req_123456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Configuración de Cliente

### **Headers Recomendados**
```http
Content-Type: application/json
Accept: application/json
User-Agent: YourApp/1.0
X-Request-ID: unique-request-id  # Para trazabilidad
```

### **Ejemplo Cliente JavaScript**
```javascript
class ChatbotClient {
  constructor(baseUrl = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
  }

  async sendMessage(message, subject, sessionId = null) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        subject,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  async getSubjects() {
    const response = await fetch(`${this.baseUrl}/subjects`);
    return await response.json();
  }
}

// Uso
const client = new ChatbotClient();
const response = await client.sendMessage(
  "¿Qué es una variable?", 
  "Programacion_I"
);
```

### **Ejemplo Cliente Python**
```python
import requests
from typing import Optional, Dict, Any

class ChatbotClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def send_message(self, message: str, subject: str, 
                    session_id: Optional[str] = None) -> Dict[Any, Any]:
        response = self.session.post(
            f"{self.base_url}/chat",
            json={
                "message": message,
                "subject": subject,
                "session_id": session_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_subjects(self) -> Dict[Any, Any]:
        response = self.session.get(f"{self.base_url}/subjects")
        response.raise_for_status()
        return response.json()

# Uso
client = ChatbotClient()
response = client.send_message("¿Qué es una variable?", "Programacion_I")
print(response["response"])
```

## 📊 Límites y Quotas

- **Rate Limiting**: 20 requests/minuto por IP
- **Tamaño máximo mensaje**: 1000 caracteres
- **Timeout de respuesta**: 30 segundos
- **Tamaño máximo archivo**: 10 MB
- **Sesiones concurrentes**: 100 por usuario
- **Duración máxima sesión**: 8 horas

## 🔄 Versionado de API

La API sigue versionado semántico:
- **Versión actual**: v2.0
- **Endpoint de versión**: `GET /version`
- **Compatibility**: Backward compatible dentro de major version

## 📚 Recursos Adicionales

- **Postman Collection**: `docs/api/chatbot-api.postman_collection.json`
- **OpenAPI Spec**: `http://localhost:8080/openapi.json`
- **Ejemplos**: `examples/api-examples/`
- **SDK Oficial**: `github.com/your-org/chatbot-sdk`

## 🆘 Soporte de API

Para problemas con la API:
1. Consultar logs: `docker-compose logs backend`
2. Verificar health endpoints
3. Revisar documentación Swagger
4. Reportar issues en GitHub con request/response examples
