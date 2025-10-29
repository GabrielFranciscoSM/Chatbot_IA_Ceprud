---
layout: default
title: Monitoreo y Métricas
nav_order: 8
parent: Documentación
permalink: /docs/monitoring
---

# Guía de Monitoreo - Chatbot IA CEPRUD
{: .no_toc }

## Tabla de Contenidos
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 🎯 Introducción al Monitoreo

El sistema de monitoreo del Chatbot IA CEPRUD está diseñado para proporcionar observabilidad completa del stack de microservicios, permitiendo detectar problemas proactivamente, optimizar rendimiento y garantizar una experiencia de usuario óptima.

## 📊 Stack de Observabilidad

### **Componentes Principales**
- **Langfuse**: Trazas y auditoría de agentes/LLMs, registros de prompts/respuestas, pasos de agentes y metadatos de RAG.
- **Logs estructurados**: Logging centralizado con formato JSON para eventos que no requieren tracing completo.
- **Health checks**: Monitoreo de salud de servicios (endpoints /health, readiness/liveness).

### **Arquitectura de Monitoreo**

```mermaid
graph TB
    subgraph "Servicios"
        BACKEND[Backend Service<br/>:8080]
        RAG[RAG Service<br/>:8082]
        LOG[Logging Service<br/>:8002]
        FRONTEND[Frontend<br/>:8090]
    end
    
    subgraph "Trazas y Recolección"
        LF[Langfuse (web & worker)<br/>:3000 / 3030]
        LOGS[Log Files<br/>JSON/CSV]
    end
    
    subgraph "Almacenamiento/Media"
        MINIO[MinIO<br/>:9090]
        CLICKHOUSE[ClickHouse<br/>:8123]
    end
    
    BACKEND --> LF
    RAG --> LF
    LOG --> LF
    FRONTEND --> LF

    BACKEND --> LOGS
    RAG --> LOGS
    LOG --> LOGS

    LF --> MINIO
    LF --> CLICKHOUSE
```

## 🚀 Configuración Rápida

### **Levantar Langfuse y dependencias**

En este repositorio se incluye un `langfuse-compose.yml` para levantar Langfuse (web + worker) y sus dependencias (ClickHouse, MinIO, Redis, Postgres). Puedes levantar el stack localmente con:

```bash
# Levantar Langfuse y dependencias (usa el archivo en la raíz del repositorio)
docker-compose -f langfuse-compose.yml up -d

# Verificar servicios
docker-compose -f langfuse-compose.yml ps

# Seguir logs (ejemplo: web)
docker-compose -f langfuse-compose.yml logs -f langfuse-web
```

### **URLs de Acceso (local)**
- **Langfuse Web UI**: http://localhost:3000  (ver `langfuse-compose.yml` si tu entorno cambia puertos)
- **Langfuse Worker (ingest / API interna)**: http://localhost:3030 (worker)
- **MinIO (S3 compatible)**: http://localhost:9091 (consola)
- **ClickHouse (HTTP)**: http://localhost:8123

Nota: los puertos anteriores coinciden con la configuración incluida en `langfuse-compose.yml` del repositorio.

## 📈 Trazas y eventos (Langfuse)

Ahora centralizamos trazas de agentes, pasos de LLM y eventos de RAG en Langfuse en lugar de Prometheus/Grafana. Langfuse permite inspeccionar todas las ejecuciones de agentes (prompts, respuestas, embeddings, pasos, metadata) y realizar búsquedas y análisis por conversación, usuario, proyecto, o experimento.

Qué enviar a Langfuse (recomendado):
- Identificadores: org_id, project_id, user_id, session_id, conversation_id
- Metadata del modelo: model name, model config, temperature
- Prompt / input: tokens, embeddings (si aplica), raw text
- Respuesta / output: text, tokens, score, latency
- Pasos de agentes: llamadas a herramientas, RAG retrievals (docs ids, scores), chain of thought
- Metrías y tiempos: latencia total, pasos individuales, memoria/CPU si te interesa
- Artefactos/Media: archivos/audio/images (subir a MinIO y referenciar desde Langfuse)

Ejemplo conceptual (Python) — usa el SDK oficial de Langfuse si está disponible; si no, envía eventos al worker/ingest:

```python
# Ejemplo conceptual de evento para Langfuse
event = {
    "type": "agent_execution",
    "project_id": "my_project",
    "user_id": "user123",
    "session_id": "sess-456",
    "model": "gpt-4-mini",
    "input": "¿Cuál es la capital de Francia?",
    "output": "París",
    "latency_ms": 120,
    "rag_results": [
        {"doc_id": "doc-1", "score": 0.92},
    ],
    "timestamp": "2025-10-29T12:34:56Z",
}

# En producción, usa el SDK oficial de Langfuse. Alternativamente, envía el evento al worker/ingest (worker habitualmente escucha en el puerto 3030).
# requests.post("http://localhost:3030/<ingest-endpoint>", json=event, headers={...})
```

Recomendaciones prácticas:
- Instrumenta los puntos clave: entrada de chat, respuesta final, fallbacks, y resultado de búsquedas RAG.
- Adjunta identificadores de usuario y sesión para poder agrupar conversaciones.
- Subir artefactos grandes (archivos, audio, imágenes) a MinIO y referenciarlos en el evento.
- Usa sampling para llamadas de alta frecuencia si necesitas ahorrar almacenamiento.

Si quieres métricas de sistema (CPU/mem), sigue exportándolas a tu solución de métricas preferida o añade sencillos Gauges en tus servicios y guárdalos junto a las trazas en Langfuse como eventos periódicos.

---

Este sistema de monitoreo proporciona observabilidad completa del Chatbot IA CEPRUD, permitiendo mantener alta disponibilidad y rendimiento óptimo mientras se obtienen insights valiosos sobre el uso y la efectividad educativa del sistema.
