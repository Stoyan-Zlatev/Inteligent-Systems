import math
from typing import List, Set, Tuple, Optional

class TicTacToe:
    """
    A Tic-Tac-Toe game that uses the Minimax algorithm with alpha-beta pruning for optimal AI play.

    Attributes:
    -----------
    board : List[List[str]]
        The game board, represented as a 3x3 list.
    available_moves : Set[Tuple[int, int]]
        Set of available moves, initialized with all board positions.
    cache : dict[str, List[int] or int]
        Tracks row, column, and diagonal sums for efficient win-checking.
    player : str
        The player's marker, 'X' by default.
    computer : str
        The computer's marker, 'O' by default.
    current_player : str
        Tracks whose turn it is, alternating between player and computer.
    """
    
    def __init__(self, player_starts: bool = True) -> None:
        self.board: List[List[str]] = [[' ' for _ in range(3)] for _ in range(3)]
        self.available_moves: Set[Tuple[int, int]] = {(i, j) for i in range(3) for j in range(3)}
        self.cache = {
            "rows": [0, 0, 0],      # Row sums
            "cols": [0, 0, 0],      # Column sums
            "diag1": 0,             # Diagonal from top-left to bottom-right
            "diag2": 0              # Diagonal from top-right to bottom-left
        }
        self.player: str = 'X'                   # Player's marker
        self.computer: str = 'O'                 # Computer's marker
        self.current_player: str = self.player if player_starts else self.computer

    def print_board(self) -> None:
        """Prints the current state of the game board."""
        print('-------------')
        for row in self.board:
            print('| ' + ' | '.join(row) + ' |')
            print('-------------')

    def check_winner_cache(self) -> Optional[str]:
        """
        Checks for a winner by using the cache to check row, column, and diagonal sums.

        Returns:
        --------
        Optional[str] : 'X' if the player wins, 'O' if the computer wins, None otherwise.
        """
        all_sums = self.cache["rows"] + self.cache["cols"] + [self.cache["diag1"], self.cache["diag2"]]
    
        # Check if any sum equals 3 (player win) or -3 (computer win)
        if any(value == 3 for value in all_sums):
            return 'X'  # Player wins
        elif any(value == -3 for value in all_sums):
            return 'O'  # Computer wins
        return None

    def is_board_full(self) -> bool:
        """Returns True if the board is full, False otherwise."""
        return len(self.available_moves) == 0

    def make_move(self, move: Tuple[int, int], player: str) -> None:
        """
        Places the player's marker on the board and updates cache for win checking.

        Parameters:
        -----------
        move : Tuple[int, int]
            The (row, col) position where the player makes the move.
        player : str
            The player's marker, 'X' or 'O'.
        """
        curr_row, curr_col = move
        self.board[curr_row][curr_col] = player
        self.available_moves.remove(move)

        # Update the cache for the winning check
        value = 1 if player == 'X' else -1
        self.cache["rows"][curr_row] += value
        self.cache["cols"][curr_col] += value
        if curr_row == curr_col:
            self.cache["diag1"] += value
        if curr_row + curr_col == 2:
            self.cache["diag2"] += value

    def undo_move(self, move: Tuple[int, int]) -> None:
        """
        Removes the player's marker from the board and updates cache.

        Parameters:
        -----------
        move : Tuple[int, int]
            The (row, col) position to clear on the board.
        """
        curr_row, curr_col = move
        player = self.board[curr_row][curr_col]
        self.board[curr_row][curr_col] = ' '
        self.available_moves.add(move)

        # Update the cache for undoing the move
        value = 1 if player == 'X' else -1
        self.cache["rows"][curr_row] -= value
        self.cache["cols"][curr_col] -= value
        if curr_row == curr_col:
            self.cache["diag1"] -= value
        if curr_row + curr_col == 2:
            self.cache["diag2"] -= value

    def minimax(self, is_maximizing: bool, alpha: float, beta: float) -> int:
        """
        Minimax algorithm with alpha-beta pruning.

        Parameters:
        -----------
        is_maximizing : bool
            True if the current turn is for maximizing player, False otherwise.
        alpha : float
            The best value that the maximizer can guarantee.
        beta : float
            The best value that the minimizer can guarantee.

        Returns:
        --------
        int : The score of the board for the maximizing player.
        """
        winner = self.check_winner_cache()
        if winner == self.computer:
            return 1
        elif winner == self.player:
            return -1
        elif self.is_board_full():
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for move in list(self.available_moves):
                self.make_move(move, self.computer)
                curr_eval = self.minimax(False, alpha, beta)
                self.undo_move(move)
                max_eval = max(max_eval, curr_eval)
                alpha = max(alpha, curr_eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in list(self.available_moves):
                self.make_move(move, self.player)
                curr_eval = self.minimax(True, alpha, beta)
                self.undo_move(move)
                min_eval = min(min_eval, curr_eval)
                beta = min(beta, curr_eval)
                if beta <= alpha:
                    break
            return min_eval

    def best_move(self) -> Optional[Tuple[int, int]]:
        """
        Determines the best move for the computer using the Minimax algorithm.

        Returns:
        --------
        Optional[Tuple[int, int]] : The optimal move (row, col) for the computer.
        """
        best_score = -math.inf
        move = None
        for m in self.available_moves:
            self.make_move(m, self.computer)
            score = self.minimax(False, -math.inf, math.inf)
            self.undo_move(m)
            if score > best_score:
                best_score = score
                move = m
        return move

    def play_game(self) -> None:
        """Runs the main game loop for player vs. computer."""
        print("Welcome to Tic-Tac-Toe!")
        while True:
            self.print_board()
            if self.current_player == self.player:
                # Player's turn
                while True:
                    try:
                        row = int(input("Enter row (1-3): ")) - 1
                        col = int(input("Enter column (1-3): ")) - 1
                        if (row, col) in self.available_moves:
                            self.make_move((row, col), self.player)
                            break
                        else:
                            print("Spot is taken! Try again.")
                    except (ValueError, IndexError):
                        print("Invalid input! Enter numbers between 1 and 3.")
            else:
                # Computer's turn
                print("Computer is thinking...")
                move = self.best_move()
                if move:
                    self.make_move(move, self.computer)

            # Check for a winner
            winner = self.check_winner_cache()
            if winner:
                self.print_board()
                print(f"{'Player' if winner == 'X' else 'Computer'} wins!")
                break
            elif self.is_board_full():
                self.print_board()
                print("It's a draw!")
                break

            # Switch player
            self.current_player = self.computer if self.current_player == self.player else self.player

def main():
    player_starts = input("Choose who starts (player/computer): ").lower() == "player"
    game = TicTacToe(player_starts)
    game.play_game()


if __name__ == "__main__":
    main()
