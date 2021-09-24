from Board import Board
import numpy as np

from Color import Color

if __name__ == "__main__":
    board = Board()
    board.print()

    player = Color.WHITE
    while not board.is_decided:
        if board.move(Color(player), np.random.randint(low=8, size=2), np.random.randint(low=8, size=2)):
            board.print()
            player = Color(not player.value)
