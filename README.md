# Swimmers Atlacomulco

Aplicación web para la gestión de la escuela de natación "Swimmers Atlacomulco".

## Descripción

Esta aplicación permite administrar de forma integral las operaciones de la escuela, incluyendo:

*   **Gestión de Socios:**
    *   Registro y perfil de cada socio (nadador).
    *   Asignación de niveles y membresías.
*   **Gestión Académica:**
    *   Inscripción de socios a los horarios disponibles.
*   **Gestión de Horarios:**
    *   Creación y administración de horarios de clase, especificando días, horas, niveles y cupo.
*   **Control de Asistencia:**
    *   Registro de asistencia de los socios a sus clases.
*   **Gestión Financiera:**
    *   Registro de pagos de mensualidades y otros conceptos.
    *   Consulta de tarifas y precios.
*   **Administración:**
    *   Dashboard con vista general del sistema.
    *   Gestión de tarifas, membresías y niveles.

## Stack Tecnológico

*   **Backend:** Flask (Python)
*   **Base de Datos:** SQLAlchemy con SQLite (configurable a otras bases de datos).
*   **Frontend:** Jinja2 Templates, HTML, CSS, JavaScript.
*   **Autenticación:** Flask-Login.
*   **Migraciones de Base de Datos:** Alembic.

## Plan de Mejoras

A continuación, se presenta un plan de mejoras para futuras versiones de la aplicación, enfocado en optimizar la funcionalidad y la experiencia de usuario.

### 1. Refactorización a Blueprints

Actualmente, todas las rutas se encuentran en un único archivo, lo que dificulta el mantenimiento y la escalabilidad.

*   **Tarea:** Organizar las rutas en Blueprints de Flask, agrupando la funcionalidad por módulos (e.g., `socios`, `finanzas`, `admin`, `asistencia`).
*   **Beneficios:**
    *   Código más modular y fácil de entender.
    *   Mejora la escalabilidad del proyecto.
    *   Facilita el trabajo en equipo.

### 2. Implementación de Roles y Permisos

Mejorar el sistema de autenticación para soportar diferentes roles de usuario (e.g., Administrador, Entrenador, Recepcionista).

*   **Tarea:**
    *   Agregar un campo `rol` al modelo de `Usuario`.
    *   Crear decoradores personalizados para restringir el acceso a ciertas rutas según el rol del usuario.
*   **Beneficios:**
    *   Mayor seguridad al limitar el acceso a funcionalidades sensibles.
    *   Experiencia de usuario personalizada para cada tipo de rol.

### 3. Dashboard Interactivo

Mejorar el dashboard de administrador para ofrecer una visión más completa y útil del estado de la escuela.

*   **Tarea:**
    *   Incorporar gráficos interactivos (e.g., usando Chart.js) para visualizar métricas clave:
        *   Socios activos vs. inactivos.
        *   Ingresos por mes.
        *   Asistencia promedio por grupo.
    *   Agregar un feed de actividad reciente.
*   **Beneficios:**
    *   Facilita la toma de decisiones basada en datos.
    *   Mejora la visualización de la información.

### 4. Notificaciones Automáticas

Implementar un sistema de notificaciones para mantener informados a los socios y al personal.

*   **Tarea:**
    *   Enviar recordatorios de pago automáticos por correo electrónico.
    *   Notificar a los socios sobre cambios en los horarios.
    *   Alertar a los administradores sobre eventos importantes (e.g., cupo lleno en un horario).
*   **Beneficios:**
    *   Mejora la comunicación con los socios.
    *   Automatiza tareas manuales.

### 5. Portal del Socio

Crear un portal donde los socios (o sus padres/tutores) puedan autogestionar su información.

*   **Tarea:**
    *   Permitir a los socios ver su historial de pagos y asistencia.
    *   Posibilidad de actualizar su información de contacto.
    *   Consultar los horarios disponibles y su inscripción actual.
*   **Beneficios:**
    *   Reduce la carga de trabajo administrativo.
    *   Empodera a los socios y mejora su experiencia.

### 6. Optimización y Pruebas

*   **Tarea:**
    *   Realizar una revisión general del código para optimizar consultas a la base de datos.
    *   Implementar pruebas unitarias y de integración para asegurar la calidad y estabilidad de la aplicación.
*   **Beneficios:**
    *   Mejora el rendimiento y la fiabilidad de la aplicación.
    *   Facilita la detección de errores antes de que lleguen a producción.
