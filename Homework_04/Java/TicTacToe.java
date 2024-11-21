import java.util.*;
import java.util.stream.Collectors;

public class TicTacToe {
    private Character[][] board;
    private int activePlayer;
    private Character playerSymbol;
    private Character computerSymbol;
    private static final int BOARD_SIZE = 3;
    private static final int MAX_POSSIBLE_SCORE = 10;

    public TicTacToe(int activePlayer) {
        board = new Character[][]{{' ', ' ', ' '}, {' ', ' ', ' '}, {' ', ' ', ' '}};
        this.activePlayer = activePlayer;
        if (activePlayer == 1) {
            computerSymbol = 'X';
            playerSymbol = 'O';
        } else if (activePlayer == 2) {
            playerSymbol = 'X';
            computerSymbol = 'O';
        }
    }

    private void printBoard() {
        System.out.println("-------------");
        for (int row = 0; row < BOARD_SIZE; row++) {
            System.out.print("| " );
            String seq =  Arrays.stream(board[row])
                    .map(String::valueOf)
                    .collect(Collectors.joining(" | "));
            System.out.print(seq);
            System.out.println(" |");
        }
        System.out.println("-------------");
    }

    private boolean hasWinner() {
        //row win
        boolean isWin;
        for (int i = 0; i < BOARD_SIZE; i++) {
            List<Character> row = Arrays.stream(board[i]).toList();
            isWin = row.stream().allMatch(row.get(0)::equals);
            if (isWin && row.get(0) != ' ') {
                return true;
            }
        }

        //column win
        for (int column = 0; column < BOARD_SIZE; column++) {
            if (board[0][column] != ' ' && board[0][column] == board[1][column]
                && board[1][column] == board[2][column]) {
                return true;
            }
        }

        //main diagonal win
        if (board[0][0] != ' ' && board[0][0] == board[1][1] && board[1][1] == board[2][2]) {
            return true;
        }

        //secondary diagonal win
        if (board[0][2] != ' ' && board[0][2] == board[1][1] && board[1][1] == board[2][0]) {
            return true;
        }

        return false;
    }

    private boolean isBoardFull() {
        for (int i = 0; i < BOARD_SIZE; i++) {
            if (Arrays.stream(board[i]).anyMatch((el) -> el == ' ')) {
                return false;
            }
        }
        return true;
    }

    private int minimaxWithPruning(int alpha, int beta, boolean isMaximizing, int depth) {
        if (hasWinner()) {
            return isMaximizing ? depth - MAX_POSSIBLE_SCORE : MAX_POSSIBLE_SCORE - depth;
        }

        if (isBoardFull()) {
            return 0;
        }

        if (isMaximizing) {
            int maxEval = Integer.MIN_VALUE;
            for (int i = 0; i < BOARD_SIZE; i++) {
                for (int j = 0; j < BOARD_SIZE; j++) {
                    if (board[i][j] == ' ') {
                        board[i][j] = computerSymbol;
                        int eval = minimaxWithPruning(alpha, beta, false, depth + 1);
                        board[i][j] = ' ';
                        maxEval = Math.max(maxEval, eval);
                        alpha = Math.max(alpha, eval);
                        if (beta <= alpha) {
                            break;
                        }
                    }
                }
            }
            return maxEval;
        } else {
            int minEval = Integer.MAX_VALUE;
            for (int i = 0; i < BOARD_SIZE; i++) {
                for (int j = 0; j < BOARD_SIZE; j++) {
                    if (board[i][j] == ' ') {
                        board[i][j] = playerSymbol;
                        int eval = minimaxWithPruning(alpha, beta, true, depth + 1);
                        board[i][j] = ' ';
                        minEval = Math.min(minEval, eval);
                        beta = Math.min(beta, eval);
                        if (beta <= alpha) {
                            break;
                        }
                    }
                }
            }
            return minEval;
        }
    }

    private List<Integer> findBestMove() {
        int bestScore = Integer.MIN_VALUE;
        List<Integer> bestMove = new ArrayList<>(List.of(-1, -1));
        for (int i = 0; i < BOARD_SIZE; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                if (board[i][j] == ' ') {
                    board[i][j] = computerSymbol;
                    int score = minimaxWithPruning(Integer.MIN_VALUE, Integer.MAX_VALUE, false, 0);
                    board[i][j] = ' ';
                    if (score > bestScore) {
                        bestScore = score;
                        bestMove.set(0, i);
                        bestMove.set(1, j);
                    }
                }
            }
        }
        return bestMove;
    }

    public void playGame(Scanner in) {
        while (true) {
            printBoard();
            if (activePlayer == 1) {
                List<Integer> move = findBestMove();
                if (move.get(0) != -1 && move.get(1) != -1) {
                    board[move.get(0)][move.get(1)] = computerSymbol;
                }
                System.out.println("Computer plays: ");

                activePlayer = 2;
            } else if (activePlayer == 2) {
                while (true) {
                    System.out.println("Enter your move: ");
                    int row = in.nextInt();
                    int column = in.nextInt();
                    
                    List<Integer> move = List.of(row - 1, column - 1);
                    if ((move.get(0) < 0 || move.get(0) >= BOARD_SIZE)
                            || (move.get(1) < 0 || move.get(1) >= BOARD_SIZE)) {
                        System.out.println("Move is not allowed. Try again!");
                        continue;
                    }
                    
                    if (board[move.get(0)][move.get(1)] != ' ') {
                        System.out.println("Move is taken. Try again!");
                    } else {
                        board[move.get(0)][move.get(1)] = playerSymbol;
                        break;
                    }
                }

                activePlayer = 1;
            }

            if (hasWinner()) {
                printBoard();
                String player = activePlayer == 1 ? "Player" : "Computer";
                System.out.println(player + " wins!");
                break;
            } else if (isBoardFull()) {
                printBoard();
                System.out.println("Draw!");
                break;
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("Choose who starts first. Computer(1) or Player(2): ");
        Scanner in = new Scanner(System.in);
        int playerStart = in.nextInt();

        TicTacToe ticTacToe = new TicTacToe(playerStart);
        ticTacToe.playGame(in);
    }
}
