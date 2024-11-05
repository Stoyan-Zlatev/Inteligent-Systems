from collections import namedtuple
from functools import partial
from random import choices, randint, randrange, random
from typing import List, Tuple, Callable

# Define types for better clarity
Genome = List[int]
Population = List[Genome]
FitnessFunc = Callable[[Genome], int]
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]

# Define the data structure for items
Thing = namedtuple('Thing', ['name', 'value', 'weight'])

# Sample items available for selection
things = [
    Thing('Laptop', 500, 2200),
    Thing('Headphones', 150, 160),
    Thing('Coffee Mug', 60, 350),
    Thing('Notepad', 40, 333),
    Thing('Water Bottle', 30, 192),
]

# Additional items
more_things = [
                  Thing('Mints', 5, 25),
                  Thing('Socks', 10, 38),
                  Thing('Tissues', 15, 80),
                  Thing('Phone', 500, 200),
                  Thing('Baseball Cap', 100, 70)
              ] + things


def generate_genome(length: int) -> Genome:
    """
    Generate a random genome of a specified length.

    Args:
        length (int): Length of the genome to generate.

    Returns:
        Genome: A list of 0s and 1s representing the genome.
    """
    return choices([0, 1], k=length)


def generate_population(size: int, genome_length: int) -> Population:
    """
    Generate a population of genomes.

    Args:
        size (int): Number of genomes in the population.
        genome_length (int): Length of each genome.

    Returns:
        Population: A list of genomes representing the population.
    """
    return [generate_genome(genome_length) for _ in range(size)]


def fitness(genome: Genome, things: [Thing], weight_limit: int) -> int:
    """
    Calculate the fitness of a genome based on the total value and weight constraints.

    Args:
        genome (Genome): Genome to evaluate.
        things (List[Thing]): List of items to consider.
        weight_limit (int): Maximum allowed weight for selection.

    Returns:
        int: The fitness score based on total item value. Returns 0 if weight limit is exceeded.
    """
    if len(genome) != len(things):
        raise ValueError("Genome and Things must have the same length")

    weight, value = 0, 0
    for i, thing in enumerate(things):
        if genome[i] == 1:
            weight += thing.weight
            value += thing.value
            if weight > weight_limit:
                return 0  # Overweight genomes have 0 fitness
    return value


def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    """
    Select a pair of genomes from the population using weighted random choice.

    Args:
        population (Population): Population to select from.
        fitness_func (FitnessFunc): Function to evaluate the fitness of each genome.

    Returns:
        Population: A pair of selected genomes.
    """
    return choices(
        population=population,
        weights=[fitness_func(genome) for genome in population],
        k=2
    )


def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    """
    Perform single-point crossover on two genomes.

    Args:
        a (Genome): First parent genome.
        b (Genome): Second parent genome.

    Returns:
        Tuple[Genome, Genome]: Two offspring genomes.
    """
    if len(a) != len(b):
        raise ValueError("Genomes a and b must have the same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[:p] + b[p:], b[:p] + a[p:]


def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    """
    Mutate a genome by flipping random genes based on a probability.

    Args:
        genome (Genome): Genome to mutate.
        num (int): Number of mutations.
        probability (float): Probability of flipping each gene.

    Returns:
        Genome: Mutated genome.
    """
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome


def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100,
) -> Tuple[Population, int]:
    """
    Run the genetic algorithm to evolve a population to meet a fitness goal.

    Args:
        populate_func (PopulateFunc): Function to generate the initial population.
        fitness_func (FitnessFunc): Function to calculate genome fitness.
        fitness_limit (int): Desired fitness score to achieve.
        selection_func (SelectionFunc): Function to select genomes for mating.
        crossover_func (CrossoverFunc): Function to perform crossover on selected genomes.
        mutation_func (MutationFunc): Function to mutate offspring genomes.
        generation_limit (int): Maximum number of generations to evolve.

    Returns:
        Tuple[Population, int]: Final population and number of generations taken.
    """
    population = populate_func()

    for i in range(generation_limit):
        population = sorted(
            population,
            key=lambda genome: fitness_func(genome),
            reverse=True
        )

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2]

        for j in range(((len(population)) // 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)

    return population, i


def genome_to_things(genome: Genome, things: [Thing]) -> [str]:
    """
    Convert a genome into a list of item names based on selected genes.

    Args:
        genome (Genome): Genome to convert.
        things (List[Thing]): List of items corresponding to the genome.

    Returns:
        List[str]: Names of items selected by the genome.
    """
    return [thing.name for i, thing in enumerate(things) if genome[i] == 1]


# Run the genetic algorithm and display results
population, generations = run_evolution(
    populate_func=partial(generate_population, size=10, genome_length=len(things)),
    fitness_func=partial(fitness, things=things, weight_limit=3000),
    fitness_limit=740,
    generation_limit=100
)

print(f"Number of generations: {generations}")
print(f"Best solution: {genome_to_things(population[0], things)}")
