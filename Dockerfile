# Usamos Python 3.11
FROM python:3.11-slim-bullseye

# Configuración básica de Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# INSTALAMOS DEPENDENCIAS DEL SISTEMA (CRÍTICO PARA WEASYPRINT)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install playwright
# 2. Instalamos las dependencias del sistema y el navegador Chromium
RUN playwright install --with-deps chromium
# Copiar el código
COPY . /app/
# Instalamos gunicorn si no está en tus requirements.txt
RUN pip install gunicorn

# Comando para arrancar Django usando el puerto que Google asigna ($PORT)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 contrataciones.wsgi:application