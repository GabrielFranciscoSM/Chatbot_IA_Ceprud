# Guía de Uso del Sistema de Logs con MongoDB

Esta guía explica cómo usar el nuevo sistema de logs basado en MongoDB.

## 🚀 Inicio Rápido

### 1. Levantar los servicios

```bash
# Levantar todos los servicios (incluido MongoDB y logging-service)
docker-compose -f docker-compose-full.yml up -d

# Verificar que el logging-service esté funcionando
curl http://localhost:8002/health
```

### 2. Crear índices en MongoDB (Recomendado)

Para optimizar las consultas, crear índices:

```bash
# Dentro del contenedor del logging-service
docker exec -it chatbot-logging-service python -m app.core.indexes
```

### 3. (Opcional) Migrar datos CSV existentes

Si tienes logs en CSV y quieres migrarlos a MongoDB:

```bash
# Ejecutar script de migración
docker exec -it chatbot-logging-service python -m app.services.migrate_csv_to_mongo
```

## 📊 Consultar Conversaciones

### Usando la API REST

#### 1. Obtener una conversación por session_id

```bash
curl http://localhost:8002/api/v1/conversations/{session_id}
```

Ejemplo de respuesta:
```json
{
  "_id": "67abc123...",
  "session_id": "uuid-123-456",
  "user_id": "student@universidad.es",
  "subject": "Cálculo I",
  "messages": [
    {
      "message_type": "user",
      "content": "¿Qué es una derivada?",
      "timestamp": "2025-10-12T10:30:00Z",
      "metadata": null
    },
    {
      "message_type": "bot",
      "content": "Una derivada es...",
      "timestamp": "2025-10-12T10:30:05Z",
      "metadata": null
    }
  ],
  "created_at": "2025-10-12T10:30:00Z",
  "updated_at": "2025-10-12T10:35:00Z"
}
```

#### 2. Obtener todas las conversaciones de un usuario

```bash
curl "http://localhost:8002/api/v1/conversations/user/{user_id}?skip=0&limit=10"
```

#### 3. Obtener conversaciones de una asignatura

```bash
curl "http://localhost:8002/api/v1/conversations/subject/Cálculo%20I?skip=0&limit=10"
```

#### 4. Obtener analytics de sesiones

```bash
# Todas las sesiones
curl "http://localhost:8002/api/v1/analytics/sessions"

# Filtrar por asignatura
curl "http://localhost:8002/api/v1/analytics/sessions?subject=Cálculo%20I"

# Filtrar por rango de fechas
curl "http://localhost:8002/api/v1/analytics/sessions?start_date=2025-10-01&end_date=2025-10-12"
```

#### 5. Obtener analytics de interacciones

```bash
curl "http://localhost:8002/api/v1/analytics/interactions?subject=Cálculo%20I"
```

### Usando Python

```python
import httpx
import asyncio

async def get_user_conversations(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8002/api/v1/conversations/user/{user_id}"
        )
        data = response.json()
        
        print(f"Usuario: {data['user_id']}")
        print(f"Total conversaciones: {data['count']}")
        
        for conv in data['conversations']:
            print(f"\nSesión: {conv['session_id']}")
            print(f"Asignatura: {conv['subject']}")
            print(f"Mensajes: {len(conv['messages'])}")
            print(f"Fecha: {conv['created_at']}")

# Ejecutar
asyncio.run(get_user_conversations("student@universidad.es"))
```

## 🔍 Consultas Directas a MongoDB

### Usando mongo-express (Interfaz Web)

1. Acceder a: http://localhost:8081
2. Usuario: `mongoexpressuser`
3. Contraseña: `mongoexpresspass`
4. Navegar a la base de datos `chatbot_logs`

### Usando MongoDB Compass

1. Conectar a: `mongodb://admin:password123@localhost:27017`
2. Seleccionar base de datos: `chatbot_logs`
3. Explorar colecciones:
   - `conversations`: Conversaciones completas por sesión
   - `interaction_analytics`: Métricas de interacciones
   - `session_events`: Eventos de sesión
   - `learning_events`: Eventos de aprendizaje

### Usando mongosh (CLI)

```bash
# Conectar al contenedor de MongoDB
docker exec -it chatbot-mongodb mongosh -u admin -p password123

# Usar la base de datos
use chatbot_logs

# Ver todas las colecciones
show collections

# Encontrar conversaciones recientes
db.conversations.find().sort({created_at: -1}).limit(5)

# Buscar conversaciones por asignatura
db.conversations.find({subject: "Cálculo I"})

# Buscar mensajes que contengan una palabra
db.conversations.find({
  "messages.content": {$regex: "derivada", $options: "i"}
})

# Agregar estadísticas por asignatura
db.conversations.aggregate([
  {
    $group: {
      _id: "$subject",
      total_conversaciones: {$sum: 1},
      total_mensajes: {$sum: {$size: "$messages"}},
      promedio_mensajes: {$avg: {$size: "$messages"}}
    }
  }
])

# Ver tipos de consultas más comunes
db.interaction_analytics.aggregate([
  {
    $group: {
      _id: "$query_type",
      count: {$sum: 1}
    }
  },
  {$sort: {count: -1}}
])
```

## 📈 Ejemplos de Análisis

### Ejemplo 1: Ver scripts de consulta

```bash
# Ejecutar script con ejemplos de consultas
docker exec -it chatbot-logging-service python -m app.services.query_examples
```

Este script mostrará:
- Conversaciones por sesión
- Conversaciones por usuario
- Conversaciones por asignatura
- Conversaciones recientes (últimos 7 días)
- Estadísticas agregadas
- Búsqueda por palabras clave
- Analytics de tipos de consulta

### Ejemplo 2: Análisis de uso por asignatura

```python
# En mongo shell
db.conversations.aggregate([
  {
    $group: {
      _id: "$subject",
      num_estudiantes: {$addToSet: "$user_id"},
      total_sesiones: {$sum: 1},
      total_mensajes: {$sum: {$size: "$messages"}}
    }
  },
  {
    $project: {
      _id: 1,
      num_estudiantes: {$size: "$num_estudiantes"},
      total_sesiones: 1,
      total_mensajes: 1,
      promedio_mensajes_sesion: {
        $divide: ["$total_mensajes", "$total_sesiones"]
      }
    }
  },
  {$sort: {total_sesiones: -1}}
])
```

### Ejemplo 3: Análisis de complejidad de consultas

```python
db.interaction_analytics.aggregate([
  {
    $group: {
      _id: {
        subject: "$subject",
        complexity: "$complexity"
      },
      count: {$sum: 1},
      avg_response_length: {$avg: "$response_length"}
    }
  },
  {$sort: {"_id.subject": 1, "_id.complexity": 1}}
])
```

## 🔧 Troubleshooting

### El servicio no se conecta a MongoDB

```bash
# Verificar que MongoDB esté corriendo
docker ps | grep mongodb

# Ver logs del logging-service
docker logs chatbot-logging-service

# Verificar variables de entorno
docker exec chatbot-logging-service env | grep MONGODB
```

### Los logs siguen yendo a CSV

El sistema tiene un fallback automático a CSV si MongoDB falla. Verificar:

```bash
# Ver logs del servicio
docker logs chatbot-logging-service --tail 100
```

### Limpiar colecciones

```bash
# Conectar a MongoDB
docker exec -it chatbot-mongodb mongosh -u admin -p password123

use chatbot_logs

# Eliminar todas las conversaciones
db.conversations.deleteMany({})

# Eliminar analytics
db.interaction_analytics.deleteMany({})
```

## 🎯 Mejores Prácticas

1. **Crear índices**: Siempre ejecutar el script de índices después de levantar el servicio
2. **Monitorear tamaño**: Las conversaciones pueden crecer, monitorear el espacio en disco
3. **Backups**: Hacer backups regulares de MongoDB
4. **Retención de datos**: Definir políticas de retención según normativas

## 📝 Notas

- Las conversaciones se agrupan automáticamente por `session_id`
- Cada mensaje nuevo en una sesión se agrega al array `messages`
- El sistema mantiene tanto `created_at` (inicio de conversación) como `updated_at` (último mensaje)
- Los timestamps se guardan como objetos `datetime` de MongoDB para facilitar consultas
