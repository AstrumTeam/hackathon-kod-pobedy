import time
import torch
import json
import gc
from transformers import AutoModelForCausalLM, AutoTokenizer, FineGrainedFP8Config


class LLMModule:
    """
    Модуль обработки письма.
    """
    def __init__(self):
        self.model_name = "Qwen/Qwen3-8B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def init_model(self):
        """
        Инициализация Qwen3-8B.
        """
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            use_safetensors=True
        ).to(self.device)


    def _work_model(self, messages: list[dict], top_k=None):
        """
        Работа с Qwen3-8B.

        Args:
            messages: list[dict] - промпт для модели, куда входит письмо.
            top_k: int - параметр top_k для модели.

        Returns:
            str - ответ модели.
        """
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=32768,
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

        response = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
        return response

    def check_correct_letter(self, letter: str):
        """
        Проверка на аутентичность письма.

        Args:
            letter: str - письмо.

        Returns:
            bool - True - если письмо аутентично, False - если нет.
        """

        prompt = '''
        Ты — историк-аналитик, специализирующийся на проверке подлинности писем времён Великой Отечественной войны.

        Перед тобой текст, предположительно являющийся письмом советского солдата периода 1941–1945 годов. Твоя задача — определить, может ли это письмо быть подлинным с точки зрения стиля, содержания и общего тона.

        Письмо можно считать подлинным, если оно:
        – написано простым, бытовым языком, как солдат мог бы писать родным;
        – содержит детали повседневной жизни, службы, воспоминания, переживания, упоминания родных;
        – может быть кратким, скучным, обрывочным или небрежным — это допустимо;
        – допускает орфографические, пунктуационные ошибки, повторения и сбивчивость речи.

        Письмо следует отклонить, только если:
        – в нём содержится современный сленг, интернет-мемы, маты, шутки или явный троллинг;
        – оно похоже на рекламный текст, спам, бессмысленный набор слов или сгенерированный шум;

        Если не уверен — выбирай {"correct": true}.

        Ответ строго в формате JSON:
        - {"correct": true} — если письмо можно принять.
        - {"correct": false} — если письмо точно не похоже на письмо времён войны.

        Вот письмо:
        '''
        hard_prompt = '''
        Отвечай строгов формате JSON: {"correct": true}
        '''

        messages = [
            {"role": "user", "content": prompt + letter}
        ]

        print('Старт фильрации')
        start_time = time.time()

        response = '{' + self._work_model(messages).split('{')[1].split('}')[0] + '}'

        print(f"Время выполнения: {time.time() - start_time:.1f} секунд")

        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON:", response)
            response = {}

        return response    

    def normalize_text(self, letter: str):
        """
        Нормализация текста.

        Args:
            letter: str - письмо.

        Returns:
            str - нормализованный текст.
        """
        
        prompt = '''
        Ты — редактор, специализирующийся на нормализации исторических писем.  
        Твоя задача — подготовить письмо советского солдата времён Великой Отечественной войны для последующей генерации аудио.

        Правила:
        1. Сохрани все слова, фразы и общий стиль письма — не удаляй и не добавляй смыслы.
        2. Преобразуй текст в литературно нормализованную форму, чтобы он звучал естественно при озвучивании.
        3. Все числа, даты и года запиши словами.  
        Примеры: «2 мая 1945 года» → «второго мая тысяча девятьсот сорок пятого года»;  
                    «4.10.1941» → «четвёртого октября тысяча девятьсот сорок первого года».
        4. Раскрывай сокращения по контексту (например, «г.» → «город», «д.» → «деревня», «т. к.» → «так как»).
        5. Удали пометки вроде «(неразборчиво)».
        6. Сохрани лексику и эмоциональный тон письма времён Великой Отечественной войны.

        Результат: один нормализованный текст, готовый для синтеза речи. Без пояснений.

        Вот письмо:
        '''

        messages = [
            {"role": "user", "content": prompt + letter}
        ]

        print('Старт нормализации текста')
        start_time = time.time()

        response = self._work_model(messages)

        print(f"Время выполнения: {time.time() - start_time:.1f} секунд")

        return response
        
    def create_prompts(self, letter: str, videos_count: int):
        """
        Создание промптов для генерации визуальных сцен.

        Args:
            letter: str - письмо.
            videos_count: int - количество сцен.
        
        Returns:
            dict[str, dict[str, str]] - словарь с промптами.
        """
        # prompt = '''
        # Ты — кинорежиссёр, создающий визуальные сцены на основе письма советского солдата времён Великой Отечественной войны. 
        # Твоя задача — разбить письмо ровно на ''' + str(videos_count) + ''' простых визуальных эпизодов. Каждый эпизод должен быть конкретным, визуально насыщенным и легко интерпретируемым видеомоделью.

        # Для каждого эпизода:

        # – Опиши одно конкретное действие что именно происходит в кадре.
        # – Укажи, что сцена снята общим или средним планом с упором на окружающую обстановку.
        # – Включи движение — либо персонажа, либо камеры.
        # – Избегай метафор, символизма и описания чувств. Только визуальные и слышимые детали.
        # – Добавь аутентичные детали 1940-х годов СССР одежда, техника, быт, архитектура, природа.
        # – Описание должно быть написано на английском языке, не более 50 слов. Пиши так, будто даёшь техзадание оператору.
        # – Пример: “A Soviet soldier walks slowly through a snow-covered village. Wide shot. Wooden houses around. Smoke from chimneys. The camera pans slowly left. Cold wind blows. Boots crunch on snow.”

        # Добавь в конце каждой сцены оценку динамичности по шкале от 2 до 9 где 2 — почти статично, 9 — активно.

        # Важно: избегай абстракции и историй. Каждое описание — это один простой кадр в видео.

        # Формат ответа — JSON следующего вида:
        # {
        # "prompt_1": {
        #     "description": "Scene description in English...",
        #     "dynamic_rating": X
        # },
        # ...
        # "prompt_''' + str(videos_count) + '''": {
        #     "description": "Scene description in English...",
        #     "dynamic_rating": Y
        # }
        # }

        # Вот письмо солдата, по которому нужно построить визуальный рассказ:
        # '''
        prompt = '''
        You are a film director creating visual scenes based on a real letter from a Soviet soldier during World War II. 

        Your task is to transform the letter into exactly ''' + str(videos_count) + ''' simple, distinct cinematic scenes. These scenes should visually reflect specific details, places, or moments mentioned or implied in the letter. 

        Each scene must follow these rules:

        – Describe one specific and clear action in the frame.
        – Use wide or medium shots with a strong focus on authentic 1940s Soviet surroundings (clothes, military gear, furniture, landscape, weather, architecture).
        – Always include motion — either from the character (e.g. walking, writing, looking) or from the camera (e.g. panning, slow zoom-in). If motion isn’t possible, include an interaction with the environment (e.g. turning a page, packing gear).
        – Do not include metaphors, emotions, or internal thoughts. Only physical, visible, or audible elements.
        – Write descriptions in cinematic English no more than 50 words per scene. Write as if giving a camera operator precise instructions.
        – Include a dynamism score from 1 to 10 for each scene, where 1 = very static, 10 = very dynamic.

        Important: Scenes must be grounded in the letters content. If the letter lacks visual elements, creatively extrapolate realistic visuals from the context. Do not invent surreal or fantasy elements.

        Use the following JSON format:
        {
        "prompt_1": {
            "description": "Scene description in English...",
            "dynamic_rating": X
        },
        ...
        "prompt_''' + str(videos_count) + '''": {
            "description": "Scene description in English...",
            "dynamic_rating": Y
        }
        }

        Here is the letter you are visualizing:
        '''

        messages = [
            {"role": "user", "content": prompt + letter}
        ]

        print('Старт генерации промптов')
        start_time = time.time()

        response = self._work_model(messages)
        
        print(f"Время выполнения: {time.time() - start_time:.1f} секунд")

        try:
            scenes = json.loads(response)
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON:", response)
            scenes = {}

        return scenes