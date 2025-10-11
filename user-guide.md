---
layout: default
title: Guía de Usuario
nav_order: 3
permalink: /user-guide
---

# Guía de Usuario - Chatbot IA CEPRUD
{: .no_toc }

## Tabla de Contenidos
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 🎯 Introducción

El **Chatbot IA CEPRUD** es un asistente educativo inteligente diseñado para ayudarte con tus asignaturas de Ingeniería Informática. Esta guía te mostrará cómo usar el sistema efectivamente.

## 🚀 Inicio Rápido

### Acceso al Sistema

Hay dos formas de acceder al chatbot:

#### 1. Acceso Directo (Standalone)
{: .text-blue-300 }

Visita directamente la aplicación web:
- **URL**: `http://localhost:8090` (desarrollo) o la URL de producción proporcionada

#### 2. Acceso desde Moodle (LTI)
{: .text-green-300 }

Si tu institución ha configurado la integración LTI:
1. Entra a tu curso en Moodle
2. Busca la actividad "Chatbot CEPRUD"
3. Haz clic para lanzar el chatbot
4. El sistema te autenticará automáticamente

## 📝 Primera Configuración

### 1. Registro/Login

Si es tu primera vez usando el sistema standalone:

1. **Registrarse**:
   - Haz clic en "Registrarse"
   - Introduce tu correo electrónico UGR
   - Crea una contraseña segura
   - Completa tu nombre

2. **Iniciar Sesión**:
   - Introduce tu email y contraseña
   - Haz clic en "Iniciar Sesión"

{: .note }
> Si accedes desde Moodle, la autenticación es automática mediante LTI.

### 2. Añadir Asignaturas

Para personalizar tu experiencia, añade las asignaturas sobre las que quieres consultar:

1. **Buscar asignaturas**:
   - Usa la barra de búsqueda en el panel lateral
   - Escribe palabras clave (ej: "servidores", "metaheurísticas")

2. **Añadir a tu lista**:
   - Haz clic en cualquier asignatura de los resultados
   - Se añadirá automáticamente a "Tus Asignaturas"

3. **Eliminar asignaturas**:
   - Pasa el ratón sobre una asignatura en tu lista
   - Haz clic en el botón "×" que aparece

## 💬 Usar el Chat

### Seleccionar Asignatura

Antes de hacer preguntas:
1. Selecciona una asignatura de tu lista haciendo clic en ella
2. El nombre de la asignatura se mostrará en el encabezado del chat
3. Todas tus preguntas se contextualizarán a esa asignatura

### Hacer Preguntas

**Ejemplos de preguntas efectivas:**

✅ **Buenas preguntas:**
- "¿Qué son las metaheurísticas y para qué sirven?"
- "Explica el concepto de virtualización en servidores"
- "¿Cuáles son los temas principales del temario?"
- "¿Cómo se evalúa esta asignatura?"

❌ **Preguntas menos efectivas:**
- "Hola" (demasiado vaga)
- "Dame las respuestas del examen" (no ético)
- "¿Qué es la IA?" (sin contexto de asignatura)

### Interpretar Respuestas

El chatbot proporciona:
- **Respuesta contextualizada** basada en la guía docente
- **Referencias** a documentos fuente cuando es posible
- **Explicaciones claras** adaptadas al nivel universitario

{: .important }
> **Verificación**: Aunque el chatbot es preciso, siempre verifica información crítica con material oficial o profesores.

## 🎓 Casos de Uso Comunes

### Preparación de Exámenes
{: .text-purple-300 }

```
Usuario: "¿Cuáles son los conceptos más importantes del tema 3?"
Usuario: "Explícame la diferencia entre X y Y"
Usuario: "Dame ejemplos prácticos de Z"
```

### Entender el Temario
{: .text-blue-300 }

```
Usuario: "¿Qué temas cubre esta asignatura?"
Usuario: "¿Cuál es el objetivo de aprendizaje del tema 2?"
Usuario: "¿Qué requisitos previos necesito?"
```

### Información Administrativa
{: .text-yellow-300 }

```
Usuario: "¿Cómo se evalúa la asignatura?"
Usuario: "¿Qué porcentaje vale el proyecto final?"
Usuario: "¿Hay prácticas obligatorias?"
```

### Aclaración de Conceptos
{: .text-green-300 }

```
Usuario: "Explícame qué es un algoritmo genético de forma simple"
Usuario: "¿Puedes darme un ejemplo de aplicación real de X?"
Usuario: "No entiendo la diferencia entre A y B"
```

## ⚙️ Funciones Avanzadas

### Gestión de Sesiones

El sistema mantiene tu historial de conversaciones:
- **Automático**: Cada asignatura tiene su propio historial
- **Persistente**: Tus conversaciones se guardan automáticamente
- **Contextual**: El chatbot recuerda el contexto de la conversación

### Límites de Uso

Para garantizar un servicio equitativo:
- **Rate Limit**: 20 mensajes por minuto por defecto
- **Indicador**: El banner superior muestra tu uso actual
- **Espera**: Si alcanzas el límite, espera 1 minuto antes de continuar

### Modo LTI

Cuando accedes desde Moodle:
- **Asignatura automática**: Se selecciona según el curso de Moodle
- **Usuario automático**: Tu perfil se sincroniza con Moodle
- **Contexto del curso**: El chatbot conoce el contexto de tu curso

## 🔍 Tips para Mejores Resultados

### Formular Preguntas

1. **Sé específico**: 
   - ✅ "¿Qué es el algoritmo de recocido simulado?"
   - ❌ "Explícame el tema"

2. **Proporciona contexto**:
   - ✅ "En el contexto de metaheurísticas, ¿qué significa exploración vs explotación?"
   - ❌ "¿Qué es exploración?"

3. **Pregunta paso a paso**:
   - Si no entiendes algo, divide la pregunta en partes más simples

4. **Usa términos del curso**:
   - El chatbot conoce la terminología específica de tus asignaturas

### Uso Efectivo

- **Revisa el historial**: Tus preguntas anteriores pueden tener respuestas relacionadas
- **Experimenta**: Prueba diferentes formas de preguntar
- **Verifica**: Contrasta información importante con fuentes oficiales
- **Reporta problemas**: Si encuentras errores, repórtalos

## 🚨 Solución de Problemas

### Problemas Comunes

#### "No puedo acceder al sistema"
- Verifica que estés usando el navegador correcto (Chrome, Firefox, Edge)
- Asegúrate de estar usando la URL correcta
- Limpia el caché de tu navegador

#### "El chat no responde"
- Verifica tu conexión a Internet
- Comprueba que hayas seleccionado una asignatura
- Asegúrate de no haber alcanzado el rate limit

#### "No encuentro mi asignatura"
- Usa la barra de búsqueda con diferentes términos
- Contacta al administrador si la asignatura debería estar disponible

#### "Respuestas incorrectas o extrañas"
- Reformula tu pregunta de manera más específica
- Verifica que hayas seleccionado la asignatura correcta
- Reporta el problema incluyendo tu pregunta y la respuesta recibida

### Obtener Ayuda

Si tienes problemas que no puedes resolver:

1. **Documentación**: Consulta la [documentación completa]({{ site.baseurl }}/docs)
2. **Soporte técnico**: Contacta a tu administrador del sistema
3. **GitHub Issues**: Reporta bugs en el [repositorio](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/issues)

## 📊 Privacidad y Datos

### ¿Qué datos se guardan?

- **Mensajes del chat**: Para mejorar el servicio y proporcionar analíticas
- **Información de usuario**: Email y nombre (solo lo necesario)
- **Sesiones LTI**: Información de contexto del curso de Moodle

### ¿Cómo se usan mis datos?

- **Mejora del sistema**: Analizar patrones de uso para mejorar
- **Investigación educativa**: Estudios anónimos sobre patrones de aprendizaje
- **Nunca se comparten**: Tus datos no se comparten con terceros

{: .warning }
> **Privacidad**: No compartas información personal sensible en el chat. El sistema es seguro pero es buena práctica de seguridad.

## ✨ Mejores Prácticas

### Uso Académico Responsable

1. **Complemento, no sustituto**:
   - Usa el chatbot como apoyo al estudio
   - No sustituye asistir a clase o leer material oficial

2. **Verificación**:
   - Contrasta información crítica
   - Consulta con profesores sobre dudas importantes

3. **Aprendizaje activo**:
   - Usa el chatbot para entender, no solo para obtener respuestas
   - Formula tus propias preguntas basadas en las respuestas

4. **Ética académica**:
   - No uses el chatbot para hacer trampa en exámenes
   - Cita apropiadamente si usas información en trabajos

### Maximizar el Valor

- **Estudia regularmente**: Usa el chatbot como parte de tu rutina de estudio
- **Explora temas**: No solo preguntes sobre el temario obligatorio
- **Pregunta "por qué"**: Profundiza en los conceptos
- **Relaciona asignaturas**: Pregunta sobre conexiones entre temas

## 🎯 Próximos Pasos

Ahora que conoces el sistema:

1. **Explora**: Prueba diferentes tipos de preguntas
2. **Personaliza**: Añade todas tus asignaturas
3. **Integra**: Haz del chatbot parte de tu rutina de estudio
4. **Comparte**: Recomienda el sistema a compañeros

---

<div class="text-center mt-8">
  <p class="fs-5">
    <strong>¿Listo para empezar a estudiar con IA?</strong>
  </p>
  <a href="{{ site.baseurl }}/docs/installation" class="btn btn-primary">Instalar el Sistema</a>
  <a href="{{ site.baseurl }}/docs" class="btn btn-outline">Ver Documentación Técnica</a>
</div>
