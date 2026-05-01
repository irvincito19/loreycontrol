# Stage 1: Build
FROM node:20-slim AS build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Pasamos la URL del backend como argumento de construcción
# Por defecto usamos /api para que sea relativo al host y pase por el proxy de nginx
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve
FROM nginx:stable-alpine AS production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html

# Configuración personalizada de Nginx para SPA y proxy de API
RUN echo 'server { \
    listen 3011; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:3010/api; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 3011

CMD ["nginx", "-g", "daemon off;"]

