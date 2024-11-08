package main

import (
    "fmt"
    "math/rand"
    "time"
)

type NQueensSolver struct {
    n                  int
    queens             []int // Each index represents a column, and the value is the row
    rowConflicts       []int
    mainDiagConflicts  []int
    antiDiagConflicts  []int
}

func NewNQueensSolver(n int) *NQueensSolver {
    solver := &NQueensSolver{
        n:                 n,
        queens:            make([]int, n),
        rowConflicts:      make([]int, n),
        mainDiagConflicts: make([]int, 2*n-1),
        antiDiagConflicts: make([]int, 2*n-1),
    }
    for i := range solver.queens {
        solver.queens[i] = -1 // Initialize all columns with no queens
    }
    solver.initializeBoard()
    return solver
}

func (solver *NQueensSolver) initializeBoard() {
    col := 1
    for row := 0; row < solver.n; row++ {
        solver.queens[col] = row
        solver.rowConflicts[row]++
        solver.mainDiagConflicts[col-row+solver.n-1]++
        solver.antiDiagConflicts[col+row]++
        col += 2
        if col >= solver.n {
            col = 0
        }
    }
}

func (solver *NQueensSolver) placeQueen(col, row int) {
    if solver.queens[col] != -1 {
        solver.removeQueen(col, solver.queens[col])
    }
    solver.queens[col] = row
    solver.rowConflicts[row]++
    solver.mainDiagConflicts[row-col+solver.n-1]++
    solver.antiDiagConflicts[row+col]++
}

func (solver *NQueensSolver) removeQueen(col, row int) {
    solver.rowConflicts[row]--
    solver.mainDiagConflicts[row-col+solver.n-1]--
    solver.antiDiagConflicts[row+col]--
}

func (solver *NQueensSolver) getConflictsCount(row, col int) int {
    conflicts := solver.rowConflicts[row] +
        solver.mainDiagConflicts[row-col+solver.n-1] +
        solver.antiDiagConflicts[row+col]
    if solver.queens[col] == row {
        conflicts -= 3
    }
    return conflicts
}

func (solver *NQueensSolver) getColWithMaxConflicts() int {
    maxConflicts := -1
    maxConflictCols := []int{}
    for col := 0; col < solver.n; col++ {
        conflicts := solver.getConflictsCount(solver.queens[col], col)
        if conflicts > maxConflicts {
            maxConflicts = conflicts
            maxConflictCols = []int{col}
        } else if conflicts == maxConflicts {
            maxConflictCols = append(maxConflictCols, col)
        }
    }
    return maxConflictCols[rand.Intn(len(maxConflictCols))]
}

func (solver *NQueensSolver) getRowWithMinConflict(col int) int {
    minConflicts := solver.n * 3
    minConflictRows := []int{}
    for row := 0; row < solver.n; row++ {
        conflicts := solver.getConflictsCount(row, col)
        if conflicts < minConflicts {
            minConflicts = conflicts
            minConflictRows = []int{row}
        } else if conflicts == minConflicts {
            minConflictRows = append(minConflictRows, row)
        }
    }
    return minConflictRows[rand.Intn(len(minConflictRows))]
}

func (solver *NQueensSolver) hasConflicts() bool {
    for col := 0; col < solver.n; col++ {
        if solver.getConflictsCount(solver.queens[col], col) > 0 {
            return true
        }
    }
    return false
}

func (solver *NQueensSolver) solve() []int {
    if solver.n <= 3 {
        return nil
    }
    for {
        if !solver.hasConflicts() {
            return solver.queens
        }
        col := solver.getColWithMaxConflicts()
        row := solver.getRowWithMinConflict(col)
        solver.placeQueen(col, row)
    }
}

func printBoard(solution []int, n int) {
    board := make([][]rune, n)
    for i := range board {
        board[i] = make([]rune, n)
        for j := range board[i] {
            board[i][j] = '-'
        }
    }
    for col, row := range solution {
        if row >= 0 {
            board[row][col] = '*'
        }
    }
    for _, row := range board {
        for _, cell := range row {
            fmt.Printf("%c ", cell)
        }
        fmt.Println()
    }
}

func main() {
    var n int
    fmt.Print("Enter number of queens: ")
    fmt.Scanf("%d", &n)

    solver := NewNQueensSolver(n)
    start := time.Now()
    solution := solver.solve()
    duration := time.Since(start)

    if solution != nil {
        if n <= 100 {
            printBoard(solution, n)
        } else {
            fmt.Println("Solution length:", len(solution))
        }
    } else {
        fmt.Println(-1)
    }
    fmt.Println("Time taken:", duration)
}
