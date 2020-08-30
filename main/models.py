from django.db import models
from django.contrib.auth.models import User
from .signals import create_user

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
