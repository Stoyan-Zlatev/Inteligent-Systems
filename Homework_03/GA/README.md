# Genetic Algorithm for the Knapsack Problem

This project implements a **genetic algorithm** to solve optimization problems, demonstrated here using the **knapsack problem**. A genetic algorithm (GA) is a search heuristic inspired by the principles of natural selection, designed to find an optimal or near-optimal solution. This implementation aims to maximize the value of items in a knapsack without exceeding a specified weight limit.

### Problem Description: The Knapsack Problem

In the knapsack problem, given a list of items with specific **weights** and **values**, the goal is to select a subset of these items to maximize the total value without exceeding a specified weight limit. The GA iteratively evolves possible solutions (item combinations) to find the highest achievable value within the weight constraint.

### Example Items

Two lists of items are defined in `main.py` — `things` and `more_things` — with each item having a `name`, `value`, and `weight`. The algorithm aims to select items within a 3,000-gram weight limit, maximizing their combined value.

#### Example Item List in `main.py`

```python
things = [
    Thing('Laptop', 500, 2200),
    Thing('Headphones', 150, 160),
    Thing('Coffee Mug', 60, 350),
    Thing('Notepad', 40, 333),
    Thing('Water Bottle', 30, 192),
]
```

The `more_things` list adds additional items to provide a more diverse set for the GA to optimize.

### Genetic Algorithm Components
1. `Genome Representation`: A genome is a list of binary values (`0` or `1`), each representing the presence or absence of an item in the knapsack.
2. `Fitness Function`: Calculates the total value of items in a genome. If the weight exceeds the limit, the fitness value is set to `0`.
3. `Selection`: Selects pairs of genomes from the population based on their fitness values.
4. `Crossover`: Performs a single-point crossover between two genomes to create offspring.
5. `Mutation`: Randomly flips bits in a genome based on a given mutation probability

### Running the algorithm 
The main function `run_evolution` orchestrates the GA process over multiple generations, aiming to maximize the knapsack value within the weight limit.

### Parameters
- `Population Size`: Number of genomes (solutions) in each generation.
- `Fitness Limit`: Desired fitness threshold to terminate the algorithm.
- `Generation Limit`: Maximum number of generations to run.

### Example Execution
In `main.py`, the `run_evolution` function is configured as follows:
```python
population, generations = run_evolution(
    populate_func=partial(generate_population, size=10, genome_length=len(more_things)),
    fitness_func=partial(fitness, things=more_things, weight_limit=3000),
    fitness_limit=740,
    generation_limit=100
)
```

This setup aims to find the best combination of items in `more_things` within a 3,000-gram weight limit, targeting a fitness value of 740 or more.

## Sample Output
After running the algorithm, the best solution and the number of generations taken to reach it are printed:
```python
print(f"Number of generations: {generations}")
print(f"Best solution: {genome_to_things(population[0], more_things)}")
```

Examplpe output
```plaintext
Number of generations: 57
Best solution: ['Laptop', 'Headphones', 'Water Bottle']
```

## Customization

To adapt this algorithm to different instances of the knapsack problem or to experiment with different settings, you can adjust the following parameters:

- **Items**: Modify the lists `things` or `more_things` by adding or removing `Thing` objects, each defined by a `name`, `value`, and `weight`.
- **Weight Limit**: Change the `weight_limit` parameter in the `fitness_func` to experiment with different knapsack capacities.
- **Population Size**: Increase or decrease the population size in `generate_population` to impact the diversity of solutions.
- **Fitness Limit**: Set a different `fitness_limit` to change the target value for terminating the algorithm early.
- **Mutation Probability**: Adjust the probability of mutation in the `mutation` function to explore the effect of randomness on solution variety.
- **Generation Limit**: Modify `generation_limit` in `run_evolution` to control the maximum number of generations before stopping.

By experimenting with these parameters, you can tailor the GA for different types of optimization problems or improve solution accuracy and convergence speed for the knapsack problem.