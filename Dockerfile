# Base de l'image Docker officielle Python 3.11 slim (allégée)
FROM python:3.11-slim

# Définit le répertoire de travail dans l'image
WORKDIR /app

# Copier seulement le fichier des dépendances pour optimiser la mise en cache Docker
COPY requirements.txt requirements.txt

# Installer les dépendances Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du projet dans l'image Docker
COPY . .

# Exposer le port utilisé par l'application Flask (ici 5000)
EXPOSE 5000

# Commande pour démarrer l'application Flask
CMD ["python", "src/main.py"]
