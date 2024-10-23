bool isNativeMode = args.Any();

int N = ReadN();

var initial = new Node(GetInitialArray(), N);
var final = new Node(GetFinalArray(), N);

var path = new Stack<Node>();

bool hasSolution = false;
Node[]? solution = null;

path.Push(initial);

var startTime = DateTime.Now;

FindSolution();

PrintElapsedTime();

PrintSolution();

Halt();

void FindSolution()
{
    if (hasSolution) return;

    var current = path.Peek();

    if (current.Array.SequenceEqual(final.Array))
    {
        hasSolution = true;
        solution = new Node[path.Count];
        path.CopyTo(solution, 0);
        return;
    }

    ExecuteArrangement(current, current.SpaceIndex - 1, i => i >= 0, '>');
    ExecuteArrangement(current, current.SpaceIndex - 2, i => i >= 0, '>');
    ExecuteArrangement(current, current.SpaceIndex + 1, i => i <= 2 * N, '<');
    ExecuteArrangement(current, current.SpaceIndex + 2, i => i <= 2 * N, '<');
}

void ExecuteArrangement(Node current, int newIndex, Func<int, bool> checkIndex, char checkChar)
{
    if (checkIndex(newIndex) && current.Array[newIndex] == checkChar)
    {
        path.Push(CreateNode(current, newIndex));
        FindSolution();

        path.Pop();
    }
}

int ReadN()
{
    int n;
    if (isNativeMode && args.Contains("-N"))
    {
        var nIndex = Array.IndexOf(args, "-N") + 1;
        if (nIndex >= args.Length)
        {
            throw new ArgumentException("Missing N parameter");
        }

        if (!int.TryParse(args[nIndex], out n))
        {
            throw new ArgumentOutOfRangeException("N must be positive integer");
        }
    }
    else
    {
        Console.Write("N = ");
        if (!int.TryParse(Console.ReadLine()!, out n))
        {
            throw new ArgumentOutOfRangeException("N must be positive integer");
        }
    }

    if (n < 1)
    {
        throw new ArgumentOutOfRangeException("N must be positive integer");
    }

    return n;
}

void PrintElapsedTime()
{
    if (!isNativeMode || args.Contains("-time"))
    {
        Console.WriteLine($"Execution time: {(DateTime.Now - startTime).TotalMilliseconds} ms");
    }
}

void PrintSolution()
{
    if (!isNativeMode || args.Contains("-print"))
    {
        foreach (var arrangement in solution!.Reverse())
        {
            Console.WriteLine(arrangement.String);
        }
    }
}

void Halt()
{
    if (!isNativeMode)
    {
        Console.Write("Press any key to continue...");
        Console.ReadKey();
    }
}

char[] GetInitialArray()
{
    var initialArr = new char[2 * N + 1];
    Array.Fill(initialArr, '>', 0, N);
    Array.Fill(initialArr, '<', N + 1, N);
    initialArr[N] = '_';
    return initialArr;
}

char[] GetFinalArray()
{
    var finalArr = new char[2 * N + 1];
    Array.Fill(finalArr, '<', 0, N);
    Array.Fill(finalArr, '>', N + 1, N);
    finalArr[N] = '_';
    return finalArr;
}

Node CreateNode(Node current, int newSpaceInd)
{
    var result = new char[2 * N + 1];
    current.Array.CopyTo(result, 0);
    result[current.SpaceIndex] = current.Array[newSpaceInd];
    result[newSpaceInd] = '_';
    return new Node(result, newSpaceInd);
}

class Node(char[] arr, int spaceIndex)
{
    public char[] Array = arr;
    public int SpaceIndex = spaceIndex;

    private string? str = null;

    public string String
    {
        get
        {
            if (str == null) str = string.Join("", Array);
            return str;
        }
    }
}
