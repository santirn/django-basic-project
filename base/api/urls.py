from django.urls import path, include
from . import views

urlpatterns=[
    path('', views.getRoutes),
    path('rooms/', views.getRooms),
    path('room/<str:pk>', views.getRoom),
    
]