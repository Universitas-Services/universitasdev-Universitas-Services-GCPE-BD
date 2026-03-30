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
# Instalamos las dependencias del sistema y el navegador Chromium
RUN playwright install --with-deps chromium
# Copiar el código
COPY . /app/

# Recopilar archivos estáticos (necesario para Swagger UI y WhiteNoise)
# Usamos una SECRET_KEY temporal porque Django la requiere para cualquier comando manage.py
# La key real se inyecta en runtime vía variables de entorno de Render
RUN SECRET_KEY=temp-build-key DATABASE_URL=sqlite:///tmp.db python manage.py collectstatic --noinput

# Comando de arranque para Render usando Gunicorn y auto-correr migraciones
CMD sh -c "python manage.py migrate && gunicorn contrataciones.wsgi:application --bind 0.0.0.0:$PORT"
