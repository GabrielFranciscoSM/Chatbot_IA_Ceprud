# Resumen de Cambios - Sistema de Logs con MongoDB

## 📋 Cambios Realizados

### 1. Configuración (`logging-service/app/core/`)

#### `config.py`
- ✅ Agregadas variables de entorno para MongoDB:
  - `MONGODB_URL`: URL de conexión a MongoDB
  - `MONGODB_DATABASE`: Nombre de la base de datos (por defecto: `chatbot_logs`)

#### `database.py` (NUEVO)
- ✅ Clase `MongoDB` para gestionar conexión a MongoDB
- ✅ Métodos para conectar, cerrar, y obtener colecciones
- ✅ Gestión de ciclo de vida de la conexión

#### `indexes.py` (NUEVO)
- ✅ Script para crear índices en MongoDB
- ✅ Optimización de consultas por:
  - `session_id`, `user_id`, `subject`
  - `timestamp`, `query_type`, `complexity`

### 2. Modelos de Datos (`logging-service/app/models.py`)

#### Modelos MongoDB agregados:
- ✅ `ConversationMessage`: Mensaje individual (usuario o bot)
- ✅ `ConversationDocument`: Documento de conversación completa por sesión
- ✅ `SessionEventDocument`: Documento para eventos de sesión
- ✅ `InteractionAnalyticsDocument`: Documento para analytics de interacciones
- ✅ `LearningEventDocument`: Documento para eventos de aprendizaje

### 3. Servicio Principal (`logging-service/app/main.py`)

- ✅ Agregado `lifespan` context manager para gestionar conexión MongoDB
- ✅ Conexión a MongoDB al iniciar la aplicación
- ✅ Cierre de conexión al apagar la aplicación
- ✅ Actualizada versión a 2.0.0

### 4. Servicio de Logging (`logging-service/app/services/logging_service.py`)

#### Funcionalidades agregadas:
- ✅ Almacenamiento en MongoDB como sistema principal
- ✅ Fallback automático a CSV en caso de error
- ✅ `log_conversation_message()`: Agrupa mensajes por sesión automáticamente
- ✅ `log_user_message()`: Guarda analytics en colección separada
- ✅ `log_session_event()`: Registra eventos de sesión
- ✅ `log_learning_event()`: Registra eventos de aprendizaje

#### Estructura de Conversaciones:
- Las conversaciones se organizan por `session_id`
- Cada mensaje nuevo se agrega al array `messages` de la sesión
- Se mantienen timestamps de creación y actualización

### 5. Rutas API (`logging-service/app/routers/log_router.py`)

#### Nuevos endpoints de consulta:
- ✅ `GET /api/v1/conversations/{session_id}`: Obtener conversación por sesión
- ✅ `GET /api/v1/conversations/user/{user_id}`: Conversaciones de un usuario
- ✅ `GET /api/v1/conversations/subject/{subject}`: Conversaciones por asignatura
- ✅ `GET /api/v1/analytics/sessions`: Analytics de sesiones con filtros
- ✅ `GET /api/v1/analytics/interactions`: Analytics de interacciones

Todos los endpoints existentes se mantienen funcionando.

### 6. Scripts de Utilidad

#### `migrate_csv_to_mongo.py` (NUEVO)
- ✅ Migración de `conversations.csv` a MongoDB
- ✅ Migración de `chat_interactions_enhanced.csv` a MongoDB
- ✅ Migración de `learning_sessions.csv` a MongoDB
- ✅ Migración de `learning_events.csv` a MongoDB
- ✅ Agrupa mensajes por sesión automáticamente

#### `query_examples.py` (NUEVO)
- ✅ Ejemplos de consultas a MongoDB
- ✅ Búsqueda por sesión, usuario, asignatura
- ✅ Filtrado por fechas
- ✅ Agregaciones y estadísticas
- ✅ Búsqueda por palabras clave en contenido

### 7. Dependencias (`logging-service/requirements.txt`)

Agregadas:
- ✅ `motor==3.3.2` (driver asíncrono de MongoDB)
- ✅ `pymongo==4.6.1` (driver de MongoDB)

### 8. Docker Compose (`docker-compose-full.yml`)

Actualizado `logging-service`:
- ✅ Agregada variable `MONGODB_URL`
- ✅ Agregada variable `MONGODB_DATABASE`
- ✅ Agregada dependencia de `mongodb`

### 9. Documentación

#### `README.md`
- ✅ Documentación completa del nuevo sistema
- ✅ Estructura de colecciones MongoDB
- ✅ Ejemplos de documentos
- ✅ Lista completa de endpoints
- ✅ Guía de configuración
- ✅ Arquitectura del sistema

#### `USAGE.md` (NUEVO)
- ✅ Guía de uso paso a paso
- ✅ Ejemplos de consultas API
- ✅ Ejemplos de consultas directas a MongoDB
- ✅ Scripts de análisis
- ✅ Troubleshooting
- ✅ Mejores prácticas

## 🗂️ Estructura de Colecciones MongoDB

### `conversations`
Conversaciones completas organizadas por sesión:
- Documentos únicos por `session_id`
- Array `messages` con todos los mensajes de la sesión
- Timestamps de creación y última actualización

### `interaction_analytics`
Métricas de cada interacción:
- Longitud de mensajes
- Tipo de consulta
- Complejidad
- Fuentes utilizadas
- Modelo LLM usado

### `session_events`
Eventos de sesión:
- Inicio/fin de sesión
- Usuario y asignatura
- Timestamps

### `learning_events`
Eventos de aprendizaje:
- Tópicos estudiados
- Niveles de confianza
- Tipos de evento

## 🎯 Ventajas del Nuevo Sistema

1. **Estructura Jerárquica**: Las conversaciones se agrupan naturalmente por sesión
2. **Consultas Flexibles**: Búsqueda por múltiples criterios sin procesar CSV
3. **Escalabilidad**: MongoDB maneja grandes volúmenes eficientemente
4. **Analytics Avanzados**: Agregaciones complejas sin post-procesamiento
5. **Compatibilidad**: Mantiene fallback a CSV para compatibilidad
6. **NoSQL**: Schema flexible para añadir metadata adicional

## 🚀 Cómo Empezar

1. **Levantar servicios**:
   ```bash
   docker-compose -f docker-compose-full.yml up -d --build logging-service
   ```

2. **Crear índices** (recomendado):
   ```bash
   docker exec -it chatbot-logging-service python -m app.core.indexes
   ```

3. **(Opcional) Migrar datos CSV**:
   ```bash
   docker exec -it chatbot-logging-service python -m app.services.migrate_csv_to_mongo
   ```

4. **Verificar funcionamiento**:
   ```bash
   curl http://localhost:8002/health
   ```

5. **Ver ejemplos de consultas**:
   ```bash
   docker exec -it chatbot-logging-service python -m app.services.query_examples
   ```

## 📊 Acceso a los Datos

### API REST
- http://localhost:8002/api/v1/conversations/{session_id}
- http://localhost:8002/api/v1/conversations/user/{user_id}
- http://localhost:8002/api/v1/analytics/sessions
- http://localhost:8002/api/v1/analytics/interactions

### Mongo Express (UI Web)
- URL: http://localhost:8081
- Usuario: `mongoexpressuser`
- Contraseña: `mongoexpresspass`

### MongoDB CLI
```bash
docker exec -it chatbot-mongodb mongosh -u admin -p password123
use chatbot_logs
db.conversations.find().limit(5)
```

## ⚠️ Notas Importantes

- El sistema mantiene **compatibilidad hacia atrás** con CSV como fallback
- Los logs existentes en CSV pueden migrarse con el script de migración
- Se recomienda crear índices para optimizar el rendimiento
- Las conversaciones se almacenan con el `user_id` completo (consideraciones de privacidad)

## 🔄 Próximos Pasos Sugeridos

1. Implementar políticas de retención de datos
2. Agregar dashboards de visualización (Grafana/Streamlit)
3. Implementar búsqueda de texto completo
4. Agregar exportación de conversaciones en PDF/HTML
5. Implementar sistema de tags/categorización automática
