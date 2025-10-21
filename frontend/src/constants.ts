import { Subject } from './types';

export const SUBJECTS: Subject[] = [
  {
    id: 'ingenieria_de_servidores',
    name: 'Ingeniería de Servidores',
    icon: '💻',
    description: 'Gestión y configuración de servidores'
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
    id: 'inferencia_estadistica_1',
    name: 'Inferencia Estadistica I (Estadistica)',
    icon: '📄',
    description: ''
  },
  {
    id: 'estadistica',
    name: 'Estadistica (Ingeniería Informática)',
    icon: '📄',
    description: ''
  },
  {
    id: 'DBA',
    name: 'Desarrollo basada en agentes',
    icon: '🗄️',
    description: 'Desarrollo basada en agentes'
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
