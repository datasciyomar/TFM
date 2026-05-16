FROM python:3.10-slim

# Evitar que Python escriba archivos .pyc y forzar logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias de sistema necesarias para compilar paquetes como scikit-survival y XGBoost
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Primero copiamos solo requirements para aprovechar la cache de Docker
COPY requirements_app.txt .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements_app.txt

# Copiar el código del proyecto
COPY . /app

# Informar que Streamlit corre en el puerto 8501
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando por defecto para iniciar la aplicación (ejecutar desde la raiz /app, para que "models" y "data" existan en el cwd)
# Aunque es posible ejecutar app.py en mvp_hct/app.py, los scripts asumen que la raiz es el directorio de invocación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
