from django.urls import path
from . import views

urlpatterns = [
    path('play/', views.play_game, name='play'),
    path('blackjack/', views.blackjack, name='blackjack'),
]
