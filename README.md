# 🦷 LoReyDent - Dental Practice Management System

LoReyDent es un sistema integral de gestión para consultorios dentales, diseñado para ser moderno, rápido y fácil de usar desde cualquier dispositivo. Permite llevar un control preciso de pacientes, agendar citas de forma visual y gestionar los pagos de los tratamientos.

## 🚀 Características Principales

*   **Gestión de Pacientes**: CRUD completo con historial clínico y notas.
*   **Agenda Visual**: Cronograma interactivo para la gestión de citas (Pendiente, Atendido, Cancelado).
*   **Módulo de Pagos**: Registro de ingresos, métodos de pago y seguimiento financiero.
*   **Autenticación Segura**: Sistema de login basado en JWT (JSON Web Tokens).
*   **Diseño Premium**: Interfaz clínica limpia, responsive y con modo claro optimizado.

## 🛠️ Stack Tecnológico

*   **Backend**: FastAPI (Python 3.11) + SQLAlchemy.
*   **Frontend**: Svelte 5 + Vite + Tailwind CSS v4.
*   **Base de Datos**: SQLite (almacenada localmente para portabilidad).
*   **Contenedores**: Docker & Docker Compose.

---

## 💻 Desarrollo y Ejecución

### Opción A: Usando Docker (Recomendado)

La forma más rápida de iniciar es usando Docker Compose, ya que configura automáticamente el backend, el frontend y la base de datos.

1.  **Construir e iniciar los servicios**:
    ```bash
    docker compose up --build -d
    ```
2.  **Inicializar la base de datos con un usuario administrador**:
    ```bash
    docker compose exec backend python seed.py
    ```
    *   **Usuario**: `admin`
    *   **Contraseña**: `admin123`

3.  **Acceso**:
    *   Frontend: `http://localhost:3011`
    *   API / Swagger: `http://localhost:3010/docs`

### Opción B: Ejecución Local (Sin Docker)

Si deseas desarrollar sin contenedores, sigue estos pasos:

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py  # Solo la primera vez
uvicorn main:app --reload --port 3010
```

#### Frontend
```bash
cd frontend
npm install
npm run dev -- --port 3011
```

---

## 🌐 Despliegue a Producción

Para llevar LoReyDent a producción, considera los siguientes puntos:

1.  **Seguridad de JWT**: Cambia la `SECRET_KEY` en el archivo `backend/auth.py` o pásala como variable de entorno.
2.  **Configuración de CORS**: En `backend/main.py`, ajusta `allow_origins` para permitir solo el dominio donde alojarás el sistema.
3.  **Persistencia de Datos**: Al usar el contenedor de Docker actual, la base de datos se guarda en `backend/data/loreydent.db`. Se recomienda configurar un volumen en `docker-compose.yml` para asegurar que los datos no se pierdan al borrar el contenedor.

    ```yaml
    volumes:
      - ./backend/data:/app/data
    ```
4.  **Servidor Web**: Para producción, se recomienda usar un proxy inverso como **Nginx** o **Caddy** para servir el frontend y gestionar certificados SSL (HTTPS).

## 📄 Licencia

Este proyecto ha sido desarrollado como una solución personalizada para la gestión dental profesional.

---
© 2026 LoReyDent - Gestión Dental Profesional.
