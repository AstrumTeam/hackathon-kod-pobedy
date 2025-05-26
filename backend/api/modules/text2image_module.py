import torch
from diffusers import StableDiffusion3Pipeline        
from PIL import Image
import os
import time
from huggingface_hub import login

class Text2ImageModule:
    def __init__(self):
        self.model_name = "stabilityai/stable-diffusion-3.5-medium"
        self.output_dir = "preview_images"
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def init_model(self):
        self.pipeline = StableDiffusion3Pipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            use_safetensors=True
        ).to(self.device)
        self.pipeline.enable_model_cpu_offload()
    

    def generate_image(self, prompt: str, guidance_scale=7.5, num_inference_steps=10, output_filename=None):
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