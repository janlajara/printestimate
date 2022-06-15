# VUE
FROM node:14-slim as frontend
WORKDIR /frontend

# Install dependencies
COPY ./frontend/package*.json ./
RUN npm install

# Copy project
COPY ./frontend .
RUN npm run build



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