#TODO needs optimization to find the optimal solution

import random
from typing import List, Tuple
from collections import namedtuple
from functools import partial

# Define data structure for items
Item = namedtuple('Item', ['weight', 'value'])

# Type definitions for better readability
Genome = List[int]
Population = List[Genome]


def load_data(filename: str) -> Tuple[int, List[Item]]:
    """Load knapsack capacity and items from an input file."""
    with open(filename, 'r') as file:
        lines = file.readlines()
    max_weight, num_items = map(int, lines[0].split())
    items = [Item(*map(int, line.split())) for line in lines[1:]]
    return max_weight, items


def generate_genome(length: int, items: List[Item], max_weight: int) -> Genome:
    """Generate a random valid genome, attempting to keep weight under max_weight."""
    genome = [0] * length
    indices = list(range(length))
    random.shuffle(indices)
    weight = 0

    for i in indices:
    #     if weight + items[i].weight <= max_weight:
        genome[i] = 1
    #         weight += items[i].weight
    return genome


def generate_population(size: int, genome_length: int, items: List[Item], max_weight: int) -> Population:
    """Generate a population of genomes."""
    return [generate_genome(genome_length, items, max_weight) for _ in range(size)]


def fitness(genome: Genome, items: List[Item], max_weight: int) -> int:
    """Calculate the fitness value of a genome."""
    weight, value = 0, 0
    for i, gene in enumerate(genome):
        if gene == 1:
            weight += items[i].weight
            value += items[i].value
            if weight > max_weight:
                return 0  # Exceeding max weight renders fitness 0
    return value


def selection_pair(population: Population, fitness_func) -> Tuple[Genome, Genome]:
    """Select two genomes from the population, weighted by their fitness."""
    weights = [fitness_func(genome) for genome in population]
    if sum(weights) == 0:  # All genomes have zero fitness
        raise ValueError("Population fitness sum is zero; reinitialization may be needed.")
    return random.choices(population, weights=weights, k=2)


def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    """Perform single-point crossover on two genomes."""
    p = random.randint(1, len(a) - 1)
    return a[:p] + b[p:], b[:p] + a[p:]


def mutation(genome: Genome, probability: float = 0.05) -> Genome:
    """Mutate a genome by flipping genes with a given probability."""
    # if random.random() > probability:
    #     return genome  # No mutation

    # Select random indices for chunk boundaries and reverse the chunk
    # start, end = sorted(random.sample(range(len(genome)), 2))
    # genome[start:end + 1] = reversed(genome[start:end + 1])
    #genome[1:-1] = reversed(genome[1:-1])

    return [gene if random.random() > probability else 1 - gene for gene in genome]

def run_evolution(
        max_weight: int,
        items: List[Item],
        population_size: int,
        generations: int,
        fitness_limit: int,
        mutation_probability: float = 0.05,
) -> None:
    """Run the genetic algorithm and print best fitness at specific generations."""
    # Initialize population
    population = generate_population(size=population_size, genome_length=len(items), items=items, max_weight=max_weight)
    fitness_func = partial(fitness, items=items, max_weight=max_weight)

    for generation in range(generations):
        # Sort population by fitness
        population = sorted(population, key=fitness_func, reverse=True)

        # Print the best fitness at required generations
        # if generation == 0 or generation == generations - 1 or generation % (generations // 10) == 0:
        #     print(f"Generation {generation}: Best fitness = {fitness_func(population[0])}")

        # Check for early stopping if fitness limit is reached
        if fitness_func(population[0]) >= fitness_limit:
            break

        # Check for valid population fitness
        if all(fitness_func(genome) == 0 for genome in population):
            # Reinitialize population if all fitness values are zero
            print("Reinitializing population due to zero fitness across all genomes.")
            population = generate_population(size=population_size, genome_length=len(items), items=items,
                                             max_weight=max_weight)

        # Next generation
        next_generation = population[:2]  # Elitism: carry over top 2 individuals

        # Generate offspring pairs from selected parents
        for _ in range((population_size - 2) // 2):
            parents = selection_pair(population, fitness_func)
            offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
            next_generation += [mutation(offspring_a, mutation_probability),
                                mutation(offspring_b, mutation_probability)]

        population = next_generation

    # Final result
    best_genome = max(population, key=fitness_func)
    print(f"Final best fitness: {fitness_func(best_genome)}")

def main():
    option = input("Enter short/long: ")
    # Load data and run the genetic algorithm
    max_weight, items = load_data(f"../TestData/{option}_test_data")

    # Run evolution with defined parameters
    run_evolution(
        max_weight=max_weight,
        items=items,
        population_size=len(items),
        generations=10000,  # Adjust generation limit as needed
        fitness_limit=1130 if option == 'short' else 5119,  # Known optimal for "test data"
        mutation_probability=0.01
    )

if __name__ == '__main__':
    main()