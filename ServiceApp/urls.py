from django.urls import path
from ServiceApp import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('new/', views.CreateNewNote.as_view()),
    path('<str:pk>/', views.GetNoteDetails.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
