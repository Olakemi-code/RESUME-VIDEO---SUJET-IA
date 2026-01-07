# Chargement des bibliothèques nécessaires
import yt_dlp
import json
import re
from urllib.parse import urlparse, parse_qs

# Définir la fonction permettant d'extraire l'identifiant de la vidéo YouTube afin que l'on puisse 
# l'utiliser pour obtenir la transcription
def extraire_id_youtube(youtube_url: str) -> str:
    """Extrait l'ID d'une vidéo YouTube à partir d'une URL."""

    # Cette regex (expression régulière) gère les formats : youtu.be, youtube.com/watch, shorts, et les paramètres ?si=
    # Elle extrait les 11 caractères uniques qui identifient la vidéo
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    
    # Si une correspondance est trouvée, extraire l'ID de la vidéo
    if match:
        video_id = match.group(1)
        return video_id
    
    # Si aucune correspondance n'est trouvée, une erreur s'affiche
    raise ValueError(f"Impossible d'extraire l'ID de l'URL : {youtube_url}")


# Définir la fonction permettant d'obtenir la transcription de la vidéo YouTube identifiée
def obtenir_transcription_ytdlp(video_id: str, langues_preferees: list = None) -> str:
    """
    Utilise yt-dlp pour obtenir et extraire la transcription d'une vidéo YouTube.
    """
    # Si aucune langue préférée n'est spécifiée, utiliser le français et l'anglais par défaut
    if langues_preferees is None:
        langues_preferees = ['fr', 'en']
    
    # Afficher un message pour indiquer que la recherche de transcription est en cours
    print(f"Recherche de transcription avec yt-dlp pour la vidéo: {video_id}")
    
    # Configurer les options pour yt-dlp
    # On dit à l'outil de ne pas télécharger la vidéo, de juste récupérer les sous-titres disponibles.
    # S'il n'y a pas de sous-titres au préalable, il cherche les sous-titres générés par l'IA de Youtube.
    # On lui dit de chercher les sous-titres dans les langues spécifiées et de les télécharger.
    # Par ailleurs, on lui dit de ne pas afficher les messages d'erreur ni les avertissements.
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': langues_preferees,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    # Essayer d'obtenir la transcription
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # Extraire les informations de la vidéo sans télécharger cette dernière
            info = ydl.extract_info(video_id, download=False)
            
            # Afficher des informations de la vidéo telles que le titre et la durée
            print(f"\nInformations de la vidéo {video_id}:")
            print(f"Titre: {info.get('title', 'N/A')}")
            print(f"Durée: {info.get('duration', 'N/A')} secondes")
            
            # Si le mot 'subtitles' est présent dans les informations de la vidéo, on affiche les sous-titres manuels
            if 'subtitles' in info and info['subtitles']:
                print("Sous-titres manuels:")
                for lang, subs in info['subtitles'].items():
                    # afficher la langue et le nombre de formats disponibles
                    print(f"  - {lang}: {len(subs)} format(s)")
            
            # Si le mot 'automatic_captions' est présent dans les informations de la vidéo, on affiche les sous-titres automatiques
            if 'automatic_captions' in info and info['automatic_captions']:
                print("Sous-titres automatiques:")
                for lang, subs in info['automatic_captions'].items():
                    print(f"  - {lang}: {len(subs)} format(s)")
            
            # Si on a des sous-titres manuels pour chaque langue préférée
            # Si l'un des formats de sous-titres manuels est trouvé, on l'utilise; les sous-titres sont donc téléchargés
            # et parsés, c'est-à-dire convertis en texte lisible
            for langue in langues_preferees:
                if 'subtitles' in info and langue in info['subtitles']:
                    print(f"\nTentative d'extraction des sous-titres manuels en {langue}...")
                    for subtitle in info['subtitles'][langue]:
                        if subtitle.get('ext') in ['json3', 'vtt', 'srv3', 'srv2', 'srv1', 'ttml']:
                            try:
                                text = telecharger_et_parser_sous_titres(subtitle['url'], subtitle.get('ext'))
                                if text:
                                    print(f"✓ Transcription manuelle en {langue} trouvée")
                                    return text
                            except Exception as e:
                                print(f"Erreur avec format {subtitle.get('ext')}: {e}")
            
            # Si on a des sous-titres automatiques pour chaque langue préférée, on les utilise et on procède de la même façon que précédemment.
            for langue in langues_preferees:
                if 'automatic_captions' in info and langue in info['automatic_captions']:
                    print(f"\nTentative d'extraction des sous-titres automatiques en {langue}...")
                    for subtitle in info['automatic_captions'][langue]:
                        if subtitle.get('ext') in ['json3', 'vtt', 'srv3', 'srv2', 'srv1', 'ttml']:
                            try:
                                text = telecharger_et_parser_sous_titres(subtitle['url'], subtitle.get('ext'))
                                if text:
                                    print(f"✓ Transcription automatique en {langue} trouvée")
                                    return text
                            except Exception as e:
                                print(f"Erreur avec format {subtitle.get('ext')}: {e}")
            
            
            print("\nRecherche de n'importe quelle transcription disponible...")
            
            # Vérifier toutes les transcriptions disponibles (manuelles ou automatiques) et on les met toutes
            # dans une liste commune.
            all_subs = []
            if 'subtitles' in info:
                for lang, subs in info['subtitles'].items():
                    all_subs.extend(subs)
            if 'automatic_captions' in info:
                for lang, subs in info['automatic_captions'].items():
                    all_subs.extend(subs)
            
            # Pour chaque sous-titre trouvé, on tente de le télécharger et de le parser.
            for subtitle in all_subs:
                if subtitle.get('ext') in ['json3', 'vtt', 'srv3', 'srv2', 'srv1', 'ttml']:
                    try:
                        text = telecharger_et_parser_sous_titres(subtitle['url'], subtitle.get('ext'))
                        if text:
                            print(f"✓ Transcription trouvée (format: {subtitle.get('ext')})")
                            return text
                    except Exception as e:
                        continue
            
            print("✗ Aucune transcription téléchargeable trouvée")
            return ""
            
    except Exception as e:
        print(f"Erreur yt-dlp: {e}")
        import traceback
        traceback.print_exc()
        return ""

# Définir une fonction pour télécharger et parser les sous-titres selon leur format.
def telecharger_et_parser_sous_titres(url: str, format_type: str) -> str:
    """Télécharge et parse les sous-titres selon leur format."""
    import urllib.request
    import json
    
    try:
        # Configurer les en-têtes pour éviter les erreurs 403
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }
        
        # Faire une requête HTTP pour obtenir le contenu des sous-titres
        req = urllib.request.Request(url, headers=headers)

        # Télécharger le contenu
        response = urllib.request.urlopen(req)

        # Décoder le contenu en UTF-8
        content = response.read().decode('utf-8')
        
        print(f"  Téléchargé: {len(content)} caractères (format: {format_type})")
        
        # Parser selon le format des sous-titres
        if format_type == 'json3':
            return parser_json3(content)
        elif format_type == 'vtt':
            return parser_vtt(content)
        elif format_type == 'ttml':
            return parser_ttml(content)
        elif format_type in ['srv1', 'srv2', 'srv3']:
            return parser_srv(content)
        else:
            # Essayer de deviner le format
            return parser_generique(content)
            
    except Exception as e:
        print(f"  Erreur lors du téléchargement/parsing: {e}")
        return ""


# Définir une fonction pour parser les sous-titres au format JSON3.
def parser_json3(content: str) -> str:
    """Parse le format JSON3 de YouTube."""

    # Tente de charger le contenu JSON
    try:
        data = json.loads(content) # Charger le contenu JSON
        text_segments = [] # Liste pour stocker les segments de texte
        
        # Format JSON3 standard : si la clé 'events' existe, extraire les segments
        if 'events' in data:
            for event in data['events']:
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            text_segments.append(seg['utf8'])
        
        # Autre format possible : liste de dictionnaires avec la clé 'text'
        if not text_segments and isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'text' in item:
                    text_segments.append(item['text'])
        
        text = ' '.join(text_segments) # Joindre tous les segments de texte
        return text.replace('\n', ' ').strip() # Remplacer les sauts de ligne par des espaces
        
    except Exception as e:
        print(f"  Erreur parsing JSON3: {e}") # Afficher l'erreur
        return ""


# Définir une fonction pour parser les sous-titres au format VTT.
def parser_vtt(content: str) -> str:
    """Parse le format WebVTT."""

    # Tenter de parser le contenu VTT
    try:
        lines = content.split('\n') # Diviser le contenu en lignes
        text_segments = [] # Liste pour stocker les segments de texte
        in_cue = False # Variable pour savoir si on est dans un cue
        
        for line in lines:
            line = line.strip()
            # Ignorer les entêtes et les timestamps
            if line == '' or '-->' in line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                continue
            if line.isdigit():  # Numéro de cue
                continue
            
            text_segments.append(line) # On ajoute le segment de texte à la liste
        
        text = ' '.join(text_segments) # On joint tous les segments de texte
        return text.replace('  ', ' ').strip() # On remplace les doubles espaces par des espaces simples
        
    except Exception as e:
        print(f"  Erreur parsing VTT: {e}") # Afficher l'erreur au cas où le contenu VTT n'est pas parsé
        return ""


# Définir la fonction pour parser les sous-titres au format TTML.
def parser_ttml(content: str) -> str:
    """Parse le format TTML (Timed Text Markup Language)."""

    # Tenter de parser le contenu TTML
    try:
        # Nettoyer les balises XML
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    except Exception as e:
        print(f"  Erreur parsing TTML: {e}")
        return ""

# Définir la fonction pour parser les sous-titres au format SRV.
def parser_srv(content: str) -> str:
    """Parse les formats SRV (anciens formats YouTube)."""

    # Tenter de parser le contenu SRV
    try:
        # Extraire le texte entre les balises
        text_segments = re.findall(r'<text[^>]*>([^<]+)</text>', content)
        text = ' '.join(text_segments)
        return text.strip()
        
    except Exception as e:
        print(f"  Erreur parsing SRV: {e}")
        return ""

# Définir la fonction pour parser les sous-titres au format générique.
def parser_generique(content: str) -> str:
    """Parser générique pour les formats inconnus."""

    # Tenter de parser le contenu générique
    try:
        # On essaye d'abord le format JSON
        if content.strip().startswith('{') or content.strip().startswith('['):
            data = json.loads(content)
            # Essayer d'extraire récursivement tout texte
            def extract_text(obj):
                if isinstance(obj, str):
                    return [obj]
                elif isinstance(obj, dict):
                    texts = []
                    for key, value in obj.items():
                        texts.extend(extract_text(value))
                    return texts
                elif isinstance(obj, list):
                    texts = []
                    for item in obj:
                        texts.extend(extract_text(item))
                    return texts
                return []
            
            text_segments = extract_text(data)
            return ' '.join(text_segments)
        
        # Essayer d'enlever les balises XML/HTML
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text)
        
        # Enlever les timestamps
        text = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}', ' ', text)
        
        return text.strip()
        
    except:
        return content





