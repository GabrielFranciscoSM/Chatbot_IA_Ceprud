---
layout: default
title: Visión General del Proyecto
nav_order: 1
parent: Documentación
permalink: /docs/project-overview
---

# Visión General del Proyecto - Chatbot IA CEPRUD
{: .no_toc }

## Tabla de Contenidos
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 🎓 Contexto Educativo

El **Chatbot IA CEPRUD** es una solución de inteligencia artificial diseñada específicamente para CEPRUD (Centro de Producción de Recursos para la Universidad Digital) de la Universidad de Granada. El proyecto surge de la necesidad de proporcionar asistencia educativa personalizada y escalable para estudiantes de la UGR.

## 🎯 Objetivos del Proyecto

### **Objetivo Principal**
Desarrollar un sistema de chatbot inteligente que utilice técnicas de RAG (Retrieval-Augmented Generation) para responder preguntas específicas sobre asignaturas de Ingeniería Informática, utilizando como fuente de conocimiento las guías docentes y materiales oficiales de la universidad.

### **Objetivos Específicos**
1. **Accesibilidad 24/7**: Proporcionar asistencia educativa disponible en cualquier momento
2. **Personalización**: Adaptar respuestas según la asignatura y nivel del estudiante
3. **Escalabilidad**: Manejar múltiples usuarios simultáneamente sin degradación del servicio
4. **Precisión**: Generar respuestas basadas en información oficial y verificada
5. **Trazabilidad**: Proporcionar fuentes y referencias para todas las respuestas
6. **Analytics**: Recopilar datos sobre patrones de aprendizaje y uso

## 🔬 Metodología y Enfoque Técnico

### **Paradigma de Desarrollo**
- **Domain-Driven Design (DDD)**: Organización del código basada en el dominio educativo
- **Microservicios**: Arquitectura distribuida para mayor escalabilidad y mantenibilidad
- **DevOps Culture**: Integración y deployment continuos

### **Stack Tecnológico Seleccionado**

#### **Backend**
- **Python 3.10+**: Lenguaje principal por su ecosistema de IA/ML
- **FastAPI**: Framework web moderno, rápido y con documentación automática
- **Pydantic**: Validación de datos y serialización type-safe
- **AsyncIO**: Programación asíncrona para mejor rendimiento

**Justificación**: Python ofrece el mejor ecosistema para IA/ML, FastAPI proporciona rendimiento comparable a Node.js con la simplicidad de Python, y AsyncIO permite manejar múltiples requests concurrentes eficientemente.

#### **Frontend**
- **React 18**: Framework UI moderno con excelente ecosistema
- **TypeScript**: Superset de JavaScript para type safety
- **Vite**: Build tool moderno y rápido
- **Axios**: Cliente HTTP robusto para comunicación con API

**Justificación**: React ofrece la mejor experiencia de desarrollo para UIs complejas, TypeScript reduce bugs y mejora la experiencia de desarrollo, Vite proporciona hot reload ultra-rápido.

#### **IA/ML**
- **Hugging Face Transformers**: Acceso a modelos pre-entrenados de última generación
- **vLLM**: Optimización de inferencia para modelos de lenguaje grandes
- **ChromaDB**: Base de datos vectorial especializada para RAG
- **Sentence Transformers**: Embeddings semánticos de alta calidad

**Justificación**: Hugging Face es el estándar de facto para modelos de IA, vLLM ofrece la mejor optimización para inferencia de LLMs, ChromaDB está específicamente diseñada para casos de uso RAG.

#### **Infraestructura**
- **Podman**: Containerización para consistency across environments
- **Podman Compose**: Orquestación de servicios para desarrollo y testing

**Justificación**: Podman garantiza que "funciona en mi máquina" no sea un problema.

## 🏗️ Decisiones de Arquitectura

### **Microservicios vs Monolito**
**Decisión**: Arquitectura de microservicios
**Justificación**:
- **Escalabilidad independiente**: RAG service puede escalar independientemente del backend
- **Tecnología heterogénea**: Diferentes servicios pueden usar diferentes tecnologías
- **Fault isolation**: Fallo en un servicio no afecta a otros
- **Team autonomy**: Diferentes equipos pueden trabajar independientemente

### **Base de Datos Vectorial**
**Decisión**: ChromaDB
**Alternativas consideradas**: Pinecone, Weaviate, Qdrant
**Justificación**:
- **Simplicidad**: Fácil de configurar y mantener
- **Open source**: No vendor lock-in
- **Python-native**: Integración natural con el stack
- **Optimizada para RAG**: Diseñada específicamente para este caso de uso

### **Modelo de Lenguaje**
**Decisión**: Phi-3-mini-4k-instruct-AWQ (cuantizado)
**Alternativas consideradas**: Llama-2, Mistral, GPT-3.5
**Justificación**:
- **Tamaño eficiente**: Cabe en GPUs comerciales (8GB VRAM)
- **Rendimiento**: Excelente calidad de respuesta para su tamaño
- **Quantización AWQ**: Mantiene calidad con reducción significativa de memoria
- **Fine-tuning friendly**: Permite personalización futura

## 🎓 Impacto Educativo Esperado

### **Para Estudiantes**
- **Acceso inmediato** a información sobre asignaturas
- **Aprendizaje autodirigido** con asistencia IA
- **Reducción de barreras** para hacer preguntas
- **Disponibilidad 24/7** sin depender de horarios de profesores

### **Para Profesores**
- **Reducción de preguntas repetitivas** en consultas
- **Insights sobre temas** que más confunden a estudiantes
- **Liberación de tiempo** para consultas más complejas
- **Standardización de información** proporcionada

### **Para la Institución**
- **Mejora en satisfacción estudiantil**
- **Reducción de carga** en servicios de atención
- **Datos valiosos** sobre patrones de aprendizaje
- **Innovación tecnológica** visible
