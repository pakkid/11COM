import random

CHOICES = ["rock", "paper", "scissors"]
WINS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

player_choice = CHOICES[int(input("Choose 1-rock, 2-paper, 3-scissors: ")) - 1]
computer_choice = random.choice(CHOICES)

print(f"Player: {player_choice}\nComputer: {computer_choice}")

if player_choice == computer_choice:
    print("Tie!")
elif WINS[player_choice] == computer_choice:
    print("Player wins!")
else:
    print("Computer wins!")
