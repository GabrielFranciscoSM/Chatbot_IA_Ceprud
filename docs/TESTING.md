# Guía de Testing - Chatbot IA CEPRUD

## 🎯 Estrategia de Testing

El proyecto implementa una estrategia de testing exhaustiva con múltiples niveles para asegurar la calidad y confiabilidad del sistema.

## 🏗️ Pirámide de Testing

```
         / \
        /   \
       / E2E \    ← Tests End-to-End (pocos, costosos)
      /______ \
     /         \
    /Integration\  ← Tests de Integración (moderados)
   /_____________\
  /               \
 /   Unit Tests    \  ← Tests Unitarios (muchos, rápidos)
/___________________\
```

## 🧪 Tipos de Tests

### **1. Tests Unitarios**
- **Ubicación**: `unitTests/`
- **Enfoque**: Componentes individuales
- **Velocidad**: Muy rápida
- **Cobertura**: > 80%

### **2. Tests de Integración**
- **Ubicación**: `tests/integration/`
- **Enfoque**: Interacción entre servicios
- **Velocidad**: Moderada
- **Cobertura**: Flujos críticos de negocio

### **3. Tests End-to-End**
- **Ubicación**: `tests/e2e/`
- **Enfoque**: Flujos completos de usuario
- **Velocidad**: Lenta
- **Cobertura**: User journeys principales

### **4. Tests de Infraestructura**
- **Ubicación**: `tests/infrastructure/`
- **Enfoque**: Conectividad y salud de servicios
- **Velocidad**: Rápida
- **Cobertura**: Health checks y conectividad

## 🛠️ Configuración de Testing

### **Dependencias**

```bash
# Instalar dependencias de testing
pip install -r requirements-test.txt

# Dependencias principales:
# - pytest: Framework de testing
# - pytest-asyncio: Soporte para async/await
# - pytest-cov: Coverage reporting
# - httpx: Cliente HTTP async para tests
# - pytest-mock: Mocking utilities
```

### **Configuración Pytest**

```ini
[pytest]
testpaths = tests unitTests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = app
addopts = --hosts=podman://

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    infrastructure: Infrastructure tests using testinfra

# Environment variables for testing
env =
    VLLM_URL=http://localhost:8000
    VLLM_EMBEDDING_URL=http://localhost:8001
    BASE_CHROMA_PATH=tests/test_chroma
    BASE_DATA_PATH=tests/test_data
    RAG_SERVICE_URL=http://localhost:8082

