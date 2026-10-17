import tkinter as tk
import random
import math
import array

# =========================
# Audio setup
# =========================
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    SOUND_ENABLED = True
except Exception as error:
    pygame = None
    SOUND_ENABLED = False
    print("Sound is unavailable:", error)


def play_sound(name):
    """Generate simple retro 8-bit style sounds without external audio files."""
    if not SOUND_ENABLED:
        return

    melodies = {
        "win": [(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.30)],
        "lose": [(494, 0.18), (392, 0.18), (330, 0.25), (262, 0.40)],
        "draw": [(440, 0.15), (440, 0.15), (523, 0.30)],
    }

    if name not in melodies:
        return

    sample_rate = 44100
    audio = array.array("h")

    for frequency, duration in melodies[name]:
        samples = int(sample_rate * duration)

        for i in range(samples):
            t = i / sample_rate
            wave = 1 if math.sin(2 * math.pi * frequency * t) >= 0 else -1
            fade = min(1.0, i / 300, (samples - i) / 300)
            audio.append(int(8500 * wave * max(0, fade)))

        # Short silence between notes
        audio.extend(array.array("h", [0] * 1800))

    try:
        sound = pygame.mixer.Sound(buffer=audio.tobytes())
        sound.play()
    except Exception as error:
        print("Could not play sound:", error)


# =========================
# Game settings
# =========================
WIDTH = 1000
HEIGHT = 680

BG_COLORS = [
    "#10002B",
    "#160B38",
    "#0B1D3A",
    "#101B33",
    "#200B35",
]

CHOICES = {
    "Rock": {"emoji": "✊", "beats": "Scissors"},
    "Paper": {"emoji": "✋", "beats": "Rock"},
    "Scissors": {"emoji": "✌️", "beats": "Paper"},
}

player_score = 0
computer_score = 0
round_number = 0
current_bg = 0
animation_step = 0

# =========================
# Main window
# =========================
root = tk.Tk()
root.title("Neon Battle | Rock Paper Scissors")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.minsize(850, 600)
root.configure(bg=BG_COLORS[0])

main = tk.Frame(root, bg=BG_COLORS[0])
main.pack(fill="both", expand=True)

title_label = tk.Label(
    main,
    text="ROCK  •  PAPER  •  SCISSORS",
    font=("Arial", 24, "bold"),
    fg="#00F5FF",
    bg=BG_COLORS[0],
)
title_label.pack(pady=(20, 5))

subtitle = tk.Label(
    main,
    text="NEON BATTLE  |  CHOOSE YOUR MOVE",
    font=("Arial", 10, "bold"),
    fg="#C77DFF",
    bg=BG_COLORS[0],
)
subtitle.pack(pady=(0, 14))

# =========================
# Scoreboard
# =========================
score_frame = tk.Frame(main, bg=BG_COLORS[0])
score_frame.pack(pady=5)

computer_score_label = tk.Label(
    score_frame, text="COMPUTER  0",
    font=("Arial", 14, "bold"), fg="#FF4DCE",
    bg=BG_COLORS[0], width=18
)
computer_score_label.pack(side="left", padx=15)

round_label = tk.Label(
    score_frame, text="ROUND 0",
    font=("Arial", 12, "bold"), fg="white",
    bg=BG_COLORS[0]
)
round_label.pack(side="left", padx=15)

player_score_label = tk.Label(
    score_frame, text="YOU  0",
    font=("Arial", 14, "bold"), fg="#00F5FF",
    bg=BG_COLORS[0], width=15
)
player_score_label.pack(side="left", padx=15)

# =========================
# Battle arena
# Computer LEFT / Player RIGHT
# =========================
arena = tk.Frame(
    main, bg="#191433",
    highlightbackground="#7448FF",
    highlightthickness=2
)
arena.pack(fill="both", expand=True, padx=35, pady=16)

arena.grid_columnconfigure(0, weight=1)
arena.grid_columnconfigure(1, weight=0)
arena.grid_columnconfigure(2, weight=1)

computer_panel = tk.Frame(arena, bg="#191433")
computer_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)

center_panel = tk.Frame(arena, bg="#191433")
center_panel.grid(row=0, column=1, sticky="ns", padx=8, pady=15)

player_panel = tk.Frame(arena, bg="#191433")
player_panel.grid(row=0, column=2, sticky="nsew", padx=10, pady=20)

tk.Label(
    computer_panel, text="COMPUTER",
    font=("Arial", 15, "bold"), fg="#FF4DCE",
    bg="#191433"
).pack(pady=5)

computer_hand = tk.Label(
    computer_panel, text="❔",
    font=("DejaVu Sans", 76), fg="white",
    bg="#191433"
)
computer_hand.pack(pady=15)

computer_choice_label = tk.Label(
    computer_panel, text="Waiting...",
    font=("Arial", 12, "bold"), fg="#FFB3EC",
    bg="#191433"
)
computer_choice_label.pack()

# Exact center divider and VS
tk.Frame(center_panel, bg="#7448FF", width=3).pack(
    fill="y", side="left", padx=5
)

tk.Label(
    center_panel, text="V\nS",
    font=("Arial", 20, "bold"), fg="#00F5FF",
    bg="#191433"
).pack(side="left", padx=8, expand=True, fill="y")

tk.Label(
    player_panel, text="PLAYER",
    font=("Arial", 15, "bold"), fg="#00F5FF",
    bg="#191433"
).pack(pady=5)

player_hand = tk.Label(
    player_panel, text="❔",
    font=("DejaVu Sans", 76), fg="white",
    bg="#191433"
)
player_hand.pack(pady=15)

player_choice_label = tk.Label(
    player_panel, text="Choose your move!",
    font=("Arial", 12, "bold"), fg="#A7F9FF",
    bg="#191433"
)
player_choice_label.pack()

# =========================
# Result labels
# =========================
result_label = tk.Label(
    main, text="READY TO BATTLE?",
    font=("Arial", 19, "bold"), fg="#FFD166",
    bg=BG_COLORS[0]
)
result_label.pack(pady=(3, 2))

detail_label = tk.Label(
    main, text="Choose Rock, Paper, or Scissors below",
    font=("Arial", 10), fg="white",
    bg=BG_COLORS[0]
)
detail_label.pack(pady=3)

# =========================
# Game logic
# =========================
def update_scoreboard():
    computer_score_label.config(text=f"COMPUTER  {computer_score}")
    player_score_label.config(text=f"YOU  {player_score}")
    round_label.config(text=f"ROUND {round_number}")


def choose_move(player_choice):
    global player_score, computer_score, round_number

    computer_choice = random.choice(list(CHOICES.keys()))
    round_number += 1

    player_hand.config(text=CHOICES[player_choice]["emoji"])
    computer_hand.config(text=CHOICES[computer_choice]["emoji"])
    player_choice_label.config(text=player_choice.upper())
    computer_choice_label.config(text=computer_choice.upper())

    if player_choice == computer_choice:
        result = "IT'S A TIE!"
        color = "#FFD166"
        detail = "Great minds think alike!"
        play_sound("draw")
    elif CHOICES[player_choice]["beats"] == computer_choice:
        player_score += 1
        result = "YOU WIN!"
        color = "#00F5FF"
        detail = f"{player_choice} beats {computer_choice}!"
        play_sound("win")
    else:
        computer_score += 1
        result = "YOU LOSE!"
        color = "#FF4DCE"
        detail = f"{computer_choice} beats {player_choice}!"
        play_sound("lose")

    result_label.config(text=result, fg=color)
    detail_label.config(text=detail)
    update_scoreboard()


# =========================
# Choice buttons
# =========================
buttons_frame = tk.Frame(main, bg=BG_COLORS[0])
buttons_frame.pack(pady=(9, 5))


def make_choice_button(parent, text, emoji, color, choice):
    return tk.Button(
        parent,
        text=f"{emoji}  {text}",
        font=("Arial", 13, "bold"),
        bg=color,
        fg="white",
        activebackground="#FFFFFF",
        activeforeground="#10002B",
        relief="flat",
        cursor="hand2",
        width=15,
        pady=10,
        command=lambda: choose_move(choice),
    )


make_choice_button(
    buttons_frame, "ROCK", "✊", "#6930C3", "Rock"
).pack(side="left", padx=7)

make_choice_button(
    buttons_frame, "PAPER", "✋", "#4361EE", "Paper"
).pack(side="left", padx=7)

make_choice_button(
    buttons_frame, "SCISSORS", "✌️", "#C9188B", "Scissors"
).pack(side="left", padx=7)

# =========================
# Reset game
# =========================
def reset_game():
    global player_score, computer_score, round_number

    player_score = 0
    computer_score = 0
    round_number = 0

    player_hand.config(text="❔")
    computer_hand.config(text="❔")
    player_choice_label.config(text="Choose your move!")
    computer_choice_label.config(text="Waiting...")
    result_label.config(text="READY TO BATTLE?", fg="#FFD166")
    detail_label.config(text="Choose Rock, Paper, or Scissors below")
    update_scoreboard()


tk.Button(
    main,
    text="↻  RESET GAME",
    font=("Arial", 10, "bold"),
    bg="#252044",
    fg="white",
    activebackground="#7448FF",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=reset_game,
    padx=18,
    pady=7,
).pack(pady=(5, 12))

# =========================
# Animated background
# =========================
def animate_background():
    global current_bg, animation_step

    animation_step += 1
    if animation_step >= 45:
        animation_step = 0
        current_bg = (current_bg + 1) % len(BG_COLORS)

    color = BG_COLORS[current_bg]

    root.configure(bg=color)
    main.configure(bg=color)
    score_frame.configure(bg=color)
    buttons_frame.configure(bg=color)

    title_label.configure(bg=color)
    subtitle.configure(bg=color)
    result_label.configure(bg=color)
    detail_label.configure(bg=color)
    computer_score_label.configure(bg=color)
    player_score_label.configure(bg=color)
    round_label.configure(bg=color)

    root.after(100, animate_background)


# =========================
# Run game
# =========================
update_scoreboard()
animate_background()
root.mainloop()