# Utilise une image Python légère
FROM python:3.11-slim

# Installe les dépendances système nécessaires (pour yt-dlp)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Définit le dossier de travail
WORKDIR /app

# Copie le fichier des dépendances
COPY requirements.txt .

# Installe les bibliothèques Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du code
COPY . .

# Expose le port par défaut de Streamlit
EXPOSE 7860

# Commande pour lancer l'application sur Hugging Face
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]