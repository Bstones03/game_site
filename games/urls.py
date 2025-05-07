from django.urls import path
from . import views

urlpatterns = [
    path('play/', views.play_game, name='play'),
    path('blackjack/', views.blackjack, name='blackjack'),
    path('rtb/', views.ride_the_bus, name='ride_the_bus'),
    path('baccarat/', views.baccarat, name='baccarat'),
    path('three-card-poker/', views.three_card_poker, name='three_card_poker'),
    path('war/', views.war, name='war'),
]
