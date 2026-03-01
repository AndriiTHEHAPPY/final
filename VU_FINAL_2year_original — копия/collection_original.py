import pygame
import sys
import random
from settings import *
from buttons import Button
import sounds

# Инициализация
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кото-Паркур, Космобой и Змейка")
clock = pygame.time.Clock()


# --- УЛУЧШЕННАЯ ФУНКЦИЯ ЗАГРУЗКИ ---
def get_img(name, size):
    # Пробуем png, если не выйдет — jpg (для фонов)
    for ext in [".png", ".jpg"]:
        try:
            path = f"images/{name}{ext}"
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            continue
    # Заглушка, если файл вообще не найден
    surf = pygame.Surface(size)
    surf.fill((200, 0, 200))  # Розовый цвет ошибки
    return surf


# --- ЗАГРУЗКА ВСЕХ РЕСУРСОВ ---
# Дино (Кото-паркур)
cat_img = get_img("cat", (60, 60))
sky_bg = get_img("skyforcat", (WIDTH, HEIGHT))
pipe_img = get_img("chimney", (50, 100))
house_img = get_img("house", (100, 100))

# Космос
space_bg = get_img("spacebackground", (WIDTH, HEIGHT))
ship_img = get_img("spaceship", (60, 60))
enemy_img = get_img("spaceenemy", (60, 60))
bullet_img = get_img("spacepatron", (15, 35))

# Змейка
snake_bg = get_img("backgroundforsnake1", (WIDTH, HEIGHT))
s_head_img = get_img("snake_head", (20, 20))
s_body_img = get_img("snake_bottom", (20, 20))

# Кнопки меню
btn_snake = Button(300, 200, 200, 50, "Змейка", GREEN, (0, 150, 0))
btn_shooter = Button(300, 280, 200, 50, "Космобой", BLUE, (0, 0, 150))
btn_dino = Button(300, 360, 200, 50, "Кото-Паркур", GRAY, (100, 100, 100))

state = MENU


# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ИГР ---
def reset_all():
    global dino_y, dino_vel, is_jump, obstacles, ship_x, bullets, enemies
    global snake_pos, snake_dir, apple_pos, last_snake_update
    # Dino
    dino_y, dino_vel, is_jump = 430, 0, False
    obstacles = []
    # Shooter
    ship_x = WIDTH // 2 - 30
    bullets, enemies = [], []
    # Snake
    snake_pos = [[100, 100], [80, 100], [60, 100]]
    snake_dir = "RIGHT"
    apple_pos = [random.randrange(0, 39) * 20, random.randrange(0, 29) * 20]
    last_snake_update = pygame.time.get_ticks()


reset_all()


# --- ЛОГИКА ИГР ---

def run_dino():
    global dino_y, dino_vel, is_jump, state
    screen.blit(sky_bg, (0, 0))

    # Прыжок
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not is_jump:
        dino_vel = -16
        is_jump = True
        if sounds.jump_snd: sounds.jump_snd.play()

    if is_jump:
        dino_vel += 0.8
        dino_y += dino_vel
        if dino_y >= 430:
            dino_y = 430
            is_jump = False

    cat_rect = screen.blit(cat_img, (100, dino_y))

    # Препятствия
    if random.random() < 0.015:
        type_obj = random.choice(["pipe", "house"])
        img = pipe_img if type_obj == "pipe" else house_img
        y_pos = 410 if type_obj == "pipe" else 390
        obstacles.append({"img": img, "rect": img.get_rect(topleft=(WIDTH, y_pos))})

    for o in obstacles[:]:
        o["rect"].x -= 8
        screen.blit(o["img"], o["rect"])
        # Проверка столкновения (чуть уменьшаем хитбокс для честности)
        if cat_rect.inflate(-15, -15).colliderect(o["rect"]):
            if sounds.meow_snd: sounds.meow_snd.play()
            state = MENU
        if o["rect"].right < 0: obstacles.remove(o)


def run_shooter():
    global ship_x, state
    screen.blit(space_bg, (0, 0))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and ship_x > 0: ship_x -= 7
    if keys[pygame.K_RIGHT] and ship_x < WIDTH - 60: ship_x += 7

    ship_rect = pygame.Rect(ship_x, 500, 60, 60)
    screen.blit(ship_img, ship_rect)

    # Пули
    for b in bullets[:]:
        b.y -= 12
        screen.blit(bullet_img, (b.x, b.y))
        if b.bottom < 0: bullets.remove(b)

    # Враги
    if random.random() < 0.025:
        enemies.append(enemy_img.get_rect(topleft=(random.randint(0, WIDTH - 60), -60)))

    for e in enemies[:]:
        e.y += 4
        screen.blit(enemy_img, e)
        if e.colliderect(ship_rect):
            if sounds.hit_snd: sounds.hit_snd.play()
            state = MENU
        for b in bullets[:]:
            if e.colliderect(b):
                if e in enemies: enemies.remove(e)
                bullets.remove(b)
        if e.top > HEIGHT: enemies.remove(e)


def run_snake():
    global snake_dir, apple_pos, state, last_snake_update
    screen.blit(snake_bg, (0, 0))

    now = pygame.time.get_ticks()
    # Двигаем змейку раз в 100мс, чтобы она не летала
    if now - last_snake_update > 100:
        last_snake_update = now
        head = list(snake_pos[0])
        if snake_dir == "UP": head[1] -= 20
        if snake_dir == "DOWN": head[1] += 20
        if snake_dir == "LEFT": head[0] -= 20
        if snake_dir == "RIGHT": head[0] += 20

        if head == apple_pos:
            apple_pos = [random.randrange(0, 39) * 20, random.randrange(0, 29) * 20]
        else:
            snake_pos.insert(0, head)
            snake_pos.pop()

        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in snake_pos[1:]:
            state = MENU

    # Отрисовка
    pygame.draw.rect(screen, RED, (apple_pos[0], apple_pos[1], 20, 20))
    for i, pos in enumerate(snake_pos):
        img = s_head_img if i == 0 else s_body_img
        screen.blit(img, (pos[0], pos[1]))


# --- ОСНОВНОЙ ЦИКЛ ---
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == MENU:
            if btn_snake.is_clicked(event): reset_all(); state = SNAKE; sounds.play_bg("normal")
            if btn_shooter.is_clicked(event): reset_all(); state = SHOOTER; sounds.play_bg("space")
            if btn_dino.is_clicked(event): reset_all(); state = DINO; sounds.play_bg("normal")

        elif state == SHOOTER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(ship_x + 22, 480, 15, 35))

        elif state == SNAKE and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != "DOWN": snake_dir = "UP"
            if event.key == pygame.K_DOWN and snake_dir != "UP": snake_dir = "DOWN"
            if event.key == pygame.K_LEFT and snake_dir != "RIGHT": snake_dir = "LEFT"
            if event.key == pygame.K_RIGHT and snake_dir != "LEFT": snake_dir = "RIGHT"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.music.stop()
            state = MENU

    if state == MENU:
        screen.fill(BLACK)
        btn_snake.draw(screen)
        btn_shooter.draw(screen)
        btn_dino.draw(screen)
    elif state == DINO:
        run_dino()
    elif state == SHOOTER:
        run_shooter()
    elif state == SNAKE:
        run_snake()

    pygame.display.flip()
    clock.tick(FPS)