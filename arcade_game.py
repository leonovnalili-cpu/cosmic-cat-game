import tkinter as tk
import random
import pygame

# --- настройки ---
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

PLAYER_SPEED = 15
COIN_SPEED = 5
COIN_ACCELERATION = 0.005

# --- окно ---
window = tk.Tk()
window.title("Космическая охота")
window.resizable(False, False)

canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
canvas.pack()

# --- фон ---
bg_img = tk.PhotoImage(file="background.png")
canvas.create_image(0, 0, image=bg_img, anchor="nw")

# --- кадры котика ---
player_frames = [
    tk.PhotoImage(file="player1.png"),
    tk.PhotoImage(file="player2.png"),
    tk.PhotoImage(file="player3.png")
]

current_frame = 0
player_img = player_frames[current_frame]

player_width = player_img.width()
player_height = player_img.height()

# --- звезда ---
coin_img = tk.PhotoImage(file="coin.png")
coin_width = coin_img.width()
coin_height = coin_img.height()

# --- позиции ---
player_x = WINDOW_WIDTH // 2
player_y = WINDOW_HEIGHT - player_height // 2 - 10

player = canvas.create_image(player_x, player_y, image=player_img)

coin_x = random.randint(coin_width // 2, WINDOW_WIDTH - coin_width // 2)
coin_y = -coin_height // 2
coin = canvas.create_image(coin_x, coin_y, image=coin_img)

score = 0
score_text = canvas.create_text(10, 10, anchor="nw", fill="white",
                                font=("Arial", 16), text=f"Счёт: {score}")

# --- жизни ---
lives = 3
lives_text = canvas.create_text(10, 30, anchor="nw", fill="red",
                                font=("Arial", 16), text=f"Жизни: {lives}")

# --- облако ---
cloud_x = -100
cloud_y = 80
cloud = canvas.create_oval(cloud_x, cloud_y, cloud_x + 120, cloud_y + 50,
                           fill="white", outline="")

# --- падающие звёзды ---
stars = []
for _ in range(20):
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    star = canvas.create_oval(x, y, x+2, y+2, fill="white", outline="")
    stars.append(star)

# --- метеор ---
meteor_x = random.randint(20, WINDOW_WIDTH - 20)
meteor_y = -20
meteor = canvas.create_oval(meteor_x - 15, meteor_y - 15,
                            meteor_x + 15, meteor_y + 15,
                            fill="orange", outline="")

# --- управление ---
keys_pressed = set()

def key_press(event):
    keys_pressed.add(event.keysym)

def key_release(event):
    if event.keysym in keys_pressed:
        keys_pressed.remove(event.keysym)

window.bind("<KeyPress>", key_press)
window.bind("<KeyRelease>", key_release)

# --- движение игрока ---
def move_player():
    global player_x

    if "Left" in keys_pressed:
        player_x -= PLAYER_SPEED
    if "Right" in keys_pressed:
        player_x += PLAYER_SPEED

    if player_x < player_width // 2:
        player_x = player_width // 2
    if player_x > WINDOW_WIDTH - player_width // 2:
        player_x = WINDOW_WIDTH - player_width // 2

    canvas.coords(player, player_x, player_y)

# --- анимация котика ---
def animate_player():
    global current_frame, player_img
    current_frame = (current_frame + 1) % len(player_frames)
    player_img = player_frames[current_frame]
    canvas.itemconfig(player, image=player_img)
    window.after(150, animate_player)

# --- облако ---
def move_cloud():
    global cloud_x
    cloud_x += 1
    if cloud_x > WINDOW_WIDTH + 100:
        cloud_x = -120
    canvas.coords(cloud, cloud_x, cloud_y, cloud_x + 120, cloud_y + 50)

# --- падающие звёзды ---
def move_stars():
    for star in stars:
        x, y, _, _ = canvas.coords(star)
        y += 2
        if y > WINDOW_HEIGHT:
            y = random.randint(-20, 0)
            x = random.randint(0, WINDOW_WIDTH)
        canvas.coords(star, x, y, x+2, y+2)

# --- вспышка ---
def flash_effect():
    flash = canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
                                    fill="white", outline="")
    window.after(50, lambda: canvas.delete(flash))

# --- логика звезды ---
def reset_coin():
    global coin_x, coin_y, COIN_SPEED
    coin_x = random.randint(coin_width // 2, WINDOW_WIDTH - coin_width // 2)
    coin_y = -coin_height // 2
COIN_SPEED = 5
canvas.coords(coin, coin_x, coin_y)

def check_collision():
    global score

    px1 = player_x - player_width // 2
    px2 = player_x + player_width // 2
    py1 = player_y - player_height // 2
    py2 = player_y + player_height // 2

    cx1 = coin_x - coin_width // 2
    cx2 = coin_x + coin_width // 2
    cy1 = coin_y - coin_height // 2
    cy2 = coin_y + coin_height // 2

    overlap_x = (px1 < cx2) and (px2 > cx1)
    overlap_y = (py1 < cy2) and (py2 > cy1)

    if overlap_x and overlap_y:
        score += 1
        canvas.itemconfig(score_text, text=f"Счёт: {score}")

        coin_sound.play()
        flash_effect()

        if score % 5 == 0:
            canvas.create_text(WINDOW_WIDTH//2, 50, text="Отлично!",
                               fill="yellow", font=("Arial", 20))

        reset_coin()

# --- метеор ---
def move_meteor():
    global meteor_y, meteor_x, lives

    meteor_y += 6
    canvas.coords(meteor, meteor_x - 15, meteor_y - 15,
                  meteor_x + 15, meteor_y + 15)

    if meteor_y > WINDOW_HEIGHT + 20:
        meteor_x = random.randint(20, WINDOW_WIDTH - 20)
        meteor_y = -20

    px1 = player_x - player_width // 2
    px2 = player_x + player_width // 2
    py1 = player_y - player_height // 2
    py2 = player_y + player_height // 2

    mx1 = meteor_x - 15
    mx2 = meteor_x + 15
    my1 = meteor_y - 15
    my2 = meteor_y + 15

    overlap_x = (px1 < mx2) and (px2 > mx1)
    overlap_y = (py1 < my2) and (py2 > my1)

    if overlap_x and overlap_y:
        lives -= 1
        canvas.itemconfig(lives_text, text=f"Жизни: {lives}")
        flash_effect()

        meteor_x = random.randint(20, WINDOW_WIDTH - 20)
        meteor_y = -20

        if lives <= 0:
            canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2,
                               text="Игра окончена",
                               fill="red", font=("Arial", 32))
            return "STOP"

# --- музыка ---
pygame.mixer.init()
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)

coin_sound = pygame.mixer.Sound("coin.wav")

# --- движение звезды ---
def move_coin():
    global coin_y, COIN_SPEED
    coin_y += COIN_SPEED
    COIN_SPEED += COIN_ACCELERATION
    canvas.coords(coin, coin_x, coin_y)

    if coin_y - coin_height // 2 > WINDOW_HEIGHT:
        reset_coin()

    check_collision()

# --- игровой цикл ---
def game_loop():
    if move_meteor() == "STOP":
        return

    move_player()
    move_coin()
    move_cloud()
    move_stars()

    window.after(20, game_loop)

animate_player()
game_loop()
window.mainloop()