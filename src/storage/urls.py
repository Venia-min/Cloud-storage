from django.urls import path

from src.storage.views import upload_file_view, download_file_view, \
    delete_file_view, list_files_view, rename_file_view

urlpatterns = [
    path('upload/', upload_file_view, name="file-upload"),
    path('download/<path:filename>/', download_file_view, name="file-download"),
    path('delete/<path:filename>/', delete_file_view, name="file-delete"),
    path('rename/', rename_file_view, name="file-rename"),
    path('list/', list_files_view, name="file-list"),
]
