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
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                    <g class="icon">
                        <path d="M19.5 20.5h-15A2.47 2.47 0 0 1 2 18.07V5.93A2.47 2.47 0 0 1 4.5 3.5h4.6a1 1 0 0 1 .77.37l2.6 3.18h7A2.47 2.47 0 0 1 22 9.48v8.59a2.47 2.47 0 0 1-2.5 2.43zM4 13.76v4.31a.46.46 0 0 0 .5.43h15a.46.46 0 0 0 .5-.43V9.48a.46.46 0 0 0-.5-.43H12a1 1 0 0 1-.77-.37L8.63 5.5H4.5a.46.46 0 0 0-.5.43z"></path>
                    </g>
                </svg>
                <h4 style="max-width: 50%; overflow: auto">
                    ${name}
                </h4>
                <a href="${final}"
                   title="открыть">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                        <g class="icon">
                            <path d="M20 5a1 1 0 0 0-1-1h-5a1 1 0 0 0 0 2h2.57l-3.28 3.29a1 1 0 0 0 0 1.42 1 1 0 0 0 1.42 0L18 7.42V10a1 1 0 0 0 1 1 1 1 0 0 0 1-1z"></path>
                            <path d="M10.71 13.29a1 1 0 0 0-1.42 0L6 16.57V14a1 1 0 0 0-1-1 1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h5a1 1 0 0 0 0-2H7.42l3.29-3.29a1 1 0 0 0 0-1.42z"></path>
                        </g>
                    </svg>
                </a>
                <a onclick="remove('${dir_input_value}', '${name}', 'delete-folder')" title="удалить">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                        <g class="icon">
                            <path d="M21 6h-5V4.33A2.42 2.42 0 0 0 13.5 2h-3A2.42 2.42 0 0 0 8 4.33V6H3a1 1 0 0 0 0 2h1v11a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V8h1a1 1 0 0 0 0-2zM10 4.33c0-.16.21-.33.5-.33h3c.29 0 .5.17.5.33V6h-4zM18 19a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V8h12z"></path>
                        </g>
                    </svg>
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
            a.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                <g class="icon">
                    <path d="M13.29 9.29l-4 4a1 1 0 0 0 0 1.42 1 1 0 0 0 1.42 0l4-4a1 1 0 0 0-1.42-1.42z"></path>
                    <path d="M12.28 17.4L11 18.67a4.2 4.2 0 0 1-5.58.4 4 4 0 0 1-.27-5.93l1.42-1.43a1 1 0 0 0 0-1.42 1 1 0 0 0-1.42 0l-1.27 1.28a6.15 6.15 0 0 0-.67 8.07 6.06 6.06 0 0 0 9.07.6l1.42-1.42a1 1 0 0 0-1.42-1.42z"></path>
                    <path d="M19.66 3.22a6.18 6.18 0 0 0-8.13.68L10.45 5a1.09 1.09 0 0 0-.17 1.61 1 1 0 0 0 1.42 0L13 5.3a4.17 4.17 0 0 1 5.57-.4 4 4 0 0 1 .27 5.95l-1.42 1.43a1 1 0 0 0 0 1.42 1 1 0 0 0 1.42 0l1.42-1.42a6.06 6.06 0 0 0-.6-9.06z"></path>
                </g>
            </svg>
            `
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
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                        <g class="icon">
                            <path d="M19.74 8.33l-5.44-6a1 1 0 0 0-.74-.33h-7A2.53 2.53 0 0 0 4 4.5v15A2.53 2.53 0 0 0 6.56 22h10.88A2.53 2.53 0 0 0 20 19.5V9a1 1 0 0 0-.26-.67zM17.65 9h-3.94a.79.79 0 0 1-.71-.85V4h.11zm-.21 11H6.56a.53.53 0 0 1-.56-.5v-15a.53.53 0 0 1 .56-.5H11v4.15A2.79 2.79 0 0 0 13.71 11H18v8.5a.53.53 0 0 1-.56.5z"></path>
                        </g>
                    </svg>
                    <h4 style="max-width: 50%; overflow: auto">
                        ${name[i].name}
                    </h4>
                    <a href="/download/${dir_input_value}/${name[i].name}" title="скачать" download>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                            <g class="icon">
                                <rect width="24" height="24" opacity="0"></rect>
                                <rect x="4" y="18" width="16" height="2" rx="1" ry="1"></rect>
                                <rect x="3" y="17" width="4" height="2" rx="1" ry="1"
                                      transform="rotate(-90 5 18)"></rect>
                                <rect x="17" y="17" width="4" height="2" rx="1" ry="1"
                                      transform="rotate(-90 19 18)"></rect>
                                <path d="M12 15a1 1 0 0 1-.58-.18l-4-2.82a1 1 0 0 1-.24-1.39 1 1 0 0 1 1.4-.24L12 12.76l3.4-2.56a1 1 0 0 1 1.2 1.6l-4 3a1 1 0 0 1-.6.2z"></path>
                                <path d="M12 13a1 1 0 0 1-1-1V4a1 1 0 0 1 2 0v8a1 1 0 0 1-1 1z"></path>
                            </g>
                        </svg>
                    </a>
                    <a title="удалить" onclick="remove('${dir_input_value}', '${name[i].name}', 'delete-file')">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                            <g class="icon">
                                <path d="M21 6h-5V4.33A2.42 2.42 0 0 0 13.5 2h-3A2.42 2.42 0 0 0 8 4.33V6H3a1 1 0 0 0 0 2h1v11a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V8h1a1 1 0 0 0 0-2zM10 4.33c0-.16.21-.33.5-.33h3c.29 0 .5.17.5.33V6h-4zM18 19a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V8h12z"></path>
                            </g>
                        </svg>
                    </a>
                    <a onclick="makePublic('${name[i].name}', '${dir_input_value}')" title="сделать общедоступным"
                       id="---make-public-a_{{ file }}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="65px">
                            <g class="icon">
                                <path d="M8 12a1 1 0 0 0 1 1h6a1 1 0 0 0 0-2H9a1 1 0 0 0-1 1z"></path>
                                <path d="M9 16H7.21A4.13 4.13 0 0 1 3 12.37 4 4 0 0 1 7 8h2a1 1 0 0 0 0-2H7.21a6.15 6.15 0 0 0-6.16 5.21A6 6 0 0 0 7 18h2a1 1 0 0 0 0-2z"></path>
                                <path d="M23 11.24A6.16 6.16 0 0 0 16.76 6h-1.51C14.44 6 14 6.45 14 7a1 1 0 0 0 1 1h1.79A4.13 4.13 0 0 1 21 11.63 4 4 0 0 1 17 16h-2a1 1 0 0 0 0 2h2a6 6 0 0 0 6-6.76z"></path>
                            </g>
                        </svg>
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