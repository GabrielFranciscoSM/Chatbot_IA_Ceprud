# test_conversation.py
import os
from langchain_core.messages import HumanMessage
from graph import build_graph, AgentState # Asegúrate de que tu graph.py se pueda importar así

# Importa tu función de llamada, pero la modificaremos para esta prueba
from query_logic import query_rag, system_prompt

print("--- INICIANDO PRUEBA DE CONVERSACIÓN CONTROLADA ---")

# 1. Construimos el grafo UNA SOLA VEZ
rag_graph = build_graph()
print("Grafo y memoria construidos.")

# 2. Definimos un ID de conversación para toda la prueba
chat_id = "test_controlado_123"
subject = "metaheuristicas"
config = {"configurable": {"thread_id": chat_id, "subject": subject}}

# 3. TURNO 1
print("\n--- TURNO 1 ---")
print("Pregunta: ¿qué es un algoritmo greedy?")
# Llamada inicial, creamos el estado
input_1 = {
    "messages": [system_prompt, HumanMessage(content="¿qué es un algoritmo greedy?")],
    "subject": subject,
    "retrieved_docs": []
}
result_1 = rag_graph.invoke(input_1, config)
print(f"Respuesta del Agente: {result_1['messages'][-1].content}")

# Verificamos el estado guardado
state_after_1 = rag_graph.get_state(config)
print(f"Número de mensajes en memoria después del turno 1: {len(state_after_1.values['messages'])}")
assert len(state_after_1.values['messages']) > 2 # Debería ser Sys, Human, AI(tool), Tool, AI(final)

# 4. TURNO 2
print("\n--- TURNO 2 ---")
print("Pregunta: recuerdas la pregunta que te hice?")
# Llamada de continuación, SOLO enviamos el nuevo mensaje
input_2 = {
    "messages": [HumanMessage(content="recuerdas la pregunta que te hice?")]
}
result_2 = rag_graph.invoke(input_2, config)
print(f"Respuesta del Agente: {result_2['messages'][-1].content}")

state_after_2 = rag_graph.get_state(config)
print(f"Número de mensajes en memoria después del turno 2: {len(state_after_2.values['messages'])}")

print("\n--- PRUEBA FINALIZADA ---")

# La respuesta a la segunda pregunta NO debería ser "no tengo memoria"
if "no tengo memoria" not in result_2['messages'][-1].content.lower():
    print("¡ÉXITO! La memoria conversacional funcionó en el entorno controlado.")
else:
    print("FALLO: La memoria no funcionó incluso en el entorno controlado.")