from rest_framework import serializers
from django.core.validators import MaxLengthValidator, MinLengthValidator
from .models import PublicVideo

class VideoGenerationSerializer(serializers.Serializer):
    letter = serializers.CharField(allow_blank=False, required=True,
                                   validators=[
                                       MinLengthValidator(100),
                                       MaxLengthValidator(2000)
                                       ])
    speaker = serializers.ChoiceField(choices=[
        'levitan', 'vysotskaya', 'bergholz', 'hmara',
    ], allow_blank=False, required=True)
    music = serializers.BooleanField(default=True)
    subtitles = serializers.BooleanField(default=True)


class PublishVideoSerializer(serializers.Serializer):
    letter = serializers.CharField(allow_blank=False, required=True,
                                   validators=[
                                       MinLengthValidator(100),
                                       MaxLengthValidator(2000)
                                       ])
    author = serializers.CharField(min_length=5, max_length=50, allow_blank=False, required=False)
    job_id = serializers.UUIDField(required=True)


class PublicVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicVideo
        fields = '__all__'