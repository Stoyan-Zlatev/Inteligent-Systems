using System.Diagnostics;

bool isNativeMode = false;

var Transforms = new (Direction dir, int x, int y)[]
{
    (Direction.Left,0,1),
    (Direction.Right,0, -1),
    (Direction.Up,1,0),
    (Direction.Down,-1,0),
};

var OppositeDirections = new Dictionary<Direction, Direction>() {
    {Direction.Left,Direction.Right },
    {Direction.Right,Direction.Left },
    {Direction.Up,Direction.Down},
    {Direction.Down,Direction.Up},
};

var DirectionNames = new Dictionary<Direction, string>() {
    {Direction.Left, "left" },
    {Direction.Right, "right"},
    {Direction.Up, "up"},
    {Direction.Down, "down"},
};

int N = (int)Math.Sqrt(int.Parse(Console.ReadLine()!) + 1);
int EmptyIndex = int.Parse(Console.ReadLine()!);

var finalArray = GetFinalArray();
var correctPositions = GetPositionsHashSet(finalArray);

var Array = GetInitialArray();
var initialHeuristicMatrix = CalculateHeuristic(Array);
var EmptyPosition = GetInitialEmptyPos(Array);
var Heuristic = initialHeuristicMatrix.Cast<int>().Sum();

var dirs = new Stack<Direction>();

var hasSolution = HasSolution();

if (!hasSolution)
{
    Console.WriteLine("-1");
    return 0;
}


Direction[]? solution = null;

var startTime = Stopwatch.GetTimestamp();

FindSolution();

PrintElapsedTime();

PrintSolution();

Halt();

return 0;

int FindSolutionIteration(int bound, int currentDepth)
{
    if (Heuristic == 0)
    {
        solution = new Direction[dirs!.Count];
        dirs!.CopyTo(solution!, 0);
        return -1;
    }

    int cost = Heuristic + currentDepth;

    if (cost > bound)
    {
        return cost;
    }

    int min = int.MaxValue;

    foreach (var arrangement in Transforms)
    {
        if (dirs.Any() && dirs.Peek() == OppositeDirections[arrangement.dir])
        {
            continue;
        }

        var executionResult = ChangeEmptyPosition(arrangement);
        if (!executionResult.Changed)
        {
            continue;
        }

        var newCost = FindSolutionIteration(bound, currentDepth + 1);

        if (newCost == -1)
        {
            return newCost;
        }

        RevertEmptyPosition(executionResult);

        if (newCost < min)
        {
            min = newCost;
        }
    }

    return min;
}

void FindSolution()
{
    int bound = Heuristic;

    while (true)
    {
        int cost = FindSolutionIteration(bound, 0);
        if (cost == -1)
        {
            break;
        }

        bound = cost;
    }
}

(bool Changed, int HeuristicDiff, (int X, int Y) OldEmptyPosition) ChangeEmptyPosition((Direction dir, int x, int y) arrangement)
{
    var oldEmpty = EmptyPosition;
    EmptyPosition.X += arrangement.x;
    EmptyPosition.Y += arrangement.y;

    if (!(0 <= EmptyPosition.X && EmptyPosition.X < N &&
        0 <= EmptyPosition.Y && EmptyPosition.Y < N))
    {
        EmptyPosition = oldEmpty;
        return (false, 0, EmptyPosition);
    }

    dirs.Push(arrangement.dir);

    Array[oldEmpty.X, oldEmpty.Y] = Array[EmptyPosition.X, EmptyPosition.Y];
    Array[EmptyPosition.X, EmptyPosition.Y] = 0;

    var oldHeuristic = CalculateHeuristicForValue(Array[oldEmpty.X, oldEmpty.Y], EmptyPosition.X, EmptyPosition.Y);
    var newHeuristic = CalculateHeuristicForValue(Array[oldEmpty.X, oldEmpty.Y], oldEmpty.X, oldEmpty.Y);

    int diff = newHeuristic - oldHeuristic;
    Heuristic += diff;

    return (true, diff, oldEmpty);
}

void RevertEmptyPosition((bool Changed, int HeuristicDiff, (int X, int Y) OldEmptyPosition) change)
{
    Array[EmptyPosition.X, EmptyPosition.Y] = Array[change.OldEmptyPosition.X, change.OldEmptyPosition.Y];
    Array[change.OldEmptyPosition.X, change.OldEmptyPosition.Y] = 0;

    EmptyPosition = change.OldEmptyPosition;
    Heuristic -= change.HeuristicDiff;

    dirs.Pop();
}

bool HasSolution()
{
    int inversions = 0;
    int emptySquareRow = 0;
    var flattened = Array.Cast<int>().ToArray();
    for (int i = 0; i < flattened.Length; i++)
    {
        if (flattened[i] == 0) emptySquareRow = i / N;

        for (int j = i + 1; j < flattened.Length; j++)
        {
            if (flattened[i] > flattened[j] && flattened[i] != 0 && flattened[j] != 0)
            {
                inversions++;
            }
        }
    }

    return N % 2 == 0 ? (inversions + emptySquareRow) % 2 == 1 : inversions % 2 == 0;
}

void PrintElapsedTime()
{
    if (!isNativeMode || args.Contains("-time"))
    {
        Console.WriteLine($"Execution time: {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds} ms");
    }
}

void PrintSolution()
{
    if (!isNativeMode || args.Contains("-print"))
    {
        Console.WriteLine(solution!.Count());
        foreach (var direction in solution!.Reverse())
        {
            Console.WriteLine(DirectionNames[direction]);
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

int[,] GetInitialArray()
{
    var arr = new int[N, N];
    for (int i = 0; i < N; i++)
    {
        var line = Console.ReadLine()!.Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToArray();
        for (int j = 0; j < N; j++)
        {
            arr[i, j] = line[j];
        }
    }

    return arr;
}

int[,] GetFinalArray()
{
    if (EmptyIndex == -1) EmptyIndex = N * N - 1;
    int IndRow = EmptyIndex / N;
    int IndCol = EmptyIndex % N;
    var arr = new int[N, N];
    int counter = 1;
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (i == IndRow && j == IndCol)
            {
                arr[i, j] = 0;
            }
            else
            {
                arr[i, j] = counter++;
            }
        }
    }

    return arr;
}

Dictionary<int, (int row, int col)> GetPositionsHashSet(int[,] arr)
{
    var result = new Dictionary<int, (int row, int col)>();

    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            result[arr[i, j]] = (i, j);
        }
    }

    return result;
}

(int X, int Y) GetInitialEmptyPos(int[,] arr)
{
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (arr[i, j] == 0)
            {
                return (i, j);
            }
        }
    }

    return (-1, -1);
}

int CalculateHeuristicForValue(int value, int i, int j)
{
    var correctPos = correctPositions![value];
    return Math.Abs(correctPos.col - j) + Math.Abs(correctPos.row - i);
}

int[,] CalculateHeuristic(int[,] arr)
{
    var res = new int[N, N];
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (arr[i, j] != 0)
            {
                res[i, j] = CalculateHeuristicForValue(arr[i, j], i, j);
            }
            else
            {
                res[i, j] = 0;
            }
        }
    }

    return res;
}

enum Direction
{
    Up, Down, Left, Right
}
