import { Subject } from './types';

export const SUBJECTS: Subject[] = [
  {
    id: 'ingenieria_servidores',
    name: 'Ingeniería de Servidores',
    icon: '💻',
    description: 'Gestión y configuración de servidores'
  },
  {
    id: 'calculo',
    name: 'Cálculo',
    icon: '📊',
    description: 'Matemáticas y análisis matemático'
  },
  {
    id: 'algoritmica',
    name: 'Algorítmica',
    icon: '🧩',
    description: 'Algoritmos y estructuras de datos'
  },
  {
    id: 'sistemas_operativos',
    name: 'Sistemas Operativos',
    icon: '⚙️',
    description: 'Fundamentos de sistemas operativos'
  },
  {
    id: 'modelos_avanzados_computacion',
    name: 'Modelos Avanzados de Computación',
    icon: '🧠',
    description: 'Técnicas avanzadas de computación'
  },
  {
    id: 'metaheuristicas',
    name: 'Metaheurísticas',
    icon: '🔍',
    description: 'Algoritmos de optimización'
  },
  {
    id: 'ingenieria_conocimiento',
    name: 'Ingeniería del Conocimiento',
    icon: '📄',
    description: 'Gestión y representación del conocimiento'
  }
];

export const CHAT_MODES = [
  { id: 'rag', name: 'RAG', description: 'Retrieval Augmented Generation' },
  { id: 'base', name: 'Base Model', description: 'Modelo base sin RAG' },
  { id: 'rag_lora', name: 'RAG + LoRA', description: 'RAG con fine-tuning' }
] as const;

export const DEFAULT_EMAIL_DOMAIN = '@correo.ugr.es';

export const SESSION_STORAGE_KEYS = {
  USER_EMAIL: 'chatbot_user_email',
  SELECTED_SUBJECT: 'chatbot_selected_subject',
  PREFERRED_MODE: 'chatbot_preferred_mode',
  SESSIONS: 'chatbot_sessions'
} as const;
