import random
from django.shortcuts import render, redirect
from accounts.models import UserProfile

def play_game(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'games/play.html', {'profile': profile})

# Helper function to draw a card
def draw_card():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return random.choice(ranks)

# Calculate hand total
def calculate_total(hand):
    total = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']:
            total += 10
        elif card == 'A':
            aces += 1
            total += 11
        else:
            total += int(card)

    # Adjust for aces
    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

def blackjack(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    session = request.session
    if request.GET.get('reset'):
        session.pop('player_hand', None)
        session.pop('dealer_hand', None)
        session.pop('game_over', None)
        session.pop('message', None)
        return redirect('blackjack')


    # Start new game
    if request.method == 'POST' and request.POST.get('action') == 'Start':
        try:
            bet_input = request.POST.get('bet', '').strip()
            if bet_input != '':
                bet = int(bet_input)
                if bet <= 0 or bet > profile.balance:
                    raise ValueError("Invalid bet amount.")
                session['bet'] = bet  # Only overwrite if valid and new
        except Exception:
            return render(request, 'games/blackjack.html', {
                'error': 'Invalid bet amount.',
                'balance': profile.balance,
                'start_game': True
            })

        bet = session.get('bet', 0)
        if bet <= 0 or bet > profile.balance:
            return render(request, 'games/blackjack.html', {
                'error': 'No valid bet available.',
                'balance': profile.balance,
                'start_game': True
            })

        session['player_hand'] = [draw_card(), draw_card()]
        session['dealer_hand'] = [draw_card(), draw_card()]
        session['game_over'] = False
        session['message'] = ''
        profile.balance -= bet
        profile.save()


    player_hand = session.get('player_hand', [])
    dealer_hand = session.get('dealer_hand', [])
    bet = session.get('bet', 0)
    game_over = session.get('game_over', False)
    message = session.get('message', '')

    if request.method == 'POST' and not game_over:
        if request.POST.get('action') == 'Hit':
            player_hand.append(draw_card())
            session['player_hand'] = player_hand
            if calculate_total(player_hand) > 21:
                message = "You busted! You lose."
                session['game_over'] = True

        elif request.POST.get('action') == 'Stand':
            while calculate_total(dealer_hand) < 17:
                dealer_hand.append(draw_card())

            player_total = calculate_total(player_hand)
            dealer_total = calculate_total(dealer_hand)

            if dealer_total > 21 or player_total > dealer_total:
                message = "You win!"
                profile.balance += bet * 2
            elif player_total == dealer_total:
                message = "It's a tie!"
                profile.balance += bet
            else:
                message = "You lose."

            session['game_over'] = True
            profile.save()

        session['dealer_hand'] = dealer_hand
        session['message'] = message

    context = {
        'player_hand': player_hand,
        'dealer_hand': dealer_hand if session.get('game_over') else ['?', dealer_hand[1]] if dealer_hand else [],
        'player_total': calculate_total(player_hand) if player_hand else 0,
        'dealer_total': calculate_total(dealer_hand) if session.get('game_over') else '?',
        'message': session.get('message', ''),
        'game_over': session.get('game_over', False),
        'balance': profile.balance,
        'bet': session.get('bet', ''), 
        'start_game': not player_hand,
        'error': '',
    }
    return render(request, 'games/blackjack.html', context)
