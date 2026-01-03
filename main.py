from youtube_utils import extraire_id_youtube, obtenir_transcription_ytdlp
from analyseur_llm import analyser_transcription

def main():
    url = input("Entrez l'URL de la vidéo YouTube : ")
    
    if not url.strip():
        print("URL invalide.")
        return
        
    try:
        # Extraire l'ID de la vidéo
        video_id = extraire_id_youtube(url)
        print(f"ID de la vidéo : {video_id}")
        
        # Récupérer la transcription
        transcription = obtenir_transcription_ytdlp(url)
        print("Transcription obtenue avec succès!")
        if not transcription:
            print("Impossible d'obtenir la transcription.")
            return

        # Analyse de la transcription par le LLM (GEMINI 3)
        analyse = analyser_transcription(transcription)

        print("\nAnalyse LLM :")
        print(analyse)
        
        # Sauvegarde et affichage
        nom_fichier = f"analyse_video_{video_id}.md"
        with open(nom_fichier, "w", encoding="utf-8") as f:
            f.write(analyse)
        print(f"\nAnalyse sauvegardée dans {nom_fichier}")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()