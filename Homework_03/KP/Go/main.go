package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

// Item represents an item with weight and value.
type Item struct {
	Index  int
	Weight int
	Value  int
}

// Genome represents a candidate solution in the Knapsack problem.
type Genome struct {
	Chromosome []int
	Fitness    float64
}

// GeneticAlgorithm manages the GA process.
type GeneticAlgorithm struct {
	Items               []Item
	MaxWeight           int
	PopulationSize      int
	Generations         int
	Population          []Genome
	MutationProbability float64
	BestFitnessHistory  []float64
}

// Initialize the population with feasible solutions.
func (ga *GeneticAlgorithm) InitializePopulation() {
	ga.Population = make([]Genome, ga.PopulationSize)
	for i := 0; i < ga.PopulationSize; i++ {
		chromosome := ga.generateFeasibleChromosome()
		genome := Genome{Chromosome: chromosome}
		genome.CalculateFitness(ga.Items, ga.MaxWeight)
		ga.Population[i] = genome
	}
}

// Calculate the fitness of a genome by summing values and checking weight.
func (g *Genome) CalculateFitness(items []Item, maxWeight int) {
	totalWeight := 0
	totalValue := 0.0
	for i, gene := range g.Chromosome {
		if gene == 1 {
			totalWeight += items[i].Weight
			totalValue += float64(items[i].Value)
		}
	}
	if totalWeight <= maxWeight {
		g.Fitness = totalValue
	} else {
		g.Fitness = 0 // Infeasible solutions have zero fitness.
	}
}

// Generate a feasible chromosome by adding items until maxWeight is reached.
func (ga *GeneticAlgorithm) generateFeasibleChromosome() []int {
	chromosome := make([]int, len(ga.Items))
	indices := rand.Perm(len(ga.Items))
	totalWeight := 0
	for _, idx := range indices {
		if totalWeight+ga.Items[idx].Weight <= ga.MaxWeight {
			chromosome[idx] = 1
			totalWeight += ga.Items[idx].Weight
		} else {
			chromosome[idx] = 0
		}
	}
	return chromosome
}

// Tournament selection for stronger selection pressure.
func (ga *GeneticAlgorithm) TournamentSelection(tournamentSize int) Genome {
	best := ga.Population[rand.Intn(ga.PopulationSize)]
	for i := 1; i < tournamentSize; i++ {
		contender := ga.Population[rand.Intn(ga.PopulationSize)]
		if contender.Fitness > best.Fitness {
			best = contender
		}
	}
	return best
}

// Two-point crossover to generate diverse offspring.
func (ga *GeneticAlgorithm) TwoPointCrossover(parent1, parent2 Genome) (Genome, Genome) {
	child1 := Genome{Chromosome: make([]int, len(parent1.Chromosome))}
	child2 := Genome{Chromosome: make([]int, len(parent2.Chromosome))}

	point1 := rand.Intn(len(parent1.Chromosome))
	point2 := rand.Intn(len(parent1.Chromosome))
	if point1 > point2 {
		point1, point2 = point2, point1
	}

	// Copy genes between point1 and point2 from each parent
	copy(child1.Chromosome[point1:point2], parent1.Chromosome[point1:point2])
	copy(child2.Chromosome[point1:point2], parent2.Chromosome[point1:point2])

	// Fill in remaining genes from the other parent, maintaining order
	for i := 0; i < len(parent1.Chromosome); i++ {
		if i < point1 || i >= point2 {
			child1.Chromosome[i] = parent2.Chromosome[i]
			child2.Chromosome[i] = parent1.Chromosome[i]
		}
	}

	child1.CalculateFitness(ga.Items, ga.MaxWeight)
	child2.CalculateFitness(ga.Items, ga.MaxWeight)
	return child1, child2
}

// Mutation function that ensures feasible mutations.
func (ga *GeneticAlgorithm) Mutate(genome *Genome) {
	for i := range genome.Chromosome {
		if rand.Float64() < ga.MutationProbability {
			curr_weight := ga.calculateWeight(genome.Chromosome)
			if genome.Chromosome[i] == 0 {
				// Turn on the item if feasible
				if curr_weight+ga.Items[i].Weight <= ga.MaxWeight {
					genome.Chromosome[i] = 1
				}
			} else {
				// Turn off the item
				genome.Chromosome[i] = 0
				curr_weight -= ga.Items[i].Weight
			}
		}
	}
	genome.CalculateFitness(ga.Items, ga.MaxWeight)
}

// Calculate the total weight of the chromosome.
func (ga *GeneticAlgorithm) calculateWeight(chromosome []int) int {
	totalWeight := 0
	for i, gene := range chromosome {
		if gene == 1 {
			totalWeight += ga.Items[i].Weight
		}
	}
	return totalWeight
}

// Evolve Population with Elitism and Tournament Selection.
func (ga *GeneticAlgorithm) EvolvePopulationWithElitism(eliteSize, tournamentSize int) {
	newPopulation := make([]Genome, 0, ga.PopulationSize)
	sort.Slice(ga.Population, func(i, j int) bool {
		return ga.Population[i].Fitness > ga.Population[j].Fitness
	})
	// Retain elite genomes
	newPopulation = append(newPopulation, ga.Population[:eliteSize]...)

	for len(newPopulation) < ga.PopulationSize {
		parent1 := ga.TournamentSelection(tournamentSize)
		parent2 := ga.TournamentSelection(tournamentSize)
		child1, child2 := ga.TwoPointCrossover(parent1, parent2)
		ga.Mutate(&child1)
		ga.Mutate(&child2)
		newPopulation = append(newPopulation, child1, child2)
	}

	if len(newPopulation) > ga.PopulationSize {
		newPopulation = newPopulation[:ga.PopulationSize]
	}
	ga.Population = newPopulation
	ga.BestFitnessHistory = append(ga.BestFitnessHistory, ga.Population[0].Fitness)
}

// Run the genetic algorithm evolution process.
func (ga *GeneticAlgorithm) RunEvolution(fitnessThreshold float64, patience int) Genome {
	fitnessImprovements := []float64{}
	for generation := 0; generation < ga.Generations; generation++ {
		ga.EvolvePopulationWithElitism(5, 3)

		if generation > 0 {
			fitnessChange := mathAbs(ga.BestFitnessHistory[len(ga.BestFitnessHistory)-1] - ga.BestFitnessHistory[len(ga.BestFitnessHistory)-2])
			fitnessImprovements = append(fitnessImprovements, fitnessChange)

			if len(fitnessImprovements) > patience {
				fitnessImprovements = fitnessImprovements[1:]
			}

			avgFitnessChange := averageFloats(fitnessImprovements)
			if avgFitnessChange < fitnessThreshold && len(fitnessImprovements) == patience {
				fmt.Printf("Stopping early at generation %d due to minimal improvement.\n", generation)
				break
			}
		}

		if generation%10 == 0 {
			fmt.Printf("Generation %d: Best fitness = %.2f\n", generation, ga.BestFitnessHistory[len(ga.BestFitnessHistory)-1])
		}
	}
	return ga.Population[0]
}

// Utility Functions
func mathAbs(a float64) float64 {
	if a < 0 {
		return -a
	}
	return a
}

func averageFloats(a []float64) float64 {
	sum := 0.0
	for _, v := range a {
		sum += v
	}
	return sum / float64(len(a))
}

func loadItems(filename string) (int, []Item, error) {
	file, err := os.Open(filename)
	if err != nil {
		return 0, nil, err
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	var items []Item
	maxWeight := 0
	numItems := 0
	idx := 0
	if scanner.Scan() {
		line := scanner.Text()
		parts := strings.Fields(line)
		if len(parts) != 2 {
			return 0, nil, fmt.Errorf("Invalid first line in file")
		}
		maxWeight, _ = strconv.Atoi(parts[0])
		numItems, _ = strconv.Atoi(parts[1])
	}
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Fields(line)
		weight, _ := strconv.Atoi(parts[0])
		value, _ := strconv.Atoi(parts[1])
		item := Item{
			Index:  idx,
			Weight: weight,
			Value:  value,
		}
		items = append(items, item)
		idx++
	}
	if len(items) != numItems {
		return 0, nil, fmt.Errorf("Number of items does not match")
	}
	return maxWeight, items, nil
}

func main() {
	rand.Seed(time.Now().UnixNano())
	fmt.Print("Enter 'short' or 'long': ")
	var option string
	fmt.Scan(&option)
	startTime := time.Now()
	maxWeight, items, err := loadItems(fmt.Sprintf("../TestData/%s_test_data", option))
	if err != nil {
		fmt.Println("Error loading items:", err)
		return
	}

	ga := GeneticAlgorithm{
		Items:               items,
		MaxWeight:           maxWeight,
		PopulationSize:      10000,
		Generations:         2000,
		MutationProbability: 0.15,
	}
	ga.InitializePopulation()
	bestGenome := ga.RunEvolution(1e-6, 25)

	// Output the best solution found
	selectedItems := []Item{}
	totalWeight := 0
	totalValue := 0.0
	for i, gene := range bestGenome.Chromosome {
		if gene == 1 {
			selectedItems = append(selectedItems, items[i])
			totalWeight += items[i].Weight
			totalValue += float64(items[i].Value)
		}
	}

	fmt.Printf("Total value: %.0f\n", totalValue)
	fmt.Printf("Total weight: %d\n", totalWeight)
	fmt.Printf("Selected items indices: ")
	for _, item := range selectedItems {
		fmt.Printf("%d ", item.Index)
	}
	fmt.Printf("\nTime taken: %.2f seconds\n", time.Since(startTime).Seconds())
}
