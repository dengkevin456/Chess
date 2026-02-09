import pygame

class Move:
    def __init__(self, piece, src, dst, captured):
        self.piece = piece
        self.src = src
        self.dst = dst
        self.captured = captured

        # special move data
        self.castling = False
        self.rook = None
        self.rook_src = None
        self.rook_dst = None

        self.is_en_passant = False
        self.ep_captured_pos = None

        self.is_promotion = False
        self.promoted_piece = None

    def log(self):
        print("-----------")
        print(f"{type(self.piece)} {self.src} -> {self.dst}")
        print("-----------")