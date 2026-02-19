from __future__ import annotations
import random
from typing import Tuple, Optional, List

import pygame
from settings import settings
from move import Move
from piece import *

Position = Tuple[int, int]
Color = str

class Board:
    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = [[None] * 8 for _ in range(8)]
        self.to_move: Color = "white"
        self.starting_position = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        """
       ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
            
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', 'K', ' '],
            [' ', 'P', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', 'k', ' '],

        """
        self.attacked_by_white = [[False] * 8 for _ in range(8)]
        self.attacked_by_black = [[False] * 8 for _ in range(8)]
        self.flipped = False
        self.en_passant_target = None
        self.last_move = None
        self.setup()

        # Random AI timer
        self.initial_time = random.randint(100, 200)
        self.timer = self.initial_time
        # Move log
        self.move_log = []

    def board_to_screen(self, r, c):
        if self.flipped:
            return 7 - r, 7 - c
        return r, c

    def toggle_rotation(self):
        if self.flipped:
            self.flipped = False
        elif not self.flipped:
            self.flipped = True

    def screen_to_board(self, r, c):
        if self.flipped:
            return 7 - r, 7 - c
        return r, c

    def setup(self):
        for i in range(8):
            for j in range(8):
                c = self.starting_position[i][j]
                color = "white" if c.isupper() else "black"
                match c.lower():
                    case "r":
                        self.grid[i][j] = Rook((i, j), color)
                    case "b":
                        self.grid[i][j] = Bishop((i, j), color)
                    case "q":
                        self.grid[i][j] = Queen((i, j), color)
                    case "p":
                        self.grid[i][j] = Pawn((i, j), color)
                    case "n":
                        self.grid[i][j] = Knight((i, j), color)
                    case 'k':
                        self.grid[i][j] = King((i, j), color)

    @staticmethod
    def in_bounds(pos: Position) -> bool:
        r, c = pos
        return 0 <= r < 8 and 0 <= c < 8

    def update_attack_maps(self):
        self.attacked_by_white = [[False] * 8 for _ in range(8)]
        self.attacked_by_black = [[False] * 8 for _ in range(8)]

        for piece in self.all_pieces():
            attacks = piece.attack_squares(self)
            target_map = (
                self.attacked_by_white
                if piece.color == "white" else self.attacked_by_black
            )
            for (r, c) in attacks:
                target_map[r][c] = True

    def switch_color(self):
        self.to_move = "white" if self.to_move == "black" else "black"

    def get_piece(self, pos: Position) -> Optional[Piece]:
        r, c = pos
        if not self.in_bounds(pos):
            return None
        return self.grid[r][c]

    def is_square_attacked(self, pos: Position, attacker_color: Color) -> bool:
        r, c = pos
        if attacker_color == "white":
            return self.attacked_by_white[r][c]
        else:
            return self.attacked_by_black[r][c]

    def handle_en_passant(self, piece, source: Position, dest: Position) -> None:
        if isinstance(piece, Pawn) and abs(dest[0] - source[0]) == 2:
            middle_row = (source[0] + dest[0]) // 2
            if settings.undo_append:
                self.en_passant_target = (middle_row, source[1])
            else:
                self.en_passant_target = None
        # En passant capture
        elif isinstance(piece, Pawn) and dest == self.en_passant_target:
            captured_row = source[0]
            captured_col = dest[1]
            self.grid[captured_row][captured_col] = None
        else:
            self.en_passant_target = None

    def make_random_ai_move(self, color):
        if settings.is_promoting():
            return
        moves = self.all_legal_moves(color)
        if len(moves) == 0:
            return
        try:
            if self.timer < 0:
                src, target = random.choice(moves)
                self.move_piece(src, target)
                self.timer = random.randint(100, 200)
            else:
                self.timer -= 3
        except ValueError as e:
            self.timer = self.initial_time
            print(f"Value error: {e}")

    def move_piece(self, source: Position, dest: Position, undo=True) -> None:
        # Move piece from source to target
        piece = self.get_piece(source)
        captured = self.get_piece(dest)
        if piece is None:
            raise ValueError("No piece at source")
        move = Move(piece, source, dest, captured)
        # Special case : castling
        if isinstance(piece, King) and abs(dest[1] - source[1]) == 2:
            row = source[0]
            if dest[1] == 6: # King side
                rook_src = (row, 7)
                rook_dst = (row, 5)
            else: # Queen side
                rook_src = (row, 0)
                rook_dst = (row, 3)
            rook = self.get_piece(rook_src)
            move.rook = rook
            move.rook_src = rook_src
            move.rook_dst = rook_dst
            if rook is not None and isinstance(rook, Rook):
                self.grid[rook_dst[0]][rook_dst[1]] = rook
                self.grid[rook_src[0]][rook_src[1]] = None
                rook.move_to(self.grid, rook_dst)

        if undo:
            self.move_log.append(move)
        self.handle_en_passant(piece, source, dest)
        self.grid[dest[0]][dest[1]] = piece
        if undo:
            self.grid[source[0]][source[1]] = None
        else:
            self.grid[source[0]][source[1]] = self.last_move.captured if self.last_move else None
        piece.move_to(self.grid, target=dest)
        self.switch_color()
        self.update_attack_maps()


    def is_pawn_promotion(self, pos: Position):
        piece = self.get_piece(pos)
        if not isinstance(piece, Pawn):
            return False
        return True if (piece.color == "white" and pos[0] == 0) or (piece.color == "black" and pos[0] == 7) else False

    def all_pieces(self, color: Optional[Color] = None) -> List[Piece]:
        pieces: List[Piece] = []
        for row in self.grid:
            for p in row:
                if p is None:
                    continue
                if color is None or p.color == color:
                    pieces.append(p)
        return pieces

    def is_in_check(self, color: Optional[Color] = None) -> bool:
        king_pos = None
        for piece in self.all_pieces(color):
            if isinstance(piece, King):
                king_pos = piece.pos
                break
        if king_pos is None:
            return False
        opponent = "black" if color == "white" else "white"
        return self.is_square_attacked(king_pos, opponent)

    def get_all_legal_moves(self) -> List[Position]:
        legal_moves = []
        for piece in self.all_pieces(self.to_move):
            legal_moves_for_piece = self.legal_moves_for_piece(piece.pos)
            if legal_moves_for_piece is None or len(legal_moves_for_piece) == 0:
                continue
            legal_moves.append(self.legal_moves_for_piece(piece.pos))
        return legal_moves

    def all_legal_moves(self, color):
        # Returns a list in terms of (src, target) for given color (white/black)
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    src = (r, c)
                    for target in self.legal_moves_for_piece(src):
                        moves.append((src, target))
        return moves

    def legal_moves_for_piece(self, pos: Position) -> List[Position]:
        piece = self.get_piece(pos)
        if piece is None:
            return []
        legal: List[Position] = []
        candidate_moves = piece.legal_moves(self)
        color = piece.color
        for target in candidate_moves:
            src = pos
            captured = self.grid[target[0]][target[1]]
            self.grid[target[0]][target[1]] = piece
            self.grid[src[0]][src[1]] = None
            legal.append(target)
            self.update_attack_maps()

            if isinstance(piece, King):
                pass
            elif self.is_in_check(color) and target in legal:
                legal.remove(target)

            self.grid[src[0]][src[1]] = piece
            self.grid[target[0]][target[1]] = captured
            self.update_attack_maps()
        return legal

    def evaluate_material(self) -> int:
        values = {
            Pawn: 1,
            Knight: 3,
            Bishop: 3,
            Rook: 5,
            Queen: 9,
            King: 0
        }
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if not piece:
                    continue
                sign = 1 if piece.color == "white" else -1
                value = sign * values[type(piece)]
                if piece.color == "white":
                    score += value
                else:
                    score -= value
        return score

    def is_checkmate(self):
        return self.is_in_check(self.to_move) and len(self.get_all_legal_moves()) == 0

    def is_stalemate(self):
        return not self.is_in_check(self.to_move) and len(self.get_all_legal_moves()) == 0

    # Undo move
    def undo_move(self):
        if settings.animating:
            return
        if len(self.move_log) == 0:
            self.last_move = None
            return
        self.last_move = self.move_log.pop()
        self.en_passant_target = None
        # self.move_piece(move.piece.pos, (move.src[0], move.src[1]), False)

        settings.start_move_animation(self, self.last_move.dst, (self.last_move.src[0], self.last_move.src[1]), False)

        if self.last_move.castling:
            # TODO: implement castling undo
            pass





