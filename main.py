import asyncio
import pygame
import random
import math
import os
import json

# ============================================================
# WEB BUILD
# This version is structured for pygbag / browser deployment.
# ============================================================

# ============================================================
# REAL DRIVE - PAKISTAN
# Premium 2D / 2.5D Racing Game
# Prepared by Mazhar Abbas
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("REAL DRIVE - Pakistan")
clock = pygame.time.Clock()

# Colors
BLACK = (5, 7, 12)
WHITE = (245, 245, 245)
GRAY = (80, 88, 100)
LIGHT_GRAY = (180, 185, 195)
RED = (220, 45, 50)
GREEN = (45, 210, 120)
BLUE = (45, 130, 240)
GOLD = (245, 190, 60)
ORANGE = (255, 120, 35)
CYAN = (30, 220, 240)
DARK = (15, 18, 25)

FONT_BIG = pygame.font.SysFont("arial", 58, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 42, bold=True)
FONT = pygame.font.SysFont("arial", 25, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 18)
FONT_TINY = pygame.font.SysFont("arial", 14)

SAVE_FILE = "real_drive_save.json"

default_save = {
    "coins": 5000,
    "best_score": 0,
    "selected_car": 0,
    "cars": [True, False, False, False],
    "upgrades": {"speed": 1, "handling": 1, "brakes": 1, "nitro": 1}
}

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_save.copy()
    return default_save.copy()

save = load_save()

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump(save, f, indent=4)

CARS = [
    {"name": "R-SPORT", "color": (210, 25, 35), "price": 0, "speed": 250, "handling": 7, "brakes": 7},
    {"name": "GT-X", "color": (35, 100, 220), "price": 3500, "speed": 280, "handling": 8, "brakes": 8},
    {"name": "VIP BLACK", "color": (25, 25, 30), "price": 7000, "speed": 310, "handling": 9, "brakes": 9},
    {"name": "HYPER-X", "color": (150, 45, 220), "price": 12000, "speed": 350, "handling": 10, "brakes": 10}
]

STATE_MENU = "menu"
STATE_RACE = "race"
STATE_GARAGE = "garage"
STATE_CARS = "cars"
STATE_SETTINGS = "settings"
STATE_MISSIONS = "missions"
STATE_PAUSE = "pause"
STATE_GAMEOVER = "gameover"

game_state = STATE_MENU

player_x = WIDTH // 2
player_y = HEIGHT - 145
road_center = WIDTH // 2
road_width = 620

speed = 0
target_speed = 0
score = 0
coins = 0
distance = 0
health = 100
fuel = 100
nitro = 100

weather = "clear"
camera_mode = 0

traffic = []
collectibles = []
particles = []

road_offset = 0
spawn_timer = 0
coin_timer = 0
race_time = 0
near_miss = 0


def text(txt, x, y, font=FONT, color=WHITE, center=False):
    surf = font.render(str(txt), True, color)
    rect = surf.get_rect()
    rect.center = (x, y) if center else rect.center
    if not center:
        rect.topleft = (x, y)
    screen.blit(surf, rect)


def button(rect, label, active=False):
    color = (65, 80, 105) if active else (35, 40, 52)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (100, 110, 130), rect, 2, border_radius=12)
    text(label, rect.centerx, rect.centery, FONT, WHITE, True)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def draw_sky():
    for y in range(0, HEIGHT // 2):
        ratio = y / (HEIGHT // 2)
        color = (
            int(8 + 25 * ratio),
            int(12 + 30 * ratio),
            int(28 + 45 * ratio)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))


def draw_city():
    base_y = HEIGHT // 2
    random.seed(10)
    x = 0

    while x < WIDTH:
        w = random.randint(45, 100)
        h = random.randint(70, 220)
        pygame.draw.rect(screen, (20, 25, 35), (x, base_y - h, w, h))

        for wy in range(base_y - h + 20, base_y - 10, 30):
            for wx in range(x + 10, x + w - 5, 22):
                if random.random() > 0.45:
                    pygame.draw.rect(screen, (220, 190, 90), (wx, wy, 8, 10))
        x += w + 8


def draw_road():
    pygame.draw.rect(screen, (18, 50, 35), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    road_left = road_center - road_width // 2
    road_right = road_center + road_width // 2

    pygame.draw.rect(screen, (38, 40, 45), (road_left, 0, road_width, HEIGHT))

    pygame.draw.line(screen, (220, 220, 220), (road_left, 0), (road_left, HEIGHT), 7)
    pygame.draw.line(screen, (220, 220, 220), (road_right, 0), (road_right, HEIGHT), 7)

    lane_width = road_width // 3

    for lane in range(1, 3):
        x = road_left + lane * lane_width
        for y in range(-100, HEIGHT + 100, 90):
            yy = y + road_offset
            pygame.draw.rect(screen, (235, 235, 210), (x - 4, yy, 8, 50))

    for y in range(-50, HEIGHT, 100):
        yy = (y + road_offset * 0.6) % (HEIGHT + 100) - 50

        pygame.draw.line(screen, (70, 75, 80),
                         (road_left - 25, yy),
                         (road_left - 25, yy - 55), 4)
        pygame.draw.circle(screen, (255, 210, 100),
                           (road_left - 25, yy - 60), 7)

        pygame.draw.line(screen, (70, 75, 80),
                         (road_right + 25, yy),
                         (road_right + 25, yy - 55), 4)
        pygame.draw.circle(screen, (255, 210, 100),
                           (road_right + 25, yy - 60), 7)


def draw_car(x, y, car_data, scale=1.0, player=False):
    w = int(82 * scale)
    h = int(145 * scale)
    body = car_data["color"]

    pygame.draw.ellipse(screen, (5, 5, 5),
                        (x - w // 2 - 8, y + h // 2 - 5, w + 16, 25))

    wheel_w = int(15 * scale)
    wheel_h = int(38 * scale)

    for wx in [x - w // 2 - 2, x + w // 2 - wheel_w + 2]:
        pygame.draw.rect(screen, (8, 8, 10),
                         (wx, y - h // 2 + 25, wheel_w, wheel_h),
                         border_radius=5)
        pygame.draw.rect(screen, (8, 8, 10),
                         (wx, y + h // 2 - 55, wheel_w, wheel_h),
                         border_radius=5)

    body_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
    pygame.draw.rect(screen, body, body_rect, border_radius=18)

    highlight = tuple(min(255, c + 55) for c in body)
    pygame.draw.line(screen, highlight,
                     (x - w // 3, y - h // 2 + 12),
                     (x - w // 3, y + h // 2 - 12), 4)

    window_color = (25, 35, 48)

    pygame.draw.polygon(screen, window_color, [
        (x - w // 3, y - h // 2 + 22),
        (x + w // 3, y - h // 2 + 22),
        (x + w // 4, y - 5),
        (x - w // 4, y - 5)
    ])

    pygame.draw.line(screen, (120, 180, 210),
                     (x - w // 4, y - h // 2 + 28),
                     (x + w // 5, y - 15), 3)

    pygame.draw.rect(screen, (15, 15, 18),
                     (x - w // 2 + 8, y + h // 2 - 18, w - 16, 10),
                     border_radius=4)

    pygame.draw.rect(screen, (230, 245, 255),
                     (x - w // 2 + 10, y + h // 2 - 38, 18, 10),
                     border_radius=4)
    pygame.draw.rect(screen, (230, 245, 255),
                     (x + w // 2 - 28, y + h // 2 - 38, 18, 10),
                     border_radius=4)

    if player:
        pygame.draw.line(screen, CYAN,
                         (x - w // 2, y),
                         (x - w // 2, y + h // 3), 2)
        pygame.draw.line(screen, CYAN,
                         (x + w // 2, y),
                         (x + w // 2, y + h // 3), 2)


def spawn_traffic():
    lanes = [
        road_center - road_width // 3,
        road_center,
        road_center + road_width // 3
    ]
    lane = random.choice(lanes)
    car = random.choice(CARS)

    traffic.append({
        "x": lane + random.randint(-25, 25),
        "y": -150,
        "speed": random.randint(3, 7),
        "car": car,
        "scale": random.uniform(0.75, 1.0)
    })


def update_traffic():
    global health, score, near_miss

    player_rect = pygame.Rect(player_x - 35, player_y - 60, 70, 120)

    for car in traffic[:]:
        car["y"] += car["speed"] + speed / 90

        car_rect = pygame.Rect(car["x"] - 30, car["y"] - 50, 60, 100)

        if player_rect.colliderect(car_rect):
            health -= 20
            create_particles(player_x, player_y, (255, 90, 40), 18)
            if car in traffic:
                traffic.remove(car)

        elif car["y"] > HEIGHT + 150:
            traffic.remove(car)
            score += 100
            near_miss += 1


def spawn_coin():
    lanes = [
        road_center - road_width // 3,
        road_center,
        road_center + road_width // 3
    ]

    collectibles.append({
        "x": random.choice(lanes),
        "y": -30,
        "rotation": 0
    })


def update_coins():
    global coins, score

    player_rect = pygame.Rect(player_x - 40, player_y - 70, 80, 140)

    for coin in collectibles[:]:
        coin["y"] += 5 + speed / 100
        coin["rotation"] += 8

        coin_rect = pygame.Rect(
            coin["x"] - 14, coin["y"] - 14, 28, 28
        )

        if player_rect.colliderect(coin_rect):
            coins += 25
            score += 250
            create_particles(coin["x"], coin["y"], GOLD, 12)
            collectibles.remove(coin)

        elif coin["y"] > HEIGHT:
            collectibles.remove(coin)


def draw_coins():
    for coin in collectibles:
        pygame.draw.circle(screen, GOLD,
                           (int(coin["x"]), int(coin["y"])), 13)
        pygame.draw.circle(screen, (255, 225, 100),
                           (int(coin["x"]), int(coin["y"])), 7)


def create_particles(x, y, color, amount=10):
    for _ in range(amount):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 4),
            "life": random.randint(15, 35),
            "color": color
        })


def update_particles():
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)


def draw_particles():
    for p in particles:
        radius = max(1, p["life"] // 5)
        pygame.draw.circle(screen, p["color"],
                           (int(p["x"]), int(p["y"])), radius)


def draw_rain():
    if weather != "rain":
        return

    for _ in range(180):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.line(screen, (130, 160, 190),
                         (x, y), (x - 5, y + 18), 1)


def draw_bar(x, y, width, height, value, color, label):
    pygame.draw.rect(screen, (20, 20, 25),
                     (x, y, width, height), border_radius=6)
    pygame.draw.rect(screen, color,
                     (x, y, int(width * value / 100), height),
                     border_radius=6)
    text(label, x, y - 24, FONT_SMALL)


def draw_hud():
    panel = pygame.Surface((WIDTH, 95), pygame.SRCALPHA)
    panel.fill((5, 8, 15, 210))
    screen.blit(panel, (0, 0))

    text("REAL DRIVE", 25, 15, FONT_TITLE, WHITE)
    text("PAKISTAN", 27, 58, FONT_SMALL, GOLD)

    text(f"{int(speed)} KM/H", WIDTH // 2, 35,
         FONT_TITLE, CYAN, True)

    text(f"SCORE {score}", WIDTH - 270, 20, FONT, WHITE)
    text(f"COINS {coins}", WIDTH - 150, 20, FONT, GOLD)

    draw_bar(25, HEIGHT - 75, 210, 15, health, RED, "DAMAGE")
    draw_bar(270, HEIGHT - 75, 210, 15, fuel, GREEN, "FUEL")
    draw_bar(515, HEIGHT - 75, 210, 15, nitro, CYAN, "NITRO [SPACE]")

    text("WASD / ARROWS", WIDTH - 200, HEIGHT - 60,
         FONT_SMALL, LIGHT_GRAY)


def draw_garage():
    screen.fill((8, 10, 16))

    for x in range(0, WIDTH, 80):
        pygame.draw.line(screen, (18, 23, 32),
                         (x, 0), (x, HEIGHT))

    text("VIP GARAGE", WIDTH // 2, 60,
         FONT_BIG, GOLD, True)

    selected = save["selected_car"]
    car = CARS[selected]

    draw_car(WIDTH // 2, 330, car, 1.7, True)

    text(car["name"], WIDTH // 2, 480,
         FONT_TITLE, WHITE, True)

    stats = [
        ("SPEED", car["speed"], 350),
        ("HANDLING", car["handling"], 10),
        ("BRAKES", car["brakes"], 10)
    ]

    y = 530
    for name, value, maximum in stats:
        text(name, 390, y, FONT_SMALL)

        pygame.draw.rect(screen, (35, 40, 50),
                         (500, y + 3, 300, 15),
                         border_radius=7)

        pygame.draw.rect(screen, CYAN,
                         (500, y + 3,
                          int(300 * value / maximum), 15),
                         border_radius=7)
        y += 35

    button(pygame.Rect(30, HEIGHT - 70, 170, 45), "BACK")


def draw_cars_menu():
    screen.fill((8, 10, 16))

    text("CAR COLLECTION", WIDTH // 2, 60,
         FONT_BIG, WHITE, True)

    for i, car in enumerate(CARS):
        x = 80 + i * 300
        rect = pygame.Rect(x, 150, 250, 430)

        pygame.draw.rect(screen, (18, 22, 30),
                         rect, border_radius=15)

        if save["selected_car"] == i:
            pygame.draw.rect(screen, GOLD, rect,
                             3, border_radius=15)

        draw_car(x + 125, 275, car, 1.05,
                 i == save["selected_car"])

        text(car["name"], x + 125, 375,
             FONT, WHITE, True)

        if save["cars"][i]:
            if save["selected_car"] == i:
                text("SELECTED", x + 125, 430,
                     FONT_SMALL, GREEN, True)
            else:
                button(pygame.Rect(x + 50, 420, 150, 45),
                       "SELECT")
        else:
            text(f"COINS {car['price']}", x + 125, 430,
                 FONT, GOLD, True)
            button(pygame.Rect(x + 50, 490, 150, 45), "BUY")

    button(pygame.Rect(30, HEIGHT - 65, 170, 45), "BACK")


def draw_menu():
    draw_sky()
    draw_city()
    draw_road()

    car = CARS[save["selected_car"]]
    draw_car(WIDTH // 2, HEIGHT - 170, car, 1.7, True)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    screen.blit(overlay, (0, 0))

    text("REAL DRIVE", WIDTH // 2, 95,
         FONT_BIG, WHITE, True)

    text("PAKISTAN", WIDTH // 2, 150,
         FONT_TITLE, GOLD, True)

    text("PREMIUM STREET RACING EXPERIENCE",
         WIDTH // 2, 195, FONT_SMALL,
         LIGHT_GRAY, True)

    buttons = [
        ("START RACE", 270),
        ("GARAGE", 330),
        ("CARS", 390),
        ("MISSIONS", 450),
        ("SETTINGS", 510)
    ]

    for label, y in buttons:
        button(pygame.Rect(WIDTH // 2 - 140, y, 280, 48),
               label)

    text(f"BEST SCORE: {save['best_score']}",
         WIDTH // 2, 650, FONT_SMALL, GOLD, True)

    text("Prepared by Mazhar Abbas",
         WIDTH - 240, HEIGHT - 25,
         FONT_TINY, LIGHT_GRAY)


def draw_missions():
    screen.fill((8, 10, 16))

    text("MISSIONS", WIDTH // 2, 65,
         FONT_BIG, GOLD, True)

    missions = [
        ("First Drive", "Drive 2 KM", distance >= 2),
        ("Speed Demon", "Reach 250 KM/H", speed >= 250),
        ("Collector", "Collect 20 coins", coins >= 20),
        ("Survivor", "Keep damage above 50%", health >= 50),
        ("Champion", "Score 10,000 points", score >= 10000)
    ]

    y = 160

    for name, description, complete in missions:
        pygame.draw.rect(screen, (20, 25, 34),
                         (280, y, 720, 75),
                         border_radius=12)

        text(name, 310, y + 12, FONT)
        text(description, 310, y + 43,
             FONT_SMALL, LIGHT_GRAY)

        text("COMPLETED" if complete else "LOCKED",
             850, y + 25, FONT_SMALL,
             GREEN if complete else RED)

        y += 90

    button(pygame.Rect(30, HEIGHT - 70, 170, 45), "BACK")


def draw_settings():
    screen.fill((8, 10, 16))

    text("SETTINGS", WIDTH // 2, 70,
         FONT_BIG, WHITE, True)

    settings = [
        "GRAPHICS        ULTRA",
        "SOUND            ON",
        "WEATHER          " + weather.upper(),
        "CAMERA           " + ["CHASE", "HOOD", "COCKPIT"][camera_mode]
    ]

    y = 180

    for item in settings:
        pygame.draw.rect(screen, (20, 25, 34),
                         (350, y, 580, 65),
                         border_radius=10)
        text(item, 380, y + 18, FONT)
        y += 85

    text("Press W/S to change weather/camera",
         WIDTH // 2, 570, FONT_SMALL,
         LIGHT_GRAY, True)

    button(pygame.Rect(30, HEIGHT - 70, 170, 45), "BACK")


def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    text("PAUSED", WIDTH // 2, 220,
         FONT_BIG, WHITE, True)

    button(pygame.Rect(WIDTH // 2 - 130, 320, 260, 50),
           "RESUME")
    button(pygame.Rect(WIDTH // 2 - 130, 390, 260, 50),
           "MAIN MENU")


def draw_gameover():
    screen.fill((8, 8, 12))

    text("RACE OVER", WIDTH // 2, 170,
         FONT_BIG, RED, True)

    text(f"SCORE: {score}", WIDTH // 2, 270,
         FONT_TITLE, WHITE, True)

    text(f"COINS: {coins}", WIDTH // 2, 320,
         FONT, GOLD, True)

    text(f"DISTANCE: {int(distance)} KM",
         WIDTH // 2, 365, FONT, CYAN, True)

    button(pygame.Rect(WIDTH // 2 - 130, 450, 260, 50),
           "PLAY AGAIN")
    button(pygame.Rect(WIDTH // 2 - 130, 520, 260, 50),
           "MAIN MENU")


def start_race():
    global game_state, player_x, speed, target_speed
    global score, coins, health, fuel, nitro
    global distance, road_offset, spawn_timer
    global coin_timer, race_time, near_miss

    game_state = STATE_RACE
    player_x = WIDTH // 2
    speed = 0
    target_speed = 0
    score = 0
    coins = 0
    health = 100
    fuel = 100
    nitro = 100
    traffic.clear()
    collectibles.clear()
    particles.clear()
    road_offset = 0
    spawn_timer = 0
    coin_timer = 0
    distance = 0
    race_time = 0
    near_miss = 0


def update_race(keys, dt):
    global player_x, speed, target_speed
    global road_offset, spawn_timer, coin_timer
    global fuel, nitro, distance, score, race_time
    global game_state

    car = CARS[save["selected_car"]]
    handling = car["handling"] + save["upgrades"]["handling"]

    move_speed = 7 + handling * 0.35

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= move_speed

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += move_speed

    road_left = road_center - road_width // 2 + 55
    road_right = road_center + road_width // 2 - 55

    player_x = clamp(player_x, road_left, road_right)

    max_speed = car["speed"] + save["upgrades"]["speed"] * 12

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        target_speed = max_speed
        fuel -= 0.025
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        target_speed = 80
    else:
        target_speed = 145

    if keys[pygame.K_SPACE] and nitro > 0:
        target_speed += 90
        nitro -= 0.7
        create_particles(player_x, player_y + 70, CYAN, 2)
    else:
        nitro = min(100, nitro + 0.12)

    speed += (target_speed - speed) * 0.045
    speed = clamp(speed, 0, max_speed + 90)

    road_offset += speed * 0.08
    if road_offset > 90:
        road_offset -= 90

    distance += speed * dt / 100
    score += int(speed * dt * 0.7)

    fuel -= 0.008 + speed / 50000

    spawn_timer += 1
    if spawn_timer > max(20, 65 - int(speed / 10)):
        spawn_traffic()
        spawn_timer = 0

    coin_timer += 1
    if coin_timer > 100:
        spawn_coin()
        coin_timer = 0

    update_traffic()
    update_coins()
    update_particles()

    race_time += dt

    if health <= 0 or fuel <= 0:
        if score > save["best_score"]:
            save["best_score"] = score
        save_game()
        game_state = STATE_GAMEOVER


def draw_race():
    draw_sky()
    draw_city()
    draw_road()

    for car in traffic:
        draw_car(int(car["x"]), int(car["y"]),
                 car["car"], car["scale"])

    draw_coins()

    player_car = CARS[save["selected_car"]]

    if camera_mode == 0:
        player_scale = 1.35
        player_y_draw = player_y
    elif camera_mode == 1:
        player_scale = 1.1
        player_y_draw = HEIGHT - 105
    else:
        player_scale = 0.85
        player_y_draw = HEIGHT - 85

    draw_car(int(player_x), int(player_y_draw),
             player_car, player_scale, True)

    draw_particles()
    draw_rain()
    draw_hud()


def handle_menu_click(pos):
    global game_state
    x, y = pos

    if WIDTH // 2 - 140 < x < WIDTH // 2 + 140:
        if 270 < y < 318:
            start_race()
        elif 330 < y < 378:
            game_state = STATE_GARAGE
        elif 390 < y < 438:
            game_state = STATE_CARS
        elif 450 < y < 498:
            game_state = STATE_MISSIONS
        elif 510 < y < 558:
            game_state = STATE_SETTINGS


def handle_cars_click(pos):
    global game_state
    x, y = pos

    if y > HEIGHT - 90:
        game_state = STATE_MENU
        return

    for i in range(len(CARS)):
        card_x = 80 + i * 300

        if card_x < x < card_x + 250:
            if save["cars"][i]:
                save["selected_car"] = i
                save_game()
            else:
                if save["coins"] >= CARS[i]["price"]:
                    save["coins"] -= CARS[i]["price"]
                    save["cars"][i] = True
                    save["selected_car"] = i
                    save_game()


def handle_garage_click(pos):
    global game_state
    if pos[1] > HEIGHT - 90:
        game_state = STATE_MENU


running = True

async def main():
    global running, game_state
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                save_game()
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if game_state == STATE_MENU:
                    handle_menu_click(event.pos)

                elif game_state == STATE_CARS:
                    handle_cars_click(event.pos)

                elif game_state == STATE_GARAGE:
                    handle_garage_click(event.pos)

                elif game_state == STATE_MISSIONS:
                    if event.pos[1] > HEIGHT - 90:
                        game_state = STATE_MENU

                elif game_state == STATE_SETTINGS:
                    if event.pos[1] > HEIGHT - 90:
                        game_state = STATE_MENU

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if game_state == STATE_RACE:
                        game_state = STATE_PAUSE

                    elif game_state == STATE_PAUSE:
                        game_state = STATE_RACE

                    elif game_state in [
                        STATE_GARAGE,
                        STATE_CARS,
                        STATE_MISSIONS,
                        STATE_SETTINGS
                    ]:
                        game_state = STATE_MENU

                if game_state == STATE_PAUSE:

                    if event.key == pygame.K_r:
                        game_state = STATE_RACE

                    elif event.key == pygame.K_m:
                        game_state = STATE_MENU

                if game_state == STATE_GAMEOVER:

                    if event.key == pygame.K_RETURN:
                        start_race()

                    elif event.key == pygame.K_m:
                        game_state = STATE_MENU

                if game_state == STATE_SETTINGS:

                    if event.key == pygame.K_w:
                        camera_mode = (camera_mode + 1) % 3

                    elif event.key == pygame.K_s:
                        weather = "rain" if weather == "clear" else "clear"

        if game_state == STATE_RACE:
            keys = pygame.key.get_pressed()
            update_race(keys, dt)

        if game_state == STATE_MENU:
            draw_menu()
        elif game_state == STATE_RACE:
            draw_race()
        elif game_state == STATE_GARAGE:
            draw_garage()
        elif game_state == STATE_CARS:
            draw_cars_menu()
        elif game_state == STATE_MISSIONS:
            draw_missions()
        elif game_state == STATE_SETTINGS:
            draw_settings()
        elif game_state == STATE_PAUSE:
            draw_race()
            draw_pause()
        elif game_state == STATE_GAMEOVER:
            draw_gameover()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
