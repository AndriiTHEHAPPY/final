import pygame

pygame.mixer.init()

# Загрузка звуковых эффектов (WAV)
jump_snd = pygame.mixer.Sound("sounds/Jump.wav")
hit_snd = pygame.mixer.Sound("sounds/attack_hit.mp3")
meow_snd = pygame.mixer.Sound("sounds/kitten_mew-1.ogg")

# Функция для музыки (OGG)
def play_bg(game_type):
    pygame.mixer.music.stop()
    if game_type == "space":
        pygame.mixer.music.load("sounds/spacebackground.wav")
    else:
        pygame.mixer.music.load("sounds/backgroundmusic.ogg")
    pygame.mixer.music.play(-1) # Бесконечный повтор