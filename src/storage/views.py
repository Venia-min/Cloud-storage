from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from src.storage.services import (
    upload_file,
    download_file,
    delete_file,
    get_file_url,
    list_user_files,
    generate_breadcrumbs,
    rename_file,
)

from .exceptions import FileUploadError
from .forms import FileUploadForm



def index_view(request):
    """Главная страница с файлами пользователя"""
    user_id = request.user.id if request.user.is_authenticated else None
    path = request.GET.get("path", "")  # Получаем текущий путь, если есть

    # Получаем файлы и папки из MinIO
    files = list_user_files(user_id, path) if user_id else []

    # Генерация breadcrumbs (навигация)
    breadcrumbs = generate_breadcrumbs(path)

    return render(request, "index.html", {
        "files": files,
        "breadcrumbs": breadcrumbs
    })


@login_required
def upload_file_view(request):
    """
    View for upload files.
    :param request:
    :return:
    """
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            user_id = request.user.id
            filename = file.name
            try:
                upload_file(file, user_id, filename)
                file_url = get_file_url(user_id, filename)
                messages.success(request, f"Файл {filename} успешно загружкен.")
                return JsonResponse({
                    "message": f"Файл {filename} успешно загружен.",
                    "url": file_url,
                    "filename": filename,
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
def download_file_view(request, filename):
    """
    View for download files.
    :param request:
    :param filename:
    :return:
    """
    user_id = request.user.id
    file_path = download_file(user_id, filename)

    if file_path:
        return JsonResponse({
            "message": f"Файл {filename} успешно скачан.",
            "path": file_path,
        })

    return JsonResponse({"error": "Файл не найден."}, status=404)


@login_required
def delete_file_view(request, filename):
    """
    View for delete files.
    :param request:
    :param filename:
    :return:
    """
    user_id = request.user.id

    try:
        delete_file(user_id, filename)
        messages.success(request, f"Файл {filename} успешно удалён.")
    except PermissionDenied as exc:
        messages.error(request, f"Ошибка при удалении файла: {str(exc)}")
    except Exception as exc:
        messages.error(request, f"Ошибка при удалении файла: {str(exc)}")

    return redirect("home")


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
def list_files_view(request):
    """Вьюха для получения списка файлов пользователя"""
    user_id = request.user.id
    files = list_user_files(user_id)
    return JsonResponse({"files": files})
