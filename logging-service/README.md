# Logging Service

Microservicio dedicado para el manejo de logs y análisis de conversaciones del chatbot educativo. Utiliza MongoDB como sistema de almacenamiento principal, proporcionando capacidades NoSQL para estructurar conversaciones por sesión y usuario.

## 🚀 Características

- **Almacenamiento en MongoDB**: Logs estructurados en colecciones NoSQL
- **Conversaciones por sesión**: Cada sesión mantiene un historial completo de mensajes
- **Análisis de interacciones**: Métricas y analytics de uso del chatbot
- **API RESTful**: Endpoints para logging y consultas
- **Fallback a CSV**: Soporte legacy para archivos CSV en caso de fallo

## 📊 Estructura de Datos

### Colecciones MongoDB

#### 1. `conversations`
Almacena conversaciones completas organizadas por sesión:

```json
{
  "session_id": "uuid-session-123",
  "user_id": "user@example.com",
  "subject": "Cálculo I",
  "messages": [
    {
      "message_type": "user",
      "content": "¿Qué es una derivada?",
      "timestamp": "2025-10-12T10:30:00Z",
      "metadata": {}
    },
    {
      "message_type": "bot",
      "content": "Una derivada representa...",
      "timestamp": "2025-10-12T10:30:05Z",
      "metadata": {}
    }
  ],
  "created_at": "2025-10-12T10:30:00Z",
  "updated_at": "2025-10-12T10:35:00Z",
  "metadata": {}
}
```

#### 2. `interaction_analytics`
Métricas de interacciones usuario-chatbot:

```json
{
  "session_id": "uuid-session-123",
  "user_id_partial": "user@exa...",
  "subject": "Cálculo I",
  "message_length": 250,
  "query_type": "conceptual",
  "complexity": "medium",
  "response_length": 500,
  "source_count": 3,
  "llm_model_used": "granite-3.3-2b",
  "timestamp": "2025-10-12T10:30:00Z"
}
```

#### 3. `session_events`
Eventos de sesión (inicio, fin, etc.):

```json
{
  "session_id": "uuid-session-123",
  "user_id": "user@example.com",
  "subject": "Cálculo I",
  "event_type": "session_start",
  "timestamp": "2025-10-12T10:30:00Z"
}
```

#### 4. `learning_events`
Eventos relacionados con aprendizaje:

```json
{
  "session_id": "uuid-session-123",
  "event_type": "concept_mastery",
  "topic": "Derivadas",
  "confidence_level": "high",
  "timestamp": "2025-10-12T10:35:00Z"
}
```

## 🔌 API Endpoints

### Logging Endpoints

#### POST `/api/v1/logs/conversation-message`
Registra un mensaje individual (usuario o bot) en una conversación.

```json
{
  "session_id": "uuid-123",
  "user_id": "user@example.com",
  "subject": "Cálculo I",
  "message_type": "user",
  "message_content": "¿Qué es una derivada?",
  "timestamp": 1697112600.0
}
```

#### POST `/api/v1/logs/user-message`
Registra métricas de una interacción.

```json
{
  "session_id": "uuid-123",
  "user_id_partial": "user@exa...",
  "subject": "Cálculo I",
  "message_length": 250,
  "query_type": "conceptual",
  "complexity": "medium",
  "response_length": 500,
  "source_count": 3,
  "llm_model_used": "granite-3.3-2b"
}
```

#### POST `/api/v1/logs/session-event`
Registra eventos de sesión.

```json
{
  "session_id": "uuid-123",
  "user_id": "user@example.com",
  "subject": "Cálculo I",
  "event_type": "session_start"
}
```

### Query Endpoints

#### GET `/api/v1/conversations/{session_id}`
Obtiene una conversación completa por ID de sesión.

**Respuesta:**
```json
{
  "session_id": "uuid-123",
  "user_id": "user@example.com",
  "subject": "Cálculo I",
  "messages": [...],
  "created_at": "2025-10-12T10:30:00Z",
  "updated_at": "2025-10-12T10:35:00Z"
}
```

#### GET `/api/v1/conversations/user/{user_id}?skip=0&limit=10`
Obtiene todas las conversaciones de un usuario (paginado).

#### GET `/api/v1/conversations/subject/{subject}?skip=0&limit=10`
Obtiene todas las conversaciones de una asignatura (paginado).

#### GET `/api/v1/analytics/sessions?start_date=2025-10-01&end_date=2025-10-12&subject=Cálculo I`
Obtiene analytics de sesiones con filtros opcionales.

#### GET `/api/v1/analytics/interactions?start_date=2025-10-01&end_date=2025-10-12&subject=Cálculo I`
Obtiene analytics de interacciones con filtros opcionales.

## 🔧 Configuración

### Variables de Entorno

```bash
# MongoDB Configuration
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DATABASE=chatbot_logs

# Service Configuration
BASE_LOG_DIR=/app/logs  # Fallback CSV directory
```

### Docker Setup

El servicio se integra con el docker-compose existente:

```yaml
logging-service:
  build: ./logging-service
  environment:
    - MONGODB_URL=mongodb://mongodb:27017
    - MONGODB_DATABASE=chatbot_logs
  depends_on:
    - mongodb
```

## 🏗️ Arquitectura

```
┌─────────────────────┐
│   Main App          │
│   (FastAPI)         │
└──────────┬──────────┘
           │ HTTP calls
           ▼
┌─────────────────────┐
│  Logging Service    │
│  (Microservice)     │
└──────────┬──────────┘
           │
           ├─────────────┐
           ▼             ▼
    ┌──────────┐  ┌──────────┐
    │ MongoDB  │  │ CSV Files│
    │ (Primary)│  │ (Fallback)│
    └──────────┘  └──────────┘
```

## 🔍 Ventajas del Sistema MongoDB

1. **Estructura por Sesión**: Las conversaciones se agrupan automáticamente por sesión
2. **Consultas Flexibles**: Búsqueda por usuario, sesión, asignatura, fechas
3. **Escalabilidad**: MongoDB maneja grandes volúmenes de datos conversacionales
4. **Schema Flexible**: Fácil extensión con metadata adicional
5. **Análisis Avanzado**: Posibilidad de agregaciones complejas

## 📝 Migración desde CSV

Si tienes logs existentes en CSV, puedes crear un script de migración:

```python
# Ejemplo de migración (implementar según necesidad)
async def migrate_csv_to_mongodb():
    # Leer CSV
    # Agrupar por session_id
    # Crear documentos ConversationDocument
    # Insertar en MongoDB
    pass
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8002/health

# Log a conversation message
curl -X POST http://localhost:8002/api/v1/logs/conversation-message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "user_id": "test@example.com",
    "subject": "Test Subject",
    "message_type": "user",
    "message_content": "Test message",
    "timestamp": 1697112600.0
  }'

# Get conversation
curl http://localhost:8002/api/v1/conversations/test-123
```

## 📚 Dependencias

- **FastAPI**: Framework web asíncrono
- **Motor**: Driver asíncrono de MongoDB para Python
- **Pydantic**: Validación de datos
- **aiofiles**: Soporte para fallback CSV

## 🔐 Consideraciones de Privacidad

- Los IDs de usuario se anonimizan parcialmente en analytics
- Las conversaciones completas se almacenan con el user_id para trazabilidad
- Implementar políticas de retención de datos según normativas (GDPR, etc.)

## 🚧 Desarrollo Futuro

- [ ] Índices MongoDB para optimización de consultas
- [ ] Agregaciones para dashboards de analytics
- [ ] Exportación de conversaciones en formatos múltiples
- [ ] Sistema de búsqueda de texto completo en conversaciones
- [ ] Métricas de calidad de respuestas del chatbot

## Overview

This service provides RESTful APIs for logging various events and interactions from the main chatbot application:

- Session events
- User messages
- Learning events  
- Request information
- Bot responses

## Architecture

- **FastAPI**: Modern Python web framework for building APIs
- **Pydantic**: Data validation and serialization
- **CSV Storage**: Logs are written to CSV files for analytics

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Service health check
- `GET /api/v1/logs/health` - Logging health check

### Logging Endpoints
- `POST /api/v1/logs/session-event` - Log session events
- `POST /api/v1/logs/user-message` - Log user messages
- `POST /api/v1/logs/learning-event` - Log learning events
- `POST /api/v1/logs/request-info` - Log request information
- `POST /api/v1/logs/bot-response` - Log bot responses

## Configuration

The service uses environment variables for configuration:

- `BASE_LOG_DIR`: Directory for log files (default: `/app/logs`)
- Service runs on port 8002

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker

Build and run with Docker:

```bash
docker build -t logging-service .
docker run -p 8002:8002 -v ./logs:/app/logs logging-service
```

## Integration

This service is designed to be used by the main chatbot backend. The backend makes HTTP requests to this service instead of writing logs directly to files.

## File Structure

```
logging-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration settings
│   ├── routers/
│   │   ├── __init__.py
│   │   └── log_router.py    # API routes
│   └── services/
│       ├── __init__.py
│       └── logging_service.py # Core logging logic
├── requirements.txt
├── Dockerfile
└── README.md
```
