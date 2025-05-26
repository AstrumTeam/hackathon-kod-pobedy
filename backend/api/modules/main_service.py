from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy import vfx, afx
import torch
import gc
import time
import os
import sys
import subprocess
import random
import textwrap

from .llm_module import LLMModule
from .norm_module import NormModule
from .tts_module import TTSModule
from .stt_module import STTModule
from .text2video_module import Text2VideoModule
from .music_module import MusicModule
from .text2image_module import Text2ImageModule
from huggingface_hub import login


class MainService:
    def __init__(self):
        login(token="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")
        self.llmModule = LLMModule()
        self.ttsModule = TTSModule()
        self.sttModule = STTModule()
        self.normModule = NormModule()
        self.text2imageModule = Text2ImageModule()
        self.text2videoModule = Text2VideoModule()
        self.musicModule = MusicModule()

    def generate_video(self, letter: str, speaker: str, music_flag: bool, subtitles_flag: bool, job_id: str):
        # try:
            print('Старт обработки письма')
            work_time = time.time()
            torch.cuda.empty_cache()


            self.llmModule.init_model()
            response = self.llmModule.check_correct_letter(letter)
            print(response)
            if response['correct'] == False:
                return {'success': False, 'message': "Письмо не прошло филтрацию"}
            
            # normalized_letter = self.llmModule.normalize_text(letter)


            self.normModule.init_model()
            normalized_letter = self.normModule.normalize_text(normalized_letter)


            self.ttsModule.init_model()
            self.ttsModule.generate_tts(letter, speaker, output_filename=f"speech_{job_id}.wav")


            audio = AudioFileClip(f"speech_{job_id}.wav")
            videos_count = int(audio.duration // 5)
            total_duration = int(audio.duration) + 2
            audio.close()
            print("Количество видео: ", videos_count)
            print("Длина видео: ", total_duration, " секунд")


            prompts = self.llmModule.create_prompts(letter, videos_count)
            total_prompts = self._distribute_duration_by_rating(prompts, total_duration)
            torch.cuda.empty_cache()

            print(total_prompts)

            
            if music_flag:
                self.musicModule.get_music(total_duration, output_filename=f"music_{job_id}.wav")

            if subtitles_flag:
                self.sttModule.init_model()
                subtitles = self.sttModule.generate_stt(input_filename=f"speech_{job_id}.wav")
                torch.cuda.empty_cache()


            id = random.randint(1, len(total_prompts))
            self.text2imageModule.init_model()
            self.text2imageModule.generate_image(total_prompts[f'prompt_{id}']['description'],output_filename=f"image_{job_id}.png")
            torch.cuda.empty_cache()


            self.text2videoModule.init_model()
            self.text2videoModule.generate_videos(total_prompts, job_id, num_inference_steps=50)
            torch.cuda.empty_cache()


            if subtitles_flag:
                self._combine_videos(total_prompts, job_id, music_flag, subtitles_flag, subtitles)
            else:
                self._combine_videos(total_prompts, job_id, music_flag, subtitles_flag)

            torch.cuda.empty_cache()
            print(f"Общее время обработки письма: {time.time() - work_time:.1f} секунд")
            return {'success': True, 'message': "Готово"}
        
        # except Exception as e:
        #     print(str(e))
        #     torch.cuda.empty_cache()
        #     return {'success': False, 'message': str(e)}
    
    def _distribute_duration_by_rating(self, prompts: dict, total_duration: int) -> dict:
        total_rating = sum(scene['dynamic_rating'] for scene in prompts.values())
        if total_rating == 0:
            equal_time = total_duration / len(prompts)
            for scene in prompts.values():
                scene['duration_sec'] = round(equal_time)
            return prompts
        
        durations_float = [
            (key, scene['dynamic_rating'] / total_rating * total_duration)
            for key, scene in prompts.items()
        ]
        
        durations_rounded = {key: int(dur) for key, dur in durations_float}
        sum_rounded = sum(durations_rounded.values())
        remainder = total_duration - sum_rounded
        
        fractional_parts = [(key, dur - int(dur)) for key, dur in durations_float]
        fractional_parts.sort(key=lambda x: x[1], reverse=True)
        
        for i in range(remainder):
            key = fractional_parts[i][0]
            durations_rounded[key] += 1
        
        for key, dur in durations_rounded.items():
            scene = prompts[key]
            scene['duration_sec'] = dur
            scene.pop('dynamic_rating', None)
        
        return prompts

    def _combine_videos(self, total_prompts, job_id: str, music_flag: bool, subtitles_flag: bool, subtitles=None):
        videos_dir = "generated_videos"
        output_path = f"video_{job_id}.mp4"

        clips = []
        for i in range(1, len(total_prompts) + 1):
            clips.append(VideoFileClip(videos_dir + f'/video_{i}_{job_id}.mp4'))

        video = concatenate_videoclips(clips)
        video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        for clip in clips:
            clip.close()
        video.close()



        print('Старт апскейла видео')
        start_time = time.time()

        try:
            python_exe = sys.executable
            env = os.environ.copy()
            env.pop("PYTHONHASHSEED", None)
            subprocess.run([python_exe, 'api/modules/RIFE/inference_video.py', '--exp=2', f'--video=video_{job_id}.mp4', f'--output=video_x4_{job_id}.mp4'], check=True, env=env)
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при выполнении: {e}')

        print(f"Время выполнения: {time.time() - start_time:.1f} секунд")

        output_dir = 'videos'
        os.makedirs(output_dir, exist_ok=True)


        audio_path = f"speech_{job_id}.wav"
        music_path = f"music_{job_id}.wav"
        video_path = f"video_x4_{job_id}.mp4"
        output_path = output_dir+'/'+f"final_video_{job_id}.mp4"

        audio = AudioFileClip(audio_path)
        audio = audio.with_effects([afx.MultiplyVolume(1.0)])

        if music_flag:
            music = AudioFileClip(music_path)
            music = music.with_effects([afx.MultiplyVolume(0.2)])
            final_audio = CompositeAudioClip([music, audio])
        else:
            final_audio = audio

        video = VideoFileClip(video_path)
        video = video.with_audio(final_audio)

        if subtitles_flag:
            final_video = self._add_subtitles(video, subtitles)

        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        audio.close()
        if music_flag:
            music.close()
        video.close()
        final_video.close()

        os.remove(f'speech_{job_id}.wav')
        if music_flag:
            os.remove(f'music_{job_id}.wav')
        os.remove(f'video_{job_id}.mp4 ')
        os.remove(f'video_x4_{job_id}.mp4 ')
        [os.remove(os.path.join('generated_videos', f)) for f in os.listdir('generated_videos')]
        os.rmdir('generated_videos')

        torch.cuda.empty_cache()
        gc.collect()
    
    def _add_subtitles(self, clip, subtitles, font='api/font.ttf', font_size=24, color='white', stroke_color='black', stroke_width=1):
        subtitle_clips = []
        max_chars_per_line = 100  # Примерно 920 пикселей в ширину при font_size=24

        for sub in subtitles:
            wrapped_text = textwrap.fill(sub["text"], width=max_chars_per_line)

            txt_clip = (
                TextClip(
                    text=wrapped_text,
                    font_size=font_size,
                    font=font,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method='caption',  # Лучше справляется с переносами
                    size=(clip.w - 100, None),  # Ограничим ширину, высоту пусть подбирает сам
                )
                .with_position(("center", clip.h - 100))  # Чуть выше нижней границы
                .with_start(sub["start"])
                .with_end(sub["end"])
            )
            subtitle_clips.append(txt_clip)

        final = CompositeVideoClip([clip] + subtitle_clips)
        return final