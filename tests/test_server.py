import os
from ..app.logic.query_logic import query_rag, get_base_model_response

# Configuración inicial
BASE_CHROMA_PATH = "../app/RAG/chroma"
AVAILABLE_SUBJECTS = [
    "ingenieria_servidores",
    "calculo",
    "algoritmica",
    "sistemas_operativos",
    "modelos_avanzados_computacion",
    "metaheuristicas",
    "ingenieria_del_conocimiento"
]

def display_menu():
    """Muestra el menú principal del chatbot."""
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Modo RAG (Recuperación + Generación)")
    print("2. Modo RAG + LoRA (Recuperación + Fine-Tuning)")
    print("3. Modo Modelos Base")
    print("4. Salir")
    choice = input("Selecciona una opción (1/2/3/4): ").strip()
    return choice

def select_subject():
    """Permite al usuario seleccionar una asignatura."""
    print("\n=== SELECCIÓN DE ASIGNATURA ===")
    for idx, subject in enumerate(AVAILABLE_SUBJECTS, start=1):
        print(f"{idx}. {subject.replace('_', ' ').title()}")
    choice = int(input(f"Selecciona una asignatura (1-{len(AVAILABLE_SUBJECTS)}): ").strip())
    if 1 <= choice <= len(AVAILABLE_SUBJECTS):
        return AVAILABLE_SUBJECTS[choice - 1]
    else:
        print("Opción inválida. Seleccionando 'metaheuristicas' por defecto.")
        return "metaheuristicas"

def Test_server():
    """Función principal del chatbot."""
    print("=== BIENVENIDO AL CHATBOT UGR ===")
    while True:
        # Mostrar el menú y obtener la elección del usuario
        choice = display_menu()

        if choice == "1":  # Modo RAG
            print("\n=== MODO RAG ACTIVADO ===")
            subject = select_subject()
            chroma_path = os.path.join(BASE_CHROMA_PATH, subject)
            if not os.path.exists(chroma_path):
                print(f"❌ No hay datos disponibles para la asignatura '{subject}'.")
                continue
            while True:
                query_text = input("\nPregunta (o escribe 'salir' para volver al menú): ").strip()
                if query_text.lower() == "salir":
                    break
                result = query_rag(query_text, chroma_path, use_finetuned=False)
                print(f"\n🤖 Respuesta: {result['response']}")
                if result.get("sources"):
                    print(f"📚 Fuentes: {', '.join(result['sources'])}")

        elif choice == "2":  # Modo RAG + LoRA
            print("\n=== MODO RAG + LoRA ACTIVADO ===")
            subject = select_subject()
            chroma_path = os.path.join(BASE_CHROMA_PATH, subject)
            if not os.path.exists(chroma_path):
                print(f"❌ No hay datos disponibles para la asignatura '{subject}'.")
                continue
            while True:
                query_text = input("\nPregunta (o escribe 'salir' para volver al menú): ").strip()
                if query_text.lower() == "salir":
                    break
                result = query_rag(query_text, chroma_path, subject=subject, use_finetuned=True)
                print(f"\n🤖 Respuesta: {result['response']}")
                if result.get("sources"):
                    print(f"📚 Fuentes: {', '.join(result['sources'])}")

        elif choice == "3":  # Modo BASE
            print("\n=== MODELOS BASE ACTIVADO ===")
            subject = select_subject()
            while True:
                query_text = input("\nPregunta (o escribe 'salir' para volver al menú): ").strip()
                if query_text.lower() == "salir":
                    break
                response = get_base_model_response(query_text)
                print(f"\n🤖 Respuesta: {response}")

        elif choice == "4":  # Salir
            print("\n¡Hasta luego! Gracias por usar el Chatbot UGR.")
            break

        else:
            print("❌ Opción inválida. Por favor, selecciona una opción válida.")

if __name__ == "__main__":
    Test_server()
