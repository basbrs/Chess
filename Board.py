import copy
import numpy as np
import matplotlib.pyplot as plt

from Pieces import *
from Color import Color


class Board:
	def __init__(self):
		self.board = np.empty(shape=(8, 8)).astype(Piece)
		self.is_decided = False
		self.check = [False, False]
		self.points = [0, 0]
		self.from_pos = None
		self.current_player = Color.WHITE

		pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
		for x in range(len(pieces)):
			self.board[x, 0] = pieces[x](Color.BLACK, (x, 0), self)
			self.board[x, 1] = Pawn(Color.BLACK, (x, 1), self)
			self.board[x, 6] = Pawn(Color.WHITE, (x, 6), self)
			self.board[x, 7] = pieces[x](Color.WHITE, (x, 7), self)

			for y in range(2, 6):
				self.board[x, y] = NoPiece((x, y))

			self.white_king = self.board[4, 7]
			self.black_king = self.board[4, 0]

	def print(self):
		print("\n \tA\tB\tC\tD\tE\tF\tG\tH")
		for y in range(len(self.board)):
			print(8-y, "\t", end="")
			for x in range(len(self.board[y])):
				print(self.board[x, y].get_char(), end="\t")
			print("")
		print(f"WHITE at {self.points[0]} points, BLACK at {self.points[1]} points!")

	def plot(self):
		image = np.zeros(self.board.shape)

		for y in range(len(self.board)):
			for x in range(len(self.board[0])):
				if (x + y) % 2 == 0:
					image[x, y] = 1

		def onclick(event):
			x, y = round(event.xdata), round(event.ydata)
			if self.from_pos is None:
				self.from_pos = (x, y)
			else:
				print("moving", self.from_pos, "to", (x, y))
				if self.move(self.current_player, self.from_pos, (x, y)):
					self.current_player = Color(not self.current_player.value)
					self.print()
				self.from_pos = None

		plt.close()
		fig, axe = plt.subplots(nrows=1, ncols=1)
		axe.matshow(image, cmap="gray", alpha=.4)
		axe.set_xticklabels(["", "A", "B", "C", "D", "E", "F", "G", "H"])
		axe.set_yticklabels(range(9, 0, -1))
		fig.canvas.mpl_connect("button_press_event", onclick)

		for y in range(len(self.board)):
			for x in range(len(self.board[0])):
				plt.text(x - .2, y + .2, self.board[x, y].get_char(), size="xx-large")

		plt.show()

	def move(self, player: Color, pos_from: (int, int) or str or np.ndarray, pos_to: (int, int) or str or np.ndarray)\
			-> bool:
		if type(pos_from) == str:
			pos_from = str_to_tuple(pos_from)
		elif type(pos_from) == np.ndarray:
			pos_from = tuple(pos_from)
		if type(pos_to) == str:
			pos_to = str_to_tuple(pos_to)
		elif type(pos_to) == np.ndarray:
			pos_to = tuple(pos_to)


		moving_piece = self.piece_at(pos_from)
		if moving_piece.is_move_valid(player, pos_to):
			if type(moving_piece) is Pawn and moving_piece.en_passant_victim is not None:
				self.set_piece_at(moving_piece.en_passant_victim, NoPiece(moving_piece.en_passant_victim))
				moving_piece.en_passant_victim = None

			moving_piece.move_to(pos_to)

			if type(moving_piece) is King and moving_piece.castling_with is not None:
				moving_piece.castling_with.move_to((pos_from[0] + [-1, +1][pos_from[0] < pos_to[0]], pos_from[1]))
				moving_piece.castling_with = None

			for piece in [self.white_king, self.black_king]:
				if type(piece) is King and piece.is_endangered_at(piece.position):
					print(piece, "is in CHECK!")
					self.check[piece.color.value] = True

					mate = True
					try:
						for other_piece in self.board.flatten():
							if piece.color == other_piece.color:
								for y in range(len(self.board)):
									for x in range(len(self.board[0])):
										if other_piece.is_move_valid(player=piece.color, to_pos=(x, y)):
											mate = False
											raise BaseException
					except BaseException:
						pass
					if mate:
						print(piece, "is in CHECKMATE!")
						print(Color(not piece.color.value).name, "won!")
						self.is_decided = True
				else:
					self.check[piece.color.value] = False

			# can the other player move?
			can_move = False
			try:
				for piece in self.board.flatten():
					if piece.color != player:
						for y in range(len(self.board)):
							for x in range(len(self.board[0])):
								if piece.is_move_valid(player=piece.color, to_pos=(x, y)):
									can_move = True
									raise BaseException
			except BaseException:
				pass
			if not can_move and not self.is_decided:
				print(Color(not player.value).name, "can not make any moves but it not checkmate, TIE!")
				self.is_decided = True
			if len([piece for piece in self.board.flatten() if type(piece) != NoPiece]) <= 2:
				print("There are only Kings left, so no player can win: TIE!")
				self.is_decided = True
			return True
		else:
			# print("illegal move!")
			pass
		return False

	def grant_points(self, player: Color, points: int):
		self.points[player.value] += points

	def piece_at(self, position: (int, int)) -> Piece:
		if 0 <= position[0] < 8 and 0 <= position[1] < 8:
			return self.board[position]
		else:
			return NoPiece(position)

	def set_piece_at(self, new_pos, piece):
		self.board[new_pos] = piece

	def will_move_end_check(self, from_pos: (int, int), to_pos: (int, int), checked: Color) -> bool:
		new_board = copy.deepcopy(self)
		piece = new_board.piece_at(from_pos)
		piece.move_to(to_pos)

		if checked == Color.WHITE:
			return not new_board.white_king.is_endangered_at()
		else:
			return not new_board.black_king.is_endangered_at()


def str_to_tuple(string: str) -> (int, int):
	if len(string) == 2 and ("a" <= string[0] <= "h" or "A" <= string[0] <= "H") and ("1" <= string[1] <= "8"):
		return ord(string[0]) - ord("a"), 8 - int(string[1])
	else:
		print("illegal string to tuple:", string)
		return -1, -1
