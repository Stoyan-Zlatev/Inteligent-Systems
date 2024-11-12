import java.util.*;

public class NQueens {
    private int countOfQueens;
    private List<Integer> queens;
    private List<Integer> queensPerRow;
    private List<Integer> queensPerMainDiagonal;
    private List<Integer> queensPerSecondaryDiagonal;
    private boolean hasConflicts = true;
    private static final int MAX_STEPS = 5000;

    public NQueens(int countOfQueens) {
        this.countOfQueens = countOfQueens;
        queens = new ArrayList<>(Collections.nCopies(countOfQueens, 0));
        queensPerRow = new ArrayList<>(Collections.nCopies(countOfQueens, 0));
        queensPerMainDiagonal = new ArrayList<>(Collections.nCopies(2 * countOfQueens - 1, 0));
        queensPerSecondaryDiagonal = new ArrayList<>(Collections.nCopies(2 * countOfQueens - 1, 0));
    }

    private void initializeQueens() {
        int column = 1;
        for (int row = 0; row < countOfQueens; row++) {
            queens.set(column, row);
            queensPerRow.set(row, queensPerRow.get(row) + 1);
            int indexOfMainDiagonal = column - row + countOfQueens - 1;
            queensPerMainDiagonal.set(indexOfMainDiagonal,
                    queensPerMainDiagonal.get(indexOfMainDiagonal) + 1);
            int indexOfSecondaryDiagonal = column + row;
            queensPerSecondaryDiagonal.set(indexOfSecondaryDiagonal,
                    queensPerSecondaryDiagonal.get(indexOfSecondaryDiagonal) + 1);

            column += 2;
            if (column >= countOfQueens) {
                column = 0;
            }
        }
    }

    private static int getRandomPosition(List<Integer> list) {
        Random rand = new Random();
        return list.get(rand.nextInt(list.size()));
    }

    private int getCountOfConflicts(int row, int column) {
        return queensPerRow.get(row) + queensPerMainDiagonal.get(column - row + countOfQueens - 1)
                + queensPerSecondaryDiagonal.get(column + row);
    }

    private int getColumnWithMaxConflicts() {
        int maxConflicts = Integer.MIN_VALUE;
        List<Integer> columnsWithMaxConflicts = new ArrayList<>();

        for (int column = 0; column < countOfQueens; column++) {
            int row = queens.get(column);
            int countOfConflicts = getCountOfConflicts(row, column) - 3;
            if (countOfConflicts > maxConflicts) {
                columnsWithMaxConflicts.clear();
                columnsWithMaxConflicts.add(column);
                maxConflicts = countOfConflicts;
            } else if (countOfConflicts == maxConflicts) {
                columnsWithMaxConflicts.add(column);
            }
        }

        if (maxConflicts == 0) {
            hasConflicts = false;
        }

        return getRandomPosition(columnsWithMaxConflicts);
    }

    private int getRowWithMinConflicts(int column) {
        int minConflicts = Integer.MAX_VALUE;
        List<Integer> rowsWithMinConflicts = new ArrayList<>();
        int rowOfQueen = queens.get(column);

        for (int row = 0; row < countOfQueens; row++) {
            int countOfConflicts = getCountOfConflicts(row, column);
            if (rowOfQueen == row) {
                countOfConflicts -= 3;
            }
            if (countOfConflicts < minConflicts) {
                rowsWithMinConflicts.clear();
                rowsWithMinConflicts.add(row);
                minConflicts = countOfConflicts;
            } else if (countOfConflicts == minConflicts) {
                rowsWithMinConflicts.add(row);
            }
        }

        return getRandomPosition(rowsWithMinConflicts);
    }

    private void changeQueenPosition(int row, int column) {
        int oldRowPosition = queens.get(column);
        queensPerRow.set(oldRowPosition, queensPerRow.get(oldRowPosition) - 1);
        int indexOfMainDiagonal = column - oldRowPosition + countOfQueens - 1;
        queensPerMainDiagonal.set(indexOfMainDiagonal,
                queensPerMainDiagonal.get(indexOfMainDiagonal) - 1);
        int indexOfSecondaryDiagonal = column + oldRowPosition;
        queensPerSecondaryDiagonal.set(indexOfSecondaryDiagonal,
                queensPerSecondaryDiagonal.get(indexOfSecondaryDiagonal) - 1);

        queens.set(column, row);

        queensPerRow.set(row, queensPerRow.get(row) + 1);
        indexOfMainDiagonal = column - row + countOfQueens - 1;
        queensPerMainDiagonal.set(indexOfMainDiagonal,
                queensPerMainDiagonal.get(indexOfMainDiagonal) + 1);
        indexOfSecondaryDiagonal = column + row;
        queensPerSecondaryDiagonal.set(indexOfSecondaryDiagonal,
                queensPerSecondaryDiagonal.get(indexOfSecondaryDiagonal) + 1);
    }

    public void minConflicts() {
        initializeQueens();
        int column;
        int row;
        for (int i = 0; i < MAX_STEPS; i++) {
            column = getColumnWithMaxConflicts();
            if (!hasConflicts) {
                break;
            }
            row = getRowWithMinConflicts(column);
            changeQueenPosition(row, column);
        }

        if (hasConflicts) {
            minConflicts();
        }
    }

    public boolean isSolvable() {
        return countOfQueens > 0 && countOfQueens != 2 && countOfQueens != 3;
    }

    public void printQueensBoard() {
        for (int row = 0; row < countOfQueens; row++) {
            for (int column = 0; column < countOfQueens; column++) {
                String symbol = (queens.get(column) == row) ? "* " : "_ ";
                System.out.print(symbol);
            }
            System.out.println();
        }
    }

    public void printQueensPositions() {
        System.out.println(String.join(", ", queens.toString()));
    }

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int countOfQueens = in.nextInt();

        NQueens nQueens = new NQueens(countOfQueens);

        if (!nQueens.isSolvable()) {
            System.out.println(-1);
        } else {
            long startTime = System.currentTimeMillis();
            if (countOfQueens != 1) {
                nQueens.minConflicts();
            }
            long endTime = System.currentTimeMillis();
            if (countOfQueens > 100) {
                double elapsedTime = (endTime - startTime) / 1000.0;
                System.out.println(String.format("%.2f", elapsedTime));
            } else {
                nQueens.printQueensBoard();
                //nQueens.printQueensPositions();
            }
        }

    }

}
