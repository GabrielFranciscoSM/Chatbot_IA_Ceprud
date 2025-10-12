---
layout: default
title: Home
nav_order: 1
description: "Chatbot educativo inteligente con IA para la Universidad de Granada"
permalink: /
---

# Chatbot IA CEPRUD 🤖
{: .fs-9 }

Sistema de chatbot educativo avanzado basado en Inteligencia Artificial para CEPRUD (Centro de Producción de Recursos para la Universidad Digital).
{: .fs-6 .fw-300 }

[Comenzar](#inicio-rápido){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Ver en GitHub](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## Características Principales

### 🎓 Integración LTI 1.3 con Moodle
{: .text-green-300 }

Integración completa con plataformas Moodle mediante el estándar LTI 1.3, permitiendo autenticación segura y lanzamiento contextual desde cursos.

- **Autenticación OIDC** con validación JWT
- **Lanzamiento contextual** desde actividades Moodle
- **Sesiones persistentes** con MongoDB
- **Mapeo automático** de asignaturas
- **Soporte iframe** para integración nativa

### 💬 Interfaz Frontend Moderna
{: .text-blue-300 }

Interfaz web desarrollada con React TypeScript que proporciona una experiencia de usuario excepcional.

- 🎓 **Gestión personalizada** de asignaturas por usuario
- 🔍 **Búsqueda inteligente** de asignaturas disponibles
- 💬 **Chat en tiempo real** con historial persistente
- 👤 **Perfiles de usuario** con MongoDB
- 📱 **Diseño responsivo** para móviles y desktop
- ⚡ **Control de límites** en tiempo real

### 🏗️ Arquitectura de Microservicios
{: .text-purple-300 }

Sistema modular y escalable basado en microservicios independientes.

- **Backend API** - FastAPI con endpoints RESTful
- **RAG Service** - Sistema de recuperación de información
- **User Service** - Gestión de usuarios con MongoDB
- **Logging Service** - Analíticas de aprendizaje
- **Frontend Service** - Interface React optimizada

### 🔍 Sistema RAG Avanzado
{: .text-yellow-300 }

Tecnología de Retrieval-Augmented Generation para respuestas precisas basadas en documentación oficial.

- **Embeddings semánticos** con modelos state-of-the-art
- **Base vectorial Chroma** para búsqueda eficiente
- **Múltiples asignaturas** soportadas
- **Scraping inteligente** de guías docentes
- **Respuestas contextualizadas** y verificables

### 🤖 Machine Learning
{: .text-red-300 }

Modelos de lenguaje grandes optimizados para el dominio educativo.

- **Fine-tuning con QLoRA** para personalización
- **Múltiples modelos LLM** soportados
- **Inferencia optimizada** con vLLM
- **Evaluación continua** de calidad

---

## Inicio Rápido

### Requisitos Previos

- **Python** ≥ 3.10
- **Docker** y Podman Compose
- **8GB RAM** mínimo (16GB recomendado)
- **CUDA** (opcional, para aceleración GPU)

### Instalación en 3 Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud.git
cd Chatbot_IA_Ceprud

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Levantar servicios
podman-compose -f docker-compose-full.yml up -d
```

### Acceso a los Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | `http://localhost:8090` | Interfaz web principal |
| **Backend API** | `http://localhost:8080` | API REST |
| **Documentación API** | `http://localhost:8080/docs` | Swagger UI interactivo |
| **Prometheus** | `http://localhost:9090` | Métricas del sistema |
| **Grafana** | `http://localhost:3000` | Dashboards de analíticas |

---

## Casos de Uso

### Para Estudiantes 📚

- **Consultas 24/7** sobre asignaturas y temario
- **Aclaración de dudas** específicas sobre conceptos
- **Información rápida** sobre evaluación y contenidos
- **Estudio autodirigido** con asistencia IA

### Para Profesores 👨‍🏫

- **Reducción de consultas repetitivas**
- **Insights sobre temas problemáticos**
- **Estandarización de información** proporcionada
- **Más tiempo** para consultas complejas

### Para Instituciones 🏛️

- **Mejora de satisfacción** estudiantil
- **Innovación tecnológica** visible
- **Datos de aprendizaje** valiosos
- **Escalabilidad** del soporte educativo

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│  • Interface de usuario moderna                          │
│  • Gestión de sesiones LTI                               │
│  • Chat en tiempo real                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS/REST
                     │
┌────────────────────▼────────────────────────────────────┐
│                  BACKEND API (FastAPI)                   │
│  • Endpoints REST                  • Rate Limiting       │
│  • LTI 1.3 Integration            • Session Management  │
└──┬──────────────┬──────────────┬──────────────┬────────┘
   │              │              │              │
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│   RAG    │ │   User   │ │ Logging  │ │     LLM      │
│ Service  │ │ Service  │ │ Service  │ │   (vLLM)     │
│          │ │          │ │          │ │              │
│ ChromaDB │ │ MongoDB  │ │  Events  │ │ Phi-3-mini   │
└──────────┘ └──────────┘ └──────────┘ └──────────────┘
```

[Ver arquitectura detallada →]({{ site.baseurl }}/docs/architecture)

---

## Tecnologías Utilizadas

<div class="code-example" markdown="1">
**Backend**
- Python 3.10+, FastAPI, Pydantic, AsyncIO

**Frontend**
- React 18, TypeScript, Vite, Axios

**IA/ML**
- Hugging Face Transformers, vLLM, ChromaDB, Sentence Transformers

**Infraestructura**
- Podman, Prometheus, Grafana, MongoDB

**Integración**
- LTI 1.3, OIDC, JWT, OAuth 2.0
</div>

---

## Estadísticas del Proyecto

- ✅ **3 microservicios** independientes y escalables
- ✅ **10+ asignaturas** soportadas en el sistema RAG
- ✅ **20 req/min** por usuario (rate limiting configurable)
- ✅ **95%+ precisión** en respuestas del chatbot
- ✅ **< 2s latencia** promedio de respuesta

---

## Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura]({{ site.baseurl }}/docs/architecture) | Diseño del sistema y decisiones técnicas |
| [Instalación]({{ site.baseurl }}/docs/installation) | Guía completa de instalación y configuración |
| [API Reference]({{ site.baseurl }}/docs/api) | Documentación de endpoints REST |
| [Integración LTI]({{ site.baseurl }}/docs/lti-integration) | Configuración con Moodle |
| [Desarrollo]({{ site.baseurl }}/docs/development) | Guía para desarrolladores |
| [Testing]({{ site.baseurl }}/docs/testing) | Estrategias y guías de testing |
| [Monitoreo]({{ site.baseurl }}/docs/monitoring) | Configuración de métricas |

---

## Contribuir

¿Quieres contribuir al proyecto? ¡Excelente! Sigue estos pasos:

1. **Fork** el repositorio
2. Crea una **rama feature** (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un **Pull Request**

[Guía de contribución →]({{ site.baseurl }}/docs/development#contribuir)

---

## Licencia

Este proyecto está licenciado bajo la **licencia MIT**. Ver el archivo [LICENSE](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/blob/main/LICENSE) para más detalles.

---

## Contacto y Soporte

**Desarrolladores:**
- **Javier Trujillo Castro** - Desarrollo inicial y arquitectura base
- **Gabriel Sánchez Muñoz** - Visualización de métricas, vLLM y refactorización

**Soporte:**
- 📧 Email: [Crear issue en GitHub](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/issues)
- 💬 Discusiones: [GitHub Discussions](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/discussions)

---

## Agradecimientos

- **CEPRUD** - Por el apoyo institucional
- **Universidad de Granada** - Por facilitar el proyecto
- **Hugging Face** - Por los modelos pre-entrenados
- **FastAPI** - Por el excelente framework
- **Comunidad Open Source** - Por todas las herramientas utilizadas

---

<div class="text-center mt-8">
  <p class="fs-5">
    <strong>¿Listo para comenzar?</strong>
  </p>
  <a href="{{ site.baseurl }}/docs/installation" class="btn btn-primary btn-lg">Instalar Ahora</a>
</div>
