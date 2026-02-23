"use strict";
async function FetchCreateMemory(title, content) {
    var response = await fetch('/api/add', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'title': title,
            'content': content
        })
    });
    if (response.status != 200) {
        alert("Ошибка во время добавление сна");
    }
    else {
        const result = JSON.parse(await response.text());
        if (!result.success) {
            alert(result.message);
            return;
        }
        else {
            console.log(result.message);
        }
        if (result.content != null) {
            window.location.href = "/memory/" + result.content.id;
        }
    }
}
function CreateMemory() {
    var titleInputInput = document.getElementById("title");
    var contentInput = document.getElementById("content");
    if (!titleInputInput || !contentInput) {
        alert("Неудалось получить один из важных элементов");
        return;
    }
    else {
        const title = titleInputInput.value;
        const content = contentInput.value;
        if (!title) {
            alert("Введите название сна");
            return;
        }
        else if (!content) {
            alert("Введите содержание сна");
            return;
        }
        else {
            FetchCreateMemory(title, content);
        }
    }
}
