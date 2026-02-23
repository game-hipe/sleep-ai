"use strict";
// Элементы управления загрузкой
const loadingOverlay = document.getElementById('loadingOverlay');
const submitBtn = document.getElementById('submitBtn');
function showLoading() {
    if (loadingOverlay)
        loadingOverlay.style.display = 'flex';
    if (submitBtn)
        submitBtn.disabled = true;
}
function hideLoading() {
    if (loadingOverlay)
        loadingOverlay.style.display = 'none';
    if (submitBtn)
        submitBtn.disabled = false;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function startTitleSwap(loadingText, abortSignal) {
    let text = "Загрузка может занять много времени";
    let points = "";
    while (!(abortSignal === null || abortSignal === void 0 ? void 0 : abortSignal.aborted)) {
        if (points.length >= 3) {
            points = "";
        }
        else {
            points += ".";
        }
        loadingText.innerText = text + points;
        await sleep(3000);
    }
}
async function FetchCreateMemory(title, content) {
    const loadingText = document.querySelector("span.loading-text");
    const abortController = new AbortController();
    try {
        const titleSwapPromise = startTitleSwap(loadingText, abortController.signal);
        const response = await fetch('/api/add', {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content })
        });
        abortController.abort();
        await titleSwapPromise;
        if (response.status !== 200) {
            hideLoading(); // скрываем загрузку перед алертом
            alert("Ошибка во время добавления сна");
            return;
        }
        const result = JSON.parse(await response.text());
        if (!result.success) {
            hideLoading();
            alert(result.message);
            return;
        }
        loadingText.innerText = "Готово!";
        console.log(result.message);
        if (result.content != null) {
            // Редирект – загрузка остаётся видимой, страница уйдёт
            window.location.href = "/memory/" + result.content.id;
        }
        else {
            // На всякий случай, если нет контента, но success=true
            hideLoading();
        }
    }
    catch (error) {
        abortController.abort();
        loadingText.innerText = "Ошибка!";
        hideLoading();
        alert("Произошла ошибка при отправке запроса: " + error);
    }
}
function CreateMemory() {
    const titleInput = document.getElementById("title");
    const contentInput = document.getElementById("content");
    if (!titleInput || !contentInput) {
        alert("Не удалось получить один из важных элементов");
        return;
    }
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    if (!title) {
        alert("Введите название сна");
        return;
    }
    if (!content) {
        alert("Введите содержание сна");
        return;
    }
    // Показываем загрузку и блокируем кнопку
    showLoading();
    // Запускаем асинхронный запрос
    FetchCreateMemory(title, content);
}
