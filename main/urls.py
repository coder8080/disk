from django.urls import path
from . import views

urlpatterns = [
    path("author/", views.AuthorView.as_view(), name='author'),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("main/", views.PrivateOfficeView.as_view(), name='private-office'),
    path("mydisk/<str:dir>", views.DiskView.as_view(), name="mydisk"),
    path("mydisk/", views.RedirectView.as_view(), name='redirect'),
    path("download/<str:folder>/<str:filename>", views.DownloadView.as_view(), name="download"),
    path("delete/<str:folder>/<str:filename>", views.RemoveView.as_view(), name="delete"),
    path("delete-folder/<str:folder>/<str:foldername>", views.RemoveFolderView.as_view(), name="delete-folder"),
    path("create-folder", views.CreateFolderView.as_view(), name="create-folder"),
    path("text/<str:folder>/<str:filename>", views.Preview.as_view(), name='text'),
    path("retext/", views.ReWriteView.as_view(), name="retext"),
    path("public/<str:url>", views.PublicFileView.as_view(), name='public-file'),
    path("download-public/<str:code>", views.DownloadPublicView.as_view(), name='download-public'),
    path("create-public/<str:folder>/<str:filename>", views.CreatePublicFileView.as_view(), name="create-public-file"),
    path("", views.MainView.as_view(), name="main-page")
]
