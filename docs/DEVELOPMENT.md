# Guía de Desarrollo - Chatbot IA CEPRUD

## 🎯 Introducción para Desarrolladores

Esta guía está diseñada para desarrolladores que quieren contribuir al proyecto Chatbot IA CEPRUD. El proyecto utiliza una arquitectura de microservicios moderna con Python, FastAPI, React, y tecnologías de IA.

## 🛠️ Stack Tecnológico

### **Backend**
- **Python 3.10+**: Lenguaje principal
- **FastAPI**: Framework web asíncrono
- **Pydantic**: Validación de datos y serialización
- **Asyncio**: Programación asíncrona
- **SQLite**: Base de datos local
- **ChromaDB**: Base de datos vectorial

### **Frontend**
- **React 18**: Framework UI
- **TypeScript**: Superset de JavaScript con tipado
- **Vite**: Build tool y dev server
- **Axios**: Cliente HTTP
- **Lucide React**: Librería de iconos

### **IA/ML**
- **Hugging Face Transformers**: Modelos pre-entrenados
- **vLLM**: Optimización de inferencia
- **Sentence Transformers**: Embeddings semánticos
- **PyTorch**: Framework de deep learning

### **DevOps**
- **Docker**: Containerización
- **Docker Compose**: Orquestación de servicios
- **Prometheus**: Métricas
- **Grafana**: Visualización
- **Nginx**: Reverse proxy

## 🏗️ Configuración del Entorno de Desarrollo

### **Prerrequisitos**

```bash
# Verificar versiones
python --version    # >= 3.10
node --version      # >= 16
npm --version       # >= 8
docker --version    # >= 20.10
git --version       # >= 2.30
```

### **Configuración Inicial**

```bash
# 1. Clonar repositorio
git clone https://github.com/your-org/Chatbot_IA_Ceprud.git
cd Chatbot_IA_Ceprud

# 2. Crear entorno virtual Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\\Scripts\\activate  # Windows

# 3. Instalar dependencias Python
pip install -r requirements.txt

```

### **Configuración del Frontend**

```bash
# Instalar dependencias Node.js
cd frontend
npm install
```

## 🚀 Ejecutar en Modo Desarrollo

### **Podman Compose (Desarrollo)**

```bash
# Docker compose para desarrollo con hot reload
podman-compose -f docker-compose.dev.yml up --build -d

# Ver logs en tiempo real
podman-compose -f docker-compose.dev.yml logs -f
```

### **URLs de Desarrollo**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **RAG Service**: http://localhost:8082
- **Logging Service**: http://localhost:8002

## 📁 Estructura del Código

### **Backend (app/)**
```
app/
├── api_router.py              # Rutas principales de la API
├── app.py                     # Aplicación FastAPI principal
│
├── core/                      # Infraestructura base
│   ├── __init__.py
│   ├── config.py              # Configuración centralizada
│   ├── models.py              # Modelos Pydantic
│   └── rate_limiter.py        # Rate limiting
│
├── services/                  # Servicios de negocio
│   ├── __init__.py
│   ├── session_service.py     # Gestión de sesiones
│   ├── logging_service.py     # Cliente de logging
│   ├── rag_client.py          # Cliente RAG
│   └── utils_service.py       # Utilidades
│
├── domain/                    # Lógica de dominio
│   ├── __init__.py
│   ├── query_logic.py         # Procesamiento de queries
│   └── graph.py               # Configuración grafo agente
│
└── storage/                   # Almacenamiento
    ├── checkpoints.sqlite
    └── logs/
```

### **Frontend (frontend/src/)**
```
src/
├── components/                # Componentes React
│   ├── Chat/
│   ├── SubjectSelector/
│   └── common/
├── hooks/                     # Custom React hooks
├── services/                  # Servicios/API clients
├── types/                     # Definiciones TypeScript
├── utils/                     # Utilidades
├── App.tsx                    # Componente principal
└── main.tsx                   # Entry point
```

## 🧪 Testing

### **Tests Unitarios**

```bash
# Asegurar que servicios estén corriendo
podman-compose -f docker-compose-full.yml up -d

# Ejecutar todos los tests unitarios
podman exec chatbot-backend pytest app/unitTests/ -v

# Test específico
podman exec chatbot-backend pytest app/test_query_logic.py -v

# Con coverage
podman exec chatbot-backend pytest app/unitTests/ --cov=app --cov-report=html

# Ver reporte de coverage
open htmlcov/index.html
```

### **Tests de Integración**

```bash
# Asegurar que servicios estén corriendo
podman-compose -f docker-compose-full.yml up -d

# Ejecutar tests de integración
pytest tests/integration/ -v

# Test específico de integración
pytest tests/integration/test_chat_flow.py -v
```

### **Tests End-to-End**

```bash
# Tests E2E con servicios completos
pytest tests/e2e/ -v
```

## 🔌 Añadir Nuevos Endpoints

### **Backend**

```python
# 1. Definir modelo Pydantic (core/models.py)
class NewFeatureRequest(BaseModel):
    param1: str
    param2: int = 10
    param3: Optional[List[str]] = None

class NewFeatureResponse(BaseModel):
    result: str
    processed_at: datetime
    metadata: Dict[str, Any]

# 2. Implementar servicio (services/new_feature_service.py)
class NewFeatureService:
    def __init__(self, config: Config):
        self.config = config
    
    async def process_new_feature(self, request: NewFeatureRequest) -> NewFeatureResponse:
        # Lógica de negocio
        result = await self._process_logic(request)
        
        return NewFeatureResponse(
            result=result,
            processed_at=datetime.utcnow(),
            metadata={"version": "1.0"}
        )

# 3. Añadir endpoint (api_router.py)
@router.post("/new-feature", response_model=NewFeatureResponse)
async def new_feature_endpoint(
    request: NewFeatureRequest,
    service: NewFeatureService = Depends(get_new_feature_service)
):
    """
    Nueva funcionalidad del chatbot.
    
    - **param1**: Descripción del parámetro 1
    - **param2**: Descripción del parámetro 2
    """
    return await service.process_new_feature(request)

# 4. Añadir tests (unitTests/test_new_feature.py)
def test_new_feature_service():
    service = NewFeatureService(mock_config)
    request = NewFeatureRequest(param1="test", param2=5)
    
    result = await service.process_new_feature(request)
    
    assert result.result is not None
    assert result.processed_at is not None
```

### **Frontend**

```typescript
// 1. Añadir tipos (types/index.ts)
export interface NewFeatureRequest {
  param1: string;
  param2?: number;
  param3?: string[];
}

export interface NewFeatureResponse {
  result: string;
  processed_at: string;
  metadata: Record<string, any>;
}

// 2. Añadir servicio API (services/api.ts)
export const newFeatureAPI = {
  async processNewFeature(request: NewFeatureRequest): Promise<NewFeatureResponse> {
    const response = await apiClient.post('/new-feature', request);
    return response.data;
  }
};

```

## 🤝 Contribuir al Proyecto

1. **Fork** el repositorio
2. **Crear rama feature**: `git checkout -b feature/nueva-funcionalidad`
3. **Commit cambios**: `git commit -am 'Añadir nueva funcionalidad'`
4. **Push a la rama**: `git push origin feature/nueva-funcionalidad`
5. **Crear Pull Request**

### **Checklist antes de PR**
- [ ] Tests pasan localmente
- [ ] Código formateado con black/prettier
- [ ] Documentación actualizada
- [ ] Changelog actualizado
- [ ] No hay secretos en el código

¡Gracias por contribuir al desarrollo del Chatbot IA CEPRUD!
