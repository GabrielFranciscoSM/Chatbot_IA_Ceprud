# ⚡ Guía Rápida - Logging Service v2.0

## 🚀 Comandos Rápidos

### Iniciar el Servicio
```bash
# Reconstruir e iniciar (recomendado)
./rebuild-logging-service.sh

# O manualmente
docker-compose -f docker-compose-full.yml up -d --build logging-service
```

### Verificar Estado
```bash
# Health check
curl http://localhost:8002/health

# Ver logs
docker logs chatbot-logging-service -f
```

### Configuración Inicial
```bash
# 1. Crear índices (IMPORTANTE - hacer una vez)
docker exec chatbot-logging-service python -m app.core.indexes

# 2. Migrar CSV existente (opcional)
docker exec chatbot-logging-service python -m app.services.migrate_csv_to_mongo

# 3. Ejecutar test
docker exec chatbot-logging-service python test_logging.py
```

---

## 🔍 Consultas Rápidas

### Obtener una Conversación
```bash
curl http://localhost:8002/api/v1/conversations/SESSION_ID
```

### Conversaciones de un Usuario
```bash
curl "http://localhost:8002/api/v1/conversations/user/EMAIL"
```

### Conversaciones de una Asignatura
```bash
curl "http://localhost:8002/api/v1/conversations/subject/ASIGNATURA"
```

### Analytics
```bash
# Por asignatura
curl "http://localhost:8002/api/v1/analytics/interactions?subject=ASIGNATURA"

# Por rango de fechas
curl "http://localhost:8002/api/v1/analytics/sessions?start_date=2025-10-01&end_date=2025-10-12"
```

---

## 🗄️ Acceso Directo a MongoDB

### Mongo Express (Web UI)
```
URL: http://localhost:8081
Usuario: mongoexpressuser
Contraseña: mongoexpresspass
Base de datos: chatbot_logs
```

### mongosh (CLI)
```bash
# Conectar
docker exec -it chatbot-mongodb mongosh -u admin -p password123

# Usar base de datos
use chatbot_logs

# Ver colecciones
show collections

# Últimas 5 conversaciones
db.conversations.find().sort({created_at: -1}).limit(5).pretty()

# Buscar por usuario
db.conversations.find({user_id: "EMAIL"}).pretty()

# Buscar palabra en mensajes
db.conversations.find({
  "messages.content": {$regex: "PALABRA", $options: "i"}
}).pretty()

# Estadísticas por asignatura
db.conversations.aggregate([
  {$group: {
    _id: "$subject",
    total: {$sum: 1},
    avg_msgs: {$avg: {$size: "$messages"}}
  }}
])
```

---

## 📊 Ejemplos de Análisis

### Ver Ejemplos Completos
```bash
docker exec chatbot-logging-service python -m app.services.query_examples
```

### Consultas Útiles en MongoDB

#### Conversaciones por asignatura
```javascript
db.conversations.aggregate([
  {$group: {_id: "$subject", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

#### Usuarios más activos
```javascript
db.conversations.aggregate([
  {$group: {_id: "$user_id", total_sessions: {$sum: 1}}},
  {$sort: {total_sessions: -1}},
  {$limit: 10}
])
```

#### Distribución de tipos de consulta
```javascript
db.interaction_analytics.aggregate([
  {$group: {_id: "$query_type", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

#### Promedio de mensajes por conversación
```javascript
db.conversations.aggregate([
  {$project: {num_messages: {$size: "$messages"}}},
  {$group: {_id: null, avg: {$avg: "$num_messages"}}}
])
```

---

## 🐛 Troubleshooting

### El servicio no arranca
```bash
# Ver logs detallados
docker logs chatbot-logging-service --tail 100

# Verificar MongoDB
docker ps | grep mongodb

# Reiniciar servicios
docker-compose -f docker-compose-full.yml restart logging-service
```

### MongoDB no conecta
```bash
# Verificar variables de entorno
docker exec chatbot-logging-service env | grep MONGODB

# Probar conexión manual
docker exec -it chatbot-mongodb mongosh -u admin -p password123
```

### Los logs van a CSV en vez de MongoDB
```bash
# Verificar logs del servicio (buscar errores de MongoDB)
docker logs chatbot-logging-service | grep -i mongo

# El sistema tiene fallback automático a CSV si MongoDB falla
```

---

## 📁 Estructura de Archivos

```
logging-service/
├── README.md              # Documentación completa
├── USAGE.md               # Guía de uso detallada
├── ARCHITECTURE.md        # Arquitectura del sistema
├── CHANGELOG.md           # Cambios realizados
├── QUICK_START.md         # Esta guía
├── test_logging.py        # Test de verificación
├── requirements.txt       # Dependencias Python
├── app/
│   ├── main.py           # Aplicación principal
│   ├── models.py         # Modelos de datos
│   ├── core/
│   │   ├── config.py     # Configuración
│   │   ├── database.py   # Gestión MongoDB
│   │   └── indexes.py    # Creación de índices
│   ├── services/
│   │   ├── logging_service.py        # Lógica de logging
│   │   ├── migrate_csv_to_mongo.py   # Migración CSV→MongoDB
│   │   └── query_examples.py         # Ejemplos de consultas
│   └── routers/
│       └── log_router.py # Endpoints API
```

---

## 🎯 Casos de Uso Comunes

### 1. Ver conversación de un estudiante
```bash
# API
curl http://localhost:8002/api/v1/conversations/user/estudiante@universidad.es

# MongoDB
db.conversations.find({user_id: "estudiante@universidad.es"}).pretty()
```

### 2. Analizar una asignatura
```bash
# API
curl "http://localhost:8002/api/v1/conversations/subject/Cálculo%20I"

# MongoDB
db.conversations.find({subject: "Cálculo I"}).count()
```

### 3. Buscar tema específico
```bash
# MongoDB
db.conversations.find({
  "messages.content": {$regex: "derivada", $options: "i"}
})
```

### 4. Exportar conversación
```bash
curl http://localhost:8002/api/v1/conversations/SESSION_ID > conversation.json
```

---

## 📞 Más Información

- **Documentación completa**: `logging-service/README.md`
- **Guía de uso**: `logging-service/USAGE.md`
- **Arquitectura**: `logging-service/ARCHITECTURE.md`
- **Resumen de actualización**: `LOGGING_UPDATE.md`

---

## ✅ Checklist Post-Instalación

- [ ] Servicio iniciado correctamente
- [ ] Health check responde OK
- [ ] Índices creados en MongoDB
- [ ] Test de verificación ejecutado exitosamente
- [ ] (Opcional) Datos CSV migrados
- [ ] Mongo Express accesible
- [ ] Documentación revisada

---

**¿Problemas?** Ver sección de troubleshooting o revisar logs detallados.
**¿Sugerencias?** El sistema es extensible, consulta la documentación para agregar nuevas funcionalidades.
