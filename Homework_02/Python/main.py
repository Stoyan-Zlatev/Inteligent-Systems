import random
from typing import List, Optional


class NQueensSolver:
    def __init__(self, n: int):
        self.n: int = n
        self.queens: List[int] = [-1] * n  # The index here represents a column, and each value is the row

        # Initialize conflict caches
        self.row_conflicts: List[int] = [0] * n  # Conflict count for each row
        self.main_diag_conflicts: List[int] = [0] * (2 * n - 1)  # Main diagonal conflicts (row - col)
        self.anti_diag_conflicts: List[int] = [0] * (2 * n - 1)  # Anti-diagonal conflicts (row + col)

        self._initialize_board()

    def _initialize_board(self) -> None:
        """Initialize queens with a knight-like pattern to reduce initial conflicts"""
        col = 1
        for row in range(self.n):
            self.queens[col] = row
            self.row_conflicts[row] += 1
            self.main_diag_conflicts[col - row + self.n - 1] += 1
            self.anti_diag_conflicts[col + row] += 1
            col += 2
            if col >= self.n:
                col = 0

    def _place_queen(self, col: int, row: int) -> None:
        """Places a queen at (row, col) and updates conflict caches."""
        if not self.queens[col] == -1:  # If a queen is already placed there, remove it first
            self._remove_queen(col, self.queens[col])

        self.queens[col] = row  # Set queen on (row, col)
        # Increase conflicts caused by placing a queen at this row
        self.row_conflicts[row] += 1
        self.main_diag_conflicts[row - col + self.n - 1] += 1
        self.anti_diag_conflicts[row + col] += 1

    def _remove_queen(self, col: int, row: int) -> None:
        """Removes a queen from (row, col) and updates conflict caches."""
        # Decrease conflicts caused by placing a queen at new row
        self.row_conflicts[row] -= 1
        self.main_diag_conflicts[row - col + self.n - 1] -= 1
        self.anti_diag_conflicts[row + col] -= 1

    def _get_conflicts_count(self, row: int, col: int) -> int:
        """Calculates conflict count for a queen at (row, col) based on caches."""
        conflicts = (
                self.row_conflicts[row]
                + self.main_diag_conflicts[row - col + self.n - 1]
                + self.anti_diag_conflicts[row + col]
        )
        # Subtract 3 if there's already a queen in (row, col)
        return conflicts - (self.queens[col] == row) * 3

    def _get_col_with_max_conflicts(self) -> int:
        """Return the column with the most conflicts for its queen."""
        cols_conflicts = [(col, self._get_conflicts_count(self.queens[col], col)) for col in range(self.n)]
        max_conflicts = max(cols_conflicts, key=lambda x: x[1])[1]
        max_conflict_cols = [col for col, conflicts in cols_conflicts if conflicts == max_conflicts]
        return random.choice(max_conflict_cols)

    def _get_row_with_min_conflict(self, col: int) -> int:
        """Return the row with the minimum conflicts in the given column."""
        rows_conflicts = [(row, self._get_conflicts_count(row, col)) for row in range(self.n)]
        min_conflicts = min(rows_conflicts, key=lambda x: x[1])[1]
        min_conflict_rows = [row for row, conflicts in rows_conflicts if conflicts == min_conflicts]
        return random.choice(min_conflict_rows)

    def _has_conflicts(self) -> bool:
        """Checks if there are any conflicts on the board using cached data."""
        return any(
            self._get_conflicts_count(self.queens[col], col) > 0
            for col in range(self.n)
        )

    def solve(self) -> Optional[List[int]]:
        """Solves the N-Queens problem using Min-Conflicts and restart if necessary."""
        if self.n <= 3:
            return None

        while True:
            if not self._has_conflicts():
                return self.queens
            col = self._get_col_with_max_conflicts()
            row = self._get_row_with_min_conflict(col)
            self._place_queen(col, row)


def print_board(solution: List[int], n: int) -> None:
    board: List[List[str]] = [['-' for _ in range(n)] for _ in range(n)]

    # Place '*' on the board according to the positions in the solution
    for col, row in enumerate(solution):
        board[row][col] = '*'

    # Print the board
    for row in board:
        print(" ".join(row))


def main():
    n: int = int(input("Enter number of queens: "))
    from datetime import datetime
    now = datetime.now()
    solver = NQueensSolver(n)
    solution = solver.solve()
    end = datetime.now()
    if solution:
        if n <= 100:
            print_board(solution, n)
        else:
            #print("Solution:", solution)
            print(len(set(solution)))
    else:
        print(-1)
    print("{}".format(end - now))


if __name__ == "__main__":
    main()
