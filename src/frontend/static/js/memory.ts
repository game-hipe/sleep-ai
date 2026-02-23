interface BaseResponse<T> {
    success: boolean
    message: string
    content: T | null
}

interface SleepMemoryResponse {
    id: number
    title: string
    content: string
    ai_thoughts: string
    created_at: string
}

interface MemoryResponse extends BaseResponse<SleepMemoryResponse> {}

var href = document.location.href;
var splitHref = href.split("/")

const ID = splitHref[splitHref.length - 1]

function formatDate(dateString: string) {
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

async function LoadMemory(id: string | number) {
    var response = await fetch(`/api/memory/${id}`, {
        headers: {
            'accept': 'application/json'
        }
    });
    if (response.status != 200) {
        return;
    }
    
    const result = JSON.parse(await response.text()) as MemoryResponse
    if (!result.success) {
        console.log("Not Found!");
        
        alert(result.message);
        window.location.href = "/";
        return;
    } else if (!result.content) {
        alert("No content");
        return
    }
    
    const mainBox = document.querySelector("main");
    if (!mainBox) {
        alert("Не удалось найти элемент main");
        return
    } else {
        var h1 = mainBox.querySelector("h1");
        h1?.remove()
    }

    const infoBox = document.createElement("div");
    
    const title = document.createElement("h1");
    title.textContent = result.content.title;

    document.title = result.content.title;

    const content = document.createElement("p");
    content.setAttribute("class", "content-text")
    content.textContent = result.content.content;

    const aiText = document.createElement("p");
    aiText.setAttribute("class", "ai-text");
    aiText.innerHTML = result.content.ai_thoughts;

    const createdAt = document.createElement("p")
    createdAt.setAttribute("class", "created-at")
    createdAt.textContent = formatDate(result.content.created_at)

    infoBox.appendChild(title);
    infoBox.appendChild(content);
    infoBox.appendChild(aiText);
    infoBox.appendChild(createdAt);
    mainBox.appendChild(infoBox);
}


LoadMemory(ID)