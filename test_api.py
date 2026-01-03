import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Clé API manquante.")
else:
    client = genai.Client(api_key=api_key)
    
    try:
        # On utilise le tout nouveau Gemini 3 Flash
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents="Bonjour ! Confirme-moi que tu es bien opérationnel pour analyser des vidéos."
        )
        print("✅ TEST RÉUSSI !")
        print(f"Réponse de Gemini 3 : {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur persistante : {e}")