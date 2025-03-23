from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods, \
    require_GET
import json

from src.storage.services import (
    upload_file,
    download_file,
    delete_file,
    list_user_files,
    generate_breadcrumbs,
    rename_file, create_folder,
)

from .exceptions import FileUploadError


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
@require_POST
def upload_file_view(request):
    """
    View for upload files.
    :param request:
    :return:
    """
    data = request.POST
    current_path = data.get("current_path", "")
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "Файл не найден"}, status=400)
    user_id = request.user.id
    file_name = file.name
    full_file_name = f"{current_path}{file_name}" if current_path else file_name
    try:
        upload_file(file, user_id, full_file_name)
        return JsonResponse({
            "message": f"Файл {file_name} загружен.",
            "file_url": full_file_name,
            "file_name": file_name
        }, status=201)
    except FileUploadError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    # if request.method == "POST":
    #     current_path = request.POST.get("current_path", "")
    #     form = FileUploadForm(request.POST, request.FILES)
    #     print("current in view:", current_path)
    #     if form.is_valid():
    #         file = form.cleaned_data['file']
    #         user_id = request.user.id
    #         file_name = file.name
    #         full_file_name = f"{current_path}{file_name}" if current_path \
    #             else file_name
    #         try:
    #             upload_file(file, user_id, full_file_name)
    #             messages.success(request, f"Файл {file_name} успешно загружен.")
    #             return JsonResponse({
    #                 "message": f"Файл {file_name} успешно загружен.",
    #                 "url": full_file_name,
    #                 "filename": file_name,
    #             }, status=200)
    #
    #         except FileUploadError as exc:
    #             messages.error(request, f"Ошибка при загрузке файла: "
    #                                     f"{str(exc)}")
    #             return JsonResponse({
    #                 "error": f"Ошибка при загрузке файла: {str(exc)}"
    #             }, status=400)
    #
    # form = FileUploadForm()
    # return render(request, "file_upload.html", {"form": form})


@login_required
@require_GET
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
        return FileResponse(open(file_path, "rb"), as_attachment=True)

    return JsonResponse({"error": "Файл не найден."}, status=404)


@login_required
@require_http_methods(["DELETE"])
def delete_file_view(request, file_name):
    """
    View for delete files.
    :param request:
    :param file_name:
    :return:
    """
    user_id = request.user.id
    print("name:", file_name)
    try:
        delete_file(user_id, file_name)
        return JsonResponse({"success": True}, status=204)
    except PermissionDenied as exc:
        return JsonResponse({"error": str(exc)}, status=403)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@login_required
@require_http_methods(["PATCH"])
def rename_file_view(request):
    """Переименование файла"""
    try:
        data = json.loads(request.body)
        file_id = data.get("file_id")
        new_name = data.get("new_name")
        if not file_id or not new_name:
            return JsonResponse({"error": "Некорректные данные"}, status=400)
        rename_file(file_id, new_name)
        return JsonResponse({"message": "Файл успешно переименован!"}, status=200)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    # if request.method == "POST":
    #     file_id = request.POST.get("file-id")
    #     new_name = request.POST.get("new-name")
    #
    #     # Выполняем переименование через функцию в сервисах
    #     try:
    #         rename_file(file_id, new_name)
    #         messages.success(request, "Файл успешно переименован!")
    #
    #     except Exception as exc:
    #         # Добавляем ошибку в сообщения
    #         messages.error(request, f"Ошибка при переименовании: {str(exc)}")
    #
    # return redirect('home')


@login_required
@require_http_methods(["GET"])
def list_files_view(request, path):
    """Вьюха для получения списка файлов пользователя"""
    user_id = request.user.id
    files = list_user_files(user_id, path) if user_id else []
    return JsonResponse({"files": files}, status=200)


@login_required
@require_POST
def create_folder_view(request):
    """Создание папки"""
    data = json.loads(request.body)
    folder_name = data.get("folder_name")
    current_path = data.get("current_path", "")
    create_and_go = data.get("create_and_go") == "true"
    user_id = request.user.id
    if not folder_name:
        return JsonResponse({"error": "Название папки не указано"}, status=400)

    try:
        full_folder_name = f"{current_path}{folder_name}/"
        create_folder(user_id, full_folder_name)

        if create_and_go:
            return JsonResponse({"redirect": f"/?path={full_folder_name}"})

        return JsonResponse({"message": f"Папка {folder_name} успешно создана!"},
                            status=201)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    # folder_name = request.POST.get("folder_name")
    # current_path = request.POST.get("current_path", "")
    # create_and_go = request.POST.get("create_and_go") == "true"
    # user_id = request.user.id
    # full_folder_name = f"{current_path}{folder_name}" if current_path \
    #     else folder_name
    #
    # try:
    #     # Создаем папку в хранилище
    #     create_folder(user_id, full_folder_name)
    #     messages.success(request, f"Папка {folder_name} успешно создана!")
    #
    #     if create_and_go:
    #         # Перенаправляем пользователя в только что созданную папку
    #         return redirect(f"/?path={full_folder_name}/")
    #     return redirect(f"/?path={current_path}")  # Или на страницу с файлом
    #
    # except Exception as exc:
    #     messages.error(request, f"Ошибка при создании папки: {str(exc)}")
    #     return redirect(f"/?path={current_path}")
    #
    # return redirect("home")
