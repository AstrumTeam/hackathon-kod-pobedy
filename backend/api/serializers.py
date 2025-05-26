from rest_framework import serializers
from .models import PublicVideo

class VideoGenerationSerializer(serializers.Serializer):
    letter = serializers.CharField(min_length=100, max_length=3000, allow_blank=False, required=True)
    speaker = serializers.ChoiceField(choices=[
        'levitan', 'anton', 'vysotskaya', 'bergholz', 'hmara',
    ], allow_blank=False, required=True)
    music = serializers.BooleanField(default=True)
    subtitles = serializers.BooleanField(default=True)


class PublishVideoSerializer(serializers.Serializer):
    letter = serializers.CharField(min_length=100, max_length=3000, allow_blank=False, required=True)
    autor = serializers.CharField(min_length=5, max_length=50, allow_blank=False, required=False)
    job_id = serializers.UUIDField(required=True)


class PublicVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicVideo
        fields = '__all__'