# VUE
FROM node:14-slim as frontend
WORKDIR /frontend

# Install dependencies
COPY ./frontend/package*.json ./
RUN npm install

# Copy project
COPY ./frontend .
RUN npm run build


# NGINX
FROM nginx
COPY --from=frontend /frontend/dist /usr/share/nginx/html