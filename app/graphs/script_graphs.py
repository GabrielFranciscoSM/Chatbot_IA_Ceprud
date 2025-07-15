import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calmap
from matplotlib.ticker import MaxNLocator
from IPython.display import display
import numpy as np
import os

# Cargar el archivo CSV
df = pd.read_csv("logs/chat_logs.csv")

# Convertir las columnas de fecha y hora a datetime
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])

# Función para clasificar el tipo de usuario
def classify_user(user):
    if pd.isna(user):  # Manejar valores nulos (NaN)
        return "Anónimo"
    elif user.endswith("@correo.ugr.es"):
        return "UGR"
    else:
        return "Otros"

# Aplicar la función para clasificar usuarios
df['user_type'] = df['user'].apply(classify_user)

# Mostrar un resumen del DataFrame
print(df.head())

# -----------------------------
# 1. Tabla: Uso de usuarios por tipo
# -----------------------------
user_type_counts = df['user_type'].value_counts()

# Formatear la tabla con estilo
styled_table = user_type_counts.to_frame(name="Mensajes").style \
    .background_gradient(cmap="Blues") \
    .set_caption("Uso de usuarios por tipo") \
    .format("{:,}")

# Mostrar la tabla
display(styled_table)

# Gráfico: Barras para tipos de usuario
plt.figure(figsize=(8, 6))
sns.barplot(x=user_type_counts.index, y=user_type_counts.values, palette="Blues_d")
plt.title("Uso de usuarios por tipo", fontsize=16, fontweight="bold")
plt.xlabel("Tipo de usuario", fontsize=12)
plt.ylabel("Número de mensajes", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig('graphs/users.png')
plt.close()

# -----------------------------
# 2. Gráfico: Asignaturas más consultadas
# -----------------------------
subject_counts = df['subject'].value_counts()

# Formatear la tabla con estilo
styled_subjects = subject_counts.to_frame(name="Mensajes").style \
    .background_gradient(cmap="Greens") \
    .set_caption("Asignaturas más consultadas") \
    .format("{:,}")

# Mostrar la tabla
display(styled_subjects)

# Gráfico: Barras para asignaturas
plt.figure(figsize=(10, 6))
sns.barplot(x=subject_counts.index, y=subject_counts.values, palette="Greens_d")
plt.title("Asignaturas más consultadas", fontsize=16, fontweight="bold")
plt.xlabel("Asignatura", fontsize=12)
plt.ylabel("Número de mensajes", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig('graphs/subjects.png')
plt.close()

# -----------------------------
# 3. Gráfico: Hora del día con más actividad
# -----------------------------
# Extraer la hora del día
df['hour'] = df['datetime'].dt.hour

# Contar mensajes por hora
hourly_counts = df['hour'].value_counts().sort_index()

# Crear datos para el gráfico polar
hours = hourly_counts.index
activity = hourly_counts.values

# Convertir horas a radianes para el gráfico polar
theta = 2 * np.pi * hours / 24  # Convertir horas a ángulos (0-2π)
width = 2 * np.pi / 24  # Ancho de cada segmento

# Crear el gráfico polar
plt.figure(figsize=(10, 10))
ax = plt.subplot(111, projection='polar')

# Dibujar las barras circulares
bars = ax.bar(theta, activity, width=width, color=plt.cm.YlOrRd(activity / max(activity)), edgecolor='black', alpha=0.8)

# Añadir etiquetas de horas alrededor del círculo
ax.set_xticks(np.linspace(0, 2 * np.pi, 24, endpoint=False))  # Posiciones de las horas
ax.set_xticklabels([f"{h:02d}:00" for h in range(24)])  # Etiquetas de las horas
ax.tick_params(axis='x', labelsize=10)  # Tamaño de las etiquetas

# Personalizar el diseño
ax.set_theta_zero_location('N')  # Hacer que el "0" esté arriba (como un reloj)
ax.set_theta_direction(-1)  # Girar en sentido horario (como un reloj)
ax.set_rlabel_position(-90)  # Mover las etiquetas radiales hacia abajo
ax.set_title("Actividad por hora del día (formato de reloj)", fontsize=16, fontweight="bold", pad=20)

# Añadir una leyenda de color
sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(vmin=0, vmax=max(activity)))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.1, orientation='horizontal')
cbar.set_label("Número de mensajes", fontsize=12)

# Guardar el gráfico
plt.tight_layout()
plt.savefig('graphs/hours.png')
plt.close()

# -----------------------------
# 4. Gráfico: Actividad diaria (calendario)
# -----------------------------
daily_counts = df.groupby(df['datetime'].dt.date).size()
all_dates = pd.date_range(start=df['datetime'].min().date(), end=df['datetime'].max().date())
daily_counts = daily_counts.reindex(all_dates, fill_value=0)

# Calendario heatmap
plt.figure(figsize=(12, 8))
calmap.yearplot(daily_counts, year=2025, cmap='YlGn', fillcolor='lightgray', daylabels='MTWTFSS', dayticks=[0, 1, 2, 3, 4, 5, 6])
plt.title("Actividad diaria en 2025", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig('graphs/calendar.png')
plt.close()

# -----------------------------
# 5. Gráfico circular: Distribución de temas por asignatura
# -----------------------------
def plot_topic_pie_chart(df):
    """
    Genera un gráfico circular para cada asignatura que muestra la distribución
    de los archivos más utilizados.
    """
    for subject in df['subject'].unique():
        # Filtrar el DataFrame por asignatura
        subject_df = df[df['subject'] == subject]
        sources = subject_df['source'].dropna().str.split(',').explode()

        def extract_filename(source):
            if not source:
                return None
            filename_with_path = source.split(":")[0]
            filename = filename_with_path.split("\\")[-1].replace(".pdf", "")
            return filename

        clean_sources = sources.apply(extract_filename)
        source_counts = clean_sources.value_counts()

        # Crear una subcarpeta para la asignatura si no existe
        subject_folder = f"graphs/{subject.lower()}"
        os.makedirs(subject_folder, exist_ok=True)

        # Generar el gráfico circular
        plt.figure(figsize=(10, 10))  # Aumentar el tamaño del gráfico
        plt.pie(
            source_counts,
            labels=source_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("Blues"),
            textprops={'fontsize': 10}  # Aumentar el tamaño de las etiquetas
        )
        plt.title(f"Distribución de temas en {subject}", fontsize=16, fontweight="bold")
        plt.axis('equal')  # Asegura que el gráfico sea un círculo perfecto

        # Guardar el gráfico como un archivo PNG en la subcarpeta de la asignatura
        graph_filename = f"{subject_folder}/distribucion_temas_pie.png"
        plt.savefig(graph_filename, bbox_inches='tight')  # Ajustar el recorte del gráfico
        plt.close()

        print(f"Gráfico guardado: {graph_filename}")

# Llamar a la función para generar los gráficos circulares
plot_topic_pie_chart(df)