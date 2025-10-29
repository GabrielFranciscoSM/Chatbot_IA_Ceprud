# ⚡ Guía Rápida - Logging Service v2.0

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
