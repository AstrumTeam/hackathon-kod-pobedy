from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
import uuid
import os
import tempfile
from unittest import mock

from .models import PublicVideo
from .serializers import VideoGenerationSerializer, PublishVideoSerializer, PublicVideoSerializer
from .views import job_manager


class PublicVideoModelTests(TestCase):
    def setUp(self):
        self.video_data = {
            'letter': 'Тестовое письмо',
            'video_filename': 'videos/test_video.mp4',
            'preview_filename': 'preview_images/test_preview.png',
            'author': 'Тестовый автор'
        }
        self.video = PublicVideo.objects.create(**self.video_data)

    def test_public_video_creation(self):
        """Тест создания модели PublicVideo"""
        self.assertEqual(self.video.letter, self.video_data['letter'])
        self.assertEqual(self.video.video_filename, self.video_data['video_filename'])
        self.assertEqual(self.video.preview_filename, self.video_data['preview_filename'])
        self.assertEqual(self.video.author, self.video_data['author'])
        self.assertTrue(isinstance(self.video.id, uuid.UUID))

    def test_string_representation(self):
        """Тест строкового представления модели"""
        expected_str = f"{self.video.author} — {self.video.video_filename}"
        self.assertEqual(str(self.video), expected_str)


class SerializerTests(TestCase):
    def setUp(self):
        self.video_data = {
            'letter': 'Тестовое письмо',
            'video_filename': 'videos/test_video.mp4',
            'preview_filename': 'preview_images/test_preview.png',
            'author': 'Тестовый автор'
        }
        self.video = PublicVideo.objects.create(**self.video_data)

    def test_public_video_serializer(self):
        """Тест сериализатора PublicVideoSerializer"""
        serializer = PublicVideoSerializer(self.video)
        self.assertEqual(serializer.data['letter'], self.video_data['letter'])
        self.assertEqual(serializer.data['video_filename'], self.video_data['video_filename'])
        self.assertEqual(serializer.data['preview_filename'], self.video_data['preview_filename'])
        self.assertEqual(serializer.data['author'], self.video_data['author'])

    def test_video_generation_serializer_valid_data(self):
        """Тест валидации данных VideoGenerationSerializer"""
        data = {
            'letter': 'Достаточно длинное письмо для прохождения валидации минимальной длины',
            'speaker': 'levitan',
            'music': True,
            'subtitles': True
        }
        serializer = VideoGenerationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_video_generation_serializer_invalid_data(self):
        """Тест валидации недопустимых данных VideoGenerationSerializer"""
        # Слишком короткое письмо
        data = {
            'letter': 'Короткое',
            'speaker': 'levitan',
            'music': True,
            'subtitles': True
        }
        serializer = VideoGenerationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Неправильный выбор диктора
        data = {
            'letter': 'Достаточно длинное письмо для прохождения валидации минимальной длины',
            'speaker': 'неправильный_диктор',
            'music': True,
            'subtitles': True
        }
        serializer = VideoGenerationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_publish_video_serializer(self):
        """Тест сериализатора PublishVideoSerializer"""
        data = {
            'letter': 'Достаточно длинное письмо для прохождения валидации минимальной длины',
            'autor': 'Тестовый автор',
            'job_id': str(uuid.uuid4())
        }
        serializer = PublishVideoSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class APIViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_job_id = str(uuid.uuid4())
        self.test_letter = 'Это тестовое письмо достаточной длины для прохождения валидации'
        
        # Создание временных файлов для тестирования
        self.temp_video_dir = tempfile.mkdtemp(prefix='videos')
        self.temp_preview_dir = tempfile.mkdtemp(prefix='preview_images')
        
        # Создание тестового видео-файла
        self.video_path = os.path.join(self.temp_video_dir, f'final_video_{self.test_job_id}.mp4')
        with open(self.video_path, 'wb') as f:
            f.write(b'test video content')
        
        # Создание тестового изображения
        self.image_path = os.path.join(self.temp_preview_dir, f'image_{self.test_job_id}.png')
        with open(self.image_path, 'wb') as f:
            f.write(b'test image content')

        # Создание тестовой публикации видео
        self.public_video = PublicVideo.objects.create(
            id=uuid.uuid4(),
            letter='Опубликованное тестовое письмо',
            video_filename='videos/test_published.mp4',
            preview_filename='preview_images/test_published.png',
            author='Тестовый автор'
        )

    def tearDown(self):
        # Удаление временных файлов
        if os.path.exists(self.video_path):
            os.remove(self.video_path)
        if os.path.exists(self.image_path):
            os.remove(self.image_path)
        
        try:
            os.rmdir(self.temp_video_dir)
            os.rmdir(self.temp_preview_dir)
        except:
            pass

    @mock.patch('api.views.job_manager.enqueue_job')
    def test_generate_video_view(self, mock_enqueue_job):
        """Тест представления GenerateVideoView"""
        # Настройка мок-объекта
        mock_enqueue_job.return_value = (None, {
            "message": "Видео поставлено в очередь на генерацию",
            "job_id": self.test_job_id,
            "queue_position": 1
        })
        
        # Отправка запроса
        url = reverse('generate_video')
        data = {
            'letter': self.test_letter,
            'speaker': 'levitan',
            'music': True,
            'subtitles': True
        }
        response = self.client.post(url, data, format='json')
        
        # Проверка результатов
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['job_id'], self.test_job_id)
        self.assertEqual(response.data['queue_position'], 1)
        
        # Проверка вызова метода enqueue_job с правильными параметрами
        mock_enqueue_job.assert_called_once_with(
            self.test_letter, 'levitan', True, True
        )

    @mock.patch('api.views.job_manager.get_status')
    def test_video_status_view(self, mock_get_status):
        """Тест представления VideoStatusView"""
        # Настройка мок-объекта
        mock_get_status.return_value = {
            "status": "queued",
            "queue_position": 1
        }
        
        # Отправка запроса
        url = reverse('video-status', args=[self.test_job_id])
        response = self.client.get(url)
        
        # Проверка результатов
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'queued')
        self.assertEqual(response.data['queue_position'], 1)
        
        # Проверка вызова метода get_status с правильными параметрами
        mock_get_status.assert_called_once_with(self.test_job_id)
        
        # Проверка с несуществующим ID
        mock_get_status.return_value = None
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('os.path.exists')
    @mock.patch('api.views.PublishVideoSerializer')
    def test_publish_video_view(self, mock_serializer_class, mock_exists):
        """Тест представления PublishVideoView"""
        # Настройка мок-объектов
        mock_serializer = mock.MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.validated_data = {
            'letter': self.test_letter,
            'job_id': self.test_job_id,
            'author': 'Тестовый автор'
        }
        mock_serializer_class.return_value = mock_serializer
        mock_exists.return_value = True
        
        # Отправка запроса
        url = reverse('publish_video')
        data = {
            'letter': self.test_letter,
            'job_id': self.test_job_id,
            'author': 'Тестовый автор'
        }
        with mock.patch('api.views.PublicVideo.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            with mock.patch('api.views.PublicVideo') as mock_model:
                instance = mock.MagicMock()
                mock_model.return_value = instance
                
                response = self.client.post(url, data, format='json')
                
                # Проверка результатов
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.data['message'], 'Видео успешно опубликовано')
                
                # Проверка создания объекта PublicVideo
                mock_model.assert_called_once()
                instance.save.assert_called_once()

    def test_get_publicated_videos_view(self):
        """Тест представления GetPublicatedVideosView"""
        url = reverse('publicated_videos')
        response = self.client.get(url)
        
        # Проверка результатов
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Должен быть один публичный объект видео
        self.assertEqual(response.data[0]['author'], 'Тестовый автор')

    def test_get_video_info_view(self):
        """Тест представления GetVideoInfoView"""
        url = reverse('publicated_video_info', args=[str(self.public_video.id)])
        response = self.client.get(url)
        
        # Проверка результатов
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['letter'], 'Опубликованное тестовое письмо')
        self.assertEqual(response.data['author'], 'Тестовый автор')
        
        # Проверка с несуществующим ID
        url = reverse('publicated_video_info', args=[str(uuid.uuid4())])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class JobQueueManagerTests(TestCase):
    def setUp(self):
        # Сбросим состояние менеджера очереди перед каждым тестом
        self.job_manager = job_manager
        self.job_manager.queue_list = []
        self.job_manager.job_statuses = {}
        self.job_manager.letter_hashes = set()
        while not self.job_manager.request_queue.empty():
            try:
                self.job_manager.request_queue.get(block=False)
            except:
                break
                
        self.test_letter = 'Это тестовое письмо достаточной длины для прохождения валидации'
        self.test_speaker = 'levitan'

    @mock.patch('threading.Thread')
    def test_enqueue_job(self, mock_thread):
        """Тест метода enqueue_job класса JobQueueManager"""
        # Настройка мок-объекта
        mock_thread_instance = mock.MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Выполнение метода
        error, result = self.job_manager.enqueue_job(
            self.test_letter, self.test_speaker, True, True
        )
        
        # Проверка результатов
        self.assertIsNone(error)
        self.assertIn('job_id', result)
        self.assertEqual(result['queue_position'], 1)
        self.assertEqual(len(self.job_manager.queue_list), 1)
        
        # Проверка запуска потока
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        
        # Проверка добавления дубликата письма
        error, result = self.job_manager.enqueue_job(
            self.test_letter, 'anton', False, False
        )
        self.assertIsNotNone(error)
        self.assertIn('message', error)
        self.assertIn('Такое письмо уже есть в очереди', error['message'])

    def test_get_status(self):
        """Тест метода get_status класса JobQueueManager"""
        # Добавим задание в очередь
        _, result = self.job_manager.enqueue_job(
            self.test_letter, self.test_speaker, True, True
        )
        job_id = result['job_id']
        
        # Получим статус
        status_result = self.job_manager.get_status(job_id)
        
        # Проверка результатов
        self.assertIsNotNone(status_result)
        self.assertEqual(status_result['status'], 'queued')
        self.assertEqual(status_result['queue_position'], 1)
        
        # Проверка несуществующего ID
        status_result = self.job_manager.get_status('non-existent-id')
        self.assertIsNone(status_result)

    def test_normalize_letter(self):
        """Тест метода normalize_letter класса JobQueueManager"""
        # Проверка нормализации разных вариантов одного и того же письма
        letter1 = "Тестовое письмо"
        letter2 = "  Тестовое письмо"
        letter3 = "ТЕСТОВОЕ ПИСЬМО"
        
        hash1 = self.job_manager.normalize_letter(letter1)
        hash2 = self.job_manager.normalize_letter(letter2)
        hash3 = self.job_manager.normalize_letter(letter3)
        
        # Все варианты должны давать одинаковый хеш
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash1, hash3)
