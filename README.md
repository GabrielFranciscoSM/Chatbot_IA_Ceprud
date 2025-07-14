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
- Docker y Docker compose
- Las dependencias están listadas en `requirements.txt`

---

## 📦 Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/javitrucas/Chatbot_IA_Ceprud.git
   cd Chatbot_IA_Ceprud
   ```
2. Descarga el modelo (1) y (4):
   ```
    python3 download_model.py
   ```
3. Ejecuta el docker compose
  ```
  docker-compose -f docker-compose-vllm.yml up --build
  ```

---

## 🚀 Set Up de Fine-Tuning y QLoRA:
- **Añadir asignatura** (Evitar carácteres extraños) :
  ```
  python add_subject.py
  ```
- **Fine-tuning con QLoRA**:  
  1. Generar datos para una asignatura:
    ```
    generate_data.py
    ```
  2. Entrenar el modelo:
    ```
    python finetuning_qlora.py \
      --base_model model-name \
      --data data/dataset.json \
      --output_dir models/fine_tuned
    ```

- **Población de base de datos (RAG)**:
  ```
  python populate_database.py
  ```

---

## Visualización de métricas:

1. **Desplegar contenedores**:
  ```
  docker-compose -f docker-compose-prometehus-graphana.yml up -d
  ```
2. **Abrir Grafana**:
  Abrir en el buscador http://localhost:3000/
3. **Configurar DataSource**:
  Abrir http://localhost:3000/connections/datasources/new y elegir Prometheus con http://prometheus:9090
4. **Importar Dashboard**
  Abrir http://localhost:3000/dashboard/import y copiar el contenido de grafana.json
---

## 📫 Contacto

Desarrollado por Javier Trujillo Castro. Si tienes alguna duda o sugerencia contáctame vía GitHub.
Visualización de métricas e implementación de vLLM por Gabriel Sánchez Muñoz.

