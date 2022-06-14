# DJANGO 
FROM python:3.8-slim-buster as backend

# Environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /backend

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .


# VUE
FROM node:14-slim as frontend
WORKDIR /frontend

COPY ./frontend/package*.json ./
RUN npm install

COPY ./frontend .
RUN npm run build


# NGINX
FROM nginx:stable-alpine as webserver
COPY --from=frontend /frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]