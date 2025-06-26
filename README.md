# Chatbot_IA_Ceprud 🤖

Un chatbot basado en Inteligencia Artificial diseñado para CEPRUD (Centro de Producción de Recursos para la Universidad Digital). Utiliza modelos finos y técnicas RAG (Retrieval-Augmented Generation) para responder preguntas en base a un corpus de datos y documentos sobre las distintas asignaturas de la carrera de Ingeniería Informática.

---

## 🎯 Características principales

- **RAG**: combina embedding y recuperación de documentos para respuestas más precisas.  
- **Fine-tuning / QLoRA**: permite personalizar el modelo de lenguaje para dominios específicos.  
- **API REST**: API ligera para integrar fácilmente el chatbot en otras aplicaciones.  
- **Interfaz web básica**: demo funcional con frontend en HTML/CSS/JS.  
- **Visualización de logs y métricas**: incluye generación de gráficos para análisis en profundidad.  
- **Testeo automático**: con pruebas unitarias y de integración en `test_*.py`.  

---

## 🧰 Requisitos

- Python ≥ 3.10  
- Podman 
- Las dependencias están listadas en `requirements.txt`

---

## 📦 Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/javitrucas/Chatbot_IA_Ceprud.git
   cd Chatbot_IA_Ceprud
   ```

2. Crea entorno virtual e instala dependencias:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 🚀 Uso
- **Fine-tuning con QLoRA**:  
  Ejemplo:
  ```
  python finetuning_qlora.py \
    --base_model model-name \
    --data data/dataset.json \
    --output_dir models/fine_tuned
  ```

- **Generación de embeddings**:
  ```
  python get_embedding_function.py
  ```

- **Población de base de datos (RAG)**:
  ```
  python populate_database.py
  ```

---

## 📫 Contacto

Desarrollado por Javier Trujillo Castro. Si tienes alguna duda o sugerencia contáctame vía GitHub.

