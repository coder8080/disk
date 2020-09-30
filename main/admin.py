from django.contrib import admin
from .models import Disk, PublicFile


@admin.register(Disk)
class DiskAdmin(admin.ModelAdmin):
    list_display = ("user", "size", "allSize",)
    list_display_links = ("user",)
    list_editable = ("allSize",)

    def __str__(self):
        return f"{self.user.username}: {self.size}"


@admin.register(PublicFile)
class PublicFileAdmin(admin.ModelAdmin):
    list_display = ("disk", "url")
    list_display_links = ("disk", "url")

    def __str__(self):
        return f"{self.url}: {self.pathToFile}"


admin.site.site_header = "Администрирование Disk"
admin.site.site_title = "Disk"
