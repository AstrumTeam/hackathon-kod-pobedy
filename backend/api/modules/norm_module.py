from runorm import RUNorm
import torch
import time
import gc

class NormModule:
    def __init__(self):
        self.model_size = "big"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def init_model(self):
        self.normalizer = RUNorm()
        self.normalizer.load(model_size=self.model_size, device=self.device)

    def normalize_text(self, text: str):
        print('Старт нормализации текста')
        start_time = time.time()

        normalized_text = self.normalizer.norm(text)

        print(f"Время выполнения: {time.time() - start_time:.1f} секунд")
        return normalized_text