from csp import Constraint, CSP
from typing import Dict, List, Optional


class QueensConstraint(Constraint[int, int]):
    def __init__(self, columns: List[int]) -> None:
        super().__init__(columns)
        self.columns: List[int] = columns

    def satisfied(self, assignment: Dict[int, int]) -> bool:
        # q1c = queen 1 column, q1r = queen 1 row
        for q1c, q1r in assignment.items():
            # q2c = queen 2 column
            for q2c in range(q1c + 1, len(self.columns) + 1):
                if q2c in assignment:
                    q2r: int = assignment[q2c]  # q2c = queen 2 row
                    if q1r == q2r:  # same row?
                        return False
                    if abs(q1r - q2r) == abs(q1c - q2c):  # same diagonal
                        return False
        return True  # no conflict


def print_board(solution: Dict[int, int], n: int) -> None:
    # Create an 8x8 board filled with '-'
    board = [['-' for _ in range(n)] for _ in range(n)]

    # Place '*' on the board according to the positions in the dictionary
    for col, row in solution.items():
        board[row][col] = '*'  # Adjust for 0-based indexing

    # Print the board
    for row in board:
        print(" ".join(row))


if __name__ == "__main__":
    n = int(input())
    columns: List[int] = [i for i in range(n)]
    rows: Dict[int, List[int]] = {}
    for column in columns:
        rows[column] = [i for i in range(n)]
    csp: CSP[int, int] = CSP(columns, rows)
    csp.add_constraint(QueensConstraint(columns))
    solution: Optional[Dict[int, int]] = csp.backtracking_search()
    if solution is None:
        print(-1)
    else:
        print_board(solution, n)
