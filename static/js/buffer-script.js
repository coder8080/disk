let host = "localhost:8000"

function copy(token) {
    try {
        navigator.clipboard.writeText(`http://${host}/public/` + token)
            .then(() => {
                alert("Ссылка успешно скопирована в буфер обмена")
            }).catch((err) => {
            alert(`Не удалось копировать адрес в буфер обмена. Скопируйте его вручную: http://${host}/public/` + token)
        })
    }
    catch (err) {
        alert(`Не удалось скопировать ссылку. Скопируйте её вручную: http://${host}/public/` + token)
    }
}