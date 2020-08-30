# Импортируем штуку для работы с файлами
from django.core.files.storage import FileSystemStorage
# Импортируем другую штуку для работы с файлами
import os
# Импортируем инструмент для удаления папоу со всеми вложенными файлами
import shutil
# Импортируем шибкую штуку для отправки данных пользователю
from django.http import HttpResponse
# Имопртируем возможность рендерить шаблоны и перекидывать пользователя на другие странички
from django.shortcuts import render, redirect
# Импортируем класс для вообще работы всего кода
from django.views import View
# Импортируем нашу модель диска
from .models import Disk


class MainView(View):
    """Главная страница"""

    def get(self, request):
        return render(request, 'main/index.html')


class AuthorView(View):
    """Страница 'обо мне' """

    def get(self, request):
        return render(request, "main/author.html")


class UploadView(View):
    """Страница для загрузки файлов"""

    def get(self, request):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Получаем папку, в которую пользователь зочет загрузить файл
            dir = request.GET.get("dir")
            # Хз зачем я написал этот if но без него не работает
            if dir == "":
                dir = "none"
            return render(request, 'main/upload.html', {"dir": dir})
        else:
            return redirect("/accounts/login")

    """Загрузка файла"""

    def post(self, request):
        # Смотрим, авторизован ли пользователь
        if request.user.is_authenticated:
            # Получаем файл
            file = request.FILES['file']
            # Получаем папку, в которую надо загруить файл
            folder = request.POST.get("dir")
            # Получаем инструмент для работы с файлами
            fs = FileSystemStorage()
            # Корректируем путь для сохранения файла
            if folder == "none" or folder == "":
                folder = ""
            else:
                __folder = folder.split("`")
                folder = "" + "/".join(__folder) + "/"
            # Получаем абсолютный путь к будущему файлу
            filename = fs.save(name="./files/" + request.user.username + "/" + folder + "/" + file.name, content=file)
            # Прибавляем к диску пользователя вес файла (пока этот код не нужен, можно закомментировать)
            # Получаем нужный диск
            disk = Disk.objects.get(user__username=request.user.username)
            # Получаем размер файла
            sizeOfFile = fs.size(filename)
            # Добавляем размер файла к общему размеру диска
            disk.size += sizeOfFile
            # Сохраняем изменения
            disk.save()
            # Перебрасываем пользователя на страницу с его диском
            return redirect("/mydisk")
        else:
            # Если не авторизован, то перебрасываем на страницу входа
            return redirect("/accounts/login")


class PrivateOfficeView(View):
    """Личный кабинет пользователя"""

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'main/main.html')
        else:
            # Если не авторизован, то перенаправляем на страницу входа
            return redirect("/accounts/login")


class DiskView(View):
    """Обрабатываем get запрос на страницу со списком файлов"""

    def get(self, request, dir):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Оставляем исзодное значение переменной dir в отдельной переменной
            _dir = dir
            # Если папка не указана, меняем значение переменной на /
            if dir == "none":
                dir = "/"
            else:
                # Если указана, то меняем символы ` на /
                folder = dir.split("`")
                print(folder)
                # И записываем значение в переменную
                dir = "/" + "/".join(folder)

            # Объявляем переменные для анализа директории
            files = []
            folders = []
            folder = []
            # Сканируем директорию
            for i in os.walk("./media/files/" + request.user.username + dir):
                folder += [i]

            # Пытаемся получить вложенные папки
            try:
                folders = folder[0][1]
            except:
                pass

            # Пытаемся получить вложенные файлы
            try:
                files = folder[0][2]
            except:
                pass
            # Возвращаем пользователю отрендеренный шаблон
            return render(request, 'main/mydisk.html', {"files": files, "folders": folders, "dir": _dir})
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class RedirectView(View):
    """Без этой фигни ничего не будет работать"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/mydisk/none")
        else:
            return redirect("/accounts/login")


class DownloadView(View):
    """Это нужно чтобы пользователь мог скачивать файлы"""

    def get(self, request, folder, filename):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит скачиваем из главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то скачиваем из выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к будущему файлу
            filepath = folder + filename
            # Получаем сам файл
            data = open(filepath, "br").read()
            # # Готовим ответ пользователю
            # response = HttpResponse(data)
            # response['Content-Disposition'] = f'attachment; filename="{filename}"'
            # Отправляем файл пользователю
            return HttpResponse(data, "application")
        else:
            return redirect("/accounts/login")


class RemoveView(View):
    def get(self, request, folder, filename):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит скачиваем из главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то скачиваем из выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к будущему файлу
            filepath = folder + filename
            # Получаем сам файл
            # data = open(filepath, "br").read()
            os.remove(filepath)
            # # Готовим ответ пользователю
            # response = HttpResponse(data)
            # response['Content-Disposition'] = f'attachment; filename="{filename}"'
            # Отправляем файл пользователю
            return redirect("/mydisk")
        else:
            return redirect("/accounts/login")


class RemoveFolderView(View):
    def get(self, request, folder, foldername):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит скачиваем из главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то скачиваем из выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к будущему файлу
            filepath = folder + foldername
            # Получаем сам файл
            # data = open(filepath, "br").read()
            shutil.rmtree(filepath)
            # # Готовим ответ пользователю
            # response = HttpResponse(data)
            # response['Content-Disposition'] = f'attachment; filename="{filename}"'
            # Отправляем файл пользователю
            return redirect("/mydisk")
        else:
            return redirect("/accounts/login")


class CreateFolderView(View):
    def post(self, request):
        folder = request.POST.get("folder")
        foldername = request.POST.get("folderName")
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит скачиваем из главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то скачиваем из выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к будущему файлу
            path = folder + foldername
            # Получаем сам файл
            os.mkdir(path)
            # # Готовим ответ пользователю
            # response = HttpResponse(data)
            # response['Content-Disposition'] = f'attachment; filename="{filename}"'
            # Отправляем файл пользователю
            return redirect("/mydisk")
        else:
            return redirect("/accounts/login")
