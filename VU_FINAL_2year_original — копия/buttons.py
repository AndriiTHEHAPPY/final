import pygame
from settings import WHITE


class Button:
    def __init__(self, x, y, w, h, text, image_path):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

        # Пытаемся загрузить картинку
        try:
            img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(img, (w, h))
        except Exception as e:
            print(f"Ошибка загрузки картинки {image_path}: {e}")
            self.image = pygame.Surface((w, h))
            self.image.fill((200, 0, 200))  # Розовый, если картинки нет

        self.font = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        # Рисуем саму картинку кнопки
        screen.blit(self.image, self.rect)

        # Если мышка на кнопке — добавляем эффект "подсветки" (полупрозрачный слой)
        if self.rect.collidepoint(mouse_pos):
            highlight = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            highlight.fill((255, 255, 255, 40))  # Белый с прозрачностью 40
            screen.blit(highlight, self.rect)

        # Рисуем текст (если он нужен поверх картинки)
        if self.text:
            text_surf = self.font.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False