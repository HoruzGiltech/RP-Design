FROM python:3.14-slim

# No crear archivos .pyc y mostrar los logs al momento
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Las dependencias se copian primero: así Docker no las reinstala
# cada vez que cambia el código.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Arranque de producción (Railway usa la imagen tal cual):
#   1. aplica las migraciones pendientes,
#   2. reúne los archivos estáticos del panel para que Whitenoise los sirva,
#   3. arranca gunicorn en el puerto que indique la plataforma (PORT).
# --timeout 120: subir un video de 50 MB tarda más que los 30 s por defecto.
# En local este comando no se usa: docker-compose.yml pone el servidor de desarrollo.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"]
