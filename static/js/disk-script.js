function createFolder() {
    /* Функция создания папки */
    //Получаем данные из страницы
    let name = document.getElementById("folderName").value
    // document.getElementById("folderName").value = ""
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
    for (let i = 0; i < input_file.files.length; i++) {
        if (Math.floor(input_file.files[i].size / 1000000) >= 100) {
            //По умолчанию функция alert ждёт, пока пользователь нажмёт кнопку "ОК", а в данном случае нам это ожидание не нужно. Поэтому я и использую timeout
            setTimeout(function () {
                alert("Вы загружаете файл большого объёма. Учтите, что нам понадобится некоторое время на его обработку. Нажмите OK")
            }, 1)
            break
        }
    }
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

            let new_li = document.createElement("li")
            new_li.className = "list-group-item"
            new_li.id = `---folder-div_${name}`

            let final
            if (dir_input_value !== "none") {
                final = `/mydisk/${dir_input_value}\`${name}`
            } else {
                final = `/mydisk/${name}`
            }
            new_li.innerHTML = `
            <div class="fileblock">
                <img src="/static/images/folder.png" alt="Папка" width="60px" height="60px">
                <h4>
                    ${name}
                </h4>
                <a href="${final}" title="открыть">
                    <img src="/static/images/open.png" alt="открыть" width="45px" height="45px">
                </a>
                <a onclick="remove('${dir_input_value}', '${name}', 'delete-folder')" title="удалить">
                    <img src="/static/images/trash.png" alt="удалить" width="40px" height="40px">
                </a>
            </div>
            `
            folders.append(new_li)
        } else if (operation === "delete-folder") {
            //Если мы удаляли папку, то удаляем её как элемент
            let folder_remove = document.getElementById(`---folder-div_${name}`)
            folder_remove.remove()
        } else if (operation === "delete-file") {
            let file_remove = document.getElementById(`---file-div_${name}`)
            file_remove.remove()
        } else if (operation === "make-public") {
            let li = document.getElementById(`---file-div_${name}`)
            let file = li.querySelector("div")
            let a_old = document.getElementById(`---make-public-a_${name}`)
            a_old.remove()
            let a = document.createElement("a")
            response.text().then(text => a.onclick = function () {
                copy(text)
            })
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
                let ul = document.getElementById("files-ul")
                let dir_input_value = document.getElementById("dir").value

                let new_li = document.createElement("li")
                new_li.className = "list-group-item"
                new_li.id = `---file-div_${name[i].name}`
                new_li.innerHTML = `
                <div class="fileblock">
                    <img src="/static/images/file.png" alt="Файл" width="65px" height="65px">
                    <h4>
                        ${name[i].name}
                    </h4>
                    <a href="/download/${dir_input_value}/${name[i].name}" title="скачать" download>
                        <img src="/static/images/download.png" alt="скачать" width="55px" height="55px">
                    </a>
                    <a title="удалить" onclick="remove('${dir_input_value}', '${name[i].name}', 'delete-file')">
                        <img src="/static/images/trash.png" alt="удалить" width="40px" height="40px">
                    </a>
                    <a onclick="makePublic('${name[i].name}', '${dir_input_value}')" title="сделать общедоступным"
                       id="---make-public-a_${name[i].name}">
                        <img src="/static/images/add-link.png" alt="сделать общедоступным" width="40px"
                             height="40px">
                    </a>
                </div>
                `
                ul.append(new_li)
            }
        } else {
            console.log("Не указано действие.")
        }
    } else {
        //Если операцию не удалось выполнить, то отправляем пользователю соответствующие сообщениев
        if (operation === 'upload-files') {
            alert("Не достаточно места на диске.")
        } else {
            alert("Не удалось выполнить операцию. Попробуйте перезагрузить страницу или свяжитесь с системным администратором.")
        }
    }
}

const inputChanged = () => {
    let input = document.getElementById("input-file");
    let label = document.getElementById("nameOfFile");
    let text = "";
    for (let i = 0; i < input.files.length; i++) {
        text += input.files[i].name + "<br>"
    }
    label.innerHTML = text;
}