FROM python:3.11-slim

# Dependencias básicas
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /workspace

# Actualizar pip
RUN pip install --upgrade pip