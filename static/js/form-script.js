let placeholder1 = document.querySelector("#place1");
if (placeholder1 != undefined) {
    placeholder1.addEventListener('click', () => {
        let input1 = document.querySelector("#input1");
        input1.focus();
    })
}
else {
    console.log("placeholder1 is undefined");
}

let placeholder2 = document.querySelector("#place2");
if (placeholder2 != undefined) {
    placeholder2.addEventListener('click', () => {
        let input2 = document.querySelector("#input2");
        input2.focus();
    })
}
else {
    console.log("placeholder2 is undefined");
}