# Chatbot_IA_Ceprud 🤖

Un chatbot educativo avanzado basado en Inteligencia Artificial diseñado para CEPRUD (Centro de Producción de Recursos para la Universidad Digital). Utiliza arquitectura de microservicios, técnicas RAG (Retrieval-Augmented Generation) y modelos finos para responder preguntas especializadas sobre las asignaturas de la carrera de Ingeniería Informática.

## 🆕 Nueva Interfaz Frontend

Este proyecto ahora incluye una **interfaz frontend moderna** desarrollada con React TypeScript, que ofrece:

- 🎓 **Selección de Asignaturas**: Interfaz intuitiva para cambiar entre diferentes materias
- 💬 **Chat en Tiempo Real**: Experiencia de chat moderna con historial de mensajes
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
│   │   ├── types.ts         # Definiciones TypeScript  
│   │   ├── api.ts           # Cliente API
│   │   └── utils.ts         # Utilidades
│   ├── Dockerfile           # Contenedor frontend
│   └── nginx.conf           # Configuración Nginx
│
app/
├── 🚀 Puntos de Entrada
│   ├── api_router.py          # Rutas API principales (refactorizado)
│   ├── app.py                 # Aplicación web completa
│   └── api.py                 # API pura para microservicios
│
├── 🔧 Core - Infraestructura Esencial
│   ├── models.py              # Modelos Pydantic para validación
│   ├── config.py              # Gestión de configuración centralizada
│   └── rate_limiter.py        # Control de velocidad y límites
│
├── 🎯 Services - Lógica de Negocio
│   ├── session_service.py     # Gestión de sesiones de usuario
│   ├── analytics_service.py   # Analíticas de aprendizaje avanzadas
│   └── utils_service.py       # Utilidades comunes
│
├── 🧠 Domain - Lógica del Dominio
│   ├── query_logic.py         # Procesamiento de consultas
│   ├── graph.py               # Operaciones con grafos
│   └── test_conversation.py   # Manejo de conversaciones
│
├── 🔍 RAG - Sistema de Recuperación
│   ├── get_embedding_function.py  # Funciones de embedding
│   ├── populate_database.py       # Población de base vectorial
│   ├── add_subject.py             # Gestión de asignaturas
│   ├── guia_docente_scrapper.py   # Extracción de guías docentes
│   ├── data/                      # Documentos y datos
│   └── chroma/                    # Base de datos vectorial
│
├── 🤖 ML - Machine Learning
│   ├── models/                # Modelos AI descargados
│   └── finetuning/           # Scripts de fine-tuning
│       ├── finetuning_qlora.py
│       └── generate_data.py
│
├── 🌐 Web - Interfaz de Usuario
│   ├── static/               # CSS, JS, imágenes
│   └── templates/            # Plantillas HTML
│
├── 📊 Analytics - Monitoreo
│   ├── script_graphs.py      # Visualización de datos
│   └── graphs/               # Gráficos generados
│
└── 💾 Storage - Almacenamiento
    ├── logs/                 # Logs de aplicación
    └── checkpoints.sqlite*   # Puntos de control

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

Las dependencias están organizadas en `config/requirements.txt`

---

## 📦 Instalación Rápida

### 🚀 Opción 1: Setup Automático (Recomendado)
```bash
# Clonar el repositorio
git clone https://github.com/javitrucas/Chatbot_IA_Ceprud.git
cd Chatbot_IA_Ceprud

# Ejecutar setup automático
./setup.sh
```

### ⚙️ Opción 2: Setup Manual

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

# Solo backend y LLM (sin frontend)
docker-compose -f docker-compose-vllm.yml up --build
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
3. Selecciona una asignatura
4. ¡Comienza a chatear!

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
cd app/rag
python add_subject.py
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
cd app/rag
python populate_database.py --subject "nombre_asignatura"
```

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
- **Sesiones**: `app/storage/logs/learning_sessions.csv`
- **Interacciones**: `app/storage/logs/chat_interactions_enhanced.csv`
- **Eventos**: `app/storage/logs/learning_events.csv`

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

## 📚 Documentación Adicional

- [`REFACTOR_STEP1_COMPLETE.md`](REFACTOR_STEP1_COMPLETE.md) - Extracción de modelos Pydantic
- [`REFACTOR_STEP2_COMPLETE.md`](REFACTOR_STEP2_COMPLETE.md) - Rate limiting y configuración
- [`REFACTOR_STEP3_COMPLETE.md`](REFACTOR_STEP3_COMPLETE.md) - Capa de servicios
- [`STRUCTURE_IMPROVEMENT_COMPLETE.md`](STRUCTURE_IMPROVEMENT_COMPLETE.md) - Reestructuración completa

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

*Última actualización: Septiembre 2025 - Versión 2.0 (Refactorizada)*

