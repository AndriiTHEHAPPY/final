import pygame
import sys
import random
import warnings

# Скрываем предупреждение об устаревшем pkg_resources
warnings.filterwarnings("ignore", category=DeprecationWarning)

from settings import *
from buttons import Button
import sounds # Убедись, что функции в sounds.py не вызывают ошибок

# Инициализация
pygame.init()
pygame.mixer.init() # Инициализируем микшер отдельно для надежности
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кото-Паркур, Космобой и Змейка")
clock = pygame.time.Clock()
score_font = pygame.font.Font(None, 36)

# --- УЛУЧШЕННАЯ ФУНКЦИЯ ЗАГРУЗКИ ---
def get_img(name, size):
    for ext in [".png", ".jpg"]:
        try:
            path = f"images/{name}{ext}"
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            continue
    surf = pygame.Surface(size)
    surf.fill((200, 0, 200))
    return surf

# --- ЗАГРУЗКА ВСЕХ РЕСУРСОВ ---
menu_bg = get_img("settings_bg", (WIDTH, HEIGHT))

# Паркур
cat_img = get_img("cat", (60, 60))
sky_bg = get_img("skyforcat", (WIDTH, HEIGHT))
roof_img = get_img("roof", (WIDTH, 120))
pipe_img = get_img("chimney", (50, 100))
house_img = get_img("vorona", (100, 100))

# Космобой
space_bg = get_img("spacebackground", (WIDTH, HEIGHT))
ship_img = get_img("spaceship", (60, 60))
enemy_img = get_img("spaceenemy", (60, 60))
bullet_img = get_img("spacepatron", (15, 35))
repair_img = get_img("repair", (40, 40))

# Змейка
snake_bg = get_img("backgroundforsnake1", (WIDTH, HEIGHT))
S_SIZE = 40
s_head_img = get_img("snake_head", (S_SIZE, S_SIZE))
s_body_img = get_img("snake_bottom", (S_SIZE, S_SIZE))
mouse_img = get_img("mouse", (S_SIZE, S_SIZE))
virus_img = get_img("virus", (S_SIZE, S_SIZE))

# Кнопки
# Создаем кнопки с картинками (учитываем расширения с твоего скриншота!)
btn_snake = Button(300, 200, 220, 60, "Змейка", "images/button_snake.jpg")
btn_shooter = Button(300, 280, 220, 60, "Космобой", "images/button_spacebattle.png")
btn_dino = Button(300, 360, 220, 60, "Кото-паркур", "images/button_catparkour.jfif")

state = MENU
score = 0
player_health = 3

def reset_all():
    global dino_y, dino_vel, jump_count, obstacles, roof_x, score, player_health, roof_dist
    global ship_x, bullets, enemies, repair_items
    global snake_pos, snake_dir, apple_pos, virus_pos, last_snake_update
    score = 0
    dino_y, dino_vel, jump_count, roof_x, roof_dist = 430, 0, 0, 0, 0
    obstacles = []
    ship_x, player_health = WIDTH // 2 - 30, 3
    bullets, enemies, repair_items = [], [], []
    snake_pos = [[120, 120], [80, 120], [40, 120]]
    snake_dir = "RIGHT"
    apple_pos = [random.randrange(0, WIDTH//S_SIZE) * S_SIZE, random.randrange(0, HEIGHT//S_SIZE) * S_SIZE]
    virus_pos = [-S_SIZE, -S_SIZE]
    last_snake_update = pygame.time.get_ticks()

def draw_score(val, health=None):
    txt = score_font.render(f"Score: {val}", True, WHITE)
    screen.blit(txt, (WIDTH - 150, 20))
    if health is not None:
        htxt = score_font.render(f"Health: {health}", True, RED)
        screen.blit(htxt, (WIDTH - 150, 60))

# --- ИГРОВЫЕ ЛОГИКИ ---

def run_dino():
    global dino_y, dino_vel, jump_count, state, roof_x, score, roof_dist
    screen.blit(sky_bg, (0, 0))
    speed = 8
    roof_x -= speed
    roof_dist += speed
    if roof_dist >= WIDTH:
        score += 1
        roof_dist = 0
    if roof_x <= -WIDTH: roof_x = 0
    screen.blit(roof_img, (roof_x, 490))
    screen.blit(roof_img, (roof_x + WIDTH - 10, 490))

    dino_vel += 0.8
    dino_y += dino_vel
    if dino_y >= 430: dino_y, dino_vel, jump_count = 430, 0, 0

    cat_rect = screen.blit(cat_img, (100, dino_y))
    if random.random() < 0.015:
        type_obj = random.choice(["pipe", "house"])
        img, y_p = (pipe_img, 410) if type_obj == "pipe" else (house_img, 390)
        obstacles.append({"img": img, "rect": img.get_rect(topleft=(WIDTH, y_p))})

    for o in obstacles[:]:
        o["rect"].x -= speed
        screen.blit(o["img"], o["rect"])
        if cat_rect.inflate(-15, -15).colliderect(o["rect"]):
            if sounds.meow_snd: sounds.meow_snd.play()
            pygame.mixer.music.stop()
            state = MENU
        if o["rect"].right < 0: obstacles.remove(o)
    draw_score(score)

def run_shooter():
    global ship_x, state, score, player_health
    screen.blit(space_bg, (0, 0))
    k = pygame.key.get_pressed()
    if k[pygame.K_LEFT] and ship_x > 0: ship_x -= 7
    if k[pygame.K_RIGHT] and ship_x < WIDTH - 60: ship_x += 7

    ship_rect = pygame.Rect(ship_x, 500, 60, 60)
    screen.blit(ship_img, ship_rect)

    for b in bullets[:]:
        b.y -= 12
        screen.blit(bullet_img, (b.x, b.y))
        if b.bottom < 0: bullets.remove(b)

    if random.random() < 0.025:
        enemies.append(enemy_img.get_rect(topleft=(random.randint(0, WIDTH-60), -60)))

    for e in enemies[:]:
        e.y += 4
        screen.blit(enemy_img, e)
        if e.colliderect(ship_rect):
            player_health -= 1
            enemies.remove(e)
            if player_health <= 0:
                if sounds.hit_snd: sounds.hit_snd.play()
                pygame.mixer.music.stop()
                state = MENU
            elif sounds.hit_snd: sounds.hit_snd.play()
        for b in bullets[:]:
            if e.colliderect(b):
                if e in enemies: enemies.remove(e)
                if b in bullets: bullets.remove(b)
                score += 1
        if e.top > HEIGHT: enemies.remove(e)

    for r in repair_items[:]:
        r.y += 3
        screen.blit(repair_img, r)
        if r.colliderect(ship_rect):
            player_health = min(3, player_health + 1)
            if sounds.repair_snd: sounds.repair_snd.play() # Звук починки
            repair_items.remove(r)
    if random.random() < 0.005 and player_health < 3:
        repair_items.append(repair_img.get_rect(topleft=(random.randint(0, WIDTH-40), -40)))
    draw_score(score, player_health)

def run_snake():
    global snake_dir, apple_pos, virus_pos, state, last_snake_update, score
    screen.blit(snake_bg, (0, 0))
    now = pygame.time.get_ticks()
    if now - last_snake_update > 150:
        last_snake_update = now
        head = list(snake_pos[0])
        if snake_dir == "UP": head[1] -= S_SIZE
        elif snake_dir == "DOWN": head[1] += S_SIZE
        elif snake_dir == "LEFT": head[0] -= S_SIZE
        elif snake_dir == "RIGHT": head[0] += S_SIZE
        snake_pos.insert(0, head)

        if head == apple_pos:
            score += 1
            apple_pos = [random.randrange(0, WIDTH//S_SIZE)*S_SIZE, random.randrange(0, HEIGHT//S_SIZE)*S_SIZE]
            if random.random() < 0.3:
                virus_pos = [random.randrange(0, WIDTH//S_SIZE)*S_SIZE, random.randrange(0, HEIGHT//S_SIZE)*S_SIZE]
        else: snake_pos.pop()

        if head == virus_pos:
            if sounds.virus_snd: sounds.virus_snd.play() # Звук вируса
            score = max(0, score - 1)
            for _ in range(2):
                if len(snake_pos) > 2: snake_pos.pop()
            virus_pos = [-S_SIZE, -S_SIZE]

        if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT or head in snake_pos[1:]:
            if sounds.virus_snd: sounds.virus_snd.play() # Звук смерти змеи
            pygame.mixer.music.stop()
            state = MENU

    screen.blit(mouse_img, apple_pos)
    if virus_pos[0] >= 0: screen.blit(virus_img, virus_pos)
    for i, p in enumerate(snake_pos):
        if i == 0:
            a = {"UP":0, "DOWN":180, "LEFT":90, "RIGHT":270}
            screen.blit(pygame.transform.rotate(s_head_img, a[snake_dir]), p)
        else: screen.blit(s_body_img, p)
    draw_score(score)

# --- ОСНОВНОЙ ЦИКЛ ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if state == MENU:
            if btn_snake.is_clicked(event):
                reset_all(); state = SNAKE; sounds.play_bg("normal")
            if btn_shooter.is_clicked(event):
                reset_all(); state = SHOOTER; sounds.play_bg("space")
            if btn_dino.is_clicked(event):
                reset_all(); state = DINO; sounds.play_bg("normal")
        elif state == DINO and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and jump_count < 2:
                dino_vel = -16; jump_count += 1
                if sounds.jump_snd: sounds.jump_snd.play()
        elif state == SHOOTER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: bullets.append(pygame.Rect(ship_x+22, 480, 15, 35))
        elif state == SNAKE and event.type == pygame.KEYDOWN:
            dirs = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"}
            opp = {"UP":"DOWN", "DOWN":"UP", "LEFT":"RIGHT", "RIGHT":"LEFT"}
            if event.key in dirs and snake_dir != opp[dirs[event.key]]: snake_dir = dirs[event.key]
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.music.stop(); state = MENU

    if state == MENU:
        screen.blit(menu_bg, (0,0))
        btn_snake.draw(screen); btn_shooter.draw(screen); btn_dino.draw(screen)
    elif state == DINO: run_dino()
    elif state == SHOOTER: run_shooter()
    elif state == SNAKE: run_snake()

    pygame.display.flip()
    clock.tick(FPS)