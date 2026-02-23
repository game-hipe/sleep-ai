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

async function FetchCreateMemory(title: string, content: string) {
    var response = await fetch('/api/add', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(
            {
                'title': title,
                'content': content
            }
        )
    });
    if (response.status != 200) {
        alert("Ошибка во время добавление сна");
    } else {
        const result = JSON.parse(await response.text()) as MemoryResponse
        if (!result.success) {
            alert(result.message);
            return
        } else {
            console.log(result.message);
        }

        if (result.content != null) {
            window.location.href = "/memory/" + result.content.id;
        }
    }
}

function CreateMemory() {
    var titleInputInput = document.getElementById("title") as HTMLInputElement | null;
    var contentInput = document.getElementById("content") as HTMLInputElement | null;

    if (!titleInputInput || !contentInput) {
        alert("Неудалось получить один из важных элементов");
        return;
    } else {
        const title = titleInputInput.value;
        const content = contentInput.value;

        if (!title) {
            alert("Введите название сна");
            return;
        } else if (!content) {
            alert("Введите содержание сна");
            return;
        } else {
            FetchCreateMemory(title, content)
        }
    }
}