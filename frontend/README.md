# Chatbot Frontend

Modern React TypeScript frontend for the UGR CEPRUD Chatbot.

## Features

- 🎓 **Multiple Subjects**: Switch between different academic subjects with dedicated RAG documents
- 💬 **Real-time Chat**: Interactive chat interface with message history
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔄 **Session Management**: Persistent chat sessions per subject using localStorage
- ⚡ **Rate Limiting**: Built-in rate limiting with user feedback
- 🎨 **Modern UI**: Clean, academic-focused design

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Axios** for API communication
- **Lucide React** for icons
- **CSS3** with CSS custom properties for theming

## Getting Started

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Docker

```bash
# Build the frontend image
docker build -t chatbot-frontend .

# Run with docker-compose (recommended)
docker-compose -f docker-compose-full.yml up
```

## Configuration

### Environment Variables

- `VITE_API_BASE_URL`: Base URL for the API (default: `/api`)
- `VITE_DEV_API_BASE_URL`: API URL for development (default: `http://localhost:8080`)

### API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- `POST /chat`: Send chat messages
- `GET /health`: Health check
- `GET /graphs`: Analytics data
- `GET /rate-limit-info`: Rate limiting information

## Architecture

### Components

- **App.tsx**: Main application component with state management
- **SubjectSidebar.tsx**: Subject selection sidebar
- **SettingsPanel.tsx**: User settings (email, chat mode)
- **MessageList.tsx**: Chat message display
- **ChatInput.tsx**: Message input component

### State Management

- **Sessions**: Stored in localStorage, managed per subject
- **User Settings**: Email and preferred chat mode
- **Rate Limiting**: Real-time rate limit tracking

### Session Handling

Each subject has its own chat session with:
- Unique session ID
- Message history
- Last activity timestamp
- Automatic cleanup of old sessions

## Subjects Available

- 💻 Ingeniería de Servidores
- 📊 Cálculo
- 🧩 Algorítmica
- ⚙️ Sistemas Operativos
- 🧠 Modelos Avanzados de Computación
- 🔍 Metaheurísticas
- 📄 Ingeniería del Conocimiento

## Chat Modes

- **RAG**: Retrieval Augmented Generation (default)
- **Base Model**: Direct model inference without RAG
- **RAG + LoRA**: RAG with fine-tuned adapters

## Development

### File Structure

```
src/
├── components/          # React components
├── types.ts            # TypeScript type definitions
├── constants.ts        # Application constants
├── utils.ts           # Utility functions
├── api.ts             # API client
├── App.tsx            # Main application
├── App.css            # Global styles
└── main.tsx           # Application entry point
```

### Code Style

- TypeScript with strict mode enabled
- Functional components with hooks
- CSS modules for component styling
- ESLint for code quality

## Deployment

The frontend is served using Nginx with:
- Static file serving
- API proxy to backend
- Client-side routing support
- Gzip compression
- Security headers

Access the application at `http://localhost:3000` when running with docker-compose.
