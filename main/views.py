# Импортируем инструмент для работы с файлами
from django.core.files.storage import FileSystemStorage
# Импортируем другую штуку для работы с файлами
import os
# Импортируем инструмент для удаления папки со всеми вложенными файлами
import shutil
# Импортируем штуку для отправки данных пользователю
from django.http import HttpResponse, StreamingHttpResponse
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
# Импортируем инструменты шифрования
import pyAesCrypt
import io

# Запускаем возможность вывода цветов в консоль
init()


# Функция для подсчёта размера папки
def get_size(path):
    # Объявляем переменную в которой будет находится итоговый результат
    size = 0
    # Цикл для подсчёта размера всех файлов
    # Получаем все файлы находящиеся в рассматриваемой папке
    for full_path, dirs_names, files_names in os.walk(path):
        # Цикл для работы с полученными файлами
        for f in files_names:
            # Получаем полный путь к файлу
            fp = os.path.join(full_path, f)
            # Прибавляем к размеру папки размер рассматриваемого файла
            size += os.path.getsize(fp)
    # Возвращаем результат
    return size


# Функция для шифрования файла
def encrypt(filename, folder, key):
    # Генерируем временное имя файла
    temp_filename = "_" + filename
    while os.path.exists(folder + temp_filename):
        temp_filename = "_" + filename \
            # Шифруем файл
    pyAesCrypt.encryptFile(folder + filename, folder + temp_filename, key, 1024)
    # Удаляем исходный файл и заменям его зашифрованным
    os.remove(folder + filename)
    os.rename(folder + temp_filename, folder + filename)


# Функция для расшифровки файла
def decrypt(filename, key):
    # Создаём переменную в которой окажется зашифрованная информация
    data = io.BytesIO()
    # Открываем нужный файл
    with open(filename, "br") as fIn:
        # Шифруем открытый файл в переменную
        pyAesCrypt.decryptStream(fIn, data, key, 1024, os.path.getsize(filename))
    return data.getvalue()


class MainView(View):
    """Главная страница"""

    def get(self, request):
        return render(request, 'main/index.html')


class UploadView(View):
    """Загрузка файла"""

    def post(self, request):
        # Начинаем готовить ответ пользователю
        response = HttpResponse()
        # Смотрим, авторизован ли пользователь
        if request.user.is_authenticated:
            # Получаем инструмент для работы с файлами
            fs = FileSystemStorage()
            # Получаем файлы
            files = request.FILES.getlist('files')
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
                filename = "./files/" + request.user.username + "/" + folder + file.name
                # Получаем размер файла, занятое на диске пользователя место и объём диска пользователя
                size_of_file = file.size
                size_of_disk = disk.size
                size_all = disk.allSize
                # Смотрим, хватит ли места на диске пользователя для загрузки файла
                if size_of_file + size_of_disk <= size_all:
                    # Загружаем файл на диск пользователя
                    fs.save(name=filename, content=file)
                    # Получаем путь к загруженному файлу
                    key = request.user.password[34:]
                    # Шифруем файл
                    encrypt(file.name, "./media/files/" + request.user.username + "/", key)
                    # Вычисляем и записываем новое количество занятого
                    disk.size = get_size(f"./media/files/{request.user.username}")
                    # Сохраняем изменения
                    disk.save()
                else:
                    # Если у пользователя не хватило места
                    print(Fore.RED)
                    print(f"У пользователя {request.user.username} закончилось место на диске")
                    print(Style.RESET_ALL)
                    response = HttpResponse()
                    response.status_code = 404
                    return response
            # Записываем успешный результат в ответ
            response.status_code = 200
        else:
            # Записываем неуспешный результат в ответ
            response.status_code = 404
        """Почему мы возвращаем только status_code, а не страницу либо переадресацию? Если вы внимательно изучите 
        код, то узнаете, что сэтой страницой я общаюсь только через функцию fetch, из которой намного удобнее 
        работать со статусами запроса, а не возвращаемым текстом и другими типами информации."""
        return response


class PrivateOfficeView(View):
    """Личный кабинет пользователя"""

    def get(self, request):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # Получаем диск пользователя
            disk = Disk.objects.get(user__username=request.user.username)
            # Получаем, сколько процетов места занято на диске пользователя
            pct = ((disk.size / 1000000) / (disk.allSize / 1000000)) * 100
            # Отправляем шаблон с данными пользователю
            return render(request, 'main/main.html', {"busy": round(disk.size / 1000000),
                                                      "all": round(disk.allSize / 1000000),
                                                      "free": round((disk.allSize - disk.size) / 1000000),
                                                      "pct": round(pct),
                                                      "theme": request.user.disk_set.all()[0].theme
                                                      })
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

            # Объявляем переменные для анализа директории
            files_linked = []
            files_unlinked = []
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
                    # Проверяем, находится ли файл в публичном доступе
                    try:
                        model = PublicFile.objects.get(
                            pathToFile="./media/files/" + request.user.username + dir + "/" + file)
                        linked = True
                    except:
                        linked = False
                    if linked is True:
                        list_to_add = [file, model.url]
                        files_linked += [list_to_add]
                    elif linked is False:
                        files_unlinked += [file]
                    else:
                        print(Fore.RED)
                        print("ОШИБКА")
                        print(Style.RESET_ALL)
            except:
                pass
            # Возвращаем пользователю отрендеренный шаблон
            return render(request, 'main/mydisk.html',
                          {"files_linked": files_linked,
                           "files_unlinked": files_unlinked,
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
            # Получаем абсолютный путь к скачиваемому файлу
            filepath = folder + filename
            password = request.user.password
            final_data = decrypt(filepath, password[34:])
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
                # Используем shutil, потому что os отказывается удалять папку если в ней есть файлы
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
                print(disk.size)
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
    """Создание папок"""

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
            # Получаем абсолютный путь к будущей папке
            path = dir + name
            # Создаём папку
            os.mkdir(path)
            # Отправляем пользователю информацию об успелном выполнении запроса
            response = HttpResponse()
            response.status_code = 200
            return response
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


# Следующий далее закомментированный код - страрая фича, которой сейчас уже нет, но код я оставил на всякий случай (
# вдруг захочется вернуть эту возможность)

# class ReWriteView(View):
#     """Запись изменений, внесённых пользователем в текстовый файл на странице предпросмотра"""
#
#     def post(self, request):
#         # Получаем данные
#         folder = request.POST.get("folder")
#         filename = request.POST.get("filename")
#         text = request.POST.get("text")
#         # Проверяем, авторизован ли пользователь
#         if request.user.is_authenticated:
#             # Запусываем данные в файл
#             filepath = folder + filename
#             file = open(filepath, "w")
#             file.write(text)
#             file.close()
#             # Перенаправляем пользователля обратно на страницу со списком файлов
#             return redirect("/mydisk")
#         else:
#             # Если нет, то перенаправляем пользователя на страницу входа
#             return redirect("/accounts/login")


class PublicFileView(View):
    """Для просмотра общедоступных файлов"""

    def get(self, request, url):
        # Получаем общедоступный объект из базы данных
        object_file = PublicFile.objects.get(url=url)
        # Отправляем пользователя на страницу с соответствующим сообщением
        return render(request, 'main/public_file.html',
                      {"path": f"/download-public/{object_file.url}",
                       "filename": os.path.basename(object_file.pathToFile)})


class DownloadPublicView(View):
    """Загрузка публичный файлов"""

    def get(self, request, code):
        # Получаем объект общедоступного файла из базы данных
        object_file = PublicFile.objects.get(url=code)
        # Расшифровываем файл
        key = object_file.disk.user.password[34:]
        data = decrypt(object_file.pathToFile, key)
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
            model = PublicFile.objects.create(pathToFile=filepath, disk_id=Disk.objects.get(user=request.user).id)
            model.save()
            # Перенаправляем пользователя обратно на страницу со списком файлов
            return HttpResponse(model.url)
        else:
            # Если нет, то перебрасываем его на страницу входа
            return redirect("/accounts/login")


class ChangeThemeView(View):
    """Смена темы оформления"""

    def post(self, request):
        # Получаем тему на которую хочет переключиться пользователь
        theme = request.POST.get('theme')
        disk = request.user.disk_set.all()[0]
        # Устанавливаем нужную тему
        disk.theme = theme
        disk.save()
        # Отправляем информацию об успешном выполнении запроса
        response = HttpResponse()
        response.status_code = 200
        return response
