# Sistema de Gestión para Escuelas de Natación

Aplicación web interna, desarrollada con Flask, para la administración eficiente de socios, pagos y horarios en una escuela de natación.

## ✨ Características Principales

*   **Gestión de Socios:**
    *   Registro y edición de socios, incluyendo datos personales, de contacto y fotografía.
    *   Asignación de niveles (e.g., Bebé, Niño, Adulto) y membresías (e.g., Trimestral, Anual).
    *   Listado completo de socios con búsqueda y filtros.

*   **Módulo de Finanzas:**
    *   **Cobro Rápido:** Interfaz optimizada para buscar socios y registrar pagos de forma ágil.
    *   **Cálculo Automático de Precios:** El sistema sugiere montos basados en la membresía, nivel y concepto del pago (mensualidad, anualidad, etc.).
    *   **Registro de Pagos:** Guarda un historial detallado de todas las transacciones, incluyendo descuentos y método de pago.
    *   **Generación de Recibos:** Permite imprimir recibos de pago detallados.

*   **Administración y Configuración:**
    *   Gestión de tarifas, membresías y niveles a través de un panel de administración.
    *   Sistema de autenticación para proteger el acceso a la aplicación.

*   **Interfaz de Usuario Moderna:**
    *   Construida con **Tailwind CSS** y componentes de **DaisyUI** para una experiencia de usuario limpia y responsiva.
    *   Uso de JavaScript para funcionalidades dinámicas como la búsqueda de socios y el cálculo de precios en tiempo real.

## 🚀 Tecnologías Utilizadas

*   **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF.
*   **Base de Datos:** SQLite (configurable para otras bases de datos como PostgreSQL).
*   **Frontend:** HTML, Tailwind CSS, DaisyUI, JavaScript.
*   **Entorno:** Virtualenv para la gestión de dependencias.

## 🛠️ Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd <NOMBRE-DEL-DIRECTORIO>
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la base de datos:**
    *   Abre el intérprete de Flask y ejecuta los siguientes comandos para crear las tablas:
    ```bash
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```
    *   (Opcional) Para poblar la base de datos con datos de ejemplo (tarifas, niveles, etc.), puedes crear un script o hacerlo manualmente a través del panel de administración.

5.  **Ejecutar la aplicación:**
    ```bash
    flask run
    ```
    La aplicación estará disponible en `http://127.0.0.1:5000`.

## 🔮 Próximos Pasos (Roadmap)

- [ ] **Dashboard Interactivo:** Añadir gráficos para visualizar métricas clave.
- [ ] **Autenticación por Roles:** Implementar roles (Admin, Recepcionista) para restringir accesos.
- [ ] **Portal del Socio:** Permitir a los socios consultar su información y estado de cuenta.
- [ ] **Notificaciones Automáticas:** Enviar recordatorios de pago por correo electrónico.
