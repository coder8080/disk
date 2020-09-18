let showed = false;

onload = () => {
    let menu = document.querySelector("#menu");
    menu.addEventListener('click', () => {
        let hidden = document.querySelector("#hidden");
        if (showed == false) {
            hidden.style.left = "0px";
            showed = true;
            document.body.style.overflow = "hidden";
        } else {
            hidden.style.left = "-230px";
            showed = false;
            document.body.style.overflow = "auto";
        }
    })
}

function goToMain() {
    document.location.replace("/");
}

function goToLogin() {
    document.location.replace("/accounts/login");
}

function goToReg() {
    document.location.replace("/accounts/signup");
}

function goToLich() {
    document.location.replace("/main");
}

function goToMyDisk() {
    document.location.replace("/mydisk");
}

function goToOut() {
    document.location.replace("/accounts/logout");
}

function goToAdmin() {
    document.location.replace("/admin")
}

const goToAuthor = () => {
    document.location.replace("/author");
}