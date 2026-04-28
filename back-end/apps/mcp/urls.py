from django.urls import path
from .views import JobsView, ApplyJobView

app_name = 'mcp'

urlpatterns = [
    path('jobs/', JobsView.as_view(), name='jobs'),
    path('jobs/apply/', ApplyJobView.as_view(), name='apply_job'),
]
