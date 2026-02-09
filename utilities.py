import pygame
import pygame.gfxdraw
from typing import Tuple
import os

def draw_rounded_rect(surface, rect, radius, color, scale=10):
    x, y, w, h = rect
    sw, sh = w * scale, h * scale
    r = radius * scale

    temp = pygame.Surface((sw, sh), pygame.SRCALPHA)

    # center rectangles
    pygame.draw.rect(temp, color, (r, 0, sw - 2 * r, sh))
    pygame.draw.rect(temp, color, (0, r, sw, sh - 2 * r))

    # filled circles ONLY (no aacircle)
    for cx, cy in [
        (r, r),
        (sw - r - 1, r),
        (r, sh - r - 1),
        (sw - r - 1, sh - r - 1)
    ]:
        pygame.gfxdraw.filled_circle(temp, cx, cy, r, color)

    # downscale
    smooth = pygame.transform.smoothscale(temp, (w, h))
    surface.blit(smooth, (x, y))

def get_mouse_pos(surface: pygame.Surface, internal_surface: pygame.Surface):
    real_mouse_pos = pygame.mouse.get_pos()
    width_ratio = internal_surface.get_width() / surface.get_width()
    height_ratio = internal_surface.get_height() / surface.get_height()
    return (
        real_mouse_pos[0] * width_ratio,
        real_mouse_pos[1] * height_ratio
    )

def update_mouse_pos(pos, surface: pygame.Surface,
                     internal_surface: pygame.Surface):
    width_ratio = internal_surface.get_width() / surface.get_width()
    height_ratio = internal_surface.get_height() / surface.get_height()
    return (
        int(pos[0] * width_ratio),
        int(pos[1] * height_ratio)
    )

def draw_image_outline(surface: pygame.Surface, image: pygame.Surface, pos, color = "black", thickness = 1) -> None:
    mask = pygame.mask.from_surface(image)
    points = mask.outline()
    offset_points = [(p[0] + pos[0], p[1] + pos[1]) for p in points]
    if len(offset_points) > 1:
        pygame.draw.lines(surface, color, True, offset_points, thickness)

def get_piece_path_from_character(c, color) -> str:
    if color != "white":
        color = "black"
    path = ""
    match c.lower():
        case 'r':
            path = f"assets/{color}-rook.png"
        case 'n':
            path = f"assets/{color}-knight.png"
        case 'b':
            path = f"assets/{color}-bishop.png"
        case 'q':
            path = f"assets/{color}-queen.png"
        case 'k':
            path = f"assets/{color}-king.png"
        case 'p':
            path = f"assets/{color}-pawn.png"
        case _:
            path = ""
    return path

def draw_image(screen: pygame.Surface, path: str, position: Tuple[float, float], size: Tuple[float, float]):
    if not os.path.exists(path):
        print(f"File {path} not found")
        return
    image = pygame.image.load(os.path.abspath(path)).convert_alpha()
    image = pygame.transform.scale(image, size)
    image_rect = image.get_rect()
    image_rect.center = position
    image_rect.size = size
    screen.blit(image, image_rect)

def smoothstep(t):
    return t * t * (3 - 2 * t)

def lerp(t, a, b):
    return a + (b - a) * t

def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < 8 and 0 <= col < 8

def is_white(piece: str):
    return piece.isupper()

def is_black(piece: str):
    return piece


def clamp(t, minimum, maximum):
    return max(minimum, min(t, maximum))
