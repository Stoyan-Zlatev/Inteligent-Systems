import time
from collections import namedtuple
import random
from typing import List, Tuple, Optional
import csv
import matplotlib.pyplot as plt
import math

# Define City namedtuple
City = namedtuple('City', 'index name x y')


def load_data(file_names: str, file_positions: str) -> List[City]:
    """
    Load city names and positions from CSV files and create City objects.

    Args:
        file_names (str): Path to the CSV file containing city names.
        file_positions (str): Path to the CSV file containing city positions (x, y coordinates).

    Returns:
        List[City]: A list of City objects with attributes (index, name, x, y).
    """
    cities = []
    with open(file_positions, newline='') as f1, open(file_names, newline='') as f2:
        names = csv.reader(f2)
        positions = csv.reader(f1)
        for index, (name, position) in enumerate(zip(names, positions)):
            cities.append(City(index=index, name=name[0], x=float(position[0]), y=float(position[1])))
    return cities


def calculate_distance(city1: City, city2: City) -> float:
    """
    Calculate the Euclidean distance between two cities.

    Args:
        city1 (City): The first city.
        city2 (City): The second city.

    Returns:
        float: The Euclidean distance between the two cities.
    """
    return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)


def visualize_map(cities: List[City], best_route: Optional[List[int]] = None) -> None:
    """
    Visualize cities and, optionally, the best route on a 2D plot.

    Args:
        cities (List[City]): The list of cities to visualize.
        best_route (Optional[List[int]]): An optional list of city indices representing the order of the best route.
                                          If provided, the function connects cities in the specified order.
    """
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    # Plot the cities with dots
    for city in cities:
        ax.plot(city.x, city.y, 'bo')
        ax.text(city.x, city.y, city.name, fontsize=9, ha='right', color='darkred')

    if best_route:
        # Plot the best route by connecting the dots
        for i in range(len(best_route) - 1):
            city1 = cities[best_route[i]]
            city2 = cities[best_route[i + 1]]
            ax.plot([city1.x, city2.x], [city1.y, city2.y], 'r-', lw=2)  # Red lines to connect cities

        # # Connect the last city back to the first city to complete the cycle
        # city1 = cities[best_route[-1]]
        # city2 = cities[best_route[0]]
        # ax.plot([city1.x, city2.x], [city1.y, city2.y], 'r-', lw=2)  # Closing the loop with a red line

        plt.title("Best Route Visualization")
    else:
        plt.title("City Map")
    plt.show()


class Genome:
    """
    Represents a single Genome (solution) in the TSP problem.

    Attributes:
        route (List[int]): A list representing the order of cities in the route.
        fitness (float): The fitness of the genome, calculated as the inverse of the total route distance.

    Methods:
        calculate_fitness(cities): Calculate the fitness score as the inverse of the total route distance.
    """

    def __init__(self, cities: List[City]):
        """
        Initialize a Genome with a randomly shuffled route and calculate its fitness.

        Args:
            cities (List[City]): List of cities in the TSP problem.
        """
        self.route = list(range(len(cities)))
        random.shuffle(self.route)
        self.distance = self.calculate_distance(cities)
        self.fitness = self.calculate_fitness()

    def calculate_distance(self, cities: List[City]) -> float:
        """
        Calculate the  total route distance.

        Args:
            cities (List[City]): The list of cities to calculate the route distance for.

        Returns:
            float: The total distance.
        """
        distance = sum(calculate_distance(cities[self.route[i]], cities[self.route[i + 1]])
                       for i in range(len(self.route) - 1))
        return distance

    def calculate_fitness(self) -> float:
        """
        Calculate the fitness score based on the total route distance.

        Returns:
            float: The fitness score (inverse of total distance).
        """
        return 1 / (self.distance + 1)  # Adding 1 to avoid division by zero


class GeneticAlgorithm:
    """
    Manages the genetic algorithm process for solving the TSP problem, including initializing and evolving a population
    of potential solutions (genomes) through selection, crossover, and mutation.

    Attributes:
        cities (List[City]): List of cities to optimize the route for.
        population_size (int): Number of genomes in the population.
        generations (int): Number of generations to evolve.
        population (List[Genome]): Current population of genomes (candidate solutions).
        mutation_probability (float): Probability of mutation per genome per generation.
        best_fitness_history (List[float]): Record of the best fitness value found in each generation.

    Methods:
        initialize_population(): Initialize a population of random genomes.
        selection_pair(): Select two genomes for crossover, weighted by fitness.
        single_point_crossover(): Perform crossover between two genomes to create offspring.
        mutate(): Apply mutation by swapping two cities in a genome's route.
        evolve_population(): Evolve the population by selection, crossover, and mutation.
        run_evolution(): Run the genetic algorithm for a specified number of generations or until convergence.
    """

    def __init__(self, cities: List[City], population_size: int, generations: int, mutation_probability: float):
        """
        Initialize the genetic algorithm with the required parameters and a population of genomes.

        Args:
            cities (List[City]): The list of cities for the TSP problem.
            population_size (int): Number of genomes in the population.
            generations (int): Maximum number of generations to run the algorithm.
            mutation_probability (float): Probability of mutation for each genome.
        """
        self.cities = cities
        self.population_size = population_size
        self.generations = generations
        self.population = self.initialize_population(self.cities, self.population_size)
        self.mutation_probability = mutation_probability
        self.best_fitness_history = []

    def initialize_population(self, cities: List[City], population_size: int) -> List[Genome]:
        """
        Initialize a population of genomes for the genetic algorithm.

        Args:
            cities (List[City]): List of cities for the TSP problem.
            population_size (int): Number of genomes to create in the population.

        Returns:
            List[Genome]: A list of randomly generated genomes.
        """
        return [Genome(cities) for _ in range(population_size)]

    def tournament_selection(self, k: int = 3) -> Genome:
        """
        Select a single genome using tournament selection.

        Args:
            k (int): Number of genomes to sample from the population for each tournament.

        Returns:
            Genome: The genome with the highest fitness among the selected sample.
        """
        selected = random.sample(self.population, k)
        return max(selected, key=lambda genome: genome.fitness)

    def selection_pair_tournament(self) -> Tuple[Genome, Genome]:
        """
        Select a pair of genomes for crossover using tournament selection.

        Returns:
            Tuple[Genome, Genome]: A pair of genomes chosen based on their fitness.
        """
        return self.tournament_selection(), self.tournament_selection()

    def single_point_crossover(self, parent1: Genome, parent2: Genome) -> Tuple[Genome, Genome]:
        """
        Perform single-point crossover on two parent genomes to produce two offspring.

        Args:
            parent1 (Genome): The first parent genome.
            parent2 (Genome): The second parent genome.

        Returns:
            Tuple[Genome, Genome]: Two offspring genomes created by crossover of the parents.
        """
        cut = random.randint(1, len(parent1.route) - 2)
        child1_route = parent1.route[:cut] + [gene for gene in parent2.route if gene not in parent1.route[:cut]]
        child2_route = parent2.route[:cut] + [gene for gene in parent1.route if gene not in parent2.route[:cut]]
        child1 = Genome(self.cities)
        child2 = Genome(self.cities)
        child1.route = child1_route
        child2.route = child2_route
        child1.distance = child1.calculate_distance(self.cities)
        child2.distance = child2.calculate_distance(self.cities)
        child1.fitness = child1.calculate_fitness()
        child2.fitness = child2.calculate_fitness()
        return child1, child2

    def mutate(self, genome: Genome) -> None:
        """
        Mutate a genome by swapping two random cities in the route, with a set probability.

        Args:
            genome (Genome): The genome to mutate, representing a potential TSP route.
        """
        if random.random() < self.mutation_probability:
            i, j = random.sample(range(len(genome.route)), 2)
            genome.route[i], genome.route[j] = genome.route[j], genome.route[i]
            genome.distance = genome.calculate_distance(self.cities)
            genome.fitness = genome.calculate_fitness()

    def evolve_population_with_elitism(self, elite_size: int = 2) -> None:
        """
        Create a new population by retaining top genomes (elitism) and using
        tournament selection, crossover, and mutation to fill the population.

        Args:
           elite_size (int): Number of top genomes to retain in the new generation.

        Modifies:
           self.population: Updates the population with the new generation of genomes.
           self.best_fitness_history: Appends the best fitness value of the new generation.
        """
        new_population = sorted(self.population, key=lambda genome: genome.fitness, reverse=True)[:elite_size]
        while len(new_population) < self.population_size:
            parent1, parent2 = self.selection_pair_tournament()
            child1, child2 = self.single_point_crossover(parent1, parent2)
            self.mutate(child1)
            self.mutate(child2)
            new_population.extend([child1, child2])
        self.population = sorted(new_population, key=lambda genome: genome.fitness, reverse=True)
        self.best_fitness_history.append(self.population[0].fitness)

    def run_evolution(self, fitness_threshold: float = 1e-8, patience: int = 25) -> Genome:
        """
        Run the genetic algorithm with a derivative-based stopping condition.

        Args:
            fitness_threshold (float): Minimum average change in fitness over recent generations to continue running.
            patience (int): Number of generations with no change of fitness before stopping
        Returns:
            Genome: The best genome found in the population after evolution.
        """
        # List to store the recent fitness improvements for calculating moving average
        fitness_improvements = []

        for generation in range(self.generations):
            self.evolve_population_with_elitism()

            # Track fitness change from the last generation
            if generation > 0:
                fitness_change = abs(self.best_fitness_history[-1] - self.best_fitness_history[-2])
                fitness_improvements.append(fitness_change)

                # Only keep the last `patience` entries
                if len(fitness_improvements) > patience:
                    fitness_improvements.pop(0)

                # Calculate the average fitness change over the recent `patience` generations
                avg_fitness_change = sum(fitness_improvements) / len(fitness_improvements)

                # Check if the recent improvements are too small, implying convergence
                if avg_fitness_change < fitness_threshold and len(fitness_improvements) == patience:
                    print(
                        f"Stopping early at generation {generation} due to minimal improvement over {patience} generations.")
                    break

            # Optional: Logging for monitoring progress
            if generation % 10 == 0:
                print(f"Generation {generation}: Best fitness = {self.best_fitness_history[-1]}, "
                      f"Avg fitness change = {avg_fitness_change if generation > 1 else 'N/A'}")

        return self.population[
            0]  # Return the best genome found of generations to tolerate small improvements before stopping.

def generate_random_cities(N: int, x_range: Tuple[int, int] = (0, 100), y_range: Tuple[int, int] = (0, 100)) -> List[
    City]:
    """
    Generate a list of cities with random coordinates.

    Args:
        N (int): Number of cities to generate.
        x_range (Tuple[int, int]): Range for x-coordinate values (default is (0, 100)).
        y_range (Tuple[int, int]): Range for y-coordinate values (default is (0, 100)).

    Returns:
        List[City]: A list of City objects with random coordinates.
    """
    cities = []
    for i in range(N):
        name = f"City {i + 1}"
        x = random.uniform(*x_range)
        y = random.uniform(*y_range)
        cities.append(City(index=i, name=name, x=x, y=y))
    return cities

def main():
    """
    Main function to execute the TSP genetic algorithm.

    Loads city data, initializes and runs the genetic algorithm, and visualizes the best route found.
    """
    data = input("Enter 'UK12' or N: ")
    start = time.time()
    if data == 'UK12':
        cities = load_data("../TestData/uk12_name.csv", "../TestData/uk12_xy.csv")
    else:
        cities = generate_random_cities(int(data))
    # visualize_map(cities)
    ga = GeneticAlgorithm(cities, population_size=500, generations=1500, mutation_probability=0.2)
    best_genome = ga.run_evolution()

    # Output the best route found
    best_route = [cities[i].name for i in best_genome.route]
    print("Best route found:", best_route)
    print("Best fitness:", best_genome.distance)
    print('%s s' % (time.time() - start))
    visualize_map(cities, best_genome.route)


if __name__ == '__main__':
    main()
