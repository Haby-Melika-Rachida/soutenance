# ═══════════════════════════════════════════════════════════════
# Image applicative partagée : web (Gunicorn) + worker (Celery)
# La commande de démarrage est définie dans docker-compose.yml
# ═══════════════════════════════════════════════════════════════
FROM python:3.11-slim

# Métadonnées
LABEL project="rapprochement-mb-cbs-pi"
LABEL maintainer="YERE Haby Melika Rachida — LICELI Technologies"

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail
WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    # psycopg2 nécessite libpq
    libpq-dev \
    gcc \
    # Nettoyage cache apt pour réduire la taille de l'image
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python en premier
# (layer Docker mis en cache tant que requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code source de l'application
COPY . .

# Collecte des fichiers statiques Django
RUN python manage.py collectstatic --noinput --settings=reconciliation_project.settings.production || true

# Exposer le port Gunicorn (utilisé uniquement par le conteneur web)
EXPOSE 8000

# Commande par défaut : démarrage web (Gunicorn)
# Le conteneur worker override cette commande dans docker-compose.yml
CMD ["gunicorn", "reconciliation_project.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
