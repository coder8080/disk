import os


def create_user(sender, instance, signal, created, **kwargs):
    from .models import Disk

    if created:
        disk = Disk(user=instance)
        path = "./files/" + instance.username + "/"
        path_dir = "./media/files/" + instance.username + "/"
        os.mkdir(path_dir)
        disk.path = path
        disk.save()
