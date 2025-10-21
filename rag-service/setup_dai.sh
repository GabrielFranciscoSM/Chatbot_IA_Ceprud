#!/bin/bash
#
# Script genérico para configurar asignaturas en el sistema RAG
# Uso: ./setup_subject.sh <nombre_asignatura> [archivo_terminos_wikipedia.txt]
#
# Ejemplos:
#   ./setup_subject.sh DBA terminos_dba.txt
#   ./setup_subject.sh estadistica
#   ./setup_subject.sh "ingenieria_de_servidores"
#

set -e  # Salir si hay algún error

# Verificar que se proporciona el nombre de la asignatura
if [ -z "$1" ]; then
    echo "❌ Error: Debes proporcionar el nombre de la asignatura"
    echo ""
    echo "Uso: $0 <nombre_asignatura> [archivo_terminos_wikipedia.txt]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 DBA"
    echo "  $0 estadistica terminos_estadistica.txt"
    echo "  $0 'ingenieria_de_servidores'"
    exit 1
fi

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
SUBJECT_NAME="$1"
TERMINOS_FILE="$2"
DATA_DIR="data/${SUBJECT_NAME}"
RAG_URL="http://localhost:8082"

echo "🚀 Configuración de asignatura: ${SUBJECT_NAME}"
echo "=================================================="

# Paso 1: Crear directorio si no existe
echo -e "\n${BLUE}📁 Paso 1: Creando estructura de directorios${NC}"
mkdir -p "${DATA_DIR}"
echo "✅ Directorio creado: ${DATA_DIR}"

# Paso 2: Obtener guía docente
echo -e "\n${BLUE}🌐 Paso 2: Obtener Guía Docente${NC}"
echo -e "${YELLOW}⚠️  Necesitas la URL de la guía docente de ${SUBJECT_NAME}${NC}"
echo "Búscala en: https://grados.ugr.es/informatica/pages/infoacademica/guiasdocentes/"
echo ""
read -p "Introduce la URL de la guía docente (o Enter para omitir): " GUIA_URL

if [ ! -z "$GUIA_URL" ]; then
    echo "📥 Descargando guía docente..."
    python app/guia_docente_scrapper.py \
        --url "$GUIA_URL" \
        --subject "$SUBJECT_NAME" \
        --save-only \
        --output-dir "${DATA_DIR}"
    
    echo "✅ Guía docente guardada en ${DATA_DIR}/"
else
    echo "⏭️  Omitiendo guía docente"
fi

# Paso 3: Obtener artículos de Wikipedia
echo -e "\n${BLUE}📖 Paso 3: Obtener artículos de Wikipedia${NC}"

# Si se proporciona archivo de términos, usarlo
if [ ! -z "$TERMINOS_FILE" ] && [ -f "$TERMINOS_FILE" ]; then
    echo -e "${GREEN}✅ Usando términos desde: ${TERMINOS_FILE}${NC}"
    
    # Leer términos del archivo (uno por línea)
    mapfile -t terminos < "$TERMINOS_FILE"
    
    if [ ${#terminos[@]} -eq 0 ]; then
        echo -e "${RED}❌ Error: El archivo de términos está vacío${NC}"
        read -p "¿Deseas introducir términos manualmente? (s/N): " MANUAL_TERMS
    else
        echo "📋 Términos encontrados: ${#terminos[@]}"
        for i in "${!terminos[@]}"; do
            echo "   $((i+1)). ${terminos[$i]}"
        done
        
        read -p "¿Descargar estos artículos de Wikipedia? (S/n): " CONFIRM_WIKI
        
        if [[ ! "$CONFIRM_WIKI" =~ ^[Nn]$ ]]; then
            echo "📚 Descargando artículos de Wikipedia..."
            echo "💾 Los archivos se guardarán en: ${DATA_DIR}/"
            
            python app/get_wikipedia_data.py \
                --terms "${terminos[@]}" \
                --save-only \
                --output-dir "${DATA_DIR}" \
                --max-per-term 2
            
            echo "✅ Artículos de Wikipedia descargados en ${DATA_DIR}/"
        else
            echo "⏭️  Omitiendo Wikipedia"
        fi
    fi
else
    # Modo interactivo: preguntar si desea añadir Wikipedia
    if [ ! -z "$TERMINOS_FILE" ]; then
        echo -e "${YELLOW}⚠️  Archivo de términos no encontrado: ${TERMINOS_FILE}${NC}"
    fi
    
    read -p "¿Deseas añadir artículos de Wikipedia manualmente? (s/N): " ADD_WIKI
    
    if [[ "$ADD_WIKI" =~ ^[Ss]$ ]]; then
        echo ""
        echo "Introduce términos de búsqueda (uno por línea, línea vacía para terminar):"
        terminos=()
        while true; do
            read -p "Término $((${#terminos[@]} + 1)): " term
            if [ -z "$term" ]; then
                break
            fi
            terminos+=("$term")
        done
        
        if [ ${#terminos[@]} -gt 0 ]; then
            echo ""
            echo "📚 Descargando ${#terminos[@]} artículos de Wikipedia..."
            echo "💾 Los archivos se guardarán en: ${DATA_DIR}/"
            
            python app/get_wikipedia_data.py \
                --terms "${terminos[@]}" \
                --save-only \
                --output-dir "${DATA_DIR}" \
                --max-per-term 2
            
            echo "✅ Artículos de Wikipedia descargados en ${DATA_DIR}/"
        else
            echo "⏭️  No se proporcionaron términos"
        fi
    else
        echo "⏭️  Omitiendo Wikipedia"
    fi
fi

# Verificar resultado
echo -e "\n${GREEN}🎉 Descarga completada!${NC}"
echo ""
echo "📁 Archivos guardados en: ${DATA_DIR}/"
echo ""

# Contar archivos descargados
num_files=$(find "${DATA_DIR}" -type f \( -name "*.txt" -o -name "*.json" \) 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Total de archivos descargados: ${num_files}${NC}"

if [ $num_files -gt 0 ]; then
    echo ""
    echo "📄 Archivos encontrados:"
    ls -lh "${DATA_DIR}/" | grep -E '\.(txt|json)$' || true
fi

echo ""
echo -e "${YELLOW}📝 Para poblar la base de datos RAG más tarde (cuando esté activo):${NC}"
echo "   1. Asegúrate de que el RAG Service esté corriendo:"
echo "      cd .. && podman-compose -f docker-compose-full.yml up -d"
echo ""
echo "   2. Poblar la base de datos:"
echo "      python app/populate_database.py --subjects ${SUBJECT_NAME} --reset"
echo ""
echo -e "${BLUE}💡 Comandos útiles:${NC}"
echo "   • Ver archivos:           ls -lh ${DATA_DIR}/"
echo "   • Poblar base de datos:   python app/populate_database.py --subjects ${SUBJECT_NAME}"
echo "   • Verificar asignaturas:  curl ${RAG_URL}/subjects"
echo ""
echo -e "${GREEN}✨ Configuración de ${SUBJECT_NAME} completada!${NC}"
