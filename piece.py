from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Union
from utilities import get_piece_path_from_character, draw_image_outline
import pygame

Position = Tuple[int, int]
Color = str

class Piece(ABC):
    def __init__(self, position: Position, color: Color) -> None:
        self.color : Color = color
        self.pos: Position = position
        self.has_moved = False
        self.can_be_captured = False
        self.sprite = None

    def reset_state(self):
        self.can_be_captured = False

    @abstractmethod
    def legal_moves(self, board, including_self=False) -> List[Position]:
        raise NotImplementedError()

    @abstractmethod
    def attack_squares(self, board) -> List[Position]:
        raise NotImplementedError()


    def move_to(self, board, target: Position) -> None:
        self.pos = target
        self.has_moved = True

    def draw(self, surface: pygame.Surface, square_size: int, origin: Tuple[int, int] = (0, 0), board=None) -> None:
        x0, y0 = origin
        row, col = board.screen_to_board(self.pos[0], self.pos[1])
        cx = x0 + col * square_size + square_size // 2
        cy = y0 + row * square_size + square_size // 2
        radius = square_size // 3
        if self.sprite:
            self.sprite = pygame.transform.smoothscale(self.sprite, (100, 100))
            if self.can_be_captured:
                self.draw_outline(surface, (cx - square_size // 2, cy - square_size // 2))
            rect = self.sprite.get_rect(center=(cx, cy))
            surface.blit(self.sprite, rect)
        else:
            rgb = (255, 255, 255) if self.color == "white" else (0, 0, 0)
            pygame.draw.circle(surface, rgb, (cx, cy), radius)

    def draw_outline(self, surface: pygame.Surface, pos) -> None:
        # TODO: Draw the outline once the piece is captured
        if not self.can_be_captured or not self.sprite:
            return
        draw_image_outline(surface, self.sprite, pos, (255, 0, 0), 5)




class Pawn(Piece):
    def __init__(self, position: Position, color: Color) -> None:
        super().__init__(position, color)
        self.sprite = pygame.image.load(get_piece_path_from_character('p', color))

    def legal_moves(self, board, including_self=False) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        dir = -1 if self.color == "white" else 1
        one_step = (r + dir, c)
        if board.in_bounds(one_step) and board.get_piece(one_step) is None:
            moves.append(one_step)
            start_row = 6 if self.color == "white" else 1
            two_step = (r + dir * 2, c)
            if r == start_row and board.in_bounds(two_step) and board.get_piece(two_step) is None:
                moves.append(two_step)
        # Diagonal captures
        for dc in (-1, 1):
            diag = (r + dir, c + dc)
            if board.in_bounds(diag):
                piece = board.get_piece(diag)
                if piece and piece.color != self.color:
                    moves.append(diag)
        # En passant
        if board.en_passant_target:
            en_passant_row, en_passant_column = board.en_passant_target
            if en_passant_row == r + dir and abs(c - en_passant_column) == 1:
                moves.append((en_passant_row, en_passant_column))
        return moves

    def attack_squares(self, board) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        dir = -1 if self.color == "white" else 1
        for dc in (-1, 1):
            diag = (r + dir, c + dc)
            if board.in_bounds(diag):
                piece = board.get_piece(diag)
                if piece is None or piece.color == self.color:
                    moves.append(diag)
        return moves



class Rook(Piece):
    def __init__(self, position: Position, color: Color) -> None:
        super().__init__(position, color)
        self.sprite = pygame.image.load(get_piece_path_from_character('r', color))

    def legal_moves(self, board, including_self=False) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        directions = [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1)
        ]
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while board.in_bounds((rr, cc)):
                piece = board.get_piece((rr, cc))

                if piece is None:
                    moves.append((rr, cc))
                else:
                    if piece.color != self.color:
                        if including_self:
                            if not isinstance(piece, King):
                                break
                            moves.append((rr, cc))
                        else:
                            moves.append((rr, cc))
                            break
                    if piece.color == self.color:
                        if including_self:
                            moves.append((rr, cc))
                        break
                rr += dr
                cc += dc
        return moves

    def attack_squares(self, board) -> List[Position]:
        return self.legal_moves(board, True)


class Bishop(Piece):
    def __init__(self, position: Position, color: Color) -> None:
        super().__init__(position, color)
        self.sprite = pygame.image.load(get_piece_path_from_character('b', color))
    def legal_moves(self, board, including_self=False) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        directions = [
            (-1, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
        ]
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while board.in_bounds((rr, cc)):
                piece = board.get_piece((rr, cc))
                if piece is None:
                    moves.append((rr, cc))
                else:
                    if piece.color != self.color:
                        if including_self:
                            if not isinstance(piece, King):
                                break
                            moves.append((rr, cc))
                        else:
                            moves.append((rr, cc))
                            break
                    if piece.color == self.color:
                        if including_self:
                            moves.append((rr, cc))
                        break
                rr += dr
                cc += dc
        return moves

    def attack_squares(self, board) -> List[Position]:
        return self.legal_moves(board, True)


class Queen(Piece):
    def __init__(self, position: Position, color: Color) -> None:
        super().__init__(position, color)
        self.sprite = pygame.image.load(get_piece_path_from_character('q', color))
    def legal_moves(self, board, including_self=False) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        directions = [
            (-1, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ]
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while board.in_bounds((rr, cc)):
                piece = board.get_piece((rr, cc))
                if piece is None:
                    moves.append((rr, cc))
                else:
                    if piece.color != self.color:
                        if including_self:
                            if not isinstance(piece, King):
                                break
                            moves.append((rr, cc))
                        else:
                            moves.append((rr, cc))
                            break
                    if piece.color == self.color:
                        if including_self:
                            moves.append((rr, cc))
                        break
                rr += dr
                cc += dc
        return moves

    def attack_squares(self, board) -> List[Position]:
        return self.legal_moves(board, True)


class Knight(Piece):
    def __init__(self, position: Position, color: Color) -> None:
        super().__init__(position, color)
        self.sprite = pygame.image.load(get_piece_path_from_character('n', color))

    def legal_moves(self, board, including_self=False) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        directions = [
            (-2, 1),
            (1, 2),
            (2, 1),
            (1, -2),
            (2, -1),
            (-2, -1),
            (-1, -2),
            (-1, 2)
        ]
        for direction in directions:
            rr, cc = r + direction[0], c + direction[1]
            if board.in_bounds((rr, cc)):
                piece = board.get_piece((rr, cc))
                if piece is None:
                    moves.append((rr, cc))
                else:
                    if piece.color != self.color:
                        moves.append((rr, cc))
                    if piece.color == self.color and including_self:
                        moves.append((rr, cc))
        return moves

    def attack_squares(self, board) -> List[Position]:
        return self.legal_moves(board, True)


class King(Piece):
    def __init__(self, position: Position, color: Color) -> None:
        super().__init__(position, color)
        self.sprite = pygame.image.load(get_piece_path_from_character('k', color))

    def legal_moves(self, board, including_self=False) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        enemy = "black" if self.color == "white" else "white"
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            target = (rr, cc)
            if not board.in_bounds(target):
                continue
            piece = board.get_piece(target)
            if piece and piece.color == self.color:
                continue
            if not board.is_square_attacked(target, attacker_color=enemy):
                # Castling
                if not self.has_moved:
                    dirs = (-1, 1)
                    for d in dirs:
                        if dr == 0 and dc == d:
                            new_target = (r, c + 2 * d)
                            # King side
                            rook = board.get_piece((r, 7 if d == 1 else 0))
                            if isinstance(rook, Rook) and not rook.has_moved:
                                if not board.is_square_attacked(new_target, enemy) and board.get_piece(
                                        new_target) is None:
                                    moves.append(new_target)

                moves.append(target)

        return moves

    def attack_squares(self, board) -> List[Position]:
        moves: List[Position] = []
        r, c = self.pos
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            target = (rr, cc)
            if not board.in_bounds(target):
                continue
            moves.append(target)
        return moves



