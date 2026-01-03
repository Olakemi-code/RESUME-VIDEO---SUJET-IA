import os
from dotenv import load_dotenv
from google import genai

# Charger les variables du fichier .env  contenant la clé api
load_dotenv()

# Récupérer la clé api
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("La clé API GEMINI est introuvable dans le fichier .env")

client = genai.Client(api_key=API_KEY)

print("Initialisation du client LLM terminée")

def analyser_transcription(transcription: str, langue: str = "français", format_style: str = "Rapport détaillé") -> str:

    texte_limite = transcription[:50000]

    if format_style == "Résumé court":
        consigne_style = "Sois très synthétique, utilise des puces et limite-toi à l'essentiel (max 300 mots)."
    else:
        consigne_style = "Sois exhaustif, développe les points techniques et fournis une analyse approfondie."

    prompt = f"""
    Tu es un assistant de recherche spécialisé en Intelligence Artificielle.
    A partir de la transcription suivante issue d'une vidéo YouTube technique sur l'IA, 
    produis une analyse structurée en Markdown avec les sections suivantes :
    * Concepts IA clés abordés
    * Outils / Librairies mentionnés
    * Applications ou Cas d'usage
    * Résumé technique

    IMPORTANT /
    - Rédige en {langue}
    - Style: {consigne_style}
    - Respecte strictement le format demandé sans ajouter de titres supplémentaires
    - Ne commence jamais par "Voici" ou "Voici une analyse"
    - Réponds uniquement avec le contenu demandé, sans message introductif
    - Ne pas ajouter de section "Résumé" ou "Conclusion" supplémentaires
    - Ne pas inclure de préambule ou de note explicative

    Ton analyse doit être concise, très claire, professionnelle et facile à lire.
    
    Transcription:
    {texte_limite}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erreur lors de l'analyse LLM : {str(e)}"