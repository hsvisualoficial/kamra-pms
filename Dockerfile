# Stage 1: Build frontend
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package.json ./
COPY frontend/package*.json ./frontend/

WORKDIR /app/frontend
RUN npm ci || npm install

WORKDIR /app
COPY . .

WORKDIR /app/frontend
ENV VITE_BASE_PATH="/"
ENV VITE_ROUTER_BASENAME="/"
RUN npm run build

# Stage 2: Runner with Nginx
FROM nginx:alpine

# Custom Nginx config for SPA routing and API proxy on port 4000
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts to Nginx web root
COPY --from=builder /app/kamra/public/frontend /usr/share/nginx/html

EXPOSE 4000

CMD ["nginx", "-g", "daemon off;"]
