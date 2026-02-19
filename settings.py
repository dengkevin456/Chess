from typing import Tuple

import pygame
import pygame.gfxdraw



class Settings:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.WINDOW_SIZE = 800
        self.actual_window_size = 800 # Change this for actual size
        self.font = pygame.font.SysFont("Arial", 20)
        self.clicked = False
        self.scene = "main_menu"
        self.internal_window = pygame.Surface((self.WINDOW_SIZE * 1.5,
                                               self.WINDOW_SIZE))
        self.screen = pygame.display.set_mode((self.actual_window_size * 1.5, self.actual_window_size),
                                              pygame.RESIZABLE)


        self.current_cursor = pygame.SYSTEM_CURSOR_ARROW
        self.clock = pygame.time.Clock()
        self.fps = 60
        # Configurations
        self.ai_playing = False
        self.ai_difficulty = 0
        # Pawn promotion stuff
        self.promoting_pawn_pos = None
        self.promotion_color = None
        self.pieces = ["Q", "R", "N", "B"]

        # Animation
        self.animating = False
        self.anim_piece = None
        self.anim_start = None
        self.anim_end = None
        self.anim_progress = 0.0
        self.anim_duration = 0.15
        self.undo_append = True

        # Add more stuff later
    def get_window_width(self):
        return self.internal_window.get_width()

    def get_window_height(self):
        return self.internal_window.get_height()

    def start_move_animation(self, board, src: Tuple[int, int], target: Tuple[int, int], undo_append=True):
        self.animating = True
        self.undo_append = undo_append
        self.anim_piece = board.get_piece(src)
        self.anim_start = src
        self.anim_end = target
        self.anim_progress = 0.0

    def is_default_cursor(self):
        return self.current_cursor == pygame.SYSTEM_CURSOR_ARROW

    def set_cursor(self, cursor):
        self.current_cursor = cursor

    def is_promoting(self):
        return self.promotion_color is not None and self.promoting_pawn_pos is not None

    def reset_promotion_state(self):
        self.promotion_color = None
        self.promoting_pawn_pos = None

    def draw_center_text(self, text, color, center_point, size=20):
        self.font = pygame.font.SysFont("Arial", size)
        text_surf = self.font.render(text, True, color)
        if isinstance(center_point, pygame.Rect):
            target_center = center_point.center
        else:
            target_center = center_point
        text_rect = text_surf.get_rect(center=target_center)
        self.internal_window.blit(text_surf, text_rect)

    def switch_scene(self, scene: str=None):
        if not scene:
            return
        self.scene = scene
settings = Settings()
