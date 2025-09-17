from django.db import models
from core.models import ModuleModel
from django.contrib.postgres.fields import ArrayField

class MotorQuoteRequest(ModuleModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    mongo_id = models.CharField(max_length=24, unique=True)
    tasks = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    source = models.CharField(max_length=100, choices=[
        ("upload", "Upload"),
    ])