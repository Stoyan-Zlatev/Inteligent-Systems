var computer = 'O';
var player = 'X';
var emptyCell = '-';

var Scoring = new Dictionary<char, int>()
{
    {computer, 1 },
    {player,-1 },
    {emptyCell, 0},
};


bool isPlayerTurn = false;

var board = GetBoard();

Play();

return 0;


void Play()
{
    var availableMoves = GetAvailableMoves();
    char winner;
    while (true)
    {
        PrintBoard();

        if (HasGameFinished())
        {
            Console.WriteLine("Game finished! No winner!");
            return;
        }

        if ((winner = TakeWinner()) != emptyCell)
        {
            Console.WriteLine("Winner: " + winner);
            return;
        }

        if (isPlayerTurn)
        {
            Console.Write("Player: ");
            var move = ReadPlayerInput(availableMoves);
            MarkMove(move, player);
            availableMoves.RemoveMove(move);
        }
        else
        {
            Console.WriteLine("Computer: ");
            var move = GetBestMove(availableMoves);
            MarkMove(move!, computer);
            availableMoves.RemoveMove(move!);
        }

        isPlayerTurn = !isPlayerTurn;
    }
}

Move ReadPlayerInput(List<Move>? moves = null)
{
    var availableMoves = moves ?? GetAvailableMoves();
    while (true)
    {
        var move = Move.Read();
        if (move == null)
        {
            Console.WriteLine("Invalid format!");
            continue;
        }

        if (!availableMoves.HasMove(move))
        {
            Console.WriteLine("Invalid move!");
            continue;
        }

        return move;
    }
}

List<Move> GetAvailableMoves()
{
    var result = new List<Move>();
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            if (board[i, j] == emptyCell)
            {
                result.Add(new Move(i, j));
            }
        }
    }

    return result;
}

Move? GetBestMove(List<Move> availableMoves)
{
    Move? bestMove = null;
    int bestScore = int.MinValue;

    foreach (var move in availableMoves)
    {
        MarkMove(move, computer);
        if (TakeWinner() == computer)
        {
            return move;
        }

        var score = Minimax(int.MinValue, int.MaxValue, false);
        MarkMove(move, emptyCell);

        if (score > bestScore)
        {
            bestScore = score;
            bestMove = move;
        }
    }

    return bestMove;

}

int Minimax(int alpha, int beta, bool isMaxing = true, List<Move>? availableMoves = null)
{
    var winnerCandidate = TakeWinner();

    if (winnerCandidate != emptyCell)
    {
        return Scoring[winnerCandidate];
    }

    var moves = availableMoves ?? GetAvailableMoves();

    if (HasGameFinished(moves))
    {
        return Scoring[emptyCell];
    }

    if (isMaxing)
    {
        int maxScore = int.MinValue;

        foreach (var move in moves)
        {
            MarkMove(move, computer);
            var currentScore = Minimax(alpha, beta, false);
            MarkMove(move, emptyCell);

            maxScore = Math.Max(maxScore, currentScore);
            alpha = Math.Max(alpha, currentScore);

            if (beta <= alpha)
            {
                break;
            }
        }

        return maxScore;
    }
    else
    {
        int minScore = int.MaxValue;

        foreach (var move in moves)
        {
            MarkMove(move, player);
            var currentScore = Minimax(alpha, beta, true);
            MarkMove(move, emptyCell);

            minScore = Math.Min(minScore, currentScore);
            beta = Math.Min(beta, currentScore);

            if (beta <= alpha)
            {
                break;
            }
        }

        return minScore;
    }
}

bool HasGameFinished(List<Move>? moves = null)
{
    return (moves ?? GetAvailableMoves()).Count == 0;
}

void MarkMove(Move move, char symbol)
{
    board[move.X, move.Y] = symbol;
}

char TakeWinner()
{
    for (int i = 0; i < 3; i++)
    {
        if (board[i, 0] == board[i, 1] && board[i, 1] == board[i, 2] && board[i, 0] != emptyCell)
        {
            return board[i, 0];
        }

        if (board[0, i] == board[1, i] && board[1, i] == board[2, i] && board[0, i] != emptyCell)
        {
            return board[0, i];
        }
    }

    if (board[0, 0] == board[1, 1] && board[1, 1] == board[2, 2] && board[0, 0] != emptyCell)
    {
        return board[0, 0];
    }


    if (board[2, 0] == board[1, 1] && board[1, 1] == board[0, 2] && board[2, 0] != emptyCell)
    {
        return board[2, 0];
    }

    return emptyCell;
}

char[,] GetBoard()
{
    var board = new char[3, 3];
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            board[i, j] = emptyCell;
        }
    }

    return board;
}

void PrintBoard()
{
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            Console.Write(board[i, j]);
        }
        Console.WriteLine();
    }
    Console.WriteLine();
}

class Move(int x, int y)
{
    public int X { get; set; } = x;
    public int Y { get; set; } = y;

    public static Move? Read()
    {
        var move = Console.ReadLine()?.Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToList() ?? [];
        if (move.Count != 2) return null;

        if ((move[0] is < 1 or > 3) || (move[1] is < 1 or > 3))
        {
            return null;
        }

        return new Move(move[0] - 1, move[1] - 1);
    }
}

static class Helpers
{
    public static bool HasMove(this List<Move> moves, Move move)
    {
        return moves.Any(x => x.X == move.X && move.Y == x.Y);
    }

    public static void RemoveMove(this List<Move> moves, Move move)
    {
        var toRemove = moves.FirstOrDefault(x => x.X == move.X && move.Y == x.Y);
        if (toRemove == null)
        {
            return;
        }

        moves.Remove(toRemove);
    }
}
