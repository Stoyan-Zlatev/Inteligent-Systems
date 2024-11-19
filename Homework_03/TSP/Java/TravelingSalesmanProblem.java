import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.stream.IntStream;
import java.util.stream.Stream;

record City(int index, String name, double x, double y) { }

class Genome {
    private List<Integer> route;
    private double distance;
    private double fitness;

    public Genome(List<City> cities) {
        route = new ArrayList<>(IntStream.range(0, cities.size())
                .boxed()
                .toList());
        Collections.shuffle(route);
        distance = calculateDistance(cities);
        fitness = calculateFitness();
    }

    public Genome(List<City> cities, List<Integer> route) {
        this.route = route;
        distance = calculateDistance(cities);
        fitness = calculateFitness();
    }

    private double calculateDistance(City city1, City city2) {
        return Math.sqrt(Math.pow(city1.x() - city2.x(), 2) + Math.pow(city1.y() - city2.y(), 2));
    }

    private double calculateDistance(List<City> cities) {
        double totalDistance = 0.0;
        for (int i = 0; i < cities.size() - 1; i++) {
            totalDistance += calculateDistance(cities.get(route.get(i)), cities.get(route.get(i + 1)));
        }
        return totalDistance;
    }

    private double calculateFitness() {
        return 1 / (distance + 1);
    }

    public List<Integer> getRoute() {
        return route;
    }
    public double getDistance() {
        return distance;
    }
    public double getFitness() {
        return fitness;
    }
}

public class TravelingSalesmanProblem {
    private List<City> cities;
    private int sizeOfPopulation;
    private List<Genome> population;
    private int generations;
    private double mutationProbability;

    public TravelingSalesmanProblem(List<City> cities, int sizeOfPopulation, int generations,
                                    double mutationProbability) {
        this.cities = cities;
        this.sizeOfPopulation = sizeOfPopulation;
        this.generations = generations;
        this.mutationProbability = mutationProbability;
        population = new ArrayList<>(Stream.generate( () -> new Genome(cities) )
                .limit(sizeOfPopulation)
                .toList());
        population.sort(Comparator.comparingDouble(Genome::getFitness).reversed());
    }

    private static <T> T getRandomElement(List<T> list) {
        Random rand = new Random();
        return list.get(rand.nextInt(list.size()));
    }

    private Genome tournamentSelection(int sampleSize) {
        Queue<Genome> chosenGenomes = new PriorityQueue<>(Comparator.comparingDouble(Genome::getFitness).reversed());
        for (int i = 0; i < sampleSize; i++) {
            chosenGenomes.add(getRandomElement(population));
        }
        return chosenGenomes.peek();
    }

    private List<Genome> onePointCrossover(Genome parent1, Genome parent2) {
        int cuttingIndex = getRandomElement(parent1.getRoute());
        List<Integer> child1Route = new ArrayList<>(parent1.getRoute().stream()
                .limit(cuttingIndex)
                .toList());
        for (Integer gene: parent2.getRoute()) {
            if (!child1Route.contains(gene)) {
                child1Route.add(gene);
            }
            if (child1Route.size() == parent1.getRoute().size()) {
                break;
            }
        }

        List<Integer> child2Route = new ArrayList<>(parent2.getRoute().stream()
                .limit(cuttingIndex)
                .toList());
        for (Integer gene: parent1.getRoute()) {
            if (!child2Route.contains(gene)) {
                child2Route.add(gene);
            }
            if (child2Route.size() == parent2.getRoute().size()) {
                break;
            }
        }

        List<Genome> children = new ArrayList<>(2);
        children.add(new Genome(cities, child1Route));
        children.add(new Genome(cities, child2Route));

        return children;
    }

    private Genome mutate(Genome genome) {
        Random rand = new Random();
        if (rand.nextDouble() < mutationProbability) {
            int i = getRandomElement(genome.getRoute());
            int j = getRandomElement(genome.getRoute());
            if (i > j) {
                int temp = i;
                i = j;
                j = temp;
            }
            while (i < j) {
                Collections.swap(genome.getRoute(), i, j);
                i++;
                j--;
            }
        }

        return new Genome(cities, genome.getRoute());
    }

    private void evolvePopulationWithElitism(int sizeOfElites) {
        Queue<Genome> newPopulation = new PriorityQueue<>(Comparator.comparingDouble(Genome::getFitness).reversed());
        for (int i = 0; i < sizeOfElites; i++) {
            newPopulation.add(population.get(i));
        }

        while (newPopulation.size() < sizeOfPopulation) {
            Genome parent1 = tournamentSelection(3);
            Genome parent2 = tournamentSelection(3);

            List<Genome> children = onePointCrossover(parent1, parent2);
            children.set(0, mutate(children.get(0)));
            children.set(1, mutate(children.get(1)));

            newPopulation.addAll(children);
        }

        population = newPopulation.stream().toList();
    }

    public Genome runAndLogEvolution() {
        for (int i = 0; i < generations; i++) {
            evolvePopulationWithElitism(2);

            if (i % 10 == 0) {
                System.out.println(population.getFirst().getDistance());
            }
        }
        System.out.println(population.getFirst().getDistance());
        System.out.println();

        return population.getFirst();
    }

    public static void loadFiles(List<City> cities, Path fileNames, Path fileCoordinates) {
        if (fileNames == null || fileCoordinates == null) {
            throw new IllegalArgumentException("File paths cannot be null");
        }

        try (BufferedReader bufferedReaderNames = Files.newBufferedReader(fileNames);
             BufferedReader bufferedReaderCoordinates = Files.newBufferedReader(fileCoordinates)) {
            String name;
            String coordinates;
            int index = 0;
            while ((name = bufferedReaderNames.readLine()) != null
                && (coordinates = bufferedReaderCoordinates.readLine()) != null) {
                String[] coords = coordinates.split(",");
                cities.add(new City(index, name, Double.parseDouble(coords[0]), Double.parseDouble(coords[1])));
                index++;
            }

        } catch (IOException e) {
            throw new IllegalStateException("A problem occurred while reading from a file", e);
        }
    }

    public static void generateRandomCities(List<City> cities, int countOfCities) {
        for (int i = 0; i < countOfCities; i++) {
            Random rand = new Random();
            double x = rand.nextDouble(100);
            double y = rand.nextDouble(100);
            cities.add(new City(i, "City" + (i + 1), x, y));
        }
    }

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        String input = in.nextLine();

        long startTime = System.currentTimeMillis();

        List<City> cities = new ArrayList<>();
        if (input.equals("UK12")) {
            loadFiles(cities, Path.of("resource/uk12_name.csv"),
                    Path.of("resource/uk12_xy.csv"));
        } else {
            int countOfCities;
            try {
                countOfCities = Integer.parseInt(input);
            } catch (NumberFormatException e) {
                System.out.println("Invalid input");
                return;
            }
            if (countOfCities > 100) {
                System.out.println("Count of cities cannot be more than 100");
                return;
            }

            generateRandomCities(cities, countOfCities);
        }

        TravelingSalesmanProblem tsp = new TravelingSalesmanProblem(cities,
                350, 2500, 0.5);

        Genome bestGenome = tsp.runAndLogEvolution();

        List<String> path = new ArrayList<>();
        for (int i = 0; i < cities.size(); i++) {
            City currentCity = cities.get(bestGenome.getRoute().get(i));
            if (input.equals("UK12")) {
                path.add(currentCity.name());
            } else {
                path.add("(" + currentCity.x() + ", " + currentCity.y() + ")");
            }
        }
        System.out.println(String.join(" -> ", path));
        System.out.println(bestGenome.getDistance());

        double endTime = System.currentTimeMillis();
        double elapsedTime = (endTime - startTime) / 1000.0;
        System.out.println(String.format("%.2f", elapsedTime));
    }

}
