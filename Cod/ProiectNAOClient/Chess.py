import chess
import chess.engine

debug = True
# debug = False

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

    def is_special_move(self, move):
        # Check if the move is a special move (e.g., castling, en passant, pawn promotion)
        if self.board.is_castling(move):
            return "Castling"
        elif self.board.is_en_passant(move):
            return "En Passant"
        elif move.promotion is not None:
            return f"Promotion to {move.promotion}"
        else:
            return "Regular Move"

    def make_move(self, move):
        try:
            # Attempt to make the move on the board
            self.board.push_uci(move)
            self.valid_move = True
            print(self.display_board())

            # Check if the move is a special move
            mesaj = None
            mesaj = self.is_special_move(chess.Move.from_uci(move))
            if self.is_check():
                mesaj = "Check"
            if self.is_checkmate():
                mesaj = "Check Mate"
            return True, mesaj  # Move is valid

        except ValueError as e:
            self.valid_move = False
            print(self.display_board())
            return False, str(e)  # Move is invalid

    def is_check(self):
        # Check if the current position is a check
        return self.board.is_check()

    def is_checkmate(self):
        # Check if the current position is a checkmate
        return self.board.is_checkmate()


def simulate_chess_match():
    # Initialize a chess game
    game = Chess()

    # Display the initial board
    print("Initial Board:")
    print(game.display_board())

    # List of moves for a simple chess game
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "c4e6", "d7e6", "d2d4", "e5d4", "e1g1", "d4c3", "f1e1", "c3b2"]

    # Execute the moves
    for move in moves:
        move_result, move_error = game.make_move(move)
        print("\nMove:", move)
        print("Move Result:", move_result)
        #print("Board after the move:")
        #print(game.display_board())
        if not move_result:
            print("Invalid Move:", move_error)
            break

    # Display the final result of the game
    if game.is_checkmate():
        print("\nCheckmate! Game Over.")
    elif game.is_check():
        print("\nCheck! The game is still ongoing.")
    else:
        print("\nThe game has ended in a draw.")

# Run the test function
# if debug: simulate_chess_match()