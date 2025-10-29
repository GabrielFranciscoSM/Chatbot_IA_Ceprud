---
layout: default
title: Guía de Instalación
nav_order: 3
parent: Documentación
permalink: /docs/installation
---

# Guía de Instalación y Despliegue - Chatbot IA CEPRUD
{: .no_toc }

## Tabla de Contenidos
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 🎯 Requisitos del Sistema

### **Requisitos Mínimos**
- **Sistema Operativo**: Linux (Ubuntu 20.04+, CentOS 8+, etc.)
- **RAM**: 8 GB (16 GB recomendado para modelos grandes)
- **CPU**: 4 cores (8 cores recomendado)
- **Almacenamiento**: 20 GB libres (50 GB recomendado)
- **Docker**: 20.10+ y Docker Compose 2.0+

### **Requisitos Recomendados para GPU**
- **GPU**: NVIDIA con 8+ GB VRAM (RTX 3060, RTX 4060, etc.)
- **CUDA**: 11.8+ o 12.0+
- **NVIDIA Container Toolkit**: Instalado
- **RAM**: 16+ GB
- **Almacenamiento**: 50+ GB SSD

### **Software Requerido**
```bash
# Verificar versiones
podman --version          # >= 20.10
podman-compose --version  # >= 2.0
python --version          # >= 3.10
nvidia-smi               # Para verificar GPU (opcional)
```

## 🚀 Instalación Rápida

### **Instalación Manual**

#### **Paso 1: Configuración Inicial**

```bash
# Crear archivo de configuración
cp .env.example .env

# Editar variables de entorno
nano .env
```

**Configurar `.env`:**
```bash
# Hugging Face Token (requerido para descargar modelos)
HF_TOKEN=your_huggingface_token_here

# URLs de servicios (por defecto)
RAG_SERVICE_URL=http://localhost:8082
LOGGING_SERVICE_URL=http://localhost:8002
VLLM_LLM_URL=http://localhost:8000
VLLM_EMBEDDING_URL=http://localhost:8001

# Configuración de modelos
BASE_MODEL_PATH=./models
EMBEDDING_MODEL_DIR=./models/Qwen--Qwen3-Embedding-0.6B
LLM_MODEL_DIR=./models/Sreenington--Phi-3-mini-4k-instruct-AWQ

# Configuración de ChromaDB
BASE_CHROMA_PATH=./rag-service/data/chroma

# Rate Limiting
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
BASE_LOG_DIR=./logs
```

#### **Paso 2: Descargar Modelos de IA**

```bash
# Instalar dependencias para descarga
pip install huggingface_hub

# Ejecutar script de descarga
python scripts/download_llm.py
```

**Modelos que se descargarán:**
- **LLM**: `Sreenington/Phi-3-mini-4k-instruct-AWQ` (~2GB)
- **Embeddings**: `Qwen/Qwen3-Embedding-0.6B` (~1.2GB)

#### **Paso 3: Build de Containers**

```bash
# Build de todos los servicios
podman-compose -f docker-compose-full.yml build

# Verificar que las imágenes se crearon correctamente
podman images | grep chatbot
```

#### **Paso 4: Inicializar Base de Datos RAG**

```bash
# Crear directorio de datos
mkdir -p rag-service/data/chorma
mkdir -p rag-service/data/ExampleSubject

# Poblar base de datos inicial
podman-compose -f docker-compose-full.yml up rag-service -d
sleep 30

# Ejecutar población inicial (ejemplo)
$ ./scripts/repopulate_optimized.sh
```

## 🐳 Despliegue con Podman

### **Despliegue Completo**
``` bash
$ ./scripts/manage_podman_compose.sh
``` 

### **Configuración con GPU**

Para habilitar aceleración GPU, descomenta las secciones de vLLM en `docker-compose-full.yml`:

```yaml
# Descomentar servicio vLLM
vllm-openai:
    container_name: my-vllm-service
    deploy:
        resources:
            reservations:
                devices:
                    - driver: nvidia
                      device_ids: ['0']
                      capabilities:
                          - gpu
    # ... resto de configuración
```

***IMPORTANTE:*** Cambiar la variable de entorno LOCAL_INFERENCE a false en el script graph.py

## 🧪 Configuración de Testing

### **Tests Unitarios**

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio pytest-cov

# Asegurarse que están los servicios funcionando
podman-compose -f docker-compose-full.yml up -d

# Ejecutar tests unitarios
podman exec chatbot-backend pytest app/unitTests/ -v

# Con coverage
podman exec chatbot-backend pytest app/unitTests/ --cov=app --cov-report=html
```

### **Tests de Integración**

```bash
# Asegurar que servicios estén corriendo
podman-compose -f docker-compose-full.yml up -d

# Ejecutar tests de integración
pytest tests/integration/ -v

# Tests end-to-end
pytest tests/e2e/ -v
```

### **Tests de Infraestructura**

```bash
# Verificar health checks
pytest tests/infrastructure/test_health_checks.py -v

# Tests de conectividad entre servicios
pytest tests/infrastructure/test_service_connectivity.py -v
```

## 🚀 Despliegue en Producción

### **Preparación para Producción**

```bash
# 1. Optimizar imágenes Docker
podman-compose -f docker-compose-full.yml build --no-cache
```

### **Configuración de Reverse Proxy (Nginx) TODO**

```nginx
# /etc/nginx/sites-available/chatbot
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8090;  # Frontend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8080;  # Backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Health Checks**

```bash
# Verificar health de todos los servicios
curl http://localhost:8080/health  # Backend
curl http://localhost:8082/health  # RAG Service
curl http://localhost:8002/health  # Logging Service
curl http://localhost:8090/        # Frontend
```

## 📋 Checklist Post-Instalación

- [ ] Todos los servicios están corriendo (`podman-compose ps`)
- [ ] Health checks responden correctamente
- [ ] Frontend accesible en http://localhost:8090
- [ ] Backend API docs en http://localhost:8080/docs
- [ ] Base de datos RAG poblada con documentos
- [ ] Modelos de IA descargados correctamente
- [ ] Logs generándose en `./logs/`
- [ ] Tests pasando correctamente

## 🆘 Soporte

Si encuentras problemas durante la instalación:

1. **Consulta los logs**: `podman-compose logs -f`
2. **Verifica requisitos**: Versions de Docker, Python, etc.
3. **Revisa configuración**: Variables de entorno en `.env`
4. **Consulta documentación**: README.md y docs/
5. **Reporta issues**: GitHub Issues con logs y configuración

## 📚 Próximos Pasos

Una vez instalado correctamente:

1. **Leer [API.md](API.md)** - Documentación de endpoints
2. **Revisar [DEVELOPMENT.md](DEVELOPMENT.md)** - Guía de desarrollo
3. **Configurar [MONITORING.md](MONITORING.md)** - Métricas avanzadas
4. **Personalizar** - Añadir nuevas asignaturas y documentos
