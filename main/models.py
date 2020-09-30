from django.db import models
from django.contrib.auth.models import User
from .signals import create_user
import random
import string

models.signals.post_save.connect(create_user, sender=User)


class Disk(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    size = models.IntegerField("Занятое на диске место", default=0)
    allSize = models.IntegerField("Всё место на диске пользователя", default=5000000000)
    path = models.CharField("Путь к папке", max_length=500)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Диск"
        verbose_name_plural = "Диски"


def generate_token():
    duplicate = True
    while (duplicate == True):
        token = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(16))
        try:
            PublicFile.objects.get(url=token)
            duplicate = True
        except:
            duplicate = False

    return token


class PublicFile(models.Model):
    disk = models.ForeignKey(Disk, verbose_name="Диск, на котором хранится файл", on_delete=models.CASCADE)
    pathToFile = models.CharField("Путь к общедоступному файлу", max_length=1000)
    url = models.CharField("Уникальный код", max_length=1000, default=generate_token)

    def __str__(self):
        return f"path: {self.pathToFile}; url: {self.url}"

    class Meta:
        verbose_name = "Общедоступный файл"
        verbose_name_plural = "Общедоступные файлы"
