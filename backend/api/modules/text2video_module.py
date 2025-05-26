import torch
import time
import os
import gc
import cv2
from PIL import Image
from diffusers import LTXPipeline, LTXImageToVideoPipeline
from diffusers.utils import export_to_video


class Text2VideoModule:
    """
    Класс для генерации видеороликов по текстовому описанию с использованием модели LTX-Video.
    Поддерживает множественные промпты, генерацию с негативными подсказками и настройку кадров в секунду.
    """

    def __init__(self):
        """
        Инициализация параметров модуля:
            - Название модели
            - Папка вывода
            - Выбор устройства (GPU/CPU)
        """
        self.model_name = "Lightricks/LTX-Video"
        self.output_dir = "generated_videos"
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def init_model(self):
        """
        Загружает и инициализирует модель LTX-Video.
        Использует offloading моделей на CPU при необходимости для экономии видеопамяти.
        """
        self.pipeline = LTXPipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            use_safetensors=True
        ).to(self.device)
        self.pipeline.enable_model_cpu_offload()


    def generate_videos(self, prompts: dict, job_id, fps=8, num_inference_steps=10):
        """
        Генерация серии видео по заданным текстовым описаниям.

        Параметры:
            prompts (dict): Словарь, где ключи — 'prompt_1', 'prompt_2', ..., 
                            значения — словари с ключами:
                                - 'description': текстовое описание сцены
                                - 'duration_sec': длительность в секундах
            job_id (str or int): Уникальный идентификатор задачи (для именования файлов).
            fps (int): Кадров в секунду в итоговом видео. По умолчанию 8.
            num_inference_steps (int): Кол-во шагов диффузии. По умолчанию 10.

        Процесс:
            - Генерация видео по каждому промпту
            - Применение негативного промпта для улучшения качества
            - Сохранение видео в формате .mp4
        """
        
        os.makedirs(self.output_dir, exist_ok=True)

        negative_prompt = "worst quality, inconsistent motion, blurry, jittery, distorted, cartoonish, unrealistic lighting, oversaturated colors, unnatural textures, low resolution, unnatural facial expressions, modern clothing, futuristic elements"
        height, width = 576, 1024

        for i in range(1, len(prompts) + 1):
            print(f"Старт генерации видео {i}")
            start_time = time.time()

            prompt = "WWII Soviet Russia, sepia tones, cinematic lighting, photorealistic textures, 8k resolution, shallow depth of field, 35mm film grain, " + prompts[f'prompt_{i}']['description']
            seconds = prompts[f'prompt_{i}']['duration_sec']

            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_frames=seconds*fps + 1,
                num_inference_steps=num_inference_steps,
                width=width,
                height=height
            ).frames[0]

            export_to_video(result, os.path.join(self.output_dir, f"video_{i}_{job_id}.mp4"), fps=fps)

            end_time = time.time()
            print(f"Время генерации видео {i}: {end_time - start_time:.1f} секунд")