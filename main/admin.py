from django.contrib import admin
from .models import Disk


@admin.register(Disk)
class DiskAdmin(admin.ModelAdmin):
    list_display = ("user", "size", "allSize",)
    list_display_links = ("user",)

    def __str__(self):
        return "test"


admin.site.site_header = "Администрирование Disk"
admin.site.site_title = "Disk"
