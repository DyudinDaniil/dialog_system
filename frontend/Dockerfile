# Этап 1: сборка React (Vite)
FROM node:18 AS build
WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . .
ARG REACT_APP_API_BASE
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE}
RUN npm run build

# Этап 2: Nginx
FROM nginx:1.23-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf