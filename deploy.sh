#!/bin/bash

# --- Script de Despliegue Automático para LoReyDent ---
# Este script optimiza el proceso de actualización en el servidor VPS.

echo "🚀 Iniciando proceso de despliegue..."

# 1. Asegurar que estamos en el directorio correcto
# CD_PATH=$(dirname "$0")
# cd "$CD_PATH"

# 2. Descargar últimos cambios (Suele usarse si usas Git)
# echo "📥 Obteniendo cambios de Git..."
# git pull origin main

# 3. Detener contenedores actuales para liberar RAM
echo "⏹️ Deteniendo contenedores para liberar recursos..."
docker compose down

# 4. Construir e iniciar en segundo plano
echo "🛠️ Construyendo y levantando servicios..."
docker compose up --build -d

# 5. Limpiar imágenes huérfanas o antiguas para ahorrar espacio (Crucial en VPS de 2GB)
echo "🧹 Limpiando imágenes antiguas y caché..."
docker image prune -f

# 6. Esperar a que el backend esté listo
echo "⏳ Esperando a que el backend inicie..."
sleep 5

# 7. Ejecutar semilla si es necesario (Opcional, descomentar si se desea resetear)
# echo "🌱 Ejecutando base de datos inicial..."
# docker compose exec backend python seed.py

# 8. Verificar estado de los contenedores
echo "✅ Estado de los servicios:"
docker compose ps

echo "🎉 ¡Despliegue completado con éxito!"
echo "Accede a: https://loreycontrol.irisvisual.com"
