# Chargement des packages nécessaires : os et load_dotenv 
# servent à protéger la clé API utilisée pour le projet. La 
# clé sera ainsi récupérée dans le fichier caché .env. 

import os
from dotenv import load_dotenv
from google import genai

# Charger les variables du fichier .env  contenant la clé api :
load_dotenv()

# Récupérer la clé api "GEMINI_API_KEY" depuis le fichier .env :
API_KEY = os.getenv("GEMINI_API_KEY")

# Si la clé n'est pas récupérée, une erreur s'affiche car sans la 
# clé, l'appel au LLM ne peut pas fonctionner.
if not API_KEY:
    raise ValueError("La clé API GEMINI est introuvable dans le fichier .env")

# On connecte officiellement le client LLM avec la clé API :
client = genai.Client(api_key=API_KEY)

print("Initialisation du client LLM terminée")
# Le client LL est ainsi initialisé et peut faire son boulot.

# Cette fonction analyse la transcription fournie en paramètre, en prenant en compte 
# la langue et le format de sortie choisis par l'utilisateur.
def analyser_transcription(transcription: str, langue: str = "français", format_style: str = "Rapport détaillé") -> str:

    texte_limite = transcription[:50000] # par précaution afin d'éviter un dépassement de limites de mémoire

    # Choix du style :
    if format_style == "Résumé court":
        consigne_style = "Fais un résumé court et concis. Sois bref, direct et précis. Va à l'essentiel sans pour autant ne pas développer les points importants."
    else:
        consigne_style = "Donne tous les détails possibles sur la vidéo. Sois très clair, concis et détaillé. N'oublie pas de mentionner tous les points importants."

    # Prompt Engineering
    # Ici, je rédige les instructions que le client LLM effectue lorsque je lui fais appel via la clé API
    prompt = f"""
    Tu es un assistant de recherche spécialisé en Intelligence Artificielle.
    A partir de la transcription suivante issue d'une vidéo YouTube technique sur l'IA, 
    produis une analyse structurée en Markdown avec les sections suivantes :
    * Concepts IA clés abordés
    * Outils / Librairies mentionnés
    * Applications ou Cas d'usage
    * Résumé technique

    IMPORTANT :
    - Rédige en {langue}
    - Style: {consigne_style}
    - Respecte strictement le format demandé sans ajouter de titres supplémentaires
    - Ne commence jamais par "Voici" ou "Voici une analyse"
    - Réponds uniquement avec le contenu demandé, sans message introductif
    - Ne pas ajouter de section "Résumé" ou "Conclusion" supplémentaires
    - Ne pas inclure de préambule ou de note explicative
    - Termine exactement au mot avec le contenu demandé, sans phrase de clôture
    Ton analyse doit être concise, très claire, professionnelle et facile à lire.
    
    Transcription:
    {texte_limite}
    """
    
    try:
        # On appelle le modèle LLM (Gemini 3 Flash) avec le prompt généré
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except Exception as e: # gestion d'erreurs
        return f"Erreur lors de l'analyse LLM : {str(e)}"