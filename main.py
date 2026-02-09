import pygame

from board import Board
from piece import *
from utilities import *
from settings import settings
from button import Button
from widget import Slider, CheckBox


class Game:
    WINDOW_SIZE = 800
    def __init__(self):
        pygame.init()
        self.screen = settings.screen
        pygame.display.set_caption("Chess")
        self.clock = settings.clock
        self.running = True
        self.board = Board()

        self.widgets = {
            "main_menu": [
                Button(settings.get_window_width() // 3, 400, 300, 100, (70, 130, 180),
                       (100, 149, 237), (30, 60, 100), "Play",
                       lambda a="configuration": settings.switch_scene(a))
            ],
            "configuration": [
                Button(50, settings.WINDOW_SIZE - 100, 150, 50, (70, 130, 180), (100, 149, 237), (30, 60, 100),
                       "Back", lambda a="main_menu": settings.switch_scene(a)),
                Slider(settings.get_window_width() // 3, 600, 300, 20, "AI strength", 0, 10, 1,
                       None),
                Button(settings.get_window_width() // 2 - 75, settings.WINDOW_SIZE - 100, 150, 50, (70, 130, 180),
                       (100, 149, 237), (30, 60, 100),
                       "Next", lambda a="main": settings.switch_scene(a)),
                CheckBox(settings.get_window_width() // 2 - 75, settings.WINDOW_SIZE / 8, 50, 25, False, None,
                         "Play against Computer")
            ],
            "main": [
                Button(900, 500, 150, 50, (70, 130, 180), (100, 149, 237),
                       (30, 60, 100), "Rotate board", self.board.toggle_rotation),
                Button(900, 650, 150, 50, (70, 130, 180), (100, 149, 237), (30, 60, 100),
                       "Undo Move", self.board.undo_move),
                Button(900, 580, 150, 50, (70, 130, 180), (100, 149, 237), (30, 60, 100),
                       "Get move logs", self.get_move_log),
            ]
        }

        self.promotion_buttons = [
            Button(100, 100, settings.WINDOW_SIZE // 9, settings.WINDOW_SIZE // 9,
                   (70, 130, 180), (100, 149, 237),(30, 60, 100), "Q", None) for _ in range(4)
        ]
        self.dt = self.clock.tick(settings.fps)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        if settings.animating:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            settings.clicked = True
            square = self.WINDOW_SIZE // 8
            if settings.scene == "main":
                for p in self.board.all_pieces(None):
                    p.reset_state()
                mx, my = event.pos
                row, col = my // square, mx // square
                row, col = self.board.board_to_screen(row, col)
                clicked = (row, col)
                piece = self.board.get_piece(clicked)
                if piece and piece.color == self.board.to_move:
                    self.selected = clicked
                    for p in self.board.all_pieces(None):
                        p.reset_state()
                    self.valid_moves = self.board.legal_moves_for_piece(clicked)
                else:
                    if hasattr(self, "selected") and clicked in getattr(self, "valid_moves",
                                                                        []) and not settings.is_promoting():
                        # self.board.move_piece(self.selected, clicked)
                        settings.start_move_animation(self.board, self.selected, clicked, True)

                    self.selected = None
                    self.valid_moves = []
                    for p in self.board.all_pieces(None):
                        p.reset_state()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.board.is_checkmate()

        # All widget events reference
        if self.widgets.get(settings.scene):
            for widget in self.widgets[settings.scene]:
                widget.handle_event(event)

    # Moving logs
    def get_move_log(self):
        for move in self.board.move_log:
            print(move.log())

    # Promotion stuff
    def update_promotion_buttons(self):
        square = settings.WINDOW_SIZE // 9
        x = settings.WINDOW_SIZE // 3
        y = settings.WINDOW_SIZE // 2 - square // 2
        for i, label in enumerate(settings.pieces):
            self.promotion_buttons[i].set_position((x + i * square, y))
            self.promotion_buttons[i].label = label
            # Prevent late-binding closure problem
            self.promotion_buttons[i].event = lambda a=i: self.promote_pawn(a)

    def draw_promotion_menu(self):
        for i, label in enumerate(settings.pieces):
            self.promotion_buttons[i].draw(self.screen)

    def promote_pawn(self, index):
        if not settings.is_promoting():
            return
        r, c = settings.promoting_pawn_pos
        color = settings.promotion_color
        new_piece = None
        match index:
            case 0:
                new_piece = Queen((r, c), color)
            case 1:
                new_piece = Rook((r, c), color)
            case 2:
                new_piece = Knight((r, c), color)
            case _:
                new_piece = Bishop((r, c), color)
        if not new_piece:
            return
        self.board.grid[r][c] = new_piece
        settings.reset_promotion_state()
        self.board.update_attack_maps()

    # Draw widget helper
    def draw_widget(self, scene: str):
        if not self.widgets.get(scene):
            return
        for widget in self.widgets[scene]:
            widget.draw(self.screen)
    """
    Scene methods
    """

    def main_menu(self) -> None:
        self.screen.fill((0, 150, 225))
        settings.draw_center_text("CHESS", (255, 255, 255), (settings.get_window_width() // 2,
                                                             settings.get_window_height() // 6), 140)
        self.draw_widget("main_menu")

    def configuration_menu(self):
        self.screen.fill((150, 150, 150))
        settings.draw_center_text("CONFIGURATION", (255, 255, 255), (settings.get_window_width() // 2,
                                                                     80), 80)
        self.draw_widget("configuration")


    def draw_board(self) -> None:
        square = self.WINDOW_SIZE // 8
        for r in range(8):
            for c in range(8):
                color = (240, 217, 181) if (r + c) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(self.screen, color, (c * square, r * square, square, square))
        if hasattr(self, "valid_moves") and not settings.is_promoting():
            square = self.WINDOW_SIZE // 8
            for r, c in self.valid_moves:
                r, c = self.board.screen_to_board(r, c)
                cx = c * square + square // 2
                cy = r * square + square // 2
                p = self.board.get_piece(self.board.board_to_screen(r, c))
                if not p:
                    pygame.draw.circle(self.screen, (0, 255, 0), (cx, cy), square // 6)
                else:
                    p.can_be_captured = True
        # Animation
        if settings.animating:
            settings.anim_progress += (self.dt / 1000.0) / settings.anim_duration
            if settings.anim_progress >= 1.0:
                settings.animating = False
                settings.anim_progress = 1.0
                self.board.move_piece(settings.anim_start, settings.anim_end, undo=settings.undo_append)

                # Handle promotion
                clicked = settings.anim_end
                if self.board.is_pawn_promotion(clicked):
                    settings.promoting_pawn_pos = clicked
                    settings.promotion_color = self.board.get_piece(clicked).color
                    self.update_promotion_buttons()
        # draw pieces
        for piece in self.board.all_pieces(None):
            if settings.animating and piece == settings.anim_piece:
                continue
            piece.draw(self.screen, square, (0, 0), self.board)
        # Animate the piece
        if settings.animating:
            sr, sc = self.board.board_to_screen(*settings.anim_start)
            tr, tc = self.board.board_to_screen(*settings.anim_end)
            t = smoothstep(settings.anim_progress)
            r = lerp(t, sr, tr)
            c = lerp(t, sc, tc)
            x = c * square + square // 2
            y = r * square + square // 2

            if settings.anim_piece.sprite:
                rect = settings.anim_piece.sprite.get_rect(center=(x, y))
                self.screen.blit(settings.anim_piece.sprite, rect)
            else:
                color = (255, 255, 255) if settings.anim_piece.color == "white" else (0, 0, 0)
                pygame.draw.circle(self.screen, color, (x, y), square // 3)

        for widget in self.widgets["main"]:
            if isinstance(widget, Button):
                widget.enabled = not settings.is_promoting()
            widget.draw(self.screen)

        # draw checkmate outcome
        if self.board.is_checkmate():
            settings.draw_center_text(f"{"White" if self.board.to_move == "black" else "Black"} wins!",
                                      (255, 255, 255), (950, 100))
        if self.board.is_stalemate():
            settings.draw_center_text("Draw!", (255, 255, 255), (950, 100))

    def run(self):
        while self.running:
            self.dt = self.clock.tick(settings.fps)
            self.screen.fill((0, 0, 0))
            settings.clicked = False
            pygame.mouse.set_cursor(settings.current_cursor)
            match settings.scene:
                case "main_menu":
                    self.main_menu()
                case "main":
                    self.draw_board()
                    if settings.is_promoting():
                        self.draw_promotion_menu()
                case "configuration":
                    self.configuration_menu()

            for event in pygame.event.get():
                self.handle_event(event)
            pygame.display.update()


main = Game()
main.run()
print("Success!")
pygame.quit()