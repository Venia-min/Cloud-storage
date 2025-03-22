from django.urls import path

from src.storage.views import (
    upload_file_view,
    download_file_view,
    delete_file_view,
    # list_files_view,
    rename_file_view,
    create_folder_view, list_files_view,
)

urlpatterns = [
    path('files/upload/', upload_file_view, name="file-upload"),
    path('files/download/<path:file_name>/', download_file_view,
         name="file-download"),
    path('files/delete/<path:file_name>/', delete_file_view, name="file-delete"),
    path('files/rename/', rename_file_view, name="file-rename"),
    path('files/<path:path>/', list_files_view, name="file-list"),
    path('files/create/', create_folder_view, name="create-folder"),
]
