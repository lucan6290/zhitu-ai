from django.urls import path
from .views import SessionListView, SessionMessagesView, SessionDeleteView, ChatAgentView

app_name = 'chat'

urlpatterns = [
    path('sessions/', SessionListView.as_view(), name='session_list'),
    path('sessions/<int:session_id>/messages/', SessionMessagesView.as_view(), name='session_messages'),
    path('sessions/<int:session_id>/', SessionDeleteView.as_view(), name='session_delete'),
    path('agent/', ChatAgentView.as_view(), name='agent'),
]
