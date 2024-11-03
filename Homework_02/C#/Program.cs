using System.Diagnostics;

bool isNativeMode = false;

int N = int.Parse(Console.ReadLine() ?? "-1");

if (N == 1)
{
    Console.WriteLine("*");
    return 0;
}

if (N < 4)
{
    Console.WriteLine(-1);
    return 0;
}

var board = new int[N];
var queensPerRow = new int[N];
var queensPerDiagonal1 = new int[2 * N - 1];
var queensPerDiagonal2 = new int[2 * N - 1];

PlaceQueens();

var foundSolution = false;
var rnd = new Random();

var startTime = Stopwatch.GetTimestamp();

while (!foundSolution)
{
    FindSolution();
}

PrintElapsedTime();

PrintSolution();

Halt();

return 0;

void FindSolution()
{
    int iter = 0;
    int col, row;

    while (iter++ <= N)
    {
        col = GetColumnMaxConflicts();
        if (foundSolution)
        {
            break;
        }

        row = GetRowMinConflicts(col);

        PlaceQueen(col, row);
    }
}

void PlaceQueens()
{
    int col = 1;
    for (int row = 0; row < N; row++)
    {
        board[col] = row;
        queensPerRow[row]++;
        queensPerDiagonal1[col - row + N - 1]++;
        queensPerDiagonal2[col + row]++;

        col += 2;
        if (col >= N)
        {
            col = 0;
        }
    }
}

int GetColumnMaxConflicts()
{
    var cols = Enumerable.Range(0, N).Select(col => (col, conflicts: GetConflictsForPosition(board[col], col) - 3));

    var maxConflicts = cols.Max(x => x.conflicts);
    var maxColumns = cols.Where(x => x.conflicts == maxConflicts).ToList();
    int index = rnd.Next(0, maxColumns.Count());

    if (maxConflicts == 0)
    {
        foundSolution = true;
    }

    return maxColumns[index].col;
}

int GetRowMinConflicts(int col)
{
    var currentRow = board[col];
    var rows = Enumerable.Range(0, N).Select(row =>
    {
        var conflicts = GetConflictsForPosition(row, col);
        return (row, conflicts: currentRow == row ? conflicts - 3 : conflicts);
    });

    var minConflicts = rows.Where(x => x.conflicts >= 0).Min(x => x.conflicts);
    var minRows = rows.Where(x => x.conflicts == minConflicts).ToList();
    int index = rnd.Next(0, minRows.Count());

    return minRows[index].row;
}

void PlaceQueen(int col, int row)
{
    int oldRow = board[col];

    queensPerRow[oldRow]--;
    queensPerDiagonal1[col - oldRow + N - 1]--;
    queensPerDiagonal2[col + oldRow]--;

    board[col] = row;
    queensPerRow[row]++;
    queensPerDiagonal1[col - row + N - 1]++;
    queensPerDiagonal2[col + row]++;
}

int GetConflictsForPosition(int row, int col)
{
    return queensPerRow[row] + queensPerDiagonal1[col - row + N - 1] + queensPerDiagonal2[col + row];
}

double PrintElapsedTime(bool print = true)
{
    if (!isNativeMode || args.Contains("-time"))
    {
        var ms = Stopwatch.GetElapsedTime(startTime).TotalMilliseconds;
        if (print)
        {
            Console.WriteLine($"Execution time: {ms} ms");
        }
        return ms;
    }

    return 0;
}

void PrintSolution()
{
    if (!isNativeMode || args.Contains("-print"))
    {
        if (N > 50)
        {
            return;
        }

        for (int i = 0; i < N; i++)
        {
            for (int j = 0; j < N; j++)
            {
                Console.Write(board[j] == i ? "* " : "- ");
            }
            Console.WriteLine();
        }
    }
}

void Halt()
{
    if (isNativeMode && args.Contains("-halt"))
    {
        Console.Write("Press any key to continue...");
        Console.ReadKey();
    }
}
