from youtube_utils import extraire_id_youtube, obtenir_transcription_ytdlp

url = "https://youtu.be/RBSUwFGa6Fk?si=bDDdOQlSK4E8EwMd"

video_id = extraire_id_youtube(url)
print("Video ID:", video_id)

text = obtenir_transcription_ytdlp(video_id, ['fr', 'en'])
print("Transcription:", text[:1000])
print("Longueur:", len(text))