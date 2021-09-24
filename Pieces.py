import Board

from Color import Color


class Piece:
    def __init__(self, color: Color or None, position: (int, int), board: Board):
        self.color = color
        self.position = position
        self.board = board

    def get_char(self) -> str:
        pass

    def threatens(self, field: (int, int)) -> bool:
        return False

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if to_pos[0] < 0 or to_pos[0] > 7 or to_pos[1] < 0 or to_pos[1] > 7 \
                or self.board.piece_at(to_pos).color == self.color or player != self.color \
                or (self.board.check[player.value] and not self.board.will_move_end_check(self.position, to_pos, player)):
            return False
        return True

    def move_to(self, new_pos: (int, int)):
        self.board.grant_points(self.color, self.board.piece_at(new_pos).value)
        self.board.set_piece_at(self.position, NoPiece(self.position))
        self.position = new_pos
        self.board.set_piece_at(new_pos, self)

    def __str__(self):
        return self.color.name + " " + type(self).__name__ + " @ " + str(self.position)


class Pawn(Piece):  # Bauer
    def __init__(self, color, position: (int, int), board: Board):
        super().__init__(color, position, board)
        self.direction = +1
        self.value = 1
        self.en_passant_victim = None
        self.last_was_double_move = None  # none means no moves were done yet

        if self.color == Color.WHITE:
            self.direction = -1

    def move_to(self, new_pos: (int, int)):
        if (self.position[1] == 1 or self.position[1] == 6) and (new_pos[1] == 3 or new_pos[1] == 4):
            self.last_was_double_move = True
        else:
            self.last_was_double_move = False
        super().move_to(new_pos)
        if new_pos[1] == 0 or new_pos[1] == 7:
            self.board.set_piece_at(new_pos, Queen(self.color, new_pos, self.board))
            self.board.grant_points(self.color, 5)

    def get_char(self) -> str:
        if self.color == Color.WHITE:
            return "♙"
        else:
            return "♟"

    def threatens(self, field: (int, int)) -> bool:
        return (abs(self.position[0] - field[0]) == 1 and field[1] == self.position[1] + self.direction) \
               or (self.last_was_double_move and self.position[1] == field[1] and abs(self.position[0] - field[0]) == 1)

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if not super().is_move_valid(player, to_pos):
            return False

        # moving to empty square, either move, double move, en passant or illegal
        if type(self.board.piece_at(to_pos)) is NoPiece:
            move_or_double_move = \
                to_pos == (self.position[0], self.position[1] + self.direction) \
                or (self.last_was_double_move is None
                    and to_pos == (self.position[0], self.position[1] + 2 * self.direction)
                    and type(self.board.piece_at((self.position[0], self.position[1] + self.direction))) is NoPiece)
            if move_or_double_move:
                return True
            en_passant = self.last_was_double_move \
                         and abs(to_pos[0] - self.position[0]) == 1 \
                         and to_pos[1] == self.position[1] + self.direction \
                         and self.board.piece_at((to_pos[0], self.position[1])).color != self.color
            if en_passant:
                self.en_passant_victim = (to_pos[0], self.position[1])
            return en_passant
        else:
            return (to_pos == (self.position[0] - 1, self.position[1] + self.direction)
                    or to_pos == (self.position[0] + 1, self.position[1] + self.direction))


class Knight(Piece):  # Springer
    def __init__(self, color, position: (int, int), board: Board):
        super().__init__(color, position, board)
        self.value = 3

    def threatens(self, field: (int, int)) -> bool:
        return (abs(self.position[0] - field[0]) == 2 and abs(self.position[1] - field[1]) == 1) \
               or (abs(self.position[0] - field[0]) == 1 and abs(self.position[1] - field[1]) == 2)

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if not super().is_move_valid(player, to_pos):
            return False

        return self.threatens(to_pos)

    def get_char(self):
        if self.color == Color.WHITE:
            return "♘"
        else:
            return "♞"


class Bishop(Piece):  # Läufer
    def __init__(self, color, position: (int, int), board: Board):
        super().__init__(color, position, board)
        self.value = 3

    def threatens(self, field: (int, int)) -> bool:
        return _valid_bishop_move(self.position, field, self.board)

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if not super().is_move_valid(player, to_pos):
            return False

        return _valid_bishop_move(self.position, to_pos, self.board)

    def get_char(self):
        if self.color == Color.WHITE:
            return "♗"
        else:
            return "♝"


class Rook(Piece):  # Turm
    def __init__(self, color, position: (int, int), board: Board):
        super().__init__(color, position, board)
        self.has_moved = False
        self.value = 5

    def threatens(self, field: (int, int)) -> bool:
        return _valid_rook_move(self.position, field, self.board)

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if not super().is_move_valid(player, to_pos):
            return False

        return _valid_rook_move(self.position, to_pos, self.board)

    def move_to(self, new_pos: (int, int)):
        super(Rook, self).move_to(new_pos)
        self.has_moved = True

    def get_char(self):
        if self.color == Color.WHITE:
            return "♖"
        else:
            return "♜"


class Queen(Piece):  # Dame
    def __init__(self, color, position: (int, int), board: Board):
        super().__init__(color, position, board)
        self.value = 9

    def threatens(self, field: (int, int)) -> bool:
        return _valid_rook_move(self.position, field, self.board) \
               or _valid_bishop_move(self.position, field, self.board)

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if not super().is_move_valid(player, to_pos):
            return False

        return self.threatens(to_pos)

    def get_char(self):
        if self.color == Color.WHITE:
            return "♕"
        else:
            return "♛"


class King(Piece):  # König
    def __init__(self, color, position: (int, int), board: Board):
        super().__init__(color, position, board)
        self.has_moved = False
        self.castling_with = None
        self.value = 100

    def threatens(self, field: (int, int)) -> bool:
        return abs(self.position[0] - field[0]) <= 1 and abs(self.position[1] - field[1]) <= 1

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        if not super().is_move_valid(player, to_pos):
            return False

        return (not self.is_endangered_at(to_pos)) and (self.threatens(to_pos) or self.can_perform_castling(to_pos))

    def move_to(self, new_pos: (int, int)):
        super(King, self).move_to(new_pos)
        self.has_moved = True

    def get_char(self):
        if self.color == Color.WHITE:
            return "♔"
        else:
            return "♚"

    def can_perform_castling(self, rook_pos):
        if abs(rook_pos[0] - self.position[0]) == 2:
            if rook_pos[0] < self.position[0]:
                rook_pos = (0, rook_pos[1])
            else:
                rook_pos = (7, rook_pos[1])
        piece = self.board.piece_at(rook_pos)
        noone_moved = not self.has_moved and type(piece) == Rook and piece.color == self.color and not piece.has_moved

        if noone_moved:
            direction = [-1, 1][self.position[0] < piece.position[0]]
            for x in range(2):
                step_pos = (self.position[0] + direction * (x + 1), self.position[1])
                if type(self.board.piece_at(step_pos)) != NoPiece:
                    return False
                if self.is_endangered_at(step_pos):
                    return False
            self.castling_with = piece
            return True
        else:
            return False

    def is_endangered_at(self, dest: (int, int) = None) -> bool:
        if dest is None:
            dest = self.position
        for piece in self.board.board.flatten():
            if piece.color != self.color and piece.position != dest and piece.threatens(dest):
                return True
        return False


class NoPiece(Piece):
    def __init__(self, position):
        super().__init__(None, position, None)
        self.value = -1

    def is_move_valid(self, player: Color, to_pos: (int, int)) -> bool:
        return False

    def get_char(self) -> str:
        if sum(self.position) % 2 == 0:
            return " "  # "▦"
        else:
            return " "  # "□"

    def __str__(self):
        return type(self).__name__ + " @ " + str(self.position)


def _valid_rook_move(start: (int, int), dest: (int, int), board: Board) -> bool:
    if dest[0] == start[0]:
        diff_y = [-1, 1][dest[1] > start[1]]
        for i in range(1, abs(dest[1] - start[1])):
            if type(board.piece_at((dest[0], start[1] + diff_y * i))) != NoPiece:
                return False
    elif dest[1] == start[1]:
        diff_x = [-1, 1][dest[0] > start[0]]
        for i in range(1, abs(dest[0] - start[0])):
            if type(board.piece_at((start[0] + diff_x * i, dest[1]))) != NoPiece:
                return False
    else:
        return False
    return True


def _valid_bishop_move(start: (int, int), dest: (int, int), board: Board) -> bool:
    diff_x = [-1, 1][dest[0] > start[0]]
    diff_y = [-1, 1][dest[1] > start[1]]
    for i in range(1, abs(dest[0] - start[0])):
        if type(board.piece_at((start[0] + diff_x * i, start[1] + diff_y * i))) != NoPiece:
            return False

    return abs(dest[0] - start[0]) == abs(dest[1] - start[1])
