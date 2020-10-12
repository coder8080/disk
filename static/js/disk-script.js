function initForms() {
    let new_folder_form = document.getElementById("new-folder-form")
    new_folder_form.addEventListener('submit', (e) => {
        e.preventDefault()
        createFolder()
    })
    let upload_file_form = document.getElementById("upload-file-form")
    upload_file_form.addEventListener('submit', e => {
        e.preventDefault()
        uploadFiles()
    })
}

function createFolder() {
    /* Функция создания папки */
    //Получаем данные из страницы
    let name = document.getElementById("folderName").value
    document.getElementById("folderName").value = ""
    let dir = document.getElementById("dir").value
    let csrf_token = document.querySelector("input[name=csrfmiddlewaretoken]").value
    let form_data = new FormData()
    form_data.append("name", name)
    form_data.append("dir", dir)
    form_data.append("csrfmiddlewaretoken", csrf_token)
    //Отправляем на сервер запрос на создание
    fetch('/create-folder', {
        method: "POST",
        body: form_data
    }).then(response => sayToUser(response, "create", name))
}

function remove(dir, name, action) {
    /* Функция удаление папки */
    //Спрашиваем пользователя, точно ли он хочет выполнить действие
    let result = confirm("Вы точно хотите удалить объект?")
    if (result === true) {
        //Если вернулся положительный ответ, то получаем данные из страницы
        let csrf_token = document.querySelector("input[name=csrfmiddlewaretoken]").value
        let form_data = new FormData()
        form_data.append("name", name)
        form_data.append("folder", dir)
        form_data.append("csrfmiddlewaretoken", csrf_token)
        //Отправляем на сервер запрос на удаление
        fetch("/delete", {
            method: "POST",
            body: form_data
        }).then(response => sayToUser(response, action, name))
    }
//    Если пользователь ответил отрицательно, ничего не делаем
}

function makePublic(name, dir) {
    let result = confirm("Вы точно хотите сделать файл публичным?")
    if (result === true) {
        let csrf_token = document.querySelector("input[name=csrfmiddlewaretoken]").value
        let form_data = new FormData()
        form_data.append("name", name)
        form_data.append("folder", dir)
        form_data.append("csrfmiddlewaretoken", csrf_token)
        fetch("/make-public", {
            method: "POST",
            body: form_data
        }).then(response => sayToUser(response, "make-public", name))
    }
}

function uploadFiles() {
    /* Функция загрузки файлов */
    let upload_file_form = document.getElementById("upload-file-form")
    let input_file = document.getElementById("input-file")
    fetch('/upload', {
        method: "POST",
        body: new FormData(upload_file_form)
    }).then(response => sayToUser(response, "upload-files", input_file.files))
}

function sayToUser(response, operation, name) {
    /* Функия вывода результата запроса */
    if (response.status === 200) {
        //Если операция успешно выполнена, то смотрим, какую операцию мы выполняяли
        if (operation === "create") {
            //Если мы создавали папку, то добавляем её как элемент на страницу
            let dir_input_value = document.getElementById("dir").value

            let folders = document.getElementById("folders")

            let new_folder = document.createElement("div")
            new_folder.className = "fileblock"
            new_folder.id = `---folder-div_${name}`

            let img = document.createElement("img")
            img.src = "/static/images/folder.png"
            img.height = 60
            img.width = 60
            img.alt = "Папка"

            let h2 = document.createElement("h2")
            let text_h2 = document.createTextNode(name)
            h2.append(text_h2)

            let a_open = document.createElement("a")

            if (dir_input_value === "none") {
                a_open.href = `/mydisk/${name}`
            } else {
                a_open.href = `/mydisk/${dir_input_value}\`${name}`
            }
            let img_open = document.createElement("img")
            img_open.src = "/static/images/open.png"
            img_open.alt = "открыть"
            img_open.width = 45
            img_open.height = 45
            a_open.append(img_open)

            let a_remove = document.createElement("a")
            a_remove.onclick = () => {
                remove(dir_input_value, name, 'delete-folder')
            }
            let img_remove = document.createElement("img")
            img_remove.src = "/static/images/trash.png"
            img_remove.alt = "удалить"
            img_remove.width = 40
            img_remove.height = 40
            img_remove.style = "cursor: pointer;"
            a_remove.append(img_remove)

            new_folder.append(img)
            new_folder.append(h2)
            new_folder.append(a_open)
            new_folder.append(a_remove)

            folders.append(new_folder)

            //И скрываем диалоговое окно с именем папки
            hide()
        } else if (operation === "delete-folder") {
            //Если мы удаляли папку, то удаляем её как элемент
            let folder_remove = document.getElementById(`---folder-div_${name}`)
            console.log(folder_remove)
            folder_remove.remove()
        } else if (operation === "delete-file") {
            let file_remove = document.getElementById(`---file-div_${name}`)
            file_remove.remove()
        } else if (operation === "make-public") {
            let file = document.getElementById(`---file-div_${name}`)
            let a_old = document.getElementById(`---make-public-a_${name}`)
            a_old.remove()
            let a = document.createElement("a")
            response.text().then(text => a.onclick = function(){copy(text)})
            let img = document.createElement("img")
            img.src = "/static/images/link.png"
            img.width = 40
            img.height = 40
            img.style = "cursor: pointer;"
            img.alt = "копировать ссылку"
            a.append(img)
            file.append(a)
        } else if (operation === "upload-files") {
            for (let i = 0; i < name.length; i++) {
                let files = document.getElementById("fileBox")
                let dir_input_value = document.getElementById("dir").value

                let new_file = document.createElement("div")
                new_file.className = "fileblock"
                new_file.id = `---file-div_${name[i].name}`

                let img = document.createElement("img")
                img.src = "/static/images/file.png"
                img.height = 65
                img.width = 65
                img.alt = "Файл"

                let h2 = document.createElement("h2")
                let text_h2 = document.createTextNode(name[i].name)
                h2.append(text_h2)

                let a_download = document.createElement("a")
                a_download.href = `/download/${dir_input_value}/${name[i].name}`

                let img_download = document.createElement("img")
                img_download.src = "/static/images/download.png"
                img_download.alt = "скачать"
                img_download.width = 55
                img_download.height = 55
                a_download.append(img_download)

                let a_remove = document.createElement("a")
                a_remove.onclick = () => {
                    remove(dir_input_value, name[i].name, 'delete-file')
                }
                let img_remove = document.createElement("img")
                img_remove.src = "/static/images/trash.png"
                img_remove.alt = "удалить"
                img_remove.width = 40
                img_remove.height = 40
                img_remove.style = "cursor: pointer;"
                a_remove.append(img_remove)

                let a_make_public = document.createElement("a")
                a_make_public.onclick = () => {
                    makePublic(name[i].name, dir_input_value)
                }
                a_make_public.id = `---make-public-a_${name[i].name}`
                let img_make_public = document.createElement("img")
                img_make_public.src = "/static/images/add-link.png"
                img_make_public.alt = "сделать общедоступным"
                img_make_public.width = 40
                img_make_public.height = 40
                img_make_public.style = "cursor: pointer;"
                a_make_public.append(img_make_public)

                new_file.append(img)
                new_file.append(h2)
                new_file.append(a_download)
                new_file.append(a_remove)
                new_file.append(a_make_public)

                files.append(new_file)
                hide()
            }
        } else {
            console.log("Не указано действие.")
        }
    } else {
        //Если операцию не удалось выполнить, то отправляем пользователю соответствующие сообщениев
        alert("Не удалось выполнить операцию. Попробуйте перезагрузить страницу или свяжитесь с системным администратором.")
    }
}

const createDir = () => {
    let parent = document.getElementById("parent-create-folder")
    parent.style.display = "flex";
}

const showUploadForm = () => {
    let parent = document.getElementById("parent-upload-files")
    parent.style.display = "flex";
}

const hide = () => {
    let parents = document.getElementsByClassName("parent")
    for (let i = 0; i < parents.length; i++) {
        parents[i].style.display = "none";
    }
}

const inputChanged = () => {
    let input = document.getElementById("input-file");
    let label = document.getElementById("nameOfFile");
    let text = "";
    for (let i = 0; i < input.files.length; i++) {
        console.log(input.files[i].name)
        text += input.files[i].name + "<br>"
    }
    console.log(text);
    label.innerHTML = text;
}