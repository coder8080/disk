# Импортируем штуку для работы с файлами
from django.core.files.storage import FileSystemStorage
# Импортируем другую штуку для работы с файлами
import os
# Импортируем инструмент для удаления папки со всеми вложенными файлами
import shutil
# Импортируем штуку для отправки данных пользователю
from django.http import HttpResponse
# Имопртируем возможность рендерить шаблоны и перекидывать пользователя на другие странички
from django.shortcuts import render, redirect
# Импортируем класс для вообще работы всего кода
from django.views import View
# Импортируем нашу модель диска
from .models import Disk
# Импортируем штуку чтобы выводить цвета в консоли
from colorama import init, Fore, Style

# Запускаем возможность вывода цветов в консоль
init()


# Функция для подсчёта размера папки
def get_size(path):
    # Объявляем переменную в которой будет находится итоговый результат
    size = 0
    # Цикл для подсчёта размера всех файлов
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            size += os.path.getsize(fp)
    # Возвращаем результат
    return size


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
            # Получаем инструмент для работы с файлами
            fs = FileSystemStorage()
            # Получаем файл
            file = request.FILES['file']
            # Получаем папку, в которую надо загруить файл
            folder = request.POST.get("dir")
            # Корректируем путь для сохранения файла
            if folder == "none" or folder == "":
                folder = ""
            else:
                __folder = folder.split("`")
                folder = "" + "/".join(__folder) + "/"
            # Получаем абсолютный путь к будущему файлу
            filename = "./files/" + request.user.username + "/" + folder + "/" + file.name
            # Получаем нужный диск
            disk = Disk.objects.get(user__username=request.user.username)
            # Получаем размер файла, занятое на диске пользователя место и объём диска пользователя
            sizeOfFile = file.size
            sizeDisk = disk.size
            sizeAll = disk.allSize
            if sizeOfFile + sizeDisk <= sizeAll:
                # Загружаем файл на диск пользователя
                fs.save(name=filename, content=file)
                # Добавляем размер файла к общему размеру диска
                disk.size += sizeOfFile
                # Сохраняем изменения
                disk.save()
                # Перебрасываем пользователя на страницу с его диском
                return redirect("/mydisk")
            else:
                print(Fore.RED)
                print(f"У пользователя {request.user.username} закончилось место на диске")
                print(Style.RESET_ALL)
                return render(request, 'main/message.html', {
                    "label": "Недостаточно места",
                    "text": "У вас недостаточно места на диске, чтобы загрузить этот файл. Попробуйте удалить с диска "
                            "файлы, которыми вы уже не пользуетесь. Если вам нужно больше места, то свяжитесь с "
                            "администратором сайта. Скоро будут добавлены промокоды на увеличение места.",
                    "page_name": "главную", "page_url": "/"})
        else:
            # Если не авторизован, то перебрасываем на страницу входа
            return redirect("/accounts/login")


class PrivateOfficeView(View):
    """Личный кабинет пользователя"""

    def get(self, request):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Получаем диск пользователя
            disk = Disk.objects.get(user__username=request.user.username)
            # Отправляем шаблон с данными пользователю
            return render(request, 'main/main.html', {"size": round((disk.allSize - disk.size) / 1000000),
                                                      "allSize": round(disk.allSize / 1000000)})
        else:
            # Если не авторизован, то перенаправляем на страницу входа
            return redirect("/accounts/login")


class DiskView(View):
    """Страница просмотра файлов"""

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
            files_preview = []
            files_download = []
            folders = []
            folder = []
            # Сканируем директорию
            for i in os.walk("./media/files/" + request.user.username + dir):
                folder += [i]

            try:
                # Пытаемся получить вложенные папки
                folders = folder[0][1]
            except:
                pass

            try:
                # Пытаемся получить вложенные файлы
                files = folder[0][2]
                # Сортируем файлы
                for file in files:
                    testpath, ext = os.path.splitext("./media/files/" + request.user.username + dir + file)
                    # Проверяем расширение файла
                    if ext == ".txt":
                        # Если оно .txt, то относим файл к группе с возможностью предворительного просмотра
                        files_preview += [file]
                    else:
                        # Если другое, то к группе без такой возможности
                        files_download += [file]
            except:
                pass
            # Возвращаем пользователю отрендеренный шаблон
            return render(request, 'main/mydisk.html',
                          {"files_download": files_download, "files_preview": files_preview, "folders": folders,
                           "dir": _dir})
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
            # Отправляем файл пользователю
            return HttpResponse(data, "application")
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class RemoveView(View):
    """Это чтобы пользователь мог удалять файлы"""

    def get(self, request, folder, filename):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит удаляем из главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то удаляем из выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к удаляемому файлу
            filepath = folder + filename
            # Получаем размер файла
            size = os.path.getsize(filepath)
            # Получаем диск пользователя
            disk = Disk.objects.get(user__username=request.user.username)
            # Вычитаем размер файла из занятого места на диске пользователя
            disk.size -= size
            # Сохраняем изменения
            disk.save()
            # Удаляем файл
            os.remove(filepath)
            # Перенаправляем пользователля обратно на страницу со списком файлов
            return redirect("/mydisk")
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class RemoveFolderView(View):
    """Для удаления папок"""

    def get(self, request, folder, foldername):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит удаляемая папка находится в главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то значит удаляемая папка находится в выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к удаляемой папке
            filepath = folder + foldername
            # Получаем размер папки
            size_of_folder = get_size(filepath)
            # Вычитаем его из диска пользователя
            disk = Disk.objects.get(user__username=request.user.username)
            disk.size -= size_of_folder
            disk.save()
            # Удаляем папку
            shutil.rmtree(filepath)
            # Перенаправляем пользователя обратно на страницу со списком файлов
            return redirect("/mydisk")
        else:
            return redirect("/accounts/login")


class CreateFolderView(View):
    """Чтобы пользователь мог создавать папки"""

    def post(self, request):
        folder = request.POST.get("folder")
        foldername = request.POST.get("folderName")
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит создаём в главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то создаём в выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к будущемей папке
            path = folder + foldername
            # Создаём папку
            os.mkdir(path)
            # Перенаправляем пользователля обратно на страницу со списком файлов
            return redirect("/mydisk")
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class PreView(View):
    """Предпросмотр файлов"""

    def get(self, request, folder, filename):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Метод аналогичен прошлым вьюшкам, смотрите там. Мне лень нормально писать комментарии
                folder = "./media/files/" + request.user.username + "/"
            else:
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            filepath = folder + filename
            # Получаем разрешение файла
            file_ext = os.path.splitext(filepath)[1]
            if file_ext == ".txt":
                # Если оно .txt, то получаем содержимое файла
                file = open(filepath)
                text = file.read()
                file.close()
                # Перенаправляем пользователля на страницу с предпросмотром
                return render(request, 'main/text_preview.html', {"text": text, "folder": folder, "filename": filename})
            else:
                # Если другое, то говорим пользователю что данное расширение не поддерживает предворительный просмотр
                return render(request, "main/message.html", {"label": "Предвартельный просмотр не возможен",
                                                             "text": "Данный файл не поддерживает предварительный "
                                                                     "просмотр.", "page_name": "страницу моего диска",
                                                             "page_url": "/mydisk"})
        else:
            # Если оно .txt
            return redirect("/accounts/login")


class ReWriteView(View):
    """Запись изменений, внесённых пользователем в текстовый файл на странице предпросмотра"""

    def post(self, request):
        # Получаем данные
        folder = request.POST.get("folder")
        filename = request.POST.get("filename")
        text = request.POST.get("text")
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Запусываем данные в файл
            filepath = folder + filename
            file = open(filepath, "w")
            file.write(text)
            file.close()
            # Перенаправляем пользователля обратно на страницу со списком файлов
            return redirect("/mydisk")
        else:
            # Если оно .txt
            return redirect("/accounts/login")
