import math


class Board:
    def __init__(self, board, empty_pos, heuristic, move=None, depth=0):
        self.board = board  # Flat list representing the board
        self.empty_pos = empty_pos  # Index of the empty tile (0)
        self.heuristic = heuristic  # Current heuristic value (Manhattan distance)
        self.move = move  # Move that led to this state ('up', 'down', 'left', 'right')
        self.depth = depth  # Depth in the search tree (g value)
        self.size = int(math.sqrt(len(board)))  # Board dimensions (assuming square)

    def manhattan_distance(self, pos1, pos2):
        """
        Calculate Manhattan distance between two positions on the board.
        """
        row1, col1 = divmod(pos1, self.size)
        row2, col2 = divmod(pos2, self.size)
        return abs(row1 - row2) + abs(col1 - col2)

    def get_neighbors(self, goal_positions):
        """
        Generate neighboring board states by moving the empty tile in all possible directions.
        """
        neighbors = []
        size = self.size
        row, col = divmod(self.empty_pos, size)
        moves = [(-1, 0, 'down'), (1, 0, 'up'), (0, -1, 'right'), (0, 1, 'left')]

        for dr, dc, action in moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < size and 0 <= new_col < size:
                new_empty_pos = new_row * size + new_col
                new_board = self.board.copy()
                # Swap the empty tile with the adjacent tile
                new_board[self.empty_pos], new_board[new_empty_pos] = new_board[new_empty_pos], new_board[
                    self.empty_pos]
                moved_tile = new_board[self.empty_pos]  # Tile that was moved into the empty position
                # Update heuristic incrementally
                old_distance = self.manhattan_distance(new_empty_pos, goal_positions[moved_tile])
                new_distance = self.manhattan_distance(self.empty_pos, goal_positions[moved_tile])
                new_heuristic = self.heuristic - old_distance + new_distance
                neighbor = Board(new_board, new_empty_pos, new_heuristic, move=action, depth=self.depth + 1)
                neighbors.append(neighbor)
        return neighbors


def compute_heuristic(board, goal_positions):
    """
    Calculate the total Manhattan distance for the current board state.
    """
    heuristic = 0
    size = int(math.sqrt(len(board)))
    for index, tile in enumerate(board):
        if tile == 0:
            continue
        goal_index = goal_positions[tile]
        heuristic += abs((index // size) - (goal_index // size)) + abs((index % size) - (goal_index % size))
    return heuristic


def is_solvable(board, size, empty_pos, goal_empty_pos):
    """
    Determine if the given puzzle is solvable.
    """
    flat_board = [tile for tile in board if tile != 0]
    inversions = 0
    for i in range(len(flat_board)):
        for j in range(i + 1, len(flat_board)):
            if flat_board[i] > flat_board[j]:
                inversions += 1
    if size & 1:
        return not inversions & 1
    else:
        empty_row = empty_pos // size
        empty_row_from_bottom = (goal_empty_pos // size) - empty_row - 1
        return inversions & 1 if not empty_row_from_bottom & 1 else not inversions & 1


def ida_star(root, goal_positions):
    """
    Perform the IDA* search to solve the puzzle.
    """
    bound = root.heuristic
    path = [root]
    while True:
        t = search(path, 0, bound, goal_positions)
        if t == 'FOUND':
            return [node.move for node in path[1:]]  # Exclude the initial state
        if t == float('inf'):
            return None
        bound = t


def search(path, g, bound, goal_positions, prev=None):
    """
    Recursive helper function for IDA* search.
    """
    node = path[-1]
    f = g + node.heuristic
    if f > bound:
        return f
    if node.heuristic == 0:
        return 'FOUND'
    min_bound = float('inf')
    neighbors = node.get_neighbors(goal_positions)
    # Process neighbors in order of increasing f-cost
    neighbors.sort(key=lambda n: n.depth + n.heuristic)
    for neighbor in neighbors:
        if not neighbor == prev:  # Avoid cycles
            path.append(neighbor)
            result = search(path, g + 1, bound, goal_positions, node.board)
            if result == 'FOUND':
                return 'FOUND'
            min_bound = min(min_bound, result)
            path.pop()
    return min_bound


def initialize_board(board, n, k):
    empty_pos = board.index(0)
    # Initialize goal positions
    goal_positions = [0] * (n + 1)  # Index by tile number
    empty_goal_pos = k if k != -1 else n
    tile_num = 1
    for pos in range(n + 1):
        if pos == empty_goal_pos:
            goal_positions[0] = pos  # Empty tile goal position
        else:
            goal_positions[tile_num] = pos
            tile_num += 1
    heuristic = compute_heuristic(board, goal_positions)
    root = Board(board, empty_pos, heuristic)
    return root, empty_pos, goal_positions


def main():
    n = int(input())
    k = int(input())
    size = int(math.sqrt(n + 1))
    board = []
    for _ in range(size):
        row = list(map(int, input().split()))
        board.extend(row)

    root, empty_pos, goal_positions = initialize_board(board, n, k)
    if not is_solvable(board, size, empty_pos, goal_positions[0]):
        print(-1)
        print("Not solvable")
        return
    path = ida_star(root, goal_positions)
    if path:
        print(len(path))
        for move in path:
            print(move)
    else:
        print(-1)


if __name__ == '__main__':
    main()
