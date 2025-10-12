# Logging Service

Independent microservice for handling analytics and logging operations for the Chatbot IA Ceprud project.

## Overview

This service provides RESTful APIs for logging various events and interactions from the main chatbot application:

- Session events
- User messages
- Learning events  
- Request information
- Bot responses

## Architecture

- **FastAPI**: Modern Python web framework for building APIs
- **Pydantic**: Data validation and serialization
- **CSV Storage**: Logs are written to CSV files for analytics

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Service health check
- `GET /api/v1/logs/health` - Logging health check

### Logging Endpoints
- `POST /api/v1/logs/session-event` - Log session events
- `POST /api/v1/logs/user-message` - Log user messages
- `POST /api/v1/logs/learning-event` - Log learning events
- `POST /api/v1/logs/request-info` - Log request information
- `POST /api/v1/logs/bot-response` - Log bot responses

## Configuration

The service uses environment variables for configuration:

- `BASE_LOG_DIR`: Directory for log files (default: `/app/logs`)
- Service runs on port 8002

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker

Build and run with Docker:

```bash
docker build -t logging-service .
docker run -p 8002:8002 -v ./logs:/app/logs logging-service
```

## Integration

This service is designed to be used by the main chatbot backend. The backend makes HTTP requests to this service instead of writing logs directly to files.

## File Structure

```
logging-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration settings
│   ├── routers/
│   │   ├── __init__.py
│   │   └── log_router.py    # API routes
│   └── services/
│       ├── __init__.py
│       └── logging_service.py # Core logging logic
├── requirements.txt
├── Dockerfile
└── README.md
```
