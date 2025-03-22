from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from src.storage.services import (
    upload_file,
    download_file,
    delete_file,
    list_user_files,
    generate_breadcrumbs,
    rename_file, create_folder,
)

from .exceptions import FileUploadError
from .forms import FileUploadForm



def index_view(request):
    """Главная страница с файлами пользователя"""
    user_id = request.user.id if request.user.is_authenticated else None
    path = request.GET.get("path", "")  # Получаем текущий путь, если есть
    path = path.rstrip("/") + "/" if path else "" # Обязательный / в конце
    # Получение файлов и папок из MinIO
    files = list_user_files(user_id, path) if user_id else []

    # Генерация breadcrumbs
    breadcrumbs = generate_breadcrumbs(path) if user_id else []

    return render(request, "index.html", {
        "files": files,
        "breadcrumbs": breadcrumbs,
        "current_path": path
    })


@login_required
def upload_file_view(request):
    """
    View for upload files.
    :param request:
    :return:
    """
    if request.method == "POST":
        current_path = request.POST.get("current_path", "")
        form = FileUploadForm(request.POST, request.FILES)
        print("current in view:", current_path)
        if form.is_valid():
            file = form.cleaned_data['file']
            user_id = request.user.id
            file_name = file.name
            full_file_name = f"{current_path}{file_name}" if current_path \
                else file_name
            try:
                upload_file(file, user_id, full_file_name)
                messages.success(request, f"Файл {file_name} успешно загружен.")
                return JsonResponse({
                    "message": f"Файл {file_name} успешно загружен.",
                    "url": full_file_name,
                    "filename": file_name,
                }, status=200)

            except FileUploadError as exc:
                messages.error(request, f"Ошибка при загрузке файла: "
                                        f"{str(exc)}")
                return JsonResponse({
                    "error": f"Ошибка при загрузке файла: {str(exc)}"
                }, status=400)

    form = FileUploadForm()
    return render(request, "file_upload.html", {"form": form})


@login_required
def download_file_view(request, file_name):
    """
    View for download files.
    :param request:
    :param file_name:
    :return:
    """
    user_id = request.user.id
    file_path = download_file(user_id, file_name)

    if file_path:
        return JsonResponse({
            "message": f"Файл {file_name} успешно скачан.",
            "path": file_path,
        })

    return JsonResponse({"error": "Файл не найден."}, status=404)


@login_required
@require_POST
def delete_file_view(request, file_name):
    """
    View for delete files.
    :param request:
    :param file_name:
    :return:
    """
    current_path = request.POST.get("current_path", "")
    user_id = request.user.id

    try:
        delete_file(user_id, file_name)
        messages.success(request, f"Файл {file_name} успешно удалён.")
    except PermissionDenied as exc:
        messages.error(request, f"Ошибка при удалении файла: {str(exc)}")
    except Exception as exc:
        messages.error(request, f"Ошибка при удалении файла: {str(exc)}")

    return redirect(f"/?path={current_path}")


@login_required
def rename_file_view(request):
    if request.method == "POST":
        file_id = request.POST.get("file-id")
        new_name = request.POST.get("new-name")

        # Выполняем переименование через функцию в сервисах
        try:
            rename_file(file_id, new_name)
            messages.success(request, "Файл успешно переименован!")

        except Exception as exc:
            # Добавляем ошибку в сообщения
            messages.error(request, f"Ошибка при переименовании: {str(exc)}")

    return redirect('home')


@login_required
def list_files_view(request, path):
    """Вьюха для получения списка файлов пользователя"""
    user_id = request.user.id
    files = list_user_files(user_id, path) if user_id else []
    return JsonResponse({"files": files})


@login_required
@require_POST
def create_folder_view(request):
    folder_name = request.POST.get("folder_name")
    current_path = request.POST.get("current_path", "")
    create_and_go = request.POST.get("create_and_go") == "true"
    user_id = request.user.id
    full_folder_name = f"{current_path}{folder_name}" if current_path \
        else folder_name

    try:
        # Создаем папку в хранилище
        create_folder(user_id, full_folder_name)
        messages.success(request, f"Папка {folder_name} успешно создана!")

        if create_and_go:
            # Перенаправляем пользователя в только что созданную папку
            return redirect(f"/?path={full_folder_name}/")
        return redirect(f"/?path={current_path}")  # Или на страницу с файлом

    except Exception as exc:
        messages.error(request, f"Ошибка при создании папки: {str(exc)}")
        return redirect(f"/?path={current_path}")

    return redirect("home")
