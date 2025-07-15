from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch


if __name__ == "__main__":
    # Ejemplo de uso
    subject_name = input("Introduce el nombre de la asignatura: ")
    ADAPTER_PATH = f"./models/{subject_name}-deepseek-qlora"

    # Configuración
    MODEL_NAME = "deepseek-ai/deepseek-llm-7b-chat"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Usando dispositivo: {device}")

    # Cargar tokenizador y modelo base
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        trust_remote_code=True
    ).to(device)  # Forzar carga en GPU

    # Cargar adaptadores de LoRA y fusionarlos (merge)
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model = model.merge_and_unload()  # Fusionar LoRA con el modelo base
    model.eval()

    # Función para generar respuestas
    def responder(pregunta):
        inputs = tokenizer(pregunta, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.3,
                top_p=0.95,
                pad_token_id=tokenizer.eos_token_id  # Evitar errores de padding
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    pregunta = input("Pregunta al modelo con finetuning: ")
    respuesta = responder(pregunta)
    print(respuesta)
    