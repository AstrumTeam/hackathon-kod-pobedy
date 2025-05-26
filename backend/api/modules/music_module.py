import os
import random
from pydub import AudioSegment

class MusicModule:
    def __init__(self) -> None:
        self.music_directory: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs/")
        
    def get_music(self, video_length, output_filename) -> str:
        music_files = [f for f in os.listdir(self.music_directory) 
                     if os.path.isfile(os.path.join(self.music_directory, f)) and 
                     f.lower().endswith(('.mp3', '.wav'))]
        
        if not music_files:
            raise FileNotFoundError(f"No music files found in {self.music_directory}")
        
        selected_music = random.choice(music_files)
        music_path = os.path.join(self.music_directory, selected_music)
        
        audio = AudioSegment.from_file(music_path)
        
        audio_length_sec = len(audio) / 1000
        video_length_ms = video_length * 1000
        
        if audio_length_sec <= video_length:
            repetitions = int(video_length_ms / len(audio)) + 1
            output_audio = audio * repetitions
            output_audio = output_audio[:video_length_ms]
        else:
            output_audio = audio[:video_length_ms]
        
        output_audio.export(output_filename, format="wav")


