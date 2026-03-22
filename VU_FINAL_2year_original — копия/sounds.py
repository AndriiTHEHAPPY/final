import pygame
import os

pygame.mixer.init()

def load_snd(name):
    # Путь к папке sounds
    path = os.path.join("sounds", name)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Ошибка при чтении файла {name}: {e}")
            return None
    else:
        print(f"ФАЙЛ НЕ НАЙДЕН: {path}")
        return None

# Загружаем эффекты (ПРОВЕРЬ ЭТИ НАЗВАНИЯ В ПАПКЕ)
jump_snd = load_snd("jump.wav")
meow_snd = load_snd("kitten_mew-1.ogg")   # Для смерти кота
hit_snd = load_snd("attack_hit.mp3")     # Для взрыва в космосе
repair_snd = load_snd("repair.wav")
virus_snd = load_snd("virus.mp3")
mouse_eat_snd = load_snd("mouse.ogg") # Звук писка мыши

def play_bg(mode):
    pygame.mixer.music.stop()
    try:
        if mode == "space":
            pygame.mixer.music.load("sounds/spacebackground.wav")
        else:
            pygame.mixer.music.load("sounds/backgroundmusic.ogg")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Ошибка фоновой музыки: {e}")