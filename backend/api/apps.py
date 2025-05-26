from django.apps import AppConfig
import torch
import gc


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        torch.cuda.empty_cache()
        gc.collect()