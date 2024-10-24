import heapq
import math


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


def is_solvable(board, rows, empty_row, target_empty_row):
    """
    Check if a puzzle is solvable based on the number of inversions.
    """
    flat_list = [tile for row in board for tile in row if tile != 0]
    inversions = 0
    for i in range(len(flat_list)):
        for j in range(i + 1, len(flat_list)):
            if flat_list[i] > flat_list[j]:
                inversions += 1
    # If the grid width is odd, return true if the number of inversions is even.
    if rows & 1:
        return inversions % 2 == 0
    else:
        # If the grid width is even, the puzzle is solvable if:
        # - the blank is on an even row counting from the bottom and the number of inversions is odd, or
        # - the blank is on an odd row counting from the bottom and the number of inversions is even.
        empty_row_index = target_empty_row - empty_row - 1
        return (inversions % 2 == 0) if (empty_row_index % 2 == 1) else (inversions % 2 == 1)


def initialize_board_and_targets(rows, cols, k, board):
    """
    Initialize the target positions of all tiles, and return the dictionary of targets,
    the initial zero position, and the target zero position.
    """
    initial_empty_position = None
    target_empty_position = (k // rows, k % rows) if not k == -1 else (rows - 1, rows - 1)
    target_positions = {}
    tile_num = 1

    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 0:
                initial_empty_position = (row, col)  # Store the initial empty position
            if (row, col) != target_empty_position:
                target_positions[tile_num] = (row, col)
                tile_num += 1
    target_positions[0] = target_empty_position  # Add the target position for empty tile

    return target_positions, initial_empty_position


def search(board, bound, directions):
    """
    Iterative DFS function using a stack with bounded f-cost.
    """
    # Stack contains tuples of (board, g, path)
    stack = [(board, 0, [])]  # g = 0 at the start, path is empty

    min_cost = float('inf')

    while stack:
        current_board, g, path = stack.pop()

        f = g + current_board.heuristic

        # If f exceeds the bound, update the minimum cost seen
        if f > bound:
            min_cost = min(min_cost, f)
            continue

        # If the goal is reached, return the solution
        if current_board.heuristic == 0:
            return True, path

        # Expand the current board and push neighbors onto the stack
        for (x, y), direction in directions.items():
            new_row, new_col = current_board.empty_position[0] + x, current_board.empty_position[1] + y

            if current_board.can_move(new_row, new_col):
                new_empty_position = (new_row, new_col)
                new_board = current_board.move_tile(new_empty_position)

                # Push the new board state onto the stack
                stack.append((new_board, g + 1, path + [direction]))

    return min_cost, None


def solve_puzzle_ida_star(board):
    """
    Solve the puzzle using IDA* (Iterative Deepening A*) with an explicit stack.
    """
    directions = {
        (0, 1): 'left',
        (1, 0): 'up',
        (-1, 0): 'down',
        (0, -1): 'right'
    }

    # Start IDA* with the initial bound equal to the heuristic value of the initial board
    bound = board.heuristic

    while True:
        result, path = search(board, bound, directions)

        if result is True:  # Solution found
            return path

        if result == float('inf'):  # No solution exists
            return None

        # Increase bound to the minimum f-cost encountered during the last iteration
        bound = result


def main():
    # Example board setup
    n = int(input("Enter N: "))
    k = int(input("Enter K: "))
    initial_board = []

    rows = cols = int(math.sqrt(n + 1))
    for _ in range(rows):
        initial_board.append((list(map(int, input().split()))))
    target_positions, initial_zero_position = initialize_board_and_targets(rows, cols, k, initial_board)
    board = Board(initial_board, target_positions, initial_zero_position)
    if not is_solvable(board.board, rows, initial_zero_position[0], target_positions[0][0]):
        print(-1)
        print("Not solvable")
        return
    # Solve the puzzle using IDA*
    path = solve_puzzle_ida_star(board)

    if path:
        print(len(path))
        for p in path:
            print(p)
    else:
        print(-1)


if __name__ == '__main__':
    main()
