
import csv
from natasha import (
    Segmenter,
    Doc
)
from faster_whisper import WhisperModel, BatchedInferencePipeline
import torch
import time


class STTModule:
    """
    Класс для автоматического распознавания речи (Speech-to-Text) с использованием модели FasterWhisper.
    Включает обработку аудио, получение тайм-кодов слов и сегментацию текста на предложения с помощью Natasha.
    """

    def __init__(self):
        """
        Инициализация параметров модуля:
            - Название модели (Whisper)
            - Устройство выполнения (CPU/GPU)
            - Размер batch'а
            - Тип вычислений (float16 для ускорения на GPU)
            - Сегментер из библиотеки Natasha для разбивки текста на предложения
        """
        self.model_name = "large-v3-turbo"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.batch_size = 32
        self.compute_type = "float16"
        self.segmenter = Segmenter()

    def init_model(self):
        """
        Инициализирует модель Whisper и оборачивает её в пайплайн для пакетной инференции.
        """
        model = WhisperModel(self.model_name, device=self.device, compute_type=self.compute_type)
        self.model = BatchedInferencePipeline(model=model)

    def generate_stt(self, input_filename="speech.wav"):
        """
        Основной метод для распознавания речи из аудиофайла.

        Параметры:
            input_filename (str): Имя входного WAV-файла

        Возвращает:
            list: Список слов с временными метками, объединённых в предложения
        """

        print('Старт генерации субтитров')
        start_time = time.time() 
        segments, _ = self.model.transcribe(input_filename, batch_size=self.batch_size, word_timestamps=True)
        print(f"Время генерации субтитров: {time.time() - start_time} секунд")

        words = []
        for segment in segments:
            for word in segment.words:
                words.append({
                    "start": word.start,
                    "end": word.end,
                    "word": word.word
                })
        
        sentences = self.words_to_sentences(words)
        return sentences

    def split_by_sentences(self, text):
        """
        Разделяет текст на предложения с использованием Natasha.

        Параметры:
            text (str): Входной текст

        Возвращает:
            list: Список строк — предложений
        """

        doc = Doc(text)
        doc.segment(self.segmenter)

        return [x.text for x in doc.sents]


    def words_to_sentences(self, words):
        """
        Преобразует последовательность слов с таймкодами в список предложений с временными рамками.

        Параметры:
            words (list): Список слов с полями start, end и word

        Возвращает:
            list: Список предложений с метками времени
        """
        sentences = []
        i = 0
        while i < len(words):
            stop = False
            j = i + 1
            while not stop and j <= len(words):
                clip = words[i:j]
                clip_text = ''.join([x['word'] for x in clip])
                clip_sentences = self.split_by_sentences(clip_text)
                if len(clip_sentences) > 1:
                    sentences.append({
                        "start": clip[0]['start'],
                        "end": clip[-1]['start'],
                        "text": clip_sentences[0]
                    })
                    i = j - 1  # откат к началу следующего предложения
                    stop = True
                else:
                    j += 1

            # Если не нашли конец предложения — добавляем остаток
            if not stop and i < len(words):
                clip = words[i:]
                clip_text = ''.join([x['word'] for x in clip])
                sentences.append({
                    "start": clip[0]['start'],
                    "end": clip[-1]['end'],
                    "text": clip_text
                })
                break  # выход из основного цикла
        return sentences