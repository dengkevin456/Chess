from typing import Tuple

import pygame
import pygame.gfxdraw
from utilities import draw_rounded_rect
from settings import settings
from widget import Widget


class Button(Widget):
    def __init__(self, x, y, w, h, color, hover_color, click_color, label, event=None):
        super().__init__(x, y, w, h)
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color
        self.click_color = click_color
        self.current_color = color
        self.label = label
        self.event = event
        self.pressed = False
        self.font = pygame.font.SysFont("Arial", 20)
        self.clicked = -1
        self.SCALE = 2

    def set_position(self, pos: Tuple[int, int]):
        self.x = pos[0]
        self.y = pos[1]

    def set_size(self, size: Tuple[int, int]):
        self.w = size[0]
        self.h = size[1]


    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        mouse_pos = pygame.mouse.get_pos()
        self.current_color = self.color
        if self.rect.collidepoint(mouse_pos):
            if self.enabled:
                self.current_color = self.hover_color
                if pygame.mouse.get_pressed()[0]:
                    self.current_color = self.click_color
                    self.pressed = True
                    if self.clicked == -1:
                        self.clicked = 1
                else:
                    if self.pressed and self.clicked == 1:
                        if self.event is not None:
                            self.event()
                        self.pressed = False
                        self.clicked = -1
        if pygame.mouse.get_pressed()[0]:
            if not self.rect.collidepoint(mouse_pos) and not self.pressed:
                self.clicked = 0
        else:
            self.clicked = -1
            self.pressed = False
        shadow_rect = self.rect.copy()
        shadow_rect.move_ip(3, 3)
        draw_rounded_rect(surface, shadow_rect, 8, (50, 50, 50))
        draw_rounded_rect(surface, self.rect, 8, self.current_color)

        text_surf = self.font.render(self.label, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
