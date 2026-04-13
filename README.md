# 🦷 LoReyDent: Sistema de Gestión Dental Profesional

**LoReyDent** es una solución integral diseñada para clínicas dentales que buscan modernizar su gestión operativa, desde la atención al paciente hasta el control financiero y el agendado automático.

---

## ✨ Características Principales

### 👨‍⚕️ Para la Clínica (Panel Administrativo)
- **Dashboard Operativo**: Resumen rápido de citas del día y estados financieros.
- **Gestión de Pacientes**: Expedientes detallados con historial de tratamientos y notas clínicas.
- **Calendario Administrativo**: Control total sobre la agenda, creación manual de citas y gestión de estados (confirmada, cancelada, completada).
- **Módulo de Pagos**: Registro de ingresos asociados a tratamientos, manteniendo un historial claro de cobros.
- **Configuración de Disponibilidad**: Herramienta flexible para definir horarios de trabajo por día de la semana, manejando automáticamente los slots para el portal público.
- **Seguridad Robusta**: Acceso restringido mediante usuarios y contraseñas con encriptación y sesiones seguras (JWT).

### 🤳 Para el Paciente (Portal Público)
- **Auto-Agendado Online**: Interfaz intuitiva para que los pacientes seleccionen el servicio y el horario que mejor les convenga.
- **Validación en Tiempo Real**: El sistema solo muestra horarios libres basados en la configuración de la clínica y las citas existentes.
- **Confirmación vía WhatsApp**: Una vez seleccionada la cita, el sistema genera automáticamente un mensaje personalizado para confirmar vía WhatsApp con un solo clic.

---

## 🚀 Guía de Despliegue en Producción (AWS Lightsail)

Esta guía detalla cómo poner en marcha el sistema en un VPS con **2GB de RAM**, optimizando el uso de recursos.

### 1️⃣ Requisitos del Sistema
Asegúrate de tener instalados los siguientes componentes en tu servidor Linux:
- **Docker** y **Docker Compose v2+**.
- **Caddy Server** (Servidor web y proxy con SSL automático).
- **Git** (Para gestionar el código).

### 2️⃣ Configuración de Red en AWS Lightsail
En el panel de control de tu instancia de Lightsail, abre los siguientes puertos en la pestaña de **Networking**:
- `80 (HTTP)`
- `443 (HTTPS)`
- `22 (SSH)`

### 3️⃣ Instalación y Configuración del Proyecto
Clona el repositorio en tu servidor (ej. en `/home/ubuntu/loreydent`) y prepara las variables de entorno:

```bash
# Crear archivo de variables de entorno
touch .env
```

Edita el archivo `.env` y agrega una clave secreta única:
```env
JWT_SECRET_KEY=TU_CLAVE_SECRETA_SUPER_LARGA_AQUI
```

### 4️⃣ Despliegue Automatizado con `deploy.sh`
Hemos incluido un script que maneja todo el proceso de actualización y mantenimiento automático:

```bash
# Dar permisos de ejecución
chmod +x deploy.sh

# Ejecutar el despliegue
./deploy.sh
```

**¿Qué hace este script?**
1. Detiene los contenedores anteriores para liberar memoria RAM.
2. Construye las nuevas imágenes (Backend y Frontend).
3. Levanta los servicios optimizados.
4. Limpia imágenes antiguas para ahorrar espacio en disco.

### 5️⃣ Inicialización de Datos (Primer Despliegue)
Solo la primera vez, ejecuta el script de "semilla" para crear el usuario administrador:
```bash
docker compose exec backend python seed.py
```
*   **Usuario**: `admin`
*   **Contraseña**: `admin123` (Cámbiala inmediatamente en el panel).

---

## 🌐 Configuración del Proxy Inverso (Caddy)

Caddy se encargará del SSL automático (HTTPS) y de dirigir el tráfico a los contenedores correctos. Edita tu `/etc/caddy/Caddyfile`:

```caddy
loreycontrol.irisvisual.com {
    # Apuntar al Frontend de LoReyDent (Puerto 3011)
    reverse_proxy localhost:3011

    # Redirigir peticiones de API al Backend (Puerto 3010)
    handle /api/* {
        reverse_proxy localhost:3010
    }

    # Optimización y Seguridad
    encode zstd gzip
    header {
        Strict-Transport-Security "max-age=31536000;"
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy no-referrer-when-downgrade
    }
}
```

Aplica los cambios en Caddy:
```bash
sudo systemctl reload caddy
```

---

## 📊 Mantenimiento y Backups
- **Base de Datos**: Se encuentra en `backend/data/loreydent.db`. Se recomienda hacer copias de seguridad de este archivo semanalmente.
- **Logs**: Puedes ver los logs del sistema con `docker compose logs -f`.

---
© 2026 **LoReyDent** - Desarrollado para gestión odontológica de alto rendimiento.
