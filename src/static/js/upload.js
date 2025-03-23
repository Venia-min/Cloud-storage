document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.querySelector(".drop-zone");
    const fileInput = document.getElementById("file-input");
    const form = document.getElementById("upload-form");
    const uploadStatus = document.getElementById("upload-status");
    const uploadUrl = form.getAttribute("data-url");

    // Добавляем обработчик клика для открытия окна выбора файла
    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    // Drag and Drop functionality
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

    // Form submission for file upload
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
                uploadStatus.innerHTML = `<p>Ошибка: ${data.error}</p>`;
            } else {
                location.reload(); // Reload the page to update the file list
                uploadStatus.innerHTML = `<p>${data.message}</p>`;
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = `<p>Ошибка загрузки: ${error.message}</p>`;
            console.error("Ошибка загрузки:", error);
        });
    });
});