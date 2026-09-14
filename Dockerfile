# 1. Image de base légère (Le système d'exploitation)
FROM python:3.11-slim

# 2. Définition du répertoire de travail dans le conteneur
WORKDIR /app

# 3. Copie du fichier des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie de l'intégralité du code de l'API et du modèle
COPY api/ ./api/

# 5. Ouverture du port réseau pour écouter les requêtes
EXPOSE 8000

# 6. Commande de démarrage du serveur Uvicorn
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]