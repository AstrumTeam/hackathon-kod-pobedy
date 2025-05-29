from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, FileResponse
from rest_framework import status
from .serializers import VideoGenerationSerializer, PublishVideoSerializer, PublicVideoSerializer
from .modules.main_service import MainService
import os
import threading
import queue
import uuid
import time
import logging
from .models import PublicVideo
import hashlib

logger = logging.getLogger(__name__)

MAX_QUEUE_SIZE = 20
main_service = MainService()

class JobQueueManager:
    def __init__(self):
        self.request_queue = queue.Queue()
        self.job_statuses = {}
        self.queue_list = []
        self.letter_hashes = set()
        self.queue_lock = threading.Lock()
        self.worker_thread = None
        self.is_processing = False

    def normalize_letter(self, letter: str):
        return hashlib.md5(letter.strip().lower().encode('utf-8')).hexdigest()

    def enqueue_job(self, letter, speaker, music, subtitles):
        with self.queue_lock:
            if self.request_queue.qsize() >= MAX_QUEUE_SIZE:
                return {"error": "Очередь переполнена"}, None

            letter_hash = self.normalize_letter(letter)
            for job_id, info in self.job_statuses.items():
                if self.normalize_letter(info['letter']) == letter_hash and (info['status'] == 'queued' or info['status'] == 'processing'):
                    return {
                        "message": "Такое письмо уже есть в очереди",
                        "job_id": job_id,
                        "queue_position": 0
                    }, None

            job_id = str(uuid.uuid4())
            queue_position = len(self.queue_list) + 1

            self.job_statuses[job_id] = {
                'status': 'queued',
                'letter': letter,
                'speaker': speaker,
                'music': music,
                'subtitles': subtitles,
                'created_at': time.time(),
                'queue_position': queue_position
            }

            self.queue_list.append(job_id)
            self.letter_hashes.add(letter_hash)
            self.request_queue.put((job_id, letter, speaker, music, subtitles))

            if not self.is_processing or self.worker_thread is None or not self.worker_thread.is_alive():
                self.is_processing = True
                self.worker_thread = threading.Thread(target=self.process_queue)
                self.worker_thread.daemon = True
                self.worker_thread.start()

            return None, {
                "message": "Видео поставлено в очередь на генерацию",
                "job_id": job_id,
                "queue_position": queue_position
            }

    def get_status(self, job_id):
        with self.queue_lock:
            if job_id not in self.job_statuses:
                return None
            info = self.job_statuses[job_id]
            queue_position = self.queue_list.index(job_id) + 1 if job_id in self.queue_list else 0
            
            if info['status'] == 'failed':
                return {
                "status": info['status'],
                "error": info['error'],
                "queue_position": queue_position
                }
            else:
                return {
                    "status": info['status'],
                    "queue_position": queue_position
                }

    def process_queue(self):
        logger.info("Запущен поток обработки очереди")
        while not self.request_queue.empty():
            try:
                job_id, letter, speaker, music, subtitles = self.request_queue.get(block=False)

                with self.queue_lock:
                    self.job_statuses[job_id]['status'] = 'processing'
                    if job_id in self.queue_list:
                        self.queue_list.remove(job_id)
                    for i, queue_job_id in enumerate(self.queue_list):
                        self.job_statuses[queue_job_id]['queue_position'] = i + 1

                try:
                    result = main_service.generate_video(
                        letter=letter, speaker=speaker,
                        music_flag=music, subtitles_flag=subtitles,
                        job_id=job_id
                    )
                    logger.info(f"Задание {job_id} завершено со статусом {status}")

                    with self.queue_lock:
                        if result.get('success', False):
                            self.job_statuses[job_id]['status'] = 'completed'
                            self.job_statuses[job_id]['file_path'] = f'videos/final_video_{job_id}.mp4'
                        else:
                            self.job_statuses[job_id]['status'] = 'failed'
                            self.job_statuses[job_id]['error'] = result.get('message', 'error')

                except Exception as e:
                    logger.exception(f"Ошибка в задании {job_id}")
                    with self.queue_lock:
                        self.job_statuses[job_id]['status'] = 'failed'
                        self.job_statuses[job_id]['error'] = str(e)

                self.request_queue.task_done()

            except queue.Empty:
                break
            except Exception as e:
                logger.exception(f"Неожиданная ошибка в потоке: {str(e)}")

        with self.queue_lock:
            self.is_processing = False
            self.worker_thread = None
        logger.info("Поток обработки очереди завершён")

job_manager = JobQueueManager()


class GenerateVideoView(APIView):
    def post(self, request):
        logger.info("Получен запрос на генерацию видео")
        serializer = VideoGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Неверный формат данных")
            return Response({"message": "Неверный формат данных"}, status=status.HTTP_400_BAD_REQUEST)

        letter = serializer.validated_data['letter']
        speaker = serializer.validated_data['speaker']
        music = serializer.validated_data['music']
        subtitles = serializer.validated_data['subtitles']

        error_response, success_response = job_manager.enqueue_job(letter, speaker, music, subtitles)
        if error_response:
            return Response(error_response, status=status.HTTP_200_OK if "job_id" in error_response else status.HTTP_429_TOO_MANY_REQUESTS)
        return Response(success_response, status=status.HTTP_202_ACCEPTED)


class VideoStatusView(APIView):
    def get(self, request, job_id):
        result = job_manager.get_status(job_id)
        if result is None:
            return Response({"error": "Задание не найдено"}, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_200_OK)


class GetVideoView(APIView):
    def get(self, request, job_id):
        file_path = f'videos/final_video_{job_id}.mp4'

        if not os.path.exists(file_path):
            return Response({"message": "Файл изображения отсутствует на сервере"}, status=status.HTTP_404_NOT_FOUND)


        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('Range', '').strip()
        content_type = 'video/mp4'

        if range_header:
            try:
                # Пример: "bytes=500-" или "bytes=500-999"
                range_value = range_header.lower().replace('bytes=', '')
                if '-' not in range_value:
                    return HttpResponseBadRequest("Неправильный формат Range")

                start_str, end_str = range_value.split('-')

                if start_str == '':
                    # Пример: bytes=-500 (последние 500 байт)
                    length = int(end_str)
                    start = file_size - length
                    end = file_size - 1
                else:
                    start = int(start_str)
                    end = int(end_str) if end_str else file_size - 1

                if start > end or end >= file_size:
                    return HttpResponse(status=416)  # Range Not Satisfiable

                length = end - start + 1

                def file_iterator(file_path, start, length, chunk_size=8192):
                    with open(file_path, 'rb') as f:
                        f.seek(start)
                        remaining = length
                        while remaining > 0:
                            chunk = f.read(min(chunk_size, remaining))
                            if not chunk:
                                break
                            yield chunk
                            remaining -= len(chunk)

                response = StreamingHttpResponse(file_iterator(file_path, start, length), status=206, content_type=content_type)
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Accept-Ranges'] = 'bytes'
                response['Content-Length'] = str(length)
                return response

            except Exception as e:
                # Лучше логировать
                return HttpResponseBadRequest({"error": "Ошибка обработки Range-запроса"})

        # Если Range не задан — отдаём весь файл целиком через StreamingHttpResponse
        def full_file_iterator(path, chunk_size=8192):
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        response = StreamingHttpResponse(full_file_iterator(file_path), content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response


class GetImageView(APIView):
    def get(self, request, job_id):
        try:
            video = PublicVideo.objects.get(id=job_id)
        except PublicVideo.DoesNotExist:
            return Response({"message": "Видео не найдено"}, status=status.HTTP_404_NOT_FOUND)

        file_path = video.preview_filename  # или поле с путем к изображению

        if not os.path.exists(file_path):
            return Response({"message": "Файл изображения отсутствует на сервере"}, status=status.HTTP_404_NOT_FOUND)

        # Определим content_type по расширению файла
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.png': 'image/png',
        }
        content_type = content_types.get(ext, 'application/octet-stream')

        return FileResponse(open(file_path, 'rb'), content_type=content_type)


class PublishVideoView(APIView):
    def post(self, request):
        serializer = PublishVideoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Неверный формат данных"}, status=status.HTTP_400_BAD_REQUEST)
        
        letter = serializer.validated_data['letter']
        job_id = serializer.validated_data['job_id']
        author = serializer.validated_data.get('author')

        video_path = f'videos/final_video_{job_id}.mp4'
        if not os.path.exists(video_path):
            return Response({"message": "Видео не найден"}, status=status.HTTP_400_BAD_REQUEST)

        image_path = f'preview_images/image_{job_id}.png'
        if not os.path.exists(image_path):
            return Response({"message": "Превтю не найден"}, status=status.HTTP_400_BAD_REQUEST)

        if PublicVideo.objects.filter(id=job_id).exists():
            return Response({'message': 'Такое видео с job_id уже сохранено'}, status=status.HTTP_409_CONFLICT)
        
        video_instance = PublicVideo(id=job_id, letter=letter, video_filename=video_path, preview_filename=image_path)
        if author is not None:
            video_instance.author = author

        video_instance.save()

        return Response({'message': 'Видео успешно опубликовано'}, status=status.HTTP_201_CREATED)


class GetPublicatedVideosView(APIView):
    def get(self, request):
        videos = PublicVideo.objects.all()
        serializer = PublicVideoSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetVideoInfoView(APIView):
    def get(self, request, job_id):
        try:
            video = PublicVideo.objects.get(id=job_id)
        except PublicVideo.DoesNotExist:
            return Response({"message": "Видео не найдено"}, status=status.HTTP_404_NOT_FOUND)


        serializer = PublicVideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)
