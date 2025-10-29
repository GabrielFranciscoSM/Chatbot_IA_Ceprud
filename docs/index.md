---
layout: default
title: Documentación
nav_order: 2
has_children: true
permalink: /docs
---

# Documentación Completa

Bienvenido a la documentación completa del **Chatbot IA CEPRUD**. Aquí encontrarás toda la información necesaria para instalar, configurar, desarrollar y mantener el sistema.

## 📚 Guías por Audiencia

### Para Nuevos Usuarios
{: .text-blue-300 }

Si es tu primera vez con el proyecto, te recomendamos seguir este orden:

1. [Visión General del Proyecto](project-overview) - Contexto y objetivos
2. [Instalación](installation) - Configuración inicial paso a paso
3. [Guía de Usuario](../user-guide) - Cómo usar el sistema

### Para Desarrolladores
{: .text-green-300 }

Si vas a contribuir al desarrollo del proyecto:

1. [Arquitectura del Sistema](architecture) - Diseño técnico detallado
2. [Guía de Desarrollo](development) - Estándares y prácticas
3. [API Reference](api) - Documentación de endpoints
4. [Testing](testing) - Estrategias de pruebas

### Para Administradores
{: .text-purple-300 }

Si vas a desplegar y mantener el sistema:

1. [Instalación Completa](installation) - Deployment en producción
2. [Integración LTI](lti-integration) - Configuración con Moodle
3. [Monitoreo](monitoring) - Métricas y observabilidad
4. [MongoDB Integration](mongodb-integration) - Gestión de base de datos

## 📖 Índice Completo de Documentación

### Fundamentos
- [**Visión General del Proyecto**](project-overview) - Contexto educativo, objetivos y metodología
- [**Arquitectura del Sistema**](architecture) - Diseño técnico, patrones y decisiones
- [**Diagramas de Arquitectura**](architecture-diagrams) - Visualizaciones del sistema

### Instalación y Configuración
- [**Guía de Instalación**](installation) - Setup completo paso a paso
- [**Configuración de Desarrollo**](development) - Entorno de desarrollo local

### Integraciones
- [**Integración LTI 1.3**](lti-integration) - Conexión con Moodle
- [**Autenticación**](authentication-implementation) - Sistema de autenticación completo
- [**MongoDB Integration**](mongodb-integration) - Base de datos de usuarios

### Desarrollo
- [**Guía de Desarrollo**](development) - Estándares, prácticas y contribuciones
- [**API Reference**](api) - Documentación completa de endpoints REST
- [**Testing**](testing) - Estrategias de pruebas y calidad

### Operaciones
- [**Monitoreo y Métricas**](monitoring) - Langfuse y observabilidad
- [**Guía Rápida de Autenticación**](auth-quick-reference) - Referencia rápida

## 🔗 Enlaces Rápidos

| Necesito... | Ve a... |
|-------------|---------|
| Instalar el sistema | [Instalación](installation) |
| Conectar con Moodle | [Integración LTI](lti-integration) |
| Crear un nuevo endpoint | [API Reference](api) + [Desarrollo](development) |
| Añadir una asignatura | [Desarrollo](development#añadir-asignatura) |
| Ver métricas del sistema | [Monitoreo](monitoring) |
| Ejecutar tests | [Testing](testing) |
| Contribuir código | [Desarrollo](development#contribuir) |

## 🎯 Casos de Uso Comunes

### Instalación Rápida para Desarrollo

```bash
# 1. Clonar y configurar
git clone https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud.git
cd Chatbot_IA_Ceprud
cp .env.example .env

# 2. Editar .env con tus credenciales
nano .env

# 3. Levantar servicios
podman-compose -f docker-compose-full.yml up -d
```

[Ver guía completa →](installation)

### Integración con Moodle

```bash
# 1. Configurar variables de entorno LTI
MOODLE_ISSUER="https://tu-moodle.com"
MOODLE_CLIENT_ID="tu_client_id"
CHATBOT_BASE_URL="https://tu-dominio.com"

# 2. Configurar External Tool en Moodle
# 3. Añadir actividad en curso
```

[Ver guía completa →](lti-integration)

### Añadir Nueva Asignatura

```bash
# 1. Preparar documentos en rag-service/data/
# 2. Ejecutar población de base vectorial
curl -X POST "http://localhost:8082/populate" \
  -H "Content-Type: application/json" \
  -d '{"subject": "nombre_asignatura"}'
```

[Ver guía completa →](development#añadir-asignatura)

## 💡 Consejos

{: .note }
> **Nuevo en el proyecto?** Empieza por la [Visión General](project-overview) para entender el contexto y objetivos.

{: .important }
> **Vas a hacer deployment?** Lee completamente la [Guía de Instalación](installation) antes de comenzar.

{: .warning }
> **Integración con Moodle?** Necesitas HTTPS obligatoriamente. Ver [Integración LTI](lti-integration#https-para-produccion).

## 🆘 Soporte

¿No encuentras lo que buscas? Tienes varias opciones:

- 📖 Usa la **barra de búsqueda** en la parte superior
- 💬 Abre una [Discussion en GitHub](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/discussions)
- 🐛 Reporta un bug en [Issues](https://github.com/GabrielFranciscoSM/Chatbot_IA_Ceprud/issues)
- 📧 Contacta a los desarrolladores

## 🔄 Actualizaciones

Esta documentación se actualiza continuamente. Última actualización: **Octubre 2025**

---

<div class="text-center mt-8">
  <p class="fs-5">
    <strong>¿Por dónde empezar?</strong>
  </p>
  <a href="project-overview" class="btn btn-outline">Visión General</a>
  <a href="installation" class="btn btn-primary">Instalación</a>
  <a href="development" class="btn btn-outline">Desarrollo</a>
</div>
