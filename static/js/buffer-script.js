function copy(token) {
    try {
        navigator.clipboard.writeText("http://localhost:8000/public/" + token)
            .then(() => {
                alert("Ссылка успешно скопирована в буфер обмена")
            }).catch((err) => {
            alert("Не удалось копировать адрес в буфер обмена. Скопируйте его вручную: http://localhost:8000/public/" + token)
        })
    }
    catch (err) {
        alert("Не удалось скопировать ссылку. Скопируйте её вручную: http://localhost:8000/public/" + token)
    }
}