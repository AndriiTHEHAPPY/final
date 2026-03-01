import pygame
from settings import WHITE, GRAY


class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", 30)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        # Если мышка на кнопке — подсвечиваем
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False