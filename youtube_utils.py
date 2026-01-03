import yt_dlp
import json
import re
from urllib.parse import urlparse, parse_qs

def extraire_id_youtube(youtube_url: str) -> str:
    """Extrait l'ID d'une vidéo YouTube à partir d'une URL."""
    # Cette regex gère les formats : youtu.be, youtube.com/watch, shorts, et les paramètres ?si=
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    
    if match:
        video_id = match.group(1)
        return video_id
    
    raise ValueError(f"Impossible d'extraire l'ID de l'URL : {youtube_url}")

def obtenir_transcription_ytdlp(video_id: str, langues_preferees: list = None) -> str:
    """
    Utilise yt-dlp pour obtenir et extraire la transcription d'une vidéo YouTube.
    """
    if langues_preferees is None:
        langues_preferees = ['fr', 'en']
    
    print(f"Recherche de transcription avec yt-dlp pour la vidéo: {video_id}")
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': langues_preferees,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=False)
            
            # Vérifier les sous-titres disponibles
            print(f"\nInformations de la vidéo {video_id}:")
            print(f"Titre: {info.get('title', 'N/A')}")
            print(f"Durée: {info.get('duration', 'N/A')} secondes")
            
            # Sous-titres manuels
            if 'subtitles' in info and info['subtitles']:
                print("Sous-titres manuels:")
                for lang, subs in info['subtitles'].items():
                    print(f"  - {lang}: {len(subs)} format(s)")
            
            # Sous-titres automatiques
            if 'automatic_captions' in info and info['automatic_captions']:
                print("Sous-titres automatiques:")
                for lang, subs in info['automatic_captions'].items():
                    print(f"  - {lang}: {len(subs)} format(s)")
            
            # Essayer d'abord les sous-titres manuels
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
            
            # Essayer ensuite les sous-titres automatiques
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
            
            # Si aucune langue préférée, prendre la première disponible
            print("\nRecherche de n'importe quelle transcription disponible...")
            
            # Vérifier toutes les transcriptions disponibles
            all_subs = []
            if 'subtitles' in info:
                for lang, subs in info['subtitles'].items():
                    all_subs.extend(subs)
            if 'automatic_captions' in info:
                for lang, subs in info['automatic_captions'].items():
                    all_subs.extend(subs)
            
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

def telecharger_et_parser_sous_titres(url: str, format_type: str) -> str:
    """Télécharge et parse les sous-titres selon leur format."""
    import urllib.request
    import json
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        
        print(f"  Téléchargé: {len(content)} caractères (format: {format_type})")
        
        # Parser selon le format
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

def parser_json3(content: str) -> str:
    """Parse le format JSON3 de YouTube."""
    try:
        data = json.loads(content)
        text_segments = []
        
        # Format JSON3 standard
        if 'events' in data:
            for event in data['events']:
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            text_segments.append(seg['utf8'])
        
        # Autre format possible
        if not text_segments and isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'text' in item:
                    text_segments.append(item['text'])
        
        text = ' '.join(text_segments)
        return text.replace('\n', ' ').strip()
        
    except Exception as e:
        print(f"  Erreur parsing JSON3: {e}")
        return ""

def parser_vtt(content: str) -> str:
    """Parse le format WebVTT."""
    try:
        lines = content.split('\n')
        text_segments = []
        in_cue = False
        
        for line in lines:
            line = line.strip()
            # Ignorer les entêtes et les timestamps
            if line == '' or '-->' in line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                continue
            if line.isdigit():  # Numéro de cue
                continue
            
            text_segments.append(line)
        
        text = ' '.join(text_segments)
        return text.replace('  ', ' ').strip()
        
    except Exception as e:
        print(f"  Erreur parsing VTT: {e}")
        return ""

def parser_ttml(content: str) -> str:
    """Parse le format TTML (Timed Text Markup Language)."""
    try:
        # Nettoyer les balises XML
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    except Exception as e:
        print(f"  Erreur parsing TTML: {e}")
        return ""

def parser_srv(content: str) -> str:
    """Parse les formats SRV (anciens formats YouTube)."""
    try:
        # Extraire le texte entre les balises
        text_segments = re.findall(r'<text[^>]*>([^<]+)</text>', content)
        text = ' '.join(text_segments)
        return text.strip()
        
    except Exception as e:
        print(f"  Erreur parsing SRV: {e}")
        return ""

def parser_generique(content: str) -> str:
    """Parser générique pour les formats inconnus."""
    try:
        # Essayer JSON
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

# Version simplifiée pour utilisation rapide
def obtenir_transcription_simple(video_id: str) -> str:
    """
    Version simplifiée qui retourne directement la transcription.
    """
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['fr', 'en'],
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Chercher les sous-titres (manuels d'abord, puis automatiques)
            for lang in ['fr', 'en']:
                # Sous-titres manuels
                if 'subtitles' in info and lang in info['subtitles']:
                    for subtitle in info['subtitles'][lang]:
                        if subtitle.get('ext') == 'json3':
                            try:
                                import urllib.request
                                req = urllib.request.Request(subtitle['url'])
                                response = urllib.request.urlopen(req)
                                data = json.loads(response.read().decode('utf-8'))
                                
                                # Extraire le texte du JSON3
                                text_parts = []
                                if 'events' in data:
                                    for event in data['events']:
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    text_parts.append(seg['utf8'])
                                
                                return ' '.join(text_parts).replace('\n', ' ')
                            except:
                                continue
                
                # Sous-titres automatiques
                if 'automatic_captions' in info and lang in info['automatic_captions']:
                    for subtitle in info['automatic_captions'][lang]:
                        if subtitle.get('ext') == 'json3':
                            try:
                                import urllib.request
                                req = urllib.request.Request(subtitle['url'])
                                response = urllib.request.urlopen(req)
                                data = json.loads(response.read().decode('utf-8'))
                                
                                text_parts = []
                                if 'events' in data:
                                    for event in data['events']:
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    text_parts.append(seg['utf8'])
                                
                                return ' '.join(text_parts).replace('\n', ' ')
                            except:
                                continue
            
            return "Aucune transcription trouvée"
            
    except Exception as e:
        return f"Erreur: {str(e)}"
