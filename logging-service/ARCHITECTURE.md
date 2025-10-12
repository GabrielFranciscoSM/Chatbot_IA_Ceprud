# 📊 Arquitectura del Sistema de Logs v2.0

## 🏗️ Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHATBOT APPLICATION                         │
│                        (FastAPI)                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP REST API
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LOGGING SERVICE v2.0                          │
│                      (Port: 8002)                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐        │
│  │  API Routes  │  │   Service    │  │   MongoDB       │        │
│  │  (FastAPI)   │→ │   Logic      │→ │   Client        │        │
│  └──────────────┘  └──────────────┘  └────────┬────────┘        │
│                                               │                 │
│                                               │ Fallback        │
│                                               ▼                 │
│                                        ┌─────────────────┐      │
│                                        │   CSV Writer    │      │
│                                        └─────────────────┘      │
└─────────────────────────────────────────┬───────────────────────┘
                                          │
                    ┌─────────────────────┴──────────────────┐
                    │                                        │
                    ▼                                        ▼
        ┌───────────────────────┐              ┌──────────────────────┐
        │   MONGODB DATABASE    │              │   CSV FILES          │
        │   (Port: 27017)       │              │   (Fallback)         │
        │                       │              │                      │
        │  ┌─────────────────┐  │              │  - conversations.csv │
        │  │ conversations   │  │              │  - analytics.csv     │
        │  ├─────────────────┤  │              │  - sessions.csv      │
        │  │ analytics       │  │              │  - events.csv        │
        │  ├─────────────────┤  │              └──────────────────────┘
        │  │ session_events  │  │
        │  ├─────────────────┤  │
        │  │ learning_events │  │
        │  └─────────────────┘  │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   MONGO EXPRESS       │
        │   Web UI              │
        │   (Port: 8081)        │
        └───────────────────────┘
```

## 📦 Colecciones MongoDB

### 1. `conversations` Collection

**Propósito**: Almacenar conversaciones completas agrupadas por sesión

**Estructura del Documento**:
```javascript
{
  "_id": ObjectId("..."),
  "session_id": "uuid-123-456-789",
  "user_id": "student@universidad.es",
  "subject": "Cálculo I",
  "messages": [
    {
      "message_type": "user",
      "content": "¿Qué es una derivada?",
      "timestamp": ISODate("2025-10-12T10:30:00Z"),
      "metadata": {}
    },
    {
      "message_type": "bot",
      "content": "Una derivada representa...",
      "timestamp": ISODate("2025-10-12T10:30:05Z"),
      "metadata": {}
    }
  ],
  "created_at": ISODate("2025-10-12T10:30:00Z"),
  "updated_at": ISODate("2025-10-12T10:35:00Z"),
  "metadata": {}
}
```

**Índices**:
- `session_id` (unique)
- `user_id`
- `subject`
- `created_at` (descending)
- `updated_at` (descending)

**Casos de Uso**:
- Recuperar historial completo de una sesión
- Analizar patrones de conversación
- Exportar conversaciones para revisión
- Búsqueda de contenido específico

---

### 2. `interaction_analytics` Collection

**Propósito**: Almacenar métricas de cada interacción usuario-chatbot

**Estructura del Documento**:
```javascript
{
  "_id": ObjectId("..."),
  "session_id": "uuid-123-456-789",
  "user_id_partial": "student@...",  // Anonimizado
  "subject": "Cálculo I",
  "message_length": 150,
  "query_type": "conceptual",
  "complexity": "medium",
  "response_length": 500,
  "source_count": 3,
  "llm_model_used": "granite-3.3-2b",
  "timestamp": ISODate("2025-10-12T10:30:00Z"),
  "metadata": {}
}
```

**Índices**:
- `session_id`
- `user_id_partial`
- `subject`
- `timestamp` (descending)
- `query_type`, `timestamp` (compound)
- `complexity`, `timestamp` (compound)

**Casos de Uso**:
- Análisis de tipos de consultas
- Métricas de complejidad
- Evaluación de rendimiento del modelo
- Identificación de patrones de uso

---

### 3. `session_events` Collection

**Propósito**: Registrar eventos del ciclo de vida de sesiones

**Estructura del Documento**:
```javascript
{
  "_id": ObjectId("..."),
  "session_id": "uuid-123-456-789",
  "user_id": "student@universidad.es",
  "subject": "Cálculo I",
  "event_type": "session_start",  // session_start, session_end, etc.
  "timestamp": ISODate("2025-10-12T10:30:00Z"),
  "metadata": {}
}
```

**Índices**:
- `session_id`
- `user_id`
- `subject`
- `timestamp` (descending)
- `event_type`, `timestamp` (compound)

**Casos de Uso**:
- Tracking de duración de sesiones
- Análisis de abandono
- Patrones de uso temporal
- Métricas de engagement

---

### 4. `learning_events` Collection

**Propósito**: Registrar eventos relacionados con el aprendizaje

**Estructura del Documento**:
```javascript
{
  "_id": ObjectId("..."),
  "session_id": "uuid-123-456-789",
  "event_type": "concept_mastery",
  "topic": "Derivadas",
  "confidence_level": "high",
  "timestamp": ISODate("2025-10-12T10:30:00Z"),
  "metadata": {}
}
```

**Índices**:
- `session_id`
- `event_type`
- `topic`
- `timestamp` (descending)

**Casos de Uso**:
- Tracking de progreso de aprendizaje
- Identificación de dificultades
- Análisis de tópicos populares
- Métricas de efectividad educativa

---

## 🔄 Flujo de Datos

### Logging de una Conversación

```
1. Usuario envía mensaje
   ↓
2. Main App procesa y genera respuesta
   ↓
3. Main App → POST /logs/conversation-message (user)
   ↓
4. Logging Service → MongoDB
   │
   ├─ Session existe? 
   │  ├─ SÍ  → Append message to messages array
   │  └─ NO  → Create new conversation document
   │
   └─ Fallback → CSV si MongoDB falla
   ↓
5. Main App → POST /logs/conversation-message (bot)
   ↓
6. Logging Service → MongoDB (append to same session)
   ↓
7. Main App → POST /logs/user-message (analytics)
   ↓
8. Logging Service → MongoDB (interaction_analytics)
```

### Consulta de una Conversación

```
1. Cliente → GET /conversations/{session_id}
   ↓
2. Logging Service consulta MongoDB
   ↓
3. MongoDB retorna documento con todos los mensajes
   ↓
4. Logging Service formatea respuesta
   ↓
5. Cliente recibe conversación completa
```

---

## 🎯 Patrones de Acceso

### Escritura (Logging)

**Alta Frecuencia**: Cada mensaje genera 2-3 inserciones
- conversation_message: 1 insert/update
- interaction_analytics: 1 insert
- session_events: 0-1 insert (según evento)

**Optimización**:
- Operaciones asíncronas
- Batch writes cuando es posible
- Índices apropiados

### Lectura (Queries)

**Consultas Comunes**:
1. Por session_id (índice único) - O(1)
2. Por user_id (índice) - O(log n)
3. Por subject (índice) - O(log n)
4. Por rango de fechas (índice timestamp) - O(log n)

**Agregaciones**:
- Estadísticas por asignatura
- Promedios de longitud de conversación
- Distribución de tipos de consulta
- Análisis temporal

---

## 🔒 Seguridad y Privacidad

### Niveles de Datos

| Colección | Identificación | Nivel de Privacidad |
|-----------|----------------|---------------------|
| conversations | user_id completo | Alto - Trazabilidad completa |
| interaction_analytics | user_id parcial | Medio - Anonimizado |
| session_events | user_id completo | Alto - Trazabilidad completa |
| learning_events | session_id | Bajo - Sin identificación directa |

### Recomendaciones

1. **Implementar RBAC** - Control de acceso basado en roles
2. **Encriptación** - Considerar encriptar contenido sensible
3. **Retención** - Política de borrado después de X tiempo
4. **Auditoría** - Log de accesos a conversaciones
5. **GDPR Compliance** - Derecho al olvido, exportación de datos

---

## 📈 Escalabilidad

### Crecimiento Estimado

**Por día** (estimación con 100 usuarios activos):
- Conversaciones: ~500 documentos
- Mensajes: ~5,000 mensajes (10 msg/conv)
- Analytics: ~2,500 registros
- Tamaño aproximado: ~50 MB/día

**Proyección anual**:
- ~180,000 conversaciones
- ~1.8M mensajes
- ~18 GB de datos

### Optimizaciones

1. **Índices Compuestos** - Para consultas frecuentes
2. **TTL Indexes** - Auto-borrado de datos antiguos
3. **Sharding** - Distribución horizontal si es necesario
4. **Read Replicas** - Para separar lectura/escritura
5. **Archivado** - Mover datos antiguos a almacenamiento frío

---

## 🛠️ Mantenimiento

### Tareas Regulares

**Diarias**:
- Verificar salud de conexión MongoDB
- Monitorear tamaño de colecciones
- Revisar logs de errores

**Semanales**:
- Analizar performance de queries
- Revisar índices utilizados
- Verificar tasa de fallback a CSV

**Mensuales**:
- Backup completo de MongoDB
- Análisis de crecimiento de datos
- Optimización de índices si es necesario
- Limpieza de datos antiguos (si aplica)

### Comandos Útiles

```bash
# Ver tamaño de colecciones
db.stats()
db.conversations.stats()

# Analizar índices
db.conversations.getIndexes()

# Monitorear operaciones
db.currentOp()

# Backup
mongodump --uri="mongodb://admin:password123@localhost:27017/chatbot_logs"

# Restore
mongorestore --uri="mongodb://admin:password123@localhost:27017/chatbot_logs" dump/
```

---

## 🎓 Recursos Adicionales

- **[README.md](README.md)** - Documentación completa
- **[USAGE.md](USAGE.md)** - Guía de uso práctica
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios
- **MongoDB Docs**: https://docs.mongodb.com/
- **Motor Docs**: https://motor.readthedocs.io/
