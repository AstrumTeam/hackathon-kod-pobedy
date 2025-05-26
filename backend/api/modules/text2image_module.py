import torch
from diffusers import StableDiffusion3Pipeline        
from PIL import Image
import os
import time
from huggingface_hub import login

class Text2ImageModule:
    """
    Класс для генерации изображений по текстовому описанию с использованием модели Stable Diffusion 3.5.
    Поддерживает стилистическое оформление промпта и настройку качества генерации.
    """

    def __init__(self):
        """
        Инициализация параметров:
            - Название модели
            - Путь к папке сохранения изображений
            - Выбор устройства (GPU/CPU)
        """
        self.model_name = "stabilityai/stable-diffusion-3.5-medium"
        self.output_dir = "preview_images"
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def init_model(self):
        """
        Загружает модель Stable Diffusion 3.5 с использованием half precision (float16)
        и включает offload на CPU для экономии видеопамяти.
        """

        self.pipeline = StableDiffusion3Pipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            use_safetensors=True
        ).to(self.device)
        self.pipeline.enable_model_cpu_offload()
    

    def generate_image(self, prompt: str, guidance_scale=7.5, num_inference_steps=10, output_filename=None):
        """
        Генерация одного изображения по заданному текстовому описанию.

        Параметры:
            prompt (str): Основной текстовый запрос, описывающий изображение.
            guidance_scale (float): Значение "направляющей силы", определяющее степень следования промпту. Стандартное значение — 7.5.
            num_inference_steps (int): Количество шагов диффузии. Чем больше, тем выше качество (медленнее).
            output_filename (str): Имя файла для сохранения изображения (обязателен).

        Возвращает:
            str: Имя сохранённого файла.
        """
        login(token="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")
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"Старт генерации фото: {prompt}")
        start_time = time.time()

        height, width = 576, 1024
        prompt_final = "WWII Soviet Russia, sepia tones, cinematic lighting, photorealistic textures, 8k resolution, shallow depth of field, 35mm film grain, " + prompt

        image = self.pipeline(
            prompt=prompt_final,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            height=height,
            width=width,
        ).images[0]

        image.save(os.path.join(self.output_dir, output_filename))

        end_time = time.time()
        print(f"Время генерации фото: {end_time - start_time:.1f} секунд")

        return output_filename