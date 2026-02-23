"use strict";
var href = document.location.href;
var splitHref = href.split("/");
const ID = splitHref[splitHref.length - 1];
function formatDate(dateString) {
    const date = new Date(dateString);
    const months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];
    const year = date.getFullYear();
    const month = months[date.getMonth()];
    const day = date.getDate();
    // Получаем часы и минуты в локальном времени
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${year} года ${day} ${month} в ${hours}:${minutes}`;
}
async function getBot() {
    try {
        var response = await fetch("/api/bot", {
            headers: {
                'accept': 'application/json'
            }
        });
        if (response.status == 200) {
            return await response.text();
        }
    }
    catch (error) {
        console.log(error);
    }
    return null;
}
async function LoadMemory(id) {
    var response = await fetch(`/api/memory/${id}`, {
        headers: {
            'accept': 'application/json'
        }
    });
    if (response.status != 200) {
        return;
    }
    const result = JSON.parse(await response.text());
    if (!result.success) {
        console.log("Not Found!");
        alert(result.message);
        window.location.href = "/";
        return;
    }
    else if (!result.content) {
        alert("No content");
        return;
    }
    const mainBox = document.querySelector("main");
    if (!mainBox) {
        alert("Не удалось найти элемент main");
        return;
    }
    else {
        var h1 = mainBox.querySelector("h1");
        h1 === null || h1 === void 0 ? void 0 : h1.remove();
    }
    const infoBox = document.createElement("div");
    const title = document.createElement("h1");
    title.textContent = result.content.title;
    document.title = result.content.title;
    const content = document.createElement("p");
    content.setAttribute("class", "content-text");
    content.textContent = result.content.content;
    const aiText = document.createElement("p");
    aiText.setAttribute("class", "ai-text");
    aiText.innerHTML = result.content.ai_thoughts;
    const createdAt = document.createElement("p");
    createdAt.setAttribute("class", "created-at");
    createdAt.textContent = formatDate(result.content.created_at);
    const TelegraphUrl = document.createElement("a");
    if (result.content.telegraph_url) {
        TelegraphUrl.setAttribute("href", result.content.telegraph_url);
        TelegraphUrl.setAttribute("class", "telegram telegraph");
        TelegraphUrl.textContent = "Пост в Telegraph";
    }
    var bot = await getBot();
    const TelegramUrl = document.createElement("a");
    if (bot) {
        TelegramUrl.setAttribute("href", `${bot}?start=${id}`);
        TelegramUrl.setAttribute("class", "telegram phone");
        TelegramUrl.textContent = "Версия для телеграм";
    }
    console.log(result.content.telegraph_url);
    infoBox.appendChild(title);
    infoBox.appendChild(content);
    infoBox.appendChild(aiText);
    infoBox.appendChild(createdAt);
    if (result.content.telegraph_url) {
        infoBox.appendChild(TelegraphUrl);
    }
    if (bot) {
        infoBox.appendChild(document.createElement("br"));
        infoBox.appendChild(TelegramUrl);
    }
    mainBox.appendChild(infoBox);
}
LoadMemory(ID);
