from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.face.urls', namespace='face')),
    path('api/v1/chat/', include('apps.chat.urls', namespace='chat')),
    path('api/v1/mcp/', include('apps.mcp.urls', namespace='mcp')),
]
