# ---------- Etapa 1: compilar la app con Node ----------
FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci                # instala EXACTAMENTE lo que dice package-lock.json

COPY . .
RUN npm run build         # revisa los tipos (tsc) y genera archivos estáticos en /app/dist

# ---------- Etapa 2: servir los archivos con Nginx ----------
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80