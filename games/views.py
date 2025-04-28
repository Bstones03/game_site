from django.shortcuts import render
from accounts.models import UserProfile

def play_game(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'games/play.html', {'profile': profile})