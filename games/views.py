import random
from django.shortcuts import render, redirect
from accounts.models import UserProfile
from .cards import get_card
import random

DECK = get_card()

def play_game(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'games/play.html', {'profile': profile})

def draw_card():
    return random.choice(DECK)


##################################
# BLACKJACK \/ \/ \/ \/ \/
##################################

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


# Calculate hand total

def calculate_total(hand):
    total = 0
    aces = 0
    for card in hand:
        rank = card['rank']
        if rank in ['J', 'Q', 'K']:
            total += 10
        elif rank == 'A':
            aces += 1
            total += 11
        else:
            total += int(rank)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

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

##################################
# RIDE THE BUS \/ \/ \/ \/ \/
##################################

COLORS = {'♥': 'Red', '♦': 'Red', '♠': 'Black', '♣': 'Black'}
SUITS = ['♥', '♦', '♠', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {rank: i for i, rank in enumerate(RANKS, start=2)}



def ride_the_bus(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    session = request.session

    if request.GET.get("reset"):
        session_keys = [key for key in session.keys() if key.startswith("rtb_") and key != "rtb_bet"]
        for key in session_keys:
            del session[key]
        return redirect("ride_the_bus")

    # Start Game
    if request.method == "POST" and request.POST.get("action") == "Start":
        bet_input = request.POST.get("bet", "").strip()
        if bet_input:
            try:
                bet = int(bet_input)
                if bet <= 0 or bet > profile.balance:
                    raise ValueError()
                session['rtb_bet'] = bet
            except:
                return render(request, "games/ride_the_bus.html", {
                    'balance': profile.balance,
                    'error': "Invalid bet.",
                    'start_game': True,
                    'bet': session.get('rtb_bet', '')
                })

        bet = session.get("rtb_bet", 0)
        if bet <= 0 or bet > profile.balance:
            return render(request, "games/ride_the_bus.html", {
                'balance': profile.balance,
                'error': "No valid bet.",
                'start_game': True,
                'bet': session.get('rtb_bet', '')
            })

        session['rtb_stage'] = 1
        session['rtb_cards'] = []
        session['rtb_result'] = ''
        session['rtb_multiplier'] = 1
        profile.balance -= bet
        profile.save()
        return redirect("ride_the_bus")

    # Handle Guess or Pull Out
    if request.method == "POST":
        if request.POST.get("action") == "Pull Out":
            winnings = session['rtb_bet'] * session.get('rtb_multiplier', 1)
            profile.balance += winnings
            profile.save()
            session['rtb_result'] = f"You pulled out and won ${winnings}."
            return redirect("ride_the_bus")

        elif request.POST.get("action") == "Guess":
            stage = session.get('rtb_stage', 1)
            guess = request.POST.get('guess')
            cards = session.get('rtb_cards', [])
            new_card = draw_card()
            val_new = VALUES[new_card['rank']]
            correct = False

            if stage == 1:
                correct = (COLORS[new_card['suit']] == guess)
                session['rtb_multiplier'] = 2

            elif stage == 2:
                val1 = VALUES[cards[0]['rank']]
                correct = (guess == 'Higher' and val_new > val1) or (guess == 'Lower' and val_new < val1)
                session['rtb_multiplier'] = 3

            elif stage == 3:
                val1 = VALUES[cards[0]['rank']]
                val2 = VALUES[cards[1]['rank']]
                low, high = sorted([val1, val2])
                correct = (guess == 'In Between' and low < val_new < high) or (guess == 'Outside' and (val_new < low or val_new > high))
                session['rtb_multiplier'] = 4

            elif stage == 4:
                correct = (new_card['suit'] == guess)
                session['rtb_multiplier'] = 20

            cards.append(new_card)  # Always add the card
            session['rtb_cards'] = cards

            if correct:
                if stage == 4:
                    winnings = session['rtb_bet'] * session['rtb_multiplier']
                    profile.balance += winnings
                    profile.save()
                    session['rtb_result'] = f"You completed the ride and won ${winnings}!"
                else:
                    session['rtb_stage'] = stage + 1
            else:
                session['rtb_result'] = f"Wrong guess! You lost your bet of ${session['rtb_bet']} (Card was {new_card['rank']}{new_card['suit']})."

            return redirect("ride_the_bus")

    return render(request, "games/ride_the_bus.html", {
        'balance': profile.balance,
        'start_game': 'rtb_stage' not in session,
        'stage': session.get('rtb_stage', 1),
        'cards': session.get('rtb_cards', []),
        'bet': session.get('rtb_bet', ''),
        'multiplier': session.get('rtb_multiplier', 1),
        'result': session.get('rtb_result', ''),
        'error': ''
    })


SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {r: min(i+2, 10) for i, r in enumerate(RANKS)}  # for Baccarat
POKER_VALUES = {r: i for i, r in enumerate(RANKS)}

COLORS = {'♥': 'Red', '♦': 'Red', '♠': 'Black', '♣': 'Black'}



##################################
# BACCARAT
##################################

def baccarat_total(hand):
    return sum(VALUES[c['rank']] for c in hand) % 10

def baccarat(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        bet_choice = request.POST.get('bet_choice')
        bet_amount = int(request.POST.get('bet') or request.session.get('last_bet', 0))
        request.session['last_bet'] = bet_amount
        if bet_amount <= 0 or bet_amount > profile.balance:
            return render(request, 'games/baccarat.html', {'error': 'Invalid bet', 'balance': profile.balance})

        profile.balance -= bet_amount
        player = [draw_card(), draw_card()]
        banker = [draw_card(), draw_card()]
        p_total = baccarat_total(player)
        b_total = baccarat_total(banker)

        if (p_total > b_total and bet_choice == 'player') or \
           (b_total > p_total and bet_choice == 'banker') or \
           (p_total == b_total and bet_choice == 'tie'):
            payout = bet_amount * (8 if bet_choice == 'tie' else 2)
            profile.balance += payout
            result = f"You won! {bet_choice} pays ${payout}."
        else:
            result = f"You lost. Player: {p_total}, Banker: {b_total}"

        profile.save()
        return render(request, 'games/baccarat.html', {
            'player': player, 'banker': banker, 'balance': profile.balance, 'result': result
        })
    return render(request, 'games/baccarat.html', {
        'balance': profile.balance,
        'bet': request.session.get('last_bet', ''),
    })


##################################
# THREE CARD POKER
##################################

def three_card_poker(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        bet_amount = int(request.POST.get('bet') or request.session.get('last_bet', 0))
        request.session['last_bet'] = bet_amount
        if bet_amount <= 0 or bet_amount > profile.balance:
            return render(request, 'games/three_card_poker.html', {'error': 'Invalid bet', 'balance': profile.balance})

        profile.balance -= bet_amount
        player = [draw_card() for _ in range(3)]
        dealer = [draw_card() for _ in range(3)]
        player_score = max(POKER_VALUES[c['rank']] for c in player)
        dealer_score = max(POKER_VALUES[c['rank']] for c in dealer)

        if player_score > dealer_score:
            profile.balance += bet_amount * 2
            result = "You win!"
        elif player_score == dealer_score:
            profile.balance += bet_amount
            result = "Tie. Bet returned."
        else:
            result = "You lose."

        profile.save()
        return render(request, 'games/three_card_poker.html', {
            'player': player, 'dealer': dealer, 'balance': profile.balance, 'result': result
        })
    return render(request, 'games/three_card_poker.html', {
        'balance': profile.balance,
        'bet': request.session.get('last_bet', ''),
    })


##################################
# CASINO WAR
##################################

def war(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        bet_amount = int(request.POST.get('bet') or request.session.get('last_bet', 0))
        request.session['last_bet'] = bet_amount
        if bet_amount <= 0 or bet_amount > profile.balance:
            return render(request, 'games/war.html', {'error': 'Invalid bet', 'balance': profile.balance})

        profile.balance -= bet_amount
        player_card = draw_card()
        dealer_card = draw_card()
        player_val = POKER_VALUES[player_card['rank']]
        dealer_val = POKER_VALUES[dealer_card['rank']]

        if player_val > dealer_val:
            profile.balance += bet_amount * 2
            result = "You win the war!"
        elif player_val == dealer_val:
            profile.balance += bet_amount
            result = "It's a tie."
        else:
            result = "Dealer wins."

        profile.save()
        return render(request, 'games/war.html', {
            'player_card': player_card, 'dealer_card': dealer_card, 'balance': profile.balance, 'result': result
        })
    return render(request, 'games/war.html', {
        'balance': profile.balance,
        'bet': request.session.get('last_bet', ''),
    })

