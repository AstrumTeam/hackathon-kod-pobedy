from django.urls import path
from .views import (GenerateVideoView, 
                    VideoStatusView,
                    GetVideoView,
                    GetImageView,
                    PublishVideoView,
                    GetPublicatedVideosView,
                    GetVideoInfoView)

urlpatterns = [
    path('generate_video/', GenerateVideoView.as_view(), name='generate_video'),
    path('video_status/<str:job_id>/', VideoStatusView.as_view(), name='video-status'),
    path('get_video/<str:job_id>/', GetVideoView.as_view(), name='get_video'),
    path('get_image/<str:job_id>/', GetImageView.as_view(), name='get_video'),
    path('publish_video/', PublishVideoView.as_view(), name='publish_video'),
    path('publicated_videos/', GetPublicatedVideosView.as_view(), name='publicated_videos'),
    path('publicated_video_info/<str:job_id>/', GetVideoInfoView.as_view(), name='publicated_video_info'),
]