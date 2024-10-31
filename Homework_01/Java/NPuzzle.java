import java.util.*;

public class NPuzzle {
    private int countOfBlocks;
    private int sizeOfBoard;
    private int emptyPosition;
    private List<Integer> board;
    private final Map<String, Integer> directions;
    private static final int FOUND = -100;

    public NPuzzle(int countOfBlocks, int emptyPosition, List<Integer> board) {
        this.countOfBlocks = countOfBlocks;
        this.emptyPosition = emptyPosition;
        this.sizeOfBoard = (int) Math.sqrt(countOfBlocks + 1);
        this.board = board;

        directions = new HashMap<>();
        directions.put("left", 1);
        directions.put("right", -1);
        directions.put("up", sizeOfBoard);
        directions.put("down", -sizeOfBoard);
    }

    private int calculateDistance(int currentPosition, int newPosition) {
        int rowSteps = Math.abs(currentPosition / sizeOfBoard - newPosition / sizeOfBoard);
        int columnSteps = Math.abs(currentPosition % sizeOfBoard - newPosition % sizeOfBoard);

        return rowSteps + columnSteps;
    }

    private int manhattanDistance() {
        int distance = 0;
        for (int i = 0; i < board.size(); i++) {
            Integer block = board.get(i);
            if (block != 0) {
                int destination = (emptyPosition < block) ? block : block - 1;
                distance += calculateDistance(i, destination);
            }
        }
        return distance;
    }

    private boolean isMoveAllowed(int currentPosition, int newPosition) {
        if (newPosition < 0 || newPosition > countOfBlocks) {
            return false;
        }
        return calculateDistance(currentPosition, newPosition) <= 1;
    }

    private int updateManhattanDistance(int currentEmptyPosition, int newEmptyPosition) {
        int number = board.get(currentEmptyPosition);
        int destination = (emptyPosition < number) ? number : number - 1;
        return calculateDistance(currentEmptyPosition, destination)
                - calculateDistance(newEmptyPosition, destination);
    }

    private int search(int g, int h, int threshold, int currentEmptyPosition,
                       ArrayDeque<String> solutionSteps) {
        int f = g + h;

        if (h == 0) {
            return FOUND;
        }
        if (f > threshold) {
            return f;
        }

        int min = Integer.MAX_VALUE;

        for (Map.Entry<String, Integer> dir : directions.entrySet()) {
            if (!solutionSteps.isEmpty() && directions.get(solutionSteps.getLast()) == -1 * dir.getValue()) {
                continue;
            }

            int newEmptyPosition = currentEmptyPosition + dir.getValue();

            if (!isMoveAllowed(currentEmptyPosition, newEmptyPosition)) {
                continue;
            }
            Collections.swap(board, currentEmptyPosition, newEmptyPosition);
            solutionSteps.add(dir.getKey());
            int temp = search(g + 1, h + updateManhattanDistance(currentEmptyPosition, newEmptyPosition),
                    threshold, newEmptyPosition, solutionSteps);

            if (temp == FOUND) {
                return FOUND;
            }

            Collections.swap(board, currentEmptyPosition, newEmptyPosition);
            solutionSteps.removeLast();

            if (min > temp) {
                min = temp;
            }
        }

        return min;
    }

    public void idaStar(ArrayDeque<String> solutionSteps) {
        int h = manhattanDistance();
        int threshold = h;
        int currentEmptyPosition = board.indexOf(0);

        int temp;
        while (true) {
            temp = search(0, h, threshold, currentEmptyPosition, solutionSteps);
            if (temp == FOUND) {
                break;
            }
            threshold = temp;
        }
    }

    private int getInversionsCount() {
        int count = 0;
        for (int i = 0; i < board.size() - 1; i++) {
            for (int j = i + 1; j < board.size(); j++) {
                if (board.get(i) != 0 && board.get(j) != 0) {
                    if (board.get(i) > board.get(j)) {
                        count++;
                    }
                }
            }
        }
        return count;
    }

    public boolean isSolvable() {
        int inversions = getInversionsCount();
        if (sizeOfBoard % 2 == 1) {
            return inversions % 2 == 0;
        } else {
            int currentEmptyRowPosition = board.indexOf(0) / sizeOfBoard;
            return (inversions + currentEmptyRowPosition) % 2 == 1;
        }
    }

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int countOfBlocks = in.nextInt();
        int emptyPosition = in.nextInt();

        if (emptyPosition == -1) {
            emptyPosition = countOfBlocks;
        }

        List<Integer> board = new ArrayList<>();
        for (int i = 0; i <= countOfBlocks; i++) {
            board.add(in.nextInt());
        }

        NPuzzle nPuzzle = new NPuzzle(countOfBlocks, emptyPosition, board);
        ArrayDeque<String> solutionSteps = new ArrayDeque<>();

        if (!nPuzzle.isSolvable()) {
            System.out.println(-1);
        }
        else {
            long startTime = System.currentTimeMillis();
            nPuzzle.idaStar(solutionSteps);
            long endTime = System.currentTimeMillis();
            double elapsedTime = (endTime - startTime) / 1000.0;
            System.out.println(String.format("%.2f", elapsedTime) + " sec");

            System.out.println(solutionSteps.size());
            for (String step : solutionSteps) {
                System.out.println(step);
            }
        }
    }

}
