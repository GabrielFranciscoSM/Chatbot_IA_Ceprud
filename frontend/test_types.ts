// Test file to verify that our types work correctly
import { Message, ChatResponse } from './src/types';
import { createMessage } from './src/utils';

// Test creating a message with sources
const testMessageWithSources: Message = createMessage(
  "Esta es una respuesta del asistente con fuentes",
  "assistant",
  "ia",
  ["Fuente 1: Documento de IA", "Fuente 2: Paper de Machine Learning"],
  "Phi-3-mini-4k-instruct"
);

// Test ChatResponse with sources
const testChatResponse: ChatResponse = {
  response: "Esta es la respuesta del chatbot",
  subject: "ia",
  sources: ["Fuente 1", "Fuente 2"],
  model_used: "Phi-3-mini-4k-instruct",
  query_type: "academic_question"
};

console.log("Types test successful!");
console.log("Message with sources:", testMessageWithSources);
console.log("Chat response:", testChatResponse);
