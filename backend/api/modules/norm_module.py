from runorm import RUNorm
import torch
import time
import gc

class NormModule:
    """
    Класс для нормализации русского текста с использованием модели RuNorm.
    Поддерживает выбор размера модели и автоматический выбор устройства (CPU/GPU).
    """

    def __init__(self):
        """
        Инициализация параметров:
            - Размер модели (по умолчанию 'big')
            - Устройство для инференса (CUDA при наличии, иначе CPU)
        """
         
        self.model_size = "big"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def init_model(self):
        """
        Загружает модель нормализации текста (RuNorm) с заданным размером и устройством.
        """
        self.normalizer = RUNorm()
        self.normalizer.load(model_size=self.model_size, device=self.device)

    def normalize_text(self, text: str):
        """
        Нормализует входной текст (приведение к каноническому виду: числа, даты, сокращения и т.п.).

        Параметры:
            text (str): Входной текст для нормализации.

        Возвращает:
            str: Нормализованный текст.
        """
        
        print('Старт нормализации текста')
        start_time = time.time()

        normalized_text = self.normalizer.norm(text)

        print(f"Время выполнения: {time.time() - start_time:.1f} секунд")
        return normalized_text