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
from .models import Disk, PublicFile
# Импортируем штуку чтобы выводить цвета в консоли
from colorama import init, Fore, Style
# Импортируем модель публичного файла
from .models import PublicFile
import hashlib
from cryptography.fernet import Fernet

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
            files = request.FILES.getlist('files')
            print(files)
            # Получаем папку, в которую надо загруить файл
            folder = request.POST.get("dir")
            # Корректируем путь для сохранения файла
            if folder == "none" or folder == "":
                folder = ""
            else:
                __folder = folder.split("`")
                folder = "" + "/".join(__folder) + "/"
            # Получаем нужный диск
            disk = Disk.objects.get(user__username=request.user.username)
            for file in files:
                # Получаем абсолютный путь к будущему файлу
                filename = "./files/" + request.user.username + "/" + folder + "/" + file.name
                # Получаем размер файла, занятое на диске пользователя место и объём диска пользователя
                sizeOfFile = file.size
                sizeDisk = disk.size
                sizeAll = disk.allSize
                if sizeOfFile + sizeDisk <= sizeAll:
                    # Загружаем файл на диск пользователя
                    # encrypted_file = f.encrypt(file.encode())
                    fs.save(name=filename, content=file)
                    new_path = "./media/files/" + request.user.username + "/" + folder + file.name
                    print(new_path)
                    file = open(new_path, "br")
                    data = file.read()
                    file.close()
                    file.close()
                    f = Fernet(request.user.password[34:])
                    encrypted_data = f.encrypt(data)
                    file = open(new_path, "bw")
                    file.write(encrypted_data)
                    file.close()
                    del file
                    # Вычисляем и записываем новое количество занятого места
                    disk.size = get_size(f"./media/files/{request.user.username}")
                    # Сохраняем изменения
                    disk.save()
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
            # Перебрасываем пользователя на страницу с его диском
            return redirect("/mydisk")
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
                dir = ""
            else:
                # Если указана, то меняем символы ` на /
                folder = dir.split("`")
                # И записываем значение в переменную
                dir = "/" + "/".join(folder)

            # Объявляемd переменные для анализа директории
            files_preview_linked = []
            files_preview_unlinked = []
            files_download_linked = []
            files_download_unlinked = []
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
                    # Получаем расширение файла
                    ext = os.path.splitext("./media/files/" + request.user.username + dir + file)[1]
                    try:
                        test = PublicFile.objects.get(
                            pathToFile="./media/files/" + request.user.username + dir + "/" + file)
                        linked = True
                    except:
                        linked = False
                    # Проверяем расширение файла и то, в публичном ли он доступе
                    if ext == ".txt" and linked is True:
                        work = [file, test.url]
                        files_preview_linked += [work]
                    elif ext == ".txt" and linked is False:
                        files_preview_unlinked += [file]
                    elif ext != ".txt" and linked is True:
                        work = [file, test.url]
                        files_download_linked += [work]
                    elif ext != ".txt" and linked is False:
                        files_download_unlinked += [file]
                    else:
                        print(Fore.RED)
                        print("ОШИБКА")
                        print(Style.RESET_ALL)
            except:
                pass
            # Возвращаем пользователю отрендеренный шаблон
            return render(request, 'main/mydisk.html',
                          {"files_download_linked": files_download_linked,
                           "files_download_unlinked": files_download_unlinked,
                           "files_preview_linked": files_preview_linked,
                           "files_preview_unlinked": files_preview_unlinked,
                           "folders": folders,
                           "dir": _dir})
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class RedirectView(View):
    """Это нужно чтобы программа не вылетала, когда пользователь не указал папку для просмотра"""

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
            opened_data = open(filepath, "br").read()
            try:
                PublicFile.objects.get(pathToFile=filepath)
                final_data = opened_data
            except:
                f = Fernet(request.user.password[34:])
                final_data = f.decrypt(opened_data)
            # Получаем сам файл
            # Отправляем файл пользователю
            response = HttpResponse(final_data, 'application')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class RemoveView(View):
    """Для удаления файлов и папок"""

    def post(self, request):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            folder = request.POST.get("folder")
            foldername = request.POST.get("name")
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит удаляемый объект находится в главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то значит удаляемый объект находится в выбранной пользователем директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к удаляемому объекту
            filepath = folder + foldername
            # Подготавливаем ответ
            response = HttpResponse()
            # Получаем диск пользователя
            disk = Disk.objects.get(user__username=request.user.username)
            # Узнаём тип удаляемого объекта
            if os.path.isdir(filepath):
                # Если удаляемый объект является папкой
                # Удаляем папку
                shutil.rmtree(filepath)
                # Записываем статус успешного выполнения запроса в подготовленный ответ
                response.status_code = 200
                # Вычисляем и записываем новый объём занятого места
                disk.size = get_size(f"./media/files/{request.user.username}")
                disk.save()
            elif os.path.isfile(filepath):
                # Если удаляемый объект является файлом
                try:
                    model = PublicFile.objects.get(pathToFile=filepath)
                    model.delete()
                except:
                    pass
                # Удаляем файл
                os.remove(filepath)
                # Записываем статус успешного выполнения запроса в подготовленный ответ
                response.status_code = 200
                # Вычисляем и записываем новый объём занятого места
                disk.size = get_size(f"./media/files/{request.user.username}")
                disk.save()
            else:
                # Если объект не является ни фалом, ни файлом, то записываем статус ошибки в подготовленный ответ
                response.status_code = 405
            # Отправляем ответ пользователю
            return response
        else:
            # Ну тут понятно уже
            return redirect("/accounts/login")


class CreateFolderView(View):
    """Чтобы пользователь мог создавать папки"""

    def post(self, request):
        print(Fore.RED)
        print("create-folder: " + request.user.username)
        print(Style.RESET_ALL)
        name = request.POST.get("name")
        dir = request.POST.get("dir")
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if dir == "none":
                # Если нет, значит создаём в главной директории
                dir = "./media/files/" + request.user.username + "/"
            else:
                # Если да, то создаём в выбранной пользователем директории
                _folder = dir.split("`")
                dir = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к будущемей папке
            path = dir + name
            # Создаём папку
            print(Fore.RED)
            print(path)
            print(Style.RESET_ALL)
            os.mkdir(path)
            # Перенаправляем пользователля обратно на страницу со списком файлов
            response = HttpResponse()
            response.status_code = 200
            return response
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class Preview(View):
    """Предпросмотр файлов"""

    def get(self, request, folder, filename):
        _folder = folder
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
                return render(request, 'main/text_preview.html',
                              {"text": text, "folder": folder, "filename": filename, "editable": True})
            else:
                # return render(request, "main/message.html", {"label": "Предвартельный просмотр не возможен",
                #                                              "text": "Данный файл не поддерживает предварительный "
                #                                                      "просмотр.", "page_name": "страницу моего диска",
                #                                              "page_url": "/mydisk"})
                return render(request, 'main/no_preview.html',
                              {"path": f"download/{_folder}/{filename}", "filename": filename})
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
            # Если нет, то перенаправляем пользователя на страницу входа
            return redirect("/accounts/login")


class PublicFileView(View):
    """Для просмотра общедоступных файлов"""

    def get(self, request, url):
        # Получаем общедоступный объект из базы данных
        object_file = PublicFile.objects.get(url=url)
        # Получаем расширение файла
        ext = os.path.splitext(object_file.pathToFile)[1]
        if ext == ".txt":
            # Если предварительный просмотр возможен, то организуем его
            file = open(object_file.pathToFile, "r")
            data = file.read()
            file.close()
            del file
            return render(request, "main/text_preview.html", {"text": data, "editable": False})
        else:
            # Если нет, то отправляем пользователя на страницу с соответствующим сообщением
            return render(request, 'main/no_preview.html',
                          {"path": f"/download-public/{object_file.url}",
                           "filename": os.path.basename(object_file.pathToFile)})


class DownloadPublicView(View):
    """Загрузка публичный файлов"""

    def get(self, request, code):
        # Получаем объект общедоступного файла из базы данных
        object_file = PublicFile.objects.get(url=code)
        # Получаем данные из файла
        file = open(object_file.pathToFile, "br")
        data = file.read()
        file.close()
        del file
        # Отправляем файл пользователю
        response = HttpResponse(data, "application")
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(object_file.pathToFile)}'
        return response


class CreatePublicFileView(View):
    """Создание публичного файла"""

    def post(self, request):
        # Проверяем, авторизован ли пользователь
        filename = request.POST.get("name")
        folder = request.POST.get("folder")
        _folder = folder
        if request.user.is_authenticated:
            # Проверяем, указана ли папка
            if folder == "none":
                # Если нет, значит выбранный файл в главной директории
                folder = "./media/files/" + request.user.username + "/"
            else:
                # Если да, значит выбранный файл в другой директории
                _folder = folder.split("`")
                folder = "./media/files/" + request.user.username + "/" + "/".join(_folder) + "/"
            # Получаем абсолютный путь к выбранному файлу
            filepath = folder + filename
            f = Fernet(request.user.password[34:])
            file = open(filepath, "br")
            encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
            file = open(filepath, "bw")
            file.write(decrypted_data)
            file.close()
            del file
            model = PublicFile.objects.create(pathToFile=filepath, disk_id=Disk.objects.get(user=request.user).id)
            model.save()
            # Перенаправляем пользователя обратно на страницу со списком файлов
            # response = HttpResponse(model.url)
            # response.status_code = 200
            # return response
            return HttpResponse(model.url)
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")

# class TestView(View):
#     def get(self, request):
#         password = request.user.password
#         # sha = hashlib.sha1(password.encode)
#         # sha = sha.hexdigest()
#         # print(sha)
#         return HttpResponse(password)
