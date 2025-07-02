FROM python:3.11-slim

# Mise à jour et installation des outils nécessaires
RUN apt update && apt upgrade -y && apt install -y \
    hashcat \
    aircrack-ng \
    hcxtools \
    hcxdumptool \
    john \
    gcc \
    libpq-dev \
    python3-venv \
    python3-setuptools \
    python3-wheel \
    python3-build \
    wget \
    curl \
    unzip \
    opencl-headers \
    ocl-icd-opencl-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt /tmp/
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

# Création des répertoires
RUN mkdir -p /app/captures /app/results /app/wordlists /app/logs /app/templates /app/static

# Téléchargement des wordlists principales
WORKDIR /app/wordlists
RUN wget -q https://github.com/danielmiessler/SecLists/raw/master/Passwords/Leaked-Databases/rockyou.txt.tar.gz \
    && tar -xzf rockyou.txt.tar.gz \
    && rm rockyou.txt.tar.gz

# Wordlists supplémentaires
RUN wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt

# Copie de l'application
COPY app/ /app/
COPY config/ /app/config/
COPY templates/ /app/templates/

WORKDIR /app

# Permissions
RUN chmod +x /app/*.py

# Exposition du port
EXPOSE 8888

# Point d'entrée
CMD ["python3", "app.py"]