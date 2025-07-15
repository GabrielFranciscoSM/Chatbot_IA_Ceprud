from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import torch
from transformers import BitsAndBytesConfig
import os
from dotenv import load_dotenv

load_dotenv()

# Autenticación en Hugging Face
HF_TOKEN = os.getenv("HF_TOKEN")  # Reemplaza con tu token
login(token=HF_TOKEN)

MODEL="..".join(os.getenv("MODEL_DIR"))
SHORT_MODEL_NAME = os.getenv("MODEL_NAME").split("/")[1]

MODELS_DIR_PATH = "../models/"

def fine_tune_deepseek(subject):
    data_path = f"../data/{subject}/train_data.json"
    if not os.path.exists(data_path):
        raise ValueError(f"Archivo {data_path} no encontrado. Ejecuta generate_data.py primero")

    # Cargar datos
    dataset = load_dataset("json", data_files=data_path)

    # Configurar cuantización QLoRA
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # Cargar modelo
    model = AutoModelForCausalLM.from_pretrained(
        MODEL,
        quantization_config=quantization_config,
        device_map="auto",
        token=HF_TOKEN,
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    # Configuración LoRA
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)

    # Tokenizador
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL,
        token=HF_TOKEN,
        padding_side="right",
        truncation_side="right"
    )

    # Tokenización con formato correcto
    def preprocess(examples):
        inputs = tokenizer(
            examples["question"],
            examples["answer"],
            truncation=True,
            padding="max_length",
            max_length=1024,
            return_tensors="pt"
        )
        inputs["labels"] = inputs["input_ids"].clone()  # Asegurar labels como tensores
        return inputs

    tokenized_dataset = dataset.map(
        preprocess,
        batched=True,
        remove_columns=["question", "answer", "source"]
    )

    # Asegurar que el dataset use tensores de PyTorch
    tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    # Configuración de entrenamiento
    training_args = TrainingArguments(
        output_dir=MODELS_DIR_PATH.join(f"{subject}-".join(SHORT_MODEL_NAME)),
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=1e-4,
        fp16=True,
        logging_steps=10,
        save_steps=200,
        save_total_limit=2,
        report_to="none"  # Desactivar wandb si no es necesario
    )

    # Entrenador con collator correcto
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        data_collator=lambda data: {
            "input_ids": torch.stack([item["input_ids"] for item in data]),
            "attention_mask": torch.stack([item["attention_mask"] for item in data]),
            "labels": torch.stack([item["labels"] for item in data])  # Usar labels explícitas
        }
    )

    # Entrenar y guardar
    trainer.train()
    model.save_pretrained(MODELS_DIR_PATH.join(f"{subject}-",SHORT_MODEL_NAME))
    tokenizer.save_pretrained(MODELS_DIR_PATH.join(f"{subject}-",SHORT_MODEL_NAME))
    print(f"✅ Modelo guardado en: " + MODELS_DIR_PATH.join(f"{subject}-",SHORT_MODEL_NAME))

if __name__ == "__main__":
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    subject = input("Introduce la asignatura para fine-tuning: ").strip().lower()
    fine_tune_deepseek(subject)