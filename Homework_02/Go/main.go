package main

import (
	"fmt"
	"math/rand"
	"time"
)

type NQueensSolver struct {
	n                 int
	queens            []int
	rowConflicts      []int
	mainDiagConflicts []int
	antiDiagConflicts []int
}

func NewNQueensSolver(n int) *NQueensSolver {
	solver := &NQueensSolver{
		n:                 n,
		queens:            make([]int, n),
		rowConflicts:      make([]int, n),
		mainDiagConflicts: make([]int, 2*n-1),
		antiDiagConflicts: make([]int, 2*n-1),
	}

	// Initialize queens and the conflict caches
	for i := 0; i < n; i++ {
		solver.queens[i] = -1
	}
	solver.initializeBoard()
	return solver
}

func (s *NQueensSolver) initializeBoard() {
	for col := 0; col < s.n; col++ {
		row := (col * 2) % s.n
		s.placeQueen(col, row)
	}
}

func (s *NQueensSolver) placeQueen(col, row int) {
	if s.queens[col] != -1 {
		s.removeQueen(col, s.queens[col])
	}

	s.queens[col] = row
	s.rowConflicts[row]++
	s.mainDiagConflicts[row-col+s.n-1]++
	s.antiDiagConflicts[row+col]++
}

func (s *NQueensSolver) removeQueen(col, row int) {
	s.queens[col] = -1
	s.rowConflicts[row]--
	s.mainDiagConflicts[row-col+s.n-1]--
	s.antiDiagConflicts[row+col]--
}

func (s *NQueensSolver) getConflictsCount(row, col int) int {
	conflicts := s.rowConflicts[row] + s.mainDiagConflicts[row-col+s.n-1] + s.antiDiagConflicts[row+col]
	if s.queens[col] == row {
		conflicts -= 3
	}
	return conflicts
}

func (s *NQueensSolver) getColWithMaxConflicts() int {
	maxConflicts := -1
	maxConflictCols := []int{}

	for col := 0; col < s.n; col++ {
		row := s.queens[col]
		conflicts := s.getConflictsCount(row, col)
		if conflicts > maxConflicts {
			maxConflicts = conflicts
			maxConflictCols = []int{col}
		} else if conflicts == maxConflicts {
			maxConflictCols = append(maxConflictCols, col)
		}
	}

	if len(maxConflictCols) > 0 {
		return maxConflictCols[rand.Intn(len(maxConflictCols))]
	}
	return -1
}

func (s *NQueensSolver) getRowWithMinConflict(col int) int {
	minConflicts := int(^uint(0) >> 1) // Max int
	minConflictRows := []int{}

	for row := 0; row < s.n; row++ {
		conflicts := s.getConflictsCount(row, col)
		if conflicts < minConflicts {
			minConflicts = conflicts
			minConflictRows = []int{row}
		} else if conflicts == minConflicts {
			minConflictRows = append(minConflictRows, row)
		}
	}

	if len(minConflictRows) > 0 {
		return minConflictRows[rand.Intn(len(minConflictRows))]
	}
	return -1
}

func (s *NQueensSolver) hasConflicts() bool {
	for col := 0; col < s.n; col++ {
		if s.getConflictsCount(s.queens[col], col) > 0 {
			return true
		}
	}
	return false
}

func (s *NQueensSolver) solve() []int {
	if s.n <= 3 {
		return nil
	}

	for {
		if !s.hasConflicts() {
			return s.queens
		}

		col := s.getColWithMaxConflicts()
		row := s.getRowWithMinConflict(col)
		s.placeQueen(col, row)
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
		board[row][col] = '*'
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
	fmt.Scan(&n)

	start := time.Now()
	solver := NewNQueensSolver(n)
	solution := solver.solve()
	elapsed := time.Since(start)

	if solution != nil {
		if n <= 100 {
			printBoard(solution, n)
		} else {
			fmt.Println("Solution:", solution)
		}
	} else {
		fmt.Println(-1)
	}
	fmt.Printf("Elapsed time: %s\n", elapsed)
}
