from django.core.files.storage import FileSystemStorage


def create_user(sender, instance, signal, created, **kwargs):
    from .models import Disk

    if created:
        disk = Disk(user=instance)
        path = "./files/" + instance.username + "/"
        fs = FileSystemStorage()
        disk.path = path
        disk.save()
