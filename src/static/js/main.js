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
                location.reload();  // Перезагружаем страницу
                // Показать успешное сообщение и добавить файл в список
                uploadStatus.innerHTML = `<p>${data.message}</p>`;

//                let fileList = document.getElementById("file-list");
//                let newFile = document.createElement("div");
//                newFile.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
//                newFile.innerHTML = `
//                    ${data.filename}
//                    <div>
//                        <a href="${data.url}" class="btn btn-sm btn-primary">Скачать</a>
//                        <a href="#" class="btn btn-sm btn-danger">Удалить</a>
//                    </div>
//                `;
//                fileList.appendChild(newFile);
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = `<p>Ошибка загрузки: ${error.message}</p>`;
            console.error("Ошибка загрузки:", error);
        });
    });
});