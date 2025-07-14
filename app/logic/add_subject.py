import os
import shutil
import subprocess

# Configuración de rutas
DATA_DIR = "data"
TEMPLATES_DIR = "templates"
INDEX_HTML_PATH = os.path.join(TEMPLATES_DIR, "index.html")

# Mapeo de íconos por asignatura (puedes personalizarlo)
ICON_MAPPING = {
    "ingenieria_servidores": "💻",
    "calculo": "📊",
    "algoritmica": "🧩",
    "sistemas_operativos": "⚙️",
    "modelos_avanzados_computacion": "🧠",
    "metaheuristicas": "🔍",
    # Agrega aquí más asignaturas y sus íconos
}

def process_pdf_files(pdf_files_input):
    """
    Procesa las rutas de archivos PDF ingresadas por el usuario.
    Elimina comillas adicionales y devuelve una lista de rutas válidas.
    """
    if not pdf_files_input:
        return None

    # Dividir las rutas por comas y eliminar espacios y comillas adicionales
    pdf_files = [f.strip().strip('"').strip("'") for f in pdf_files_input.split(",")]
    return pdf_files

def add_new_subject(subject_name, folder_path=None, pdf_files=None):
    """
    Añade una nueva asignatura al sistema o actualiza los archivos de una asignatura existente.
    
    Args:
        subject_name (str): Nombre de la nueva asignatura.
        folder_path (str, optional): Ruta de la carpeta con archivos PDF.
        pdf_files (list, optional): Lista de archivos PDF individuales.
    """
    # Paso 1: Crear la carpeta para la nueva asignatura en data/
    subject_data_path = os.path.join(DATA_DIR, subject_name)
    if not os.path.exists(subject_data_path):
        os.makedirs(subject_data_path)
        print(f"Carpeta creada: {subject_data_path}")
    else:
        print(f"La carpeta ya existe: {subject_data_path}")

    # Paso 2: Copiar archivos PDF
    if folder_path:
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(".pdf"):
                    src_file = os.path.join(folder_path, file_name)
                    dest_file = os.path.join(subject_data_path, file_name)
                    shutil.copy(src_file, dest_file)
                    print(f"Archivo copiado: {file_name} -> {subject_data_path}")
        else:
            print(f"La carpeta no existe: {folder_path}")
    elif pdf_files:
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                file_name = os.path.basename(pdf_file)
                dest_file = os.path.join(subject_data_path, file_name)
                shutil.copy(pdf_file, dest_file)
                print(f"Archivo copiado: {file_name} -> {subject_data_path}")
            else:
                print(f"Archivo no encontrado: {pdf_file}")
    else:
        print("No se proporcionaron archivos ni carpeta. Solo se actualizará el HTML.")

    # Paso 3: Poblar la base de datos Chroma
    try:
        subprocess.run(["python3", "populate_database.py"], check=True)
        print("Base de datos Chroma poblada correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar populate_database.py: {e}")

    # Paso 4: Actualizar index.html con el formato correcto (incluyendo íconos)
    update_index_html(subject_name)

def update_index_html(subject_name):
    """
    Actualiza el archivo index.html para incluir la nueva asignatura con su ícono correspondiente.
    """
    # Obtener el ícono del mapeo o usar uno por defecto
    subject_key = subject_name.lower()
    icon = ICON_MAPPING.get(subject_key, "📄")  # Ícono por defecto si no está en el mapeo

    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Verificar si la asignatura ya existe
    subject_exists = any(f'data-subject="{subject_key}"' in line for line in lines)

    if subject_exists:
        print(f"La asignatura '{subject_name}' ya existe en index.html. No se realizaron cambios.")
        return

    # Generar la nueva línea con ícono
    new_line = f'        <li class="chat-item" data-subject="{subject_key}">\n' \
               f'          <span class="subject-icon">{icon}</span> {subject_name}\n' \
               f'        </li>\n'

    # Insertar la nueva línea antes de </ul>
    updated_lines = []
    added = False
    for line in lines:
        if "</ul>" in line and not added:
            updated_lines.append(new_line)
            added = True
        updated_lines.append(line)

    # Guardar el archivo actualizado
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)
    print(f"Archivo index.html actualizado para incluir: {subject_name} con ícono {icon}")

if __name__ == "__main__":
    # Ejemplo de uso
    subject_name = input("Introduce el nombre de la nueva asignatura: ")
    folder_path = input("Introduce la ruta de la carpeta con los archivos PDF (deja en blanco si no aplica): ").strip()
    pdf_files_input = input("Introduce las rutas de los archivos PDF separadas por comas (deja en blanco si no aplica): ").strip()

    # Procesar las entradas
    pdf_files = process_pdf_files(pdf_files_input)

    # Llamar a la función principal
    add_new_subject(subject_name, folder_path=folder_path or None, pdf_files=pdf_files)