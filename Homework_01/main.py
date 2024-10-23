import heapq


class Board:
    """
    Class to represent and manage the puzzle board.
    """

    def __init__(self, board, target_positions, empty_position):
        self.board = board  # The current state of the puzzle board
        self.target_positions = target_positions  # Dictionary with target positions of tiles
        self.empty_position = empty_position  # Original position of the empty tile (0)
        self.rows = len(board)  # Number of rows (assumes square board)
        self.cols = len(board[0]) if board else 0  # Number of columns
        self.heuristic = self.calculate_heuristic()  # Calculate and store the heuristic upon initialization

    def calculate_heuristic(self):
        """
        Calculate the heuristic (Manhattan distance) for the current board state.
        """
        heuristic = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != 0:  # Skip the empty tile (0)
                    target_row, target_col = self.target_positions[self.board[row][col]]
                    heuristic += abs(target_row - row) + abs(target_col - col)
        return heuristic

    def can_move(self, row, col):
        """
        Check if the tile can be moved within the boundaries of the board.
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def move_tile(self, new_empty_position):
        """
        Perform the move by swapping the empty tile with a neighboring tile.
        """
        new_board = [row[:] for row in self.board]  # Deep copy the current board
        zero_row, zero_col = self.empty_position
        new_row, new_col = new_empty_position
        # Swap empty tile with the target tile
        new_board[zero_row][zero_col], new_board[new_row][new_col] = new_board[new_row][new_col], new_board[zero_row][
            zero_col]
        return Board(new_board, self.target_positions, new_empty_position)

    def print_board(self):
        """
        Print the current state of the board.
        """
        for row in self.board:
            print(row)
        print()

    # Comparison methods for comparing boards based on their heuristic
    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def __eq__(self, other):
        return self.heuristic == other.heuristic

    def __repr__(self):
        return f"Board(Heuristic={self.heuristic})"


def initialize_board_and_targets(n, k, board):
    """
    Initialize the target positions of all tiles, and return the dictionary of targets,
    the initial zero position, and the target zero position.
    """
    rows = cols = len(board)
    initial_empty_position = None
    target_zero_position = (k // rows, k % rows) if not k == -1 else (rows - 1, rows - 1)
    target_positions = {}
    tile_num = 1

    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 0:
                initial_empty_position = (row, col)  # Store the initial zero position
            if (row, col) != target_zero_position:
                target_positions[tile_num] = (row, col)
                tile_num += 1
    target_positions[0] = target_zero_position  # Add the target position for zero tile

    return rows, cols, target_positions, initial_empty_position


def solve_puzzle(board):
    """
    Solve the puzzle using a heuristic-based search (A* like approach).
    """
    directions = {
        (0, 1): 'left',
        (1, 0): 'up',
        (-1, 0): 'down',
        (0, -1): 'right'
    }

    boards = []
    path = []  # List to store the sequence of moves
    heapq.heappush(boards, (board, ''))  # Add current board and direction

    moves = 0
    while boards:
        # Pop the board with the lowest heuristic
        curr_board, last_move = heapq.heappop(boards)

        print(f"Move {moves}: {last_move}")
        curr_board.print_board()
        # If the heuristic is 0, we have solved the puzzle
        if curr_board.heuristic == 0:
            path.append(last_move)  # Include the last move in the path
            return moves, path

        if last_move:  # Skip adding the first move which is an empty string
            path.append(last_move)

        moves += 1
        for x, y in directions.keys():
            new_row, new_col = curr_board.empty_position[0] + x, curr_board.empty_position[1] + y
            if curr_board.can_move(new_row, new_col):
                new_empty_position = (new_row, new_col)
                new_board = curr_board.move_tile(new_empty_position)
                heapq.heappush(boards, (new_board, directions[(x, y)]))


def main():
    # Example board setup
    n = 15
    k = 0
    initial_board = [[1, 2, 3, 0],
                     [4, 5, 6, 7],
                     [8, 9, 10, 11],
                     [12, 13, 14, 15]]

    rows, cols, target_positions, initial_zero_position = initialize_board_and_targets(n, k, initial_board)

    board = Board(initial_board, target_positions, initial_zero_position)

    # Solve the puzzle
    moves, path = solve_puzzle(board)

    if path:
        print(f"Solved in {moves} moves.")
        for move in path:
            print(move)
    else:
        print("No solution was found.")


if __name__ == '__main__':
    main()
