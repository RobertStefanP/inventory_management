import random

def roll():
    return random.randint(1, 6)

def play_turn(player_idx, player_score):
    print(f"\nPlayer {player_idx + 1} turn started!\n")
    print(f"Your total score is {players_scores[player_idx]}.\n")  
    current_score = 0   
    
    while True:
        should_roll = input("Wold you like to roll (y)? ")
        if should_roll.lower() != 'y':
            break
        
        value = roll()
        if value == 1:
            current_score = 0
            print("Rolled 1! Turn done!")
            break
        else:
            current_score += value
            print(f"You rolled a {value}.")
            print(f"Your current score is {current_score}.")
            
    return current_score
    
while True:
    nr_players = input("Enter the number of players (2-4): ")
    if nr_players.isdigit():
        nr_players = int(nr_players)
        if 2 <= nr_players <= 4:
            break
        else:
            print("Error! Number of players must be between 2 and 4. Try again!")
    else:
        print("Error! Insert a valid number, 2 to 4!")
    
max_score = 50
players_scores = [0 for _ in range(nr_players)]

while max(players_scores) < max_score:   
    for player_idx in range(nr_players):
        turn_score = play_turn(player_idx, players_scores[player_idx])        
        players_scores[player_idx] += turn_score
        print(f"Your total score is {players_scores[player_idx]}.")    

max_score = max(players_scores)            
winning_idx = players_scores.index(max_score)
print(f"Player number {winning_idx + 1} won with {max_score} points.")
        