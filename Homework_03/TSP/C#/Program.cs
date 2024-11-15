using System.Diagnostics;

bool isNativeMode = false;
var rnd = new Random();

// ~ 20 sec for custom, found best solution
// << 1 sec for uk12, found best solution
var maxGenerations = 1e3; //1e5 for large sets, 5e3 for small sets
var populationSize = 200; // 12 for large sets, 100+ for small sets
var checkpointsCount = 10;
var toleranceLevel = 5; // 10
var mutationProbability = 0.5;
var eliteCount = 2;
var tournamentSize = 3;
var shouldSelfCorrect = false; // true only for large sets

var occurs = new Dictionary<double, int>();
var maxTries = 1;
bool shouldPrintSteps = true;
bool shouldPrintTime = true;
bool shouldPrintPath = true;
bool shouldPrintHistogram = false;

long startTime;

Point[]? points = null;
Path[] population;

double minPathPrev;
int itersMinPathPrev;
bool shouldTweakGeneration;

int N;

var input = Console.ReadLine() ?? ""; //rnd.Next(1, 101).ToString();//"uk12";//"custom";//Console.ReadLine() ?? "";

for (int i = 0; i < maxTries; i++)
{
    if (int.TryParse(input, out N))
    {
        GeneratePoints();
    }
    else
    {
        ReadPoints(input);
    }

    CalculateDistances();
    GeneratePopulation();

    startTime = Stopwatch.GetTimestamp();

    minPathPrev = double.MaxValue;
    itersMinPathPrev = 0;
    shouldTweakGeneration = false;

    FindSolution();

    PrintElapsedTime(shouldPrintTime);
    PrintSolution(shouldPrintPath);
    Halt();
}

if (shouldPrintHistogram)
{
    foreach (var key in occurs.Keys)
    {
        Console.WriteLine($"{key} -> {occurs[key]}");
    }
}

return 0;

void FindSolution()
{
    var generation = 0;

    var checkpointsEnumerator = Enumerable.Range(0, checkpointsCount + 1).Select(x => x * maxGenerations / checkpointsCount).GetEnumerator();
    checkpointsEnumerator.MoveNext();

    while (generation <= maxGenerations)
    {
        if (shouldPrintSteps && checkpointsEnumerator.Current == generation)
        {
            Console.WriteLine($"Iteration {checkpointsEnumerator.Current}:");
            PrintSolution();
            checkpointsEnumerator.MoveNext();
        }

        if (shouldSelfCorrect)
        {
            var avgFitness = population.Min(x => x.CalculateFitness());
            if (minPathPrev > avgFitness)
            {
                minPathPrev = avgFitness;
                itersMinPathPrev = 0;
            }
            else if (minPathPrev == avgFitness)
            {
                itersMinPathPrev++;

                if (itersMinPathPrev >= toleranceLevel)
                {
                    itersMinPathPrev = 0;
                    shouldTweakGeneration = true;
                }
            }
        }

        GenerateNextPopulation();

        generation++;
    }
}

void GeneratePoints()
{
    points = new Point[N];
    for (int i = 0; i < N; i++)
    {
        points[i] = new Point(rnd.NextDouble() * rnd.Next((int)1e3), rnd.NextDouble() * rnd.Next((int)1e3), i);
        Cache.Names[i] = $"Point({i})";
    }
}

void ReadPoints(string setName)
{
    var coords = File.ReadAllText($"{setName.ToLower()}_xy.csv")
        .Split(new char[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)
        .Select(x => x.Split(',').Select(double.Parse).ToList())
        .ToList();

    var names = File.ReadAllText($"{setName.ToLower()}_name.csv")
        .Split(new char[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)
        .ToList();

    N = coords.Count;

    points = new Point[N];
    for (int i = 0; i < N; i++)
    {
        points[i] = new Point(coords[i][0], coords[i][1], i);
        Cache.Names[i] = names[i];
    }
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

void GenerateNextPopulation()
{
    var newPopulation = new List<Path>();

    var eliteToTake = eliteCount;
    var newGens = 0;

    var populationCopy = population.Clone() as Path[];

    var newPopSize = populationSize;
    if (shouldSelfCorrect)
    {
        if (shouldTweakGeneration)
        {
            shouldTweakGeneration = false;
            newGens = eliteCount; //eliteCount * 2; //populationSize / 2;
            //newPopSize *= 2;
            //mutationProbability += 0.05;
        }

        if ((newGens + eliteCount) % 2 == 1)
        {
            eliteCount++;
        }
    }

    var sorted = population.OrderBy(x => x.CalculateFitness()).ToArray();

    newPopulation.AddRange(sorted.Take(eliteCount));

    var crossToGenerate = (newPopSize - eliteCount - newGens) / 2;
    for (int i = 0; i < crossToGenerate; i++)
    {
        // Tournament selection
        var tournament = new List<Path>();
        for (int j = 0; j < tournamentSize; j++)
        {
            var rndInd = rnd.Next(0, populationSize);
            tournament.Add(population[rndInd]);
        }
        tournament = tournament.OrderBy(x => x.CalculateFitness()).ToList();
        var cross = CrossPaths(tournament[0], tournament[1]);

        // Random selection
        //var rnd1 = rnd.Next(0, populationSize);
        //var rnd2 = rnd.Next(0, populationSize);
        //var cross = CrossPaths(populationCopy![rnd1], populationCopy![rnd2]);

        // Common logic
        cross.First.Mutate(rnd, mutationProbability);
        cross.Second.Mutate(rnd, mutationProbability);
        newPopulation.Add(cross.First);
        newPopulation.Add(cross.Second);
    }

    for (int i = 0; i < newGens; i++)
    {
        rnd.Shuffle(points!);
        newPopulation.Add(new Path(points!.ToList()));
    }

    populationSize = newPopSize;

    population = newPopulation.ToArray();


    // Keep the best half and mutate it
    //population = population
    //    .OrderBy(x => x.CalculateFitness())
    //    .Take(populationSize / 2)
    //    .Chunk(2)
    //    .SelectMany(x =>
    //{
    //    if (x.Length == 1)
    //    {
    //        return x;
    //    }
    //
    //    var paths = CrossPaths(x[0], x[1]);
    //    paths.First.Mutate(rnd);
    //    paths.Second.Mutate(rnd);
    //    return [paths.First, paths.Second, x[0], x[1]];
    //}).ToArray();
}

(Path First, Path Second) CrossPaths(Path first, Path second)
{
    var cut = rnd.Next(0, N);
    var newFirst = new List<Point>(first.Points.Take(cut));
    var newSecond = new List<Point>(second.Points.Take(cut));

    AddOthers(second, newFirst, cut);
    AddOthers(first, newSecond, cut);

    return (new Path(newFirst), new Path(newSecond));
}

void AddOthers(Path old, List<Point> toAddTo, int cut)
{
    var pointsFromSecond = old.Points.Skip(cut).ToList();
    pointsFromSecond.AddRange(old.Points.Take(cut));
    pointsFromSecond = pointsFromSecond.Where(x => !toAddTo.Contains(x)).ToList();
    toAddTo.AddRange(pointsFromSecond);
}

void GeneratePopulation()
{
    population = new Path[populationSize];
    for (int i = 0; i < populationSize; i++)
    {
        rnd.Shuffle(points!);
        population[i] = new Path(points!.ToList());
    }
}

void CalculateDistances()
{
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j <= i; j++)
        {
            var dist = points![i].DistanceTo(points[j]);
            Cache.Distances[(points[i].Id, points[j].Id)] = dist;
            Cache.Distances[(points[j].Id, points[i].Id)] = dist;
        }
    }
}

void PrintSolution(bool printPath = false)
{
    if (!isNativeMode || args.Contains("-print"))
    {
        var bestMatch = population.OrderBy(x => x.CalculateFitness()).First();
        var result = Math.Round(bestMatch.CalculateFitness(), 2);
        Console.WriteLine(result);
        if (!occurs.ContainsKey(result))
        {
            occurs[result] = 0;
        }
        occurs[result]++;

        if (printPath)
        {
            var points = bestMatch.Points.Select(x => Cache.Names[x.Id]);
            Console.WriteLine(string.Join(" -> ", points));
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
 class Point(double x, double y, int id)
{
    public double X = x;
    public double Y = y;

    public int Id = id;

    Dictionary<int, double> DistanceToPoint = new Dictionary<int, double>();

    public double DistanceTo(Point p)
    {
        if (!DistanceToPoint.ContainsKey(p.Id))
        {
            DistanceToPoint[p.Id] = Math.Sqrt((Y - p.Y) * (Y - p.Y) + (X - p.X) * (X - p.X));
            p.DistanceToPoint[this.Id] = DistanceToPoint[p.Id];
        }

        return DistanceToPoint[p.Id];
    }

    public void Print()
    {
        Console.Write($"({X},{Y}) ");
    }
}


class Path(List<Point> points)
{
    public Path(Path old) : this(old.Points) { }
    public List<Point> Points = new List<Point>(points);

    public void Mutate(Random rnd, double mutationProbability)
    {
        if (rnd.NextDouble() > mutationProbability) return;

        fitness = 0;

        var randGene1 = rnd.Next(0, points.Count);
        var randGene2 = rnd.Next(0, points.Count);

        //Swap mutation
        //var temp = Points[randGene1];
        //Points[randGene1] = Points[randGene2];
        //Points[randGene2] = temp;

        //Reverse rotation
        var minGene = Math.Min(randGene1, randGene2);
        var maxGene = Math.Max(randGene1, randGene2);
        for (int i = 0; i < (maxGene - minGene) / 2; i++)
        {
            var temp = Points[minGene + i];
            Points[minGene + i] = Points[maxGene - i];
            Points[maxGene - i] = temp;
        }
    }

    private double fitness = 0;
    public double CalculateFitness()
    {
        if (fitness == 0)
        {
            double cost = 0;
            for (int i = 0; i < Points.Count - 1; i++)
            {
                cost += Cache.Distances[(Points[i].Id, Points[i + 1].Id)];
            }

            fitness = cost;
        }

        return fitness;
    }
}

public static class Cache
{
    public static Dictionary<(int id1, int id2), double> Distances = new Dictionary<(int id1, int id2), double>();
    public static Dictionary<int, string> Names = new Dictionary<int, string>();
}
