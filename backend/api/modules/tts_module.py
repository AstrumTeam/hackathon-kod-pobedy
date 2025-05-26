import torch
import gc
import time
import subprocess
from f5_tts.api import F5TTS
from .f5_ckpt.stress import accentuate, load
from .f5_ckpt.yoditor import recover_yo_sure

class TTSModule:
    """
    Класс для генерации речи на основе модели F5TTS. 
    Поддерживает выбор референсного голоса, акцентуацию текста и настройку скорости синтеза.
    """
    
    def __init__(self):
        """
        Инициализация параметров и файлов модели.
        Устанавливаются:
            - Название модели
            - Устройство (GPU/CPU)
            - Пути к контрольным точкам и словарям
            - Список доступных дикторов с их аудиофайлами и референсными текстами
        """
        self.model = "F5TTS_v1_Base"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        path = 'api/modules/'
        self.ckpt_file = path + "f5_ckpt/model_last.pt"
        self.vocab_file = path + "f5_ckpt/vocab.txt"
        self.speakers = {
                        "levitan": path + "speakers/levitan.wav", 
                        "hmara": path + "speakers/hmara.wav",
                        "vysotskaya": path + "speakers/vysotskaya.wav", 
                        "bergholz": path + "speakers/bergholz.wav"}
        self.ref_text = {
            "levitan": "передаём важное правительственное сообщение", 
            "hmara": "наша давняя маленькая спутница на ней нет атмосферы нет воды голый сухой каменный шар без блеска без дымки без облаков",
            "vysotskaya": "меня зовут ольга сергеевна высоцкая голос мой вы наверное не раз слышали по радио я диктор", 
            "bergholz" : "бедный ленинградский ломтик хлеба он почти не весит на руке для того чтобы жить в кольце блокады"}
        
        self.spec_words = {"сталин": "ст+алин", "войны": "войн+ы", 
                           "№": "н+омер", "органах": "+органах",
                           "воины": "в+оины", "/I": " январ+я",
                            "/II": " феврал+я", "/III": " м+арта",
                            "/IV": " апр+еля", "/V": " м+ая",
                            "/VI": " и+юня", "/VII": " и+юля",
                            "/VIII": " +августа", "/IX": " сентябр+я",
                            "/X": " октябр+я", "/XI": " ноябр+я", "/XII": " декабр+я",
                            "/1": " январ+я", "/2": " феврал+я", "/3": " м+арта",
                            "/4": " апр+еля", "/5": " м+ая", "/6": " и+юня",
                            "/7": " и+юля", "/8": " +августа", "/9": " сентябр+я",
                            "/10": " октябр+я", "/11": " ноябр+я", "/12": " декабр+я"}


    def init_model(self):
        """
        Загружает модель F5TTS с указанными параметрами.
        Обязательно вызвать перед генерацией аудио.
        """
        self.f5tts = F5TTS(ckpt_file=self.ckpt_file, vocab_file=self.vocab_file, device=self.device)

    def generate_tts(self, text, speaker, speed=1.0, output_filename="speech.wav"):
        """
        Генерация речи по заданному тексту и выбранному диктору.

        Параметры:
            text (str): Текст для синтеза речи.
            speaker (str): Имя диктора (ключ из self.speakers).
            speed (float): Скорость речи (по умолчанию 1.0).
            output_filename (str): Имя выходного WAV-файла.

        Выполняет:
            - Предобработку текста (восстановление "ё", расстановка ударений)
            - Запуск синтеза речи
            - Сохранение аудиофайла
        """
        print('Старт генерации аудио')
        start_time = time.time() 
        
        lemmas, wordforms = load()
        text = recover_yo_sure(text)
        text = accentuate(text, wordforms, lemmas)
        for k, v in self.spec_words.items():
            text = text.replace(k, v)

        self.f5tts.infer(
            ref_file=self.speakers[speaker],
            ref_text=self.ref_text[speaker],
            gen_text=text.lower(),
            file_wave=output_filename,
            speed=speed,
            seed=None,
        )
        print(f"Время генерации аудио: {time.time() - start_time} секунд")

