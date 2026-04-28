from django.urls import path
from .views import JobsView

app_name = 'mcp'

urlpatterns = [
    path('jobs/', JobsView.as_view(), name='jobs'),
]
