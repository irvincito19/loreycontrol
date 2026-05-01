#!/bin/bash

# --- Script de Despliegue Automático para LoReyDent ---
# Este script optimiza el proceso de actualización en el servidor VPS.

echo "🚀 Iniciando proceso de despliegue (MODO LIMPIEZA TOTAL)..."

# 1. Detener contenedores y ELIMINAR VOLÚMENES (Borra la base de datos para resetearla)
# ATENCIÓN: Solo usar -v en fase de pruebas o si se desea borrar todo.
echo "⏹️ Deteniendo contenedores y limpiando volúmenes..."
docker compose down -v

# 2. Eliminar imágenes específicas para asegurar reconstrucción total
echo "🗑️ Eliminando imágenes antiguas..."
docker rmi loreydent-backend loreydent-frontend || true

# 3. Construir e iniciar en segundo plano
echo "🛠️ Construyendo y levantando servicios..."
docker compose up --build -d

# 4. Limpiar caché residual de Docker
echo "🧹 Limpiando caché..."
docker image prune -f

# 5. Esperar a que el backend y MySQL estén listos
echo "⏳ Esperando a que el backend y la base de datos inicien (20s)..."
sleep 20

# 6. Ejecutar semilla para crear el administrador inicial (con reintentos)
echo "🌱 Inicializando base de datos con el administrador..."
for i in {1..5}; do
    docker compose exec backend python seed.py && break
    echo "⚠️ Intento $i fallido, reintentando en 5s..."
    sleep 5
done

# 7. Verificar estado de los contenedores
echo "✅ Estado de los servicios:"
docker compose ps

echo "🎉 ¡Despliegue y reseteo completado con éxito!"
echo "Accede localmente a: http://localhost:3011"
echo "Producción: https://loreycontrol.irisvisual.com"
