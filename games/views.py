from django.shortcuts import render
from accounts.models import UserProfile

def play_game(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'games/play.html', {'profile': profile})
