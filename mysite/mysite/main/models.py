from django.db import models

# Create your models here.
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models


# Create your models here.
class Article(models.Model):
    title = models.CharField('название статьи', max_length=50)
    text = models.TextField('текст статьи')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def get_absolute_url(self):
        return f'/{self.id}'
