from django.urls import path

from src.storage.views import (
    upload_file_view,
    download_file_view,
    delete_file_view,
    # list_files_view,
    rename_file_view,
    create_folder_view,
)

urlpatterns = [
    path('upload/', upload_file_view, name="file-upload"),
    path('download/<path:file_name>/', download_file_view,
         name="file-download"),
    path('delete/<path:file_name>/', delete_file_view, name="file-delete"),
    path('rename/', rename_file_view, name="file-rename"),
    # path('list/', list_files_view, name="file-list"),
    path('create-folder/', create_folder_view, name="create-folder"),
]
