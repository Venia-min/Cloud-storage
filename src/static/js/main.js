async function updateFileList() {
    const fileList = document.getElementById("file-list");
    const currentPath = new URLSearchParams(window.location.search).get("path") || "";
    try {
        const response = await fetch(`/files/${encodeURIComponent(currentPath)}/`);
        if (!response.ok) throw new Error("Ошибка обновления списка файлов");
        const data = await response.json();
        fileList.innerHTML = "";
        data.files.forEach(file => {
            const fileItem = document.createElement("div");
            fileItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
            fileItem.innerHTML = `
                ${file.is_folder ? `<a href="?path=${file.id}/">📁 ${file.name}</a>` : file.name}
                <div class="dropdown">
                    <button class="btn menu-btn" type="button" data-bs-toggle="dropdown" aria-expanded="false">...</button>
                    <div class="dropdown-menu">
                        <a class="dropdown-item" href="/files/download/${encodeURIComponent(file.id)}/">Скачать</a>
                        <button class="dropdown-item text-danger" onclick="deleteFile('${file.id}')">Удалить</button>
                        <button class="dropdown-item text-warning" onclick="openRenameModal('${file.id}', '${file.name}')">Переименовать</button>
                    </div>
                </div>
            `;
            fileList.appendChild(fileItem);
        });
    } catch (error) {
        console.error("Ошибка загрузки списка файлов:", error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.querySelector(".drop-zone");
    const fileInput = document.getElementById("file-input");
    const form = document.getElementById("upload-form");
    const uploadStatus = document.getElementById("upload-status");
    const uploadUrl = form.getAttribute("data-url");  // Получаем URL для загрузки

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");

        const files = e.dataTransfer.files;
        const dt = new DataTransfer();
        for (let i = 0; i < files.length; i++) {
            dt.items.add(files[i]);
        }
        fileInput.files = dt.files;
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        let formData = new FormData(form);

        fetch(uploadUrl, {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // Показать сообщение об ошибке
                uploadStatus.innerHTML = `<p>Ошибка: ${data.error}</p>`;
            } else {
                updateFileList();
                // Показать успешное сообщение и добавить файл в список
                uploadStatus.innerHTML = `<p>${data.message}</p>`;
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = `<p>Ошибка загрузки: ${error.message}</p>`;
            console.error("Ошибка загрузки:", error);
        });
    });
});

async function deleteFile(fileId) {
    const currentPath = new URLSearchParams(window.location.search).get("path") || "";
    try {
        const response = await fetch(`/files/delete/${encodeURIComponent(fileId)}/`, { method: "DELETE" });
        if (!response.ok) throw new Error("Ошибка удаления файла");
        updateFileList();
    } catch (error) {
        console.error("Ошибка при удалении файла:", error);
    }
}

async function renameFile(fileId, newName) {
    try {
        const response = await fetch(`/files/rename/`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file_id: fileId, new_name: newName })
        });
        if (!response.ok) throw new Error("Ошибка переименования файла");
        updateFileList();
    } catch (error) {
        console.error("Ошибка при переименовании файла:", error);
    }
}

function openRenameModal(fileId, fileName) {
    document.getElementById("file-id").value = fileId;
    document.getElementById("new-name").value = fileName;
}

document.getElementById("create-folder-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    try {
        const response = await fetch("/files/create/", {
            method: "POST",
            body: formData
        });
        if (!response.ok) throw new Error("Ошибка создания папки");
        updateFileList();
    } catch (error) {
        console.error("Ошибка при создании папки:", error);
    }
});