# Chatbot_IA_Ceprud 🤖

Un chatbot educativo avanzado basado en Inteligencia Artificial diseñado para CEPRUD (Centro de Producción de Recursos para la Universidad Digital). Utiliza arquitectura de microservicios, técnicas RAG (Retrieval-Augmented Generation) y modelos finos para responder preguntas especializadas sobre las asignaturas de la carrera de Ingeniería Informática.

## 🆕 Nueva Interfaz Frontend

Este proyecto ahora incluye una **interfaz frontend moderna** desarrollada con React TypeScript, que ofrece:

- 🎓 **Gestión Personalizada de Asignaturas**: Búsqueda y selección de asignaturas por usuario
- 🔍 **Búsqueda de Asignaturas**: Barra de búsqueda para encontrar y añadir asignaturas
- 💬 **Chat en Tiempo Real**: Experiencia de chat moderna con historial de mensajes
- 👤 **Perfiles de Usuario**: Gestión de usuarios con MongoDB
- 📱 **Diseño Responsivo**: Funciona perfectamente en desktop y móvil
- 🔄 **Gestión de Sesiones**: Historial persistente por asignatura usando localStorage
- ⚡ **Control de Límites**: Información en tiempo real sobre límites de API
- 🎨 **UI Académica**: Diseño limpio y profesional adaptado al entorno universitario

---

## 🏗️ Arquitectura del Proyecto

### Estructura Modular Profesional
```
├── 🌐 frontend/              # Frontend React TypeScript
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── SubjectSearch.tsx    # Búsqueda de asignaturas
│   │   │   └── SubjectSidebar.tsx   # Gestión de asignaturas
│   │   ├── types.ts         # Definiciones TypeScript  
│   │   ├── api.ts           # Cliente API (con subject mgmt)
│   │   └── utils.ts         # Utilidades
│   ├── Dockerfile           # Contenedor frontend
│   └── nginx.conf           # Configuración Nginx
│
app/
├── 🚀 Puntos de Entrada
│   ├── api_router.py          # Rutas API principales (refactorizado)
│   └── app.py                 # Aplicación web completa
│
├── 🔧 Core - Infraestructura Esencial
│   ├── models.py              # Modelos Pydantic para validación
│   ├── config.py              # Gestión de configuración centralizada
│   └── rate_limiter.py        # Control de velocidad y límites
│
├── 🎯 Services - Lógica de Negocio
│   ├── session_service.py     # Gestión de sesiones de usuario
│   ├── logging_service.py     # Cliente del servicio de logging
│   ├── rag_client.py          # Cliente del servicio RAG
│   ├── user_service.py        # Cliente del servicio de usuarios (MongoDB)
│   └── utils_service.py       # Utilidades comunes
│
├── 🧠 Domain - Lógica del Dominio
│   ├── query_logic.py         # Procesamiento de consultas
│   └── graph.py               # Operaciones con grafos
│
├── 🔍 RAG Service - Sistema de Recuperación (Microservicio)
│   ├── rag-service/app/
│   │   ├── populate_database.py       # Población de base vectorial
│   │   ├── guia_docente_scrapper.py   # Extracción de guías docentes
│   │   ├── embeddings.py             # Funciones de embedding
│   │   ├── rag_manager.py            # Gestión RAG principal
│   │   └── document_processor.py     # Procesamiento de documentos
│   └── data/                         # Documentos y datos
│
├── 🤖 ML - Machine Learning
│   ├── models/                # Modelos AI descargados
│   └── finetuning/           # Scripts de fine-tuning
│       ├── finetuning_qlora.py
│       └── generate_data.py
│
├── 🌐 Logging Service - Servicio de Logging (Microservicio)
│   └── logging-service/app/  # Microservicio independiente de logging
│
├── 👤 User Service - Servicio de Usuarios (Microservicio)
│   └── mongo-service/app/    # Gestión de usuarios con MongoDB
│
├── 📊 Analytics - Monitoreo
│   ├── script_graphs.py      # Visualización de datos
│   └── graphs/               # Gráficos generados
│
└── 💾 Storage - Almacenamiento
    └── checkpoints.sqlite    # Puntos de control

```

---

## 🎯 Características Avanzadas

### 🚀 **Arquitectura Refactorizada** (NUEVO)
- **Separación de responsabilidades**: Código modular y mantenible
- **Servicios de negocio**: Lógica encapsulada en servicios reutilizables  
- **Configuración centralizada**: Gestión uniforme de configuración
- **Rate limiting inteligente**: Control de velocidad por usuario
- **Logging avanzado**: Analíticas de aprendizaje detalladas

### 🔍 **Sistema RAG Mejorado**
- **Embeddings optimizados**: Recuperación de documentos más precisa
- **Base vectorial Chroma**: Almacenamiento eficiente de conocimiento
- **Multiples fuentes**: Soporte para diversas asignaturas
- **Scraping inteligente**: Extracción automática de guías docentes

### 🤖 **IA y Machine Learning**
- **Fine-tuning con QLoRA**: Personalización del modelo base
- **Modelos múltiples**: Soporte para diferentes LLMs
- **Inferencia optimizada**: Usando vLLM para mejor rendimiento
- **Métricas de calidad**: Evaluación continua de respuestas

### 📊 **Analíticas y Monitoreo**
- **Learning Analytics**: Seguimiento del progreso de aprendizaje
- **Métricas en tiempo real**: Dashboard con Prometheus + Grafana
- **Logs estructurados**: Análisis detallado de interacciones
- **Visualizaciones**: Gráficos automáticos de uso y rendimiento

### 🌐 **API REST Avanzada**
- **Validación robusta**: Modelos Pydantic para entrada/salida
- **Documentación automática**: OpenAPI/Swagger integrado
- **Control de errores**: Manejo elegante de excepciones
- **CORS configurado**: Listo para integración frontend

---

## 🧰 Requisitos

- **Python** ≥ 3.10  
- **Docker** y Docker Compose
- **CUDA** (opcional, para aceleración GPU)
- **8GB RAM** mínimo (16GB recomendado)

Las dependencias están organizadas en `requirements.txt`

---

## 📦 Instalación Rápida

### ⚙️ Setup Manual

#### 1. **Configurar Entorno**
```bash
# Copiar configuración de ejemplo
cp .env.example .env
# Editar con tu token de Hugging Face
nano .env
```

#### 2. **Descargar Modelos**
```bash
python3 download_llm.py
```

#### 3. **Frontend (Desarrollo)**
```bash
cd frontend
npm install
npm run dev  # Para desarrollo local
cd ..
```

#### 4. **Levantar Servicios Completos**
```bash
# Todos los servicios (Frontend + Backend + LLM)
docker-compose -f docker-compose-full.yml up --build
```

---

## 🌐 Acceso a los Servicios

### **Frontend Moderno**
- **URL**: `http://localhost:3000`
- **Descripción**: Interfaz React con chat en tiempo real y gestión de sesiones

### **Backend API**
- **URL**: `http://localhost:8080`
- **Documentación**: `http://localhost:8080/docs`
- **Health check**: `GET /health`

### **Servicios Internos**
- **LLM API**: `http://localhost:8000` (vLLM OpenAI compatible)
- **Embeddings**: `http://localhost:8001` (Servicio de embeddings)

---

## 🚀 Uso del Sistema

### **Interfaz Web (Recomendado)**
1. Navega a `http://localhost:3000`
2. Configura tu email UGR en el panel lateral
3. **Busca y añade asignaturas**: Usa la barra de búsqueda para encontrar asignaturas disponibles
4. Selecciona una asignatura de tu lista personalizada
5. ¡Comienza a chatear!

### **Gestión de Asignaturas** (NUEVO)
- **Buscar**: Escribe en la barra de búsqueda para filtrar asignaturas disponibles
- **Añadir**: Click en una asignatura de los resultados para añadirla a tu lista
- **Eliminar**: Hover sobre una asignatura y click en el botón "×" para eliminarla
- **Personalización**: Cada usuario tiene su propia lista de asignaturas

### **API REST**
- **Endpoint principal**: `POST /chat`
- **Rate limit status**: `GET /rate-limit-info`

#### Ejemplo de uso de la API:
```bash
curl -X POST "http://localhost:8080/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "¿Qué son las metaheurísticas?",
       "subject": "metaheuristicas",
       "email": "student@example.com",
       "mode": "rag"
     }'
```

---

## 🔬 Configuración Avanzada

### **Añadir Nueva Asignatura**
```bash
cd rag-service/app
python populate_database.py --subject "nombre_asignatura"
```

### **Fine-tuning con QLoRA**
```bash
# 1. Generar datos de entrenamiento
cd app/ml/finetuning
python generate_data.py --subject "nombre_asignatura"

# 2. Entrenar modelo
python finetuning_qlora.py \
  --base_model "ibm-granite/granite-3.3-2b-instruct" \
  --data "data/dataset.json" \
  --output_dir "../models/fine_tuned"
```

### **Población de Base Vectorial**
```bash
# Poblar base de datos inicial
podman-compose -f docker-compose-full.yml up rag-service -d
sleep 30

# Ejecutar población inicial (ejemplo)
curl -X POST "http://localhost:8082/populate" \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "nombre_asignatura",
       "documents_path": "/app/data/documents",
       "clear_existing": false
     }'
``````

---

## 📊 Monitoreo y Métricas

### **Dashboard de Analíticas**
```bash
# 1. Levantar stack de monitoreo
docker-compose -f prometheus/docker-compose-prometheus-graphana.yml up -d

# 2. Acceder a Grafana
# URL: http://localhost:3000/
# Usuario: admin / Password: admin
```

### **Configurar Grafana**
1. **DataSource**: Añadir Prometheus en `http://prometheus:9090`
2. **Dashboard**: Importar desde `prometheus/grafana.json`
3. **Visualizar**: Métricas en tiempo real del chatbot

### **Logs Estructurados**
- **Logs de aplicación**: `logs/api.log`
- **Sesiones**: `logs/learning_sessions.csv`
- **Interacciones**: `logs/chat_interactions_enhanced.csv`
- **Eventos**: `logs/learning_events.csv`
- **Conversaciones**: `logs/conversations.csv`

---

## 🧪 Testing

```bash
# Tests unitarios
pytest unitTests/

# Tests de integración  
pytest tests/integration/

# Tests end-to-end
pytest tests/e2e/

# Test específico de infraestructura
pytest tests/infrastructure/
```

---

## 🔧 Desarrollo

### **Estructura del Código**
- **Core**: Infraestructura y configuración base
- **Services**: Lógica de negocio reutilizable
- **Domain**: Reglas de negocio puras
- **RAG**: Sistema de recuperación de información
- **ML**: Componentes de machine learning

### **Principios de Arquitectura**
- ✅ **Separación de responsabilidades**
- ✅ **Inversión de dependencias**
- ✅ **Código limpio y testeable**
- ✅ **Configuración externa**
- ✅ **Logging estructurado**

### **Contribuir**
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📈 Rendimiento

- **Concurrencia**: Manejo asíncrono con FastAPI
- **Rate Limiting**: 20 requests/minuto por usuario (configurable)
- **Caching**: Embeddings y respuestas cacheadas
- **Optimización GPU**: Aceleración CUDA cuando disponible

---

## 🔒 Seguridad

- **Validación de entrada**: Sanitización automática
- **Rate limiting**: Protección contra abuso
- **Logs anonymizados**: Privacidad de usuarios
- **CORS configurado**: Acceso controlado

---

## 📚 Documentación Completa

El proyecto cuenta con documentación técnica exhaustiva organizada por audiencia y nivel de detalle:

### 🎯 **Documentación Principal**
- [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) - Visión general y contexto del proyecto
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - Arquitectura del sistema y diseño técnico
- [`docs/INSTALLATION.md`](docs/INSTALLATION.md) - Guía completa de instalación y despliegue
- [`docs/API.md`](docs/API.md) - Documentación detallada de la API REST
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - Guía para desarrolladores
- [`docs/TESTING.md`](docs/TESTING.md) - Estrategias y guías de testing
- [`docs/MONITORING.md`](docs/MONITORING.md) - Configuración de monitoreo y métricas

### 🚀 **Para Empezar Rápido**
1. **Nuevos usuarios**: Lee [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md)
2. **Instalación**: Sigue [`docs/INSTALLATION.md`](docs/INSTALLATION.md)
3. **Desarrollo**: Consulta [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
4. **API**: Revisa [`docs/API.md`](docs/API.md)

---

## 📫 Contacto

**Desarrolladores**:
- **Javier Trujillo Castro** - Desarrollo inicial y arquitectura base
- **Gabriel Sánchez Muñoz** - Visualización de métricas, vLLM y refactorización

Para dudas o sugerencias, contactar vía GitHub Issues.

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- **CEPRUD** - Por el apoyo institucional
- **Hugging Face** - Por los modelos pre-entrenados
- **Chroma** - Por la base de datos vectorial
- **FastAPI** - Por el framework web
- **vLLM** - Por la optimización de inferencia

---

*Última actualización: Septiembre 2025 - Versión 2.1 (Microservicios)*

