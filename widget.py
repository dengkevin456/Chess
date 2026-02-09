import pygame
from abc import ABC, abstractmethod
from utilities import clamp, draw_rounded_rect


class Widget(ABC):
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.enabled = True
        self.visible = True
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.font = pygame.font.SysFont("Arial", 20)

    def render_text(self, surface: pygame.Surface, position: tuple, label: str, color: tuple=(255, 255, 255),
                    custom_font: pygame.Font=None):
        text_surf = self.font.render(label, False, color) if not custom_font else custom_font.render(label, False, color)
        text_rect = text_surf.get_rect(center=position)
        surface.blit(text_surf, text_rect)

    def render_text_top(self, surface: pygame.Surface, position: tuple, label: str, color: tuple=(255, 255, 255),
                        custom_font: pygame.Font=None):
        text_surf = self.font.render(label, False, color) if not custom_font else custom_font.render(label, False, color)
        text_rect = text_surf.get_rect(center=(position[0] + text_surf.get_width() / 2, position[1] + text_surf.get_height() / 2))
        surface.blit(text_surf, text_rect)

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    def handle_event(self, event):
        pass



class CheckBox(Widget):
    def __init__(self, x, y, w, h, checked=False, on_toggle=None, label=None):
        super().__init__(x, y, w, h)
        self.checked = checked
        self.on_toggle = on_toggle
        self.label = label
        self.hovered = False
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.knob_radius = 10

    def handle_event(self, event):
        if not self.enabled:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        color = (0, 255, 0) if self.checked else (100, 100, 100)
        if self.hovered:
            color = (160, 160, 160)
        draw_rounded_rect(surface, self.rect, self.knob_radius, color, 10)
        knob_x = self.rect.right - self.knob_radius if self.checked else self.rect.left + self.knob_radius
        pygame.draw.circle(surface, (130, 130, 130), (knob_x, self.rect.centery), self.knob_radius)
        if self.label:
            self.render_text_top(surface, (self.x + self.w + 10, self.y), self.label)


class Slider(Widget):
    def __init__(self, x: int, y: int, w: int, h: int, label: str,
                 min_value: int, max_value: int, value: int, on_change=None):
        super().__init__(x, y, w, h)
        self.label = label
        self.min = min_value
        self.max = max_value
        self.value = value
        self.checked = False
        self.on_change = on_change
        self.dragging = False
        self.stepping = True
        self.step = 1


    def value_to_x(self):
        t = (self.value - self.min) / (self.max - self.min)
        return self.x + int(t * self.w)

    def x_to_value(self, x):
        t = (x - self.x) / self.w
        t = clamp(t, 0, 1)
        raw_value = self.min + t * (self.max - self.min)
        snapped_value = round((raw_value - self.min) / self.step) * self.step + self.min
        return snapped_value if self.stepping else raw_value

    def handle_event(self, event):
        if not self.enabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_value = self.x_to_value(event.pos[0])
            if new_value != self.value:
                self.value = new_value
                if self.on_change:
                    self.on_change(new_value)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        pygame.draw.rect(surface, (150, 150, 150), self.rect)
        fill_width = self.value_to_x() - self.x
        pygame.draw.rect(surface, (0, 50, 255), (self.x, self.y, fill_width, self.h))

        knob_x = self.value_to_x()
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, self.y + self.h / 2), 10)
        self.render_text(surface, (self.x + self.w / 2, self.y - self.h), self.label,
                         (255, 255, 255), pygame.font.SysFont("Arial", 30))
        self.render_text(surface, (self.x + self.w / 2, self.y + self.h * 2), str(self.value))


