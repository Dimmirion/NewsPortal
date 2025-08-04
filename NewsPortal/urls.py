from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),  # Все пути из news/urls.py будут относиться к корню
    path('accounts/', include('allauth.urls')),
]