# Chatbot IA CEPRUD - GitHub Pages 📖# Chatbot IA CEPRUD - GitHub Pages



Este es el branch de **GitHub Pages** para el proyecto Chatbot IA CEPRUD. Contiene la documentación y sitio web del proyecto construido con Jekyll.Este es el branch de **GitHub Pages** para el proyecto Chatbot IA CEPRUD. Contiene la documentación y sitio web del proyecto construido con Jekyll.



> **🔗 Para el código fuente del proyecto**, visita el [branch development](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/tree/development)## 🌐 Sitio Web



## 🌐 Sitio Web**URL**: [https://gabrielfranciscosm.github.io/Chatbot_IA_Ceprud/](https://gabrielfranciscosm.github.io/Chatbot_IA_Ceprud/)



**URL**: [https://gabrielfranciscosm.github.io/Chatbot_IA_Ceprud/](https://gabrielfranciscosm.github.io/Chatbot_IA_Ceprud/)## 📚 Contenido



## 📚 Contenido del SitioEste sitio incluye:

- **Landing page**: Información general del proyecto

Este sitio web incluye:- **Guía de usuario**: Cómo usar el chatbot

- **Documentación técnica completa**: 

- ✨ **Landing Page**: Información general, características y inicio rápido  - Arquitectura del sistema

- 👤 **Guía de Usuario**: Tutorial completo para usar el chatbot  - Guía de instalación

- 📖 **Documentación Técnica Completa**:   - API Reference

  - 🎯 Visión general del proyecto  - Integración LTI con Moodle

  - 🏗️ Arquitectura del sistema  - Guía de desarrollo

  - 📦 Guía de instalación  - Testing y monitoreo

  - 🔌 API Reference

  - 🎓 Integración LTI con Moodle## � Tema Jekyll

  - 💻 Guía de desarrollo

  - 🧪 Testing y calidadUtiliza el tema **[Just the Docs](https://just-the-docs.github.io/just-the-docs/)** - un tema Jekyll moderno y profesional optimizado para documentación técnica.

  - 📊 Monitoreo y métricas

### Características del Tema

## 🎨 Tema Jekyll- � **Búsqueda potente** integrada

- 📱 **Diseño responsivo** y accesible

El sitio utiliza el tema **[Just the Docs](https://just-the-docs.github.io/just-the-docs/)**, un tema moderno y profesional optimizado para documentación técnica.- 🎨 **Esquema de colores oscuro** por defecto

- 📖 **Tabla de contenidos** automática

### Características del Tema- 💻 **Syntax highlighting** para código

- 🔗 **Navegación jerárquica** clara

- 🔍 **Búsqueda potente** con índice completo del sitio

- 📱 **Diseño responsivo** que funciona en móviles y desktop## 🚀 Desarrollo Local

- 🎨 **Esquema de colores oscuro** (configurable)

- 📖 **Tabla de contenidos** automática en cada páginaPara ejecutar el sitio localmente:

- 💻 **Syntax highlighting** para bloques de código

- 🗂️ **Navegación jerárquica** clara y organizada```bash

- ⚡ **Rendimiento optimizado** con carga rápida# 1. Instalar dependencias

bundle install

## 🚀 Desarrollo Local

# 2. Servir el sitio

Si quieres ejecutar el sitio localmente para ver los cambios antes de publicar:bundle exec jekyll serve



### Requisitos Previos# 3. Visitar

# http://localhost:4000/Chatbot_IA_Ceprud/

- Ruby >= 2.7```

- Bundler├── 🌐 frontend/              # Frontend React TypeScript

- Jekyll│   ├── src/

│   │   ├── components/       # Componentes React

### Pasos│   │   ├── types.ts         # Definiciones TypeScript  

│   │   ├── api.ts           # Cliente API

```bash│   │   └── utils.ts         # Utilidades

# 1. Instalar dependencias Ruby│   ├── Dockerfile           # Contenedor frontend

bundle install│   └── nginx.conf           # Configuración Nginx

│

# 2. Servir el sitio localmenteapp/

bundle exec jekyll serve├── 🚀 Puntos de Entrada

│   ├── api_router.py          # Rutas API principales (refactorizado)

# 3. Visitar en tu navegador│   ├── app.py                 # Aplicación web completa

# http://localhost:4000/Chatbot_IA_Ceprud/│   └── api.py                 # API pura para microservicios

```│

├── 🔧 Core - Infraestructura Esencial

El sitio se recargará automáticamente cuando hagas cambios en los archivos.│   ├── models.py              # Modelos Pydantic para validación

│   ├── config.py              # Gestión de configuración centralizada

## 📁 Estructura del Sitio│   └── rate_limiter.py        # Control de velocidad y límites

│

```├── 🎯 Services - Lógica de Negocio

.│   ├── session_service.py     # Gestión de sesiones de usuario

├── _config.yml           # Configuración de Jekyll│   ├── analytics_service.py   # Analíticas de aprendizaje avanzadas

├── Gemfile              # Dependencias Ruby/Jekyll│   └── utils_service.py       # Utilidades comunes

├── index.md             # Página principal (landing page)│

├── user-guide.md        # Guía completa de usuario├── 🧠 Domain - Lógica del Dominio

├── README.md            # Este archivo│   ├── query_logic.py         # Procesamiento de consultas

└── docs/                # Documentación técnica│   ├── graph.py               # Operaciones con grafos

    ├── index.md                        # Índice de documentación│   └── test_conversation.py   # Manejo de conversaciones

    ├── PROJECT_OVERVIEW.md             # Visión general│

    ├── ARCHITECTURE.md                 # Arquitectura├── 🔍 RAG - Sistema de Recuperación

    ├── INSTALLATION.md                 # Instalación│   ├── get_embedding_function.py  # Funciones de embedding

    ├── API.md                          # API Reference│   ├── populate_database.py       # Población de base vectorial

    ├── LTI_INTEGRATION.md              # Integración LTI/Moodle│   ├── add_subject.py             # Gestión de asignaturas

    ├── DEVELOPMENT.md                  # Guía de desarrollo│   ├── guia_docente_scrapper.py   # Extracción de guías docentes

    ├── TESTING.md                      # Testing│   ├── data/                      # Documentos y datos

    ├── MONITORING.md                   # Monitoreo│   └── chroma/                    # Base de datos vectorial

    ├── AUTHENTICATION_IMPLEMENTATION.md # Autenticación│

    ├── MONGODB_INTEGRATION.md          # MongoDB├── 🤖 ML - Machine Learning

    ├── AUTH_QUICK_REFERENCE.md         # Referencia rápida│   ├── models/                # Modelos AI descargados

    └── diagrams/                       # Diagramas de arquitectura│   └── finetuning/           # Scripts de fine-tuning

```│       ├── finetuning_qlora.py

│       └── generate_data.py

## 🔄 Actualizar Documentación│

├── 🌐 Web - Interfaz de Usuario

Para sincronizar la documentación desde el branch `development`:│   ├── static/               # CSS, JS, imágenes

│   └── templates/            # Plantillas HTML

```bash│

# 1. Asegurarse de estar en main├── 📊 Analytics - Monitoreo

git checkout main│   ├── script_graphs.py      # Visualización de datos

│   └── graphs/               # Gráficos generados

# 2. Copiar documentación desde development│

git checkout development -- docs/└── 💾 Storage - Almacenamiento

    ├── logs/                 # Logs de aplicación

# 3. Commit y push (GitHub Actions construirá el sitio automáticamente)    └── checkpoints.sqlite*   # Puntos de control

git add docs/

git commit -m "docs: Update from development branch"```

git push origin main

```---



{: .note }## 🎯 Características Avanzadas

> La documentación en `docs/` ya tiene el front matter YAML necesario para Jekyll.

### 🚀 **Arquitectura Refactorizada** (NUEVO)

## 📝 Añadir Nueva Página- **Separación de responsabilidades**: Código modular y mantenible

- **Servicios de negocio**: Lógica encapsulada en servicios reutilizables  

Para añadir un nuevo documento al sitio:- **Configuración centralizada**: Gestión uniforme de configuración

- **Rate limiting inteligente**: Control de velocidad por usuario

1. **Crear archivo** `.md` en la ubicación apropiada- **Logging avanzado**: Analíticas de aprendizaje detalladas



2. **Añadir front matter** YAML al inicio del archivo:### 🔍 **Sistema RAG Mejorado**

- **Embeddings optimizados**: Recuperación de documentos más precisa

   ```yaml- **Base vectorial Chroma**: Almacenamiento eficiente de conocimiento

   ---- **Multiples fuentes**: Soporte para diversas asignaturas

   layout: default- **Scraping inteligente**: Extracción automática de guías docentes

   title: Título de la Página

   nav_order: X### 🤖 **IA y Machine Learning**

   parent: Documentación  # Si es una subpágina- **Fine-tuning con QLoRA**: Personalización del modelo base

   permalink: /ruta/de/la/pagina- **Modelos múltiples**: Soporte para diferentes LLMs

   ---- **Inferencia optimizada**: Usando vLLM para mejor rendimiento

   ```- **Métricas de calidad**: Evaluación continua de respuestas



3. **Escribir contenido** en Markdown### 📊 **Analíticas y Monitoreo**

- **Learning Analytics**: Seguimiento del progreso de aprendizaje

4. **Commit y push** - GitHub Actions publicará automáticamente- **Métricas en tiempo real**: Dashboard con Prometheus + Grafana

- **Logs estructurados**: Análisis detallado de interacciones

### Ejemplo de Front Matter- **Visualizaciones**: Gráficos automáticos de uso y rendimiento



```yaml### 🌐 **API REST Avanzada**

---- **Validación robusta**: Modelos Pydantic para entrada/salida

layout: default- **Documentación automática**: OpenAPI/Swagger integrado

title: Mi Nueva Guía- **Control de errores**: Manejo elegante de excepciones

nav_order: 12- **CORS configurado**: Listo para integración frontend

parent: Documentación

permalink: /docs/mi-nueva-guia---

---

## 🧰 Requisitos

# Mi Nueva Guía

{: .no_toc }- **Python** ≥ 3.10  

- **Docker** y Docker Compose

## Tabla de Contenidos- **CUDA** (opcional, para aceleración GPU)

{: .no_toc .text-delta }- **8GB RAM** mínimo (16GB recomendado)



1. TOCLas dependencias están organizadas en `config/requirements.txt`

{:toc}

---

---

## 📦 Instalación Rápida

## Sección 1

### 🚀 Opción 1: Setup Automático (Recomendado)

Contenido aquí...```bash

```# Clonar el repositorio

git clone https://github.com/javitrucas/Chatbot_IA_Ceprud.git

## ⚙️ Configuracióncd Chatbot_IA_Ceprud



### Modificar Configuración del Sitio# Ejecutar setup automático

./setup.sh

Edita `_config.yml` para personalizar:```



- **Información básica**: título, descripción, URL### ⚙️ Opción 2: Setup Manual

- **Tema**: colores, fuentes, layout

- **Búsqueda**: configuración de búsqueda#### 1. **Configurar Entorno**

- **Navegación**: enlaces auxiliares, footer```bash

- **Plugins**: habilitar/deshabilitar funcionalidades# Copiar configuración de ejemplo

cp .env.example .env

### Cambiar Esquema de Colores# Editar con tu token de Hugging Face

nano .env

En `_config.yml`:```



```yaml#### 2. **Descargar Modelos**

color_scheme: dark  # Opciones: light, dark, o personalizado```bash

```python3 download_llm.py

```

### Personalizar Callouts

#### 3. **Frontend (Desarrollo)**

El tema soporta callouts (cajas destacadas):```bash

cd frontend

```markdownnpm install

{: .note }npm run dev  # Para desarrollo local

> Esto es una nota importantecd ..

```

{: .warning }

> Esto es una advertencia#### 4. **Levantar Servicios Completos**

```bash

{: .important }# Todos los servicios (Frontend + Backend + LLM)

> Esto es muy importantedocker-compose -f docker-compose-full.yml up --build

```

# Solo backend y LLM (sin frontend)

## 🚀 Desplieguedocker-compose -f docker-compose-vllm.yml up --build

```

El sitio se despliega automáticamente mediante **GitHub Actions** cuando haces push a `main`.

---

### Workflow de Deployment

## 🌐 Acceso a los Servicios

1. Push a `main`

2. GitHub Actions ejecuta Jekyll build### **Frontend Moderno**

3. El sitio generado se publica en GitHub Pages- **URL**: `http://localhost:3000`

4. Disponible en: `https://gabrielfranciscosm.github.io/Chatbot_IA_Ceprud/`- **Descripción**: Interfaz React con chat en tiempo real y gestión de sesiones



### Verificar Deployment### **Backend API**

- **URL**: `http://localhost:8080`

- Ve a `Actions` en GitHub para ver el estado del build- **Documentación**: `http://localhost:8080/docs`

- Los builds típicamente tardan 1-2 minutos- **Health check**: `GET /health`



## 🎯 Guía de Estilo### **Servicios Internos**

- **LLM API**: `http://localhost:8000` (vLLM OpenAI compatible)

### Markdown- **Embeddings**: `http://localhost:8001` (Servicio de embeddings)



- Usa encabezados jerárquicos (`#`, `##`, `###`)---

- Añade tabla de contenidos a páginas largas

- Usa bloques de código con syntax highlighting## 🚀 Uso del Sistema

- Añade callouts para información importante

- Usa listas para mejorar legibilidad### **Interfaz Web (Recomendado)**

1. Navega a `http://localhost:3000`

### Front Matter2. Configura tu email UGR en el panel lateral

3. Selecciona una asignatura

Siempre incluye:4. ¡Comienza a chatear!

- `title`: Título visible en navegación

- `nav_order`: Orden en el menú (número)### **API REST**

- `parent`: Para páginas anidadas- **Endpoint principal**: `POST /chat`

- `permalink`: URL limpia- **Rate limit status**: `GET /rate-limit-info`



## 📖 Referencias#### Ejemplo de uso de la API:

```bash

- [Documentación de Jekyll](https://jekyllrb.com/docs/)curl -X POST "http://localhost:8080/chat" \

- [Guía de Just the Docs](https://just-the-docs.github.io/just-the-docs/)     -H "Content-Type: application/json" \

- [GitHub Pages Docs](https://docs.github.com/en/pages)     -d '{

- [Markdown Guide](https://www.markdownguide.org/)       "message": "¿Qué son las metaheurísticas?",

       "subject": "metaheuristicas",

## 🔗 Enlaces Útiles       "email": "student@example.com",

       "mode": "rag"

- **Código fuente**: [Branch development](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/tree/development)     }'

- **Issues**: [GitHub Issues](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/issues)```

- **Discussions**: [GitHub Discussions](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/discussions)

- **Sitio web**: [GitHub Pages](https://gabrielfranciscosm.github.io/Chatbot_IA_Ceprud/)---



## 📄 Licencia## 🔬 Configuración Avanzada



MIT License - Ver LICENSE en el repositorio principal### **Añadir Nueva Asignatura**

```bash

---cd app/rag

python add_subject.py

**Última actualización**: Octubre 2025 - Versión 3.0 (con integración LTI 1.3)```


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

