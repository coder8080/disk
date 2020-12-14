let theme_input = document.getElementById("theme-switch")
theme_input.addEventListener("change", e => {
    e.preventDefault()
    let theme_input = document.getElementById("theme-switch")
    let csrf_token = document.querySelector("input[name=csrfmiddlewaretoken]").value
    let form_data = new FormData()
    form_data.append("csrfmiddlewaretoken", csrf_token)
    if (theme_input.checked === true) {
        form_data.append("theme", "dark")
        theme_input.checked = true
    } else {
        form_data.append("theme", 'light')
        theme_input.checked = false
    }
    fetch('/change-theme/', {
        method: 'POST',
        body: form_data
    }).then(response => {
        if (response.ok) {
            document.location.reload()
        } else {
            alert("Ошибка.")
        }
    })
})