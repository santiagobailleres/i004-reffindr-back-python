FROM python:3.9.13-slim as base

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Evita que Python almacene en búfer stdout y stderr para asegurar que los logs
# se escriban directamente en tiempo real, incluso si la aplicación falla
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Crea un usuario no privilegiado para ejecutar la aplicación
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copia el archivo de dependencias e instala las librerías necesarias
# Usa un caché de pip para acelerar instalaciones en futuras construcciones
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de la aplicación al contenedor
COPY . .

# Elimina archivos innecesarios para mantener el contenedor más liviano
RUN rm -f requirements.txt

# Cambia al usuario no privilegiado para ejecutar la aplicación
USER appuser

# Exponer el puerto en el que escucha la aplicación
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación
CMD ["gunicorn", "app:app", "--bind=0.0.0.0:8000", "--workers=4"]
