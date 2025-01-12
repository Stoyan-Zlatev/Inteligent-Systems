import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Iterator;
import java.util.Scanner;

public class FrogLeap {
    public static boolean dfs(int emptySpace, int slots, StringBuilder currentState,
                              String targetState, Deque<String> path) {
        if (currentState.toString().equals(targetState)) {
            Iterator<String> descendingIterator = path.descendingIterator();
            while (descendingIterator.hasNext()) {
                System.out.println(descendingIterator.next());
            }
            return true;
        }

        for (int i = 1; i < 3; i++) {
            int newIndex = emptySpace - i;
            if (newIndex >= 0 && currentState.charAt(newIndex) == '>') {
                char symbolAtNewIndex = currentState.charAt(newIndex);
                currentState.setCharAt(emptySpace, symbolAtNewIndex);
                currentState.setCharAt(newIndex, '_');
                path.push(new String(currentState));

                if (dfs(newIndex, slots, currentState, targetState, path)) {
                    return true;
                }

                path.pop();
                currentState.setCharAt(emptySpace, '_');
                currentState.setCharAt(newIndex, symbolAtNewIndex);
            }
        }

        for (int i = 1; i < 3; i++) {
            int newIndex = emptySpace + i;
            if (newIndex < slots && currentState.charAt(newIndex) == '<') {
                char symbolAtNewIndex = currentState.charAt(newIndex);
                currentState.setCharAt(emptySpace, symbolAtNewIndex);
                currentState.setCharAt(newIndex, '_');
                path.push(new String(currentState));

                if (dfs(newIndex, slots, currentState, targetState, path)) {
                    return true;
                }

                path.pop();
                currentState.setCharAt(emptySpace, '_');
                currentState.setCharAt(newIndex, symbolAtNewIndex);
            }
        }

        return false;
    }

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        System.out.print("Enter N: ");
        int frogsCount = in.nextInt();
        int slots = 2 * frogsCount + 1;

        String leftFrogs = ">".repeat(frogsCount);
        String rightFrogs = "<".repeat(frogsCount);
        StringBuilder initialState = new StringBuilder(leftFrogs + "_" + rightFrogs);
        String targetState = rightFrogs + "_" + leftFrogs;

        Deque<String> path = new ArrayDeque<>();
        path.push(new String(initialState));

        long startTime = System.currentTimeMillis();
        dfs(frogsCount, slots, initialState, targetState, path);
        long endTime = System.currentTimeMillis();
        double elapsedTime = (endTime - startTime) / 1000.0;
        System.out.println(String.format("%.2f", elapsedTime));
    }
}
