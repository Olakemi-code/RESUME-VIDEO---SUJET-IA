import streamlit as st
from youtube_utils import extraire_id_youtube, obtenir_transcription_ytdlp
from analyseur_llm import analyser_transcription

# Configuration de la page
st.set_page_config(page_title="RESUME VIDEO IA", page_icon="🤖", layout="wide")

st.title(" 🎥Résumé Vidéo IA")

# Zone de saisie
url_video = st.text_input("🔗 URL de la vidéo YouTube :", placeholder="https://www.youtube.com/watch?v=...")

if url_video:
    try:
        video_id = extraire_id_youtube(url_video)
        # --- AJOUT DU LECTEUR VIDÉO ---
        st.video(f"https://www.youtube.com/watch?v={video_id}")
        # ------------------------------
    except:
        st.error("URL non valide")

with st.sidebar:
    st.title("Configuration")
    langue_choisie = st.selectbox(
        "Langue :",
        ["Français", "Anglais", "Espagnol", "Allemand"]
    )
    
    # NOUVEAU : Choix du format
    format_choisi = st.radio(
        "Format de l'analyse :",
        ["Résumé court", "Rapport détaillé"],
        index=1
    )
    
    st.divider()
    st.info(f"Analyse en **{langue_choisie}** au format **{format_choisi}**.")

if st.button("Lancer l'analyse", type="primary"):
    if not url_video:
        st.error("Veuillez entrer une URL valide.")
    else:
        try:
            with st.status("Traitement en cours...", expanded=True) as status:
                video_id = extraire_id_youtube(url_video)
                
                st.write("Récupération de la transcription...")
                texte = obtenir_transcription_ytdlp(video_id)
                
                if texte:
                    st.write(f"Analyse par l'IA en cours ({langue_choisie}, {format_choisi})...")
                    
                    # CORRECTION : On passe les variables récupérées dans la sidebar
                    compte_rendu = analyser_transcription(
                        texte, 
                        langue=langue_choisie, 
                        format_style=format_choisi
                    )
                    
                    status.update(label="Analyse terminée !", state="complete", expanded=False)

                    # --- MISE EN PAGE DES RÉSULTATS ---
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader(f"📝 Rapport d'Analyse ({langue_choisie})")
                        st.markdown(compte_rendu)
                    
                    with col2:
                        st.subheader("⚙️ Options")
                        st.download_button(
                            label="📥 Télécharger (.md)",
                            data=compte_rendu,
                            file_name=f"analyse_{video_id}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                        if st.button("Effacer les résultats", use_container_width=True):
                            st.rerun()
                    
                else:
                    st.error("Transcription introuvable.")
        except Exception as e:
            st.error(f"Erreur : {e}")