document.addEventListener("DOMContentLoaded", function () {
    // Удаление файла
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener("click", function (e) {
            const fileId = e.target.getAttribute("data-file-id");

            if (confirm("Вы уверены, что хотите удалить этот файл?")) {
                fetch(`storage/files/delete/${fileId}/`, {
                    method: "DELETE", // Используем DELETE метод
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                })
                .then(response => {
                    if (response.ok) {
                        location.reload();  // Перезагружаем страницу после успешного удаления
                    } else {
                        return response.json().then(data => {
                            alert(data.error || "Ошибка при удалении файла.");
                        });
                    }
                })
                .catch(error => {
                    alert("Ошибка при удалении файла.");
                    console.error("Ошибка:", error);
                });
            }
        });
    });

    // Переименование файла
    document.querySelectorAll('.rename-btn').forEach(button => {
        button.addEventListener("click", function () {
            const fileId = this.getAttribute("data-file-id");
            const newName = prompt("Введите новое имя файла:");

            if (newName) {
                fetch('storage/files/rename/', {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        file_id: fileId,
                        new_name: newName
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert("Ошибка при переименовании файла.");
                    } else {
                        updateFileList(); // Обновить список файлов
                    }
                })
                .catch(error => alert("Ошибка при переименовании файла."));
            }
        });
    });

    // Обновление списка файлов после действий
    function updateFileList() {
        fetch('storage/files/')
            .then(response => response.json())
            .then(data => {
                const fileList = document.getElementById('file-list');
                fileList.innerHTML = '';
                data.files.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.classList.add('file-item');
                    fileItem.innerHTML = `
                        <div class="file-name">${file.name}</div>
                        <button class="delete-btn" data-file-id="${file.id}">Удалить</button>
                        <button class="rename-btn" data-file-id="${file.id}">Переименовать</button>
                    `;
                    fileList.appendChild(fileItem);
                });
            })
            .catch(error => console.error('Ошибка загрузки файлов:', error));
    }
});
