from django.urls import path
from .views import chat_bot, analyze_image,chatbot,nutrition,mental_health,reset_chat
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', chatbot, name='chatbot'),
    path('analyze-image/', analyze_image, name='analyze_image'),
    path('chat_bot/', chat_bot, name='chat_bot'),
    path('nutrition/', nutrition, name='nutrition'),
    path('mental_health/', mental_health, name='mental_health'),
    path("reset_chat/", reset_chat, name="reset_chat"),
] 
 