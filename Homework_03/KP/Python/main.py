import random
from typing import List, Tuple
from collections import namedtuple
import time

# Define the Item class
Item = namedtuple('Item', ['index', 'weight', 'value'])

class Genome:
    def __init__(self, items: List[Item], max_weight: int, chromosome: List[int] = None):
        self.items = items
        self.max_weight = max_weight
        self.chromosome = chromosome if chromosome else self.generate_feasible_chromosome()
        self.fitness = self.calculate_fitness()

    def generate_feasible_chromosome(self) -> List[int]:
        # Generate a feasible chromosome by adding items randomly until max_weight is reached
        chromosome = [0] * len(self.items)
        indices = list(range(len(self.items)))
        random.shuffle(indices)
        total_weight = 0
        for i in indices:
            if total_weight + self.items[i].weight <= self.max_weight:
                chromosome[i] = 1
                total_weight += self.items[i].weight
        return chromosome

    def calculate_fitness(self) -> float:
        total_weight = sum(item.weight for item, gene in zip(self.items, self.chromosome) if gene)
        total_value = sum(item.value for item, gene in zip(self.items, self.chromosome) if gene)
        # Penalize overweight solutions by reducing fitness proportionally to excess weight
        if total_weight > self.max_weight:
            return 0
        else:
            return total_value

class GeneticAlgorithm:
    def __init__(self, items: List[Item], max_weight: int, population_size: int, generations: int, mutation_probability: float):
        self.items = items
        self.max_weight = max_weight
        self.population_size = population_size
        self.generations = generations
        self.mutation_probability = mutation_probability
        self.population = self.initialize_population()
        self.best_fitness_history = []

    def initialize_population(self) -> List[Genome]:
        # Initialize the population with feasible chromosomes
        return [Genome(self.items, self.max_weight) for _ in range(self.population_size)]

    def tournament_selection(self, k: int = 3) -> Genome:
        # Select a genome using tournament selection
        selected = random.sample(self.population, k)
        return max(selected, key=lambda genome: genome.fitness)

    def two_point_crossover(self, parent1: Genome, parent2: Genome) -> Tuple[Genome, Genome]:
        # Perform two-point crossover
        length = len(parent1.chromosome)
        if length < 2:
            return parent1, parent2

        point1 = random.randint(1, length - 2)
        point2 = random.randint(point1 + 1, length - 1)

        child1_chromosome = (
            parent1.chromosome[:point1] + parent2.chromosome[point1:point2] + parent1.chromosome[point2:]
        )
        child2_chromosome = (
            parent2.chromosome[:point1] + parent1.chromosome[point1:point2] + parent2.chromosome[point2:]
        )

        child1 = Genome(self.items, self.max_weight, chromosome=child1_chromosome)
        child2 = Genome(self.items, self.max_weight, chromosome=child2_chromosome)
        return child1, child2

    def mutate(self, genome: Genome) -> None:
        # Mutate the genome by flipping bits with a set probability, enforcing feasibility
        for i in range(len(genome.chromosome)):
            if random.random() < self.mutation_probability:
                # Attempt to flip the bit
                if genome.chromosome[i] == 0:
                    # Turn on the item if feasible
                    if self.calculate_weight(genome.chromosome) + self.items[i].weight <= self.max_weight:
                        genome.chromosome[i] = 1
                else:
                    # Turn off the item
                    genome.chromosome[i] = 0
        genome.fitness = genome.calculate_fitness()

    def calculate_weight(self, chromosome: List[int]) -> int:
        # Calculate the total weight of a chromosome
        return sum(item.weight for item, gene in zip(self.items, chromosome) if gene)

    def evolve_population_with_elitism(self, elite_size: int = 2) -> None:
        # Create a new population by retaining elites and using selection, crossover, and mutation
        new_population = sorted(self.population, key=lambda genome: genome.fitness, reverse=True)[:elite_size]
        while len(new_population) < self.population_size:
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child1, child2 = self.two_point_crossover(parent1, parent2)
            self.mutate(child1)
            self.mutate(child2)
            new_population.extend([child1, child2])
        self.population = sorted(new_population, key=lambda genome: genome.fitness, reverse=True)[:self.population_size]
        self.best_fitness_history.append(self.population[0].fitness)

    def run_evolution(self, fitness_threshold: float = 1e-6, patience: int = 25) -> Genome:
        # Run the genetic algorithm with stopping condition based on fitness improvement
        fitness_improvements = []
        avg_fitness_change = None

        for generation in range(self.generations):
            self.evolve_population_with_elitism()

            if generation > 0:
                fitness_change = abs(self.best_fitness_history[-1] - self.best_fitness_history[-2])
                fitness_improvements.append(fitness_change)

                if len(fitness_improvements) > patience:
                    fitness_improvements.pop(0)

                avg_fitness_change = sum(fitness_improvements) / len(fitness_improvements)

                if avg_fitness_change < fitness_threshold and len(fitness_improvements) == patience:
                    print(f"Stopping early at generation {generation} due to minimal improvement.")
                    break

            if generation % 10 == 0:
                avg_fitness_change_str = f"{avg_fitness_change:.6f}" if avg_fitness_change else "N/A"
                print(f"Generation {generation}: Best fitness = {self.best_fitness_history[-1]}, Avg fitness change = {avg_fitness_change_str}")

        # Ensure the best genome found is feasible
        feasible_population = [genome for genome in self.population if self.calculate_weight(genome.chromosome) <= self.max_weight]
        return max(feasible_population, key=lambda genome: genome.fitness) if feasible_population else self.population[0]

def load_items(filename: str) -> Tuple[int, List[Item]]:
    # Load items from a file
    with open(filename, 'r') as file:
        lines = file.readlines()
    max_weight, num_items = map(int, lines[0].split())
    items = [Item(index=idx, weight=int(line.split()[0]), value=int(line.split()[1])) for idx, line in enumerate(lines[1:])]
    return max_weight, items

def main():
    option = input("Enter short/long: ")
    start_time = time.time()
    max_weight, items = load_items(f"../TestData/{option}_test_data")

    ga = GeneticAlgorithm(
        items=items,
        max_weight=max_weight,
        population_size=1000,
        generations=1000,
        mutation_probability=0.05
    )

    best_genome = ga.run_evolution()

    # Output the best solution found
    selected_items = [item for item, gene in zip(items, best_genome.chromosome) if gene]
    total_weight = sum(item.weight for item in selected_items)
    total_value = sum(item.value for item in selected_items)

    print(f"Total value: {total_value}")
    print(f"Total weight: {total_weight}")
    print(f"Selected items: {[item.index for item in selected_items]}")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
