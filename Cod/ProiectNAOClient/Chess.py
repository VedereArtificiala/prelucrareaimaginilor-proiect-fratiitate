import chess
import chess.engine


class Chess:
    def __init__(self):
        # Create a new chess board
        self.board = chess.Board()
        self.valid_move = None

    def get_best_move(self, time=3.0):
        with chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe") as engine:
            result = engine.play(self.board, chess.engine.Limit(time=time))
            return result.move

    def display_board(self):
        # Display the current board as a string
        return str(self.board)

    def get_last_move_result(self):
        return self.valid_move

    def make_move(self, move):
        try:
            # Attempt to make the move on the board
            self.board.push_uci(move)
            self.valid_move = True
            return True, None  # Move is valid
        except ValueError as e:
            self.valid_move = False
            return False, str(e)  # Move is invalid


def test():
    game = Chess()
    print("Initial Board:")
    print(game.display_board())

    # Make a valid move
    move_result, move_error = game.make_move("e2e4")
    print("\nMove Result:", move_result)
    print("Board after e2e4:")
    print(game.display_board())

    # Make an invalid move
    move_result, move_error = game.make_move("e2e5")
    print("\nMove Result:", move_result)
    print("Board after attempting e2e5 (even if it's invalid):")
    if move_result:
        print(game.display_board())
    print("Invalid Move:", move_error)

# test()
