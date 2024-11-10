package main

import (
    "encoding/csv"
	"fmt"
	"math"
	"math/rand"
	"os"
	"sort"
	"strconv"
	"time"
)

// City represents a city with coordinates.
type City struct {
	Index int
	Name  string
	X     float64
	Y     float64
}

// Genome represents a candidate solution (route) in the TSP.
type Genome struct {
	Route    []int
	Distance float64
	Fitness  float64
}

// loadCities loads city names and positions from CSV files and creates City objects.
func loadCities(fileNames string, filePositions string) ([]City, error) {
	var cities []City

	// Open the two files
	f1, err := os.Open(filePositions)
	if err != nil {
		return nil, fmt.Errorf("could not open positions file: %v", err)
	}
	defer f1.Close()

	f2, err := os.Open(fileNames)
	if err != nil {
		return nil, fmt.Errorf("could not open names file: %v", err)
	}
	defer f2.Close()

	// Create CSV readers for both files
	namesReader := csv.NewReader(f2)
	positionsReader := csv.NewReader(f1)

	// Read the data from both files line by line
	index := 0
	for {
		nameRecord, err := namesReader.Read()
		if err != nil {
			break
		}
		positionRecord, err := positionsReader.Read()
		if err != nil {
			break
		}

		// Parse the x and y positions as floats
		x, err := strconv.ParseFloat(positionRecord[0], 64)
		if err != nil {
			return nil, fmt.Errorf("invalid x coordinate for city %s: %v", nameRecord[0], err)
		}
		y, err := strconv.ParseFloat(positionRecord[1], 64)
		if err != nil {
			return nil, fmt.Errorf("invalid y coordinate for city %s: %v", nameRecord[0], err)
		}

		// Create and append the city to the list
		city := City{
			Index: index,
			Name:  nameRecord[0],
			X:     x,
			Y:     y,
		}
		cities = append(cities, city)
		index++
	}

	return cities, nil
}

// calculateDistanceBetweenPoints calculates the Euclidean distance between two points (x1, y1) and (x2, y2).
func calculateDistanceBetweenPoints(x1, y1, x2, y2 float64) float64 {
	return math.Sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))
}

// CalculateDistance computes the total distance of the route.
func (g *Genome) CalculateDistance(cities []City) float64 {
	distance := 0.0
	for i := 0; i < len(g.Route)-1; i++ {
		city1 := cities[g.Route[i]]
		city2 := cities[g.Route[i+1]]
		dist := calculateDistanceBetweenPoints(city1.X, city1.Y, city2.X, city2.Y)
		distance += dist
	}
	g.Distance = distance
	return distance
}

// CalculateFitness computes the fitness score (inverse of distance).
func (g *Genome) CalculateFitness() float64 {
	g.Fitness = 1.0 / (g.Distance + 1) // +1 to avoid division by zero
	return g.Fitness
}

// GeneticAlgorithm manages the GA process.
type GeneticAlgorithm struct {
	Cities              []City
	PopulationSize      int
	Generations         int
	Population          []Genome
	MutationProbability float64
	BestFitnessHistory  []float64
}

// InitializePopulation creates an initial population of genomes.
func (ga *GeneticAlgorithm) InitializePopulation() {
	ga.Population = make([]Genome, ga.PopulationSize)
	for i := 0; i < ga.PopulationSize; i++ {
		route := rand.Perm(len(ga.Cities))
		genome := Genome{Route: route}
		genome.CalculateDistance(ga.Cities)
		genome.CalculateFitness()
		ga.Population[i] = genome
	}
}

// TournamentSelection selects a genome using tournament selection.
func (ga *GeneticAlgorithm) TournamentSelection(k int) Genome {
	selected := make([]Genome, k)
	for i := 0; i < k; i++ {
		idx := rand.Intn(len(ga.Population))
		selected[i] = ga.Population[idx]
	}
	sort.Slice(selected, func(i, j int) bool {
		return selected[i].Fitness > selected[j].Fitness
	})
	return selected[0]
}

// SelectionPairTournament selects two genomes for crossover.
func (ga *GeneticAlgorithm) SelectionPairTournament() (Genome, Genome) {
	return ga.TournamentSelection(3), ga.TournamentSelection(3)
}

// SinglePointCrossover performs one-point crossover between two parents.
func (ga *GeneticAlgorithm) SinglePointCrossover(parent1, parent2 Genome) (Genome, Genome) {
	cut := rand.Intn(len(parent1.Route)-2) + 1 // Ensure cut is between 1 and len-2
	child1Route := make([]int, len(parent1.Route))
	child2Route := make([]int, len(parent2.Route))

	// Initialize slices
	for i := range child1Route {
		child1Route[i] = -1
		child2Route[i] = -1
	}

	copy(child1Route[:cut], parent1.Route[:cut])
	copy(child2Route[:cut], parent2.Route[:cut])

	fillRoute := func(childRoute []int, parentRoute []int, cut int) {
		idx := cut
		for _, gene := range parentRoute {
			if !contains(childRoute, gene) {
				childRoute[idx] = gene
				idx++
				if idx >= len(childRoute) {
					idx = 0
				}
			}
		}
	}

	fillRoute(child1Route, parent2.Route, cut)
	fillRoute(child2Route, parent1.Route, cut)

	child1 := Genome{Route: child1Route}
	child1.CalculateDistance(ga.Cities)
	child1.CalculateFitness()

	child2 := Genome{Route: child2Route}
	child2.CalculateDistance(ga.Cities)
	child2.CalculateFitness()

	return child1, child2
}

// Mutate applies reverse mutation to a genome.
func (ga *GeneticAlgorithm) Mutate(genome *Genome) {
	if rand.Float64() < ga.MutationProbability {
		i := rand.Intn(len(genome.Route))
		j := rand.Intn(len(genome.Route))
		if i > j {
			i, j = j, i
		}
		reverse(genome.Route[i : j+1])
		genome.CalculateDistance(ga.Cities)
		genome.CalculateFitness()
	}
}

// EvolvePopulationWithElitism evolves the population with elitism.
func (ga *GeneticAlgorithm) EvolvePopulationWithElitism(eliteSize int) {
	newPopulation := make([]Genome, eliteSize)
	sort.Slice(ga.Population, func(i, j int) bool {
		return ga.Population[i].Fitness > ga.Population[j].Fitness
	})
	copy(newPopulation, ga.Population[:eliteSize])

	for len(newPopulation) < ga.PopulationSize {
		parent1, parent2 := ga.SelectionPairTournament()
		child1, child2 := ga.SinglePointCrossover(parent1, parent2)
		ga.Mutate(&child1)
		ga.Mutate(&child2)
		newPopulation = append(newPopulation, child1, child2)
	}

	ga.Population = newPopulation[:ga.PopulationSize]

	sort.Slice(ga.Population, func(i, j int) bool {
		return ga.Population[i].Fitness > ga.Population[j].Fitness
	})

	ga.BestFitnessHistory = append(ga.BestFitnessHistory, ga.Population[0].Fitness)
}

// RunEvolution runs the genetic algorithm evolution process.
func (ga *GeneticAlgorithm) RunEvolution(fitnessThreshold float64, patience int) Genome {
	var avgFitnessChange float64
	fitnessImprovements := make([]float64, 0, patience)
	for generation := 0; generation < ga.Generations; generation++ {
		ga.EvolvePopulationWithElitism(2)

		if generation > 0 {
			fitnessChange := math.Abs(ga.BestFitnessHistory[len(ga.BestFitnessHistory)-1] - ga.BestFitnessHistory[len(ga.BestFitnessHistory)-2])
			fitnessImprovements = append(fitnessImprovements, fitnessChange)

			if len(fitnessImprovements) > patience {
				fitnessImprovements = fitnessImprovements[1:]
			}

			sumFitnessChange := 0.0
			for _, v := range fitnessImprovements {
				sumFitnessChange += v
			}
			avgFitnessChange = sumFitnessChange / float64(len(fitnessImprovements))

			if avgFitnessChange < fitnessThreshold && len(fitnessImprovements) == patience {
				fmt.Printf("Stopping early at generation %d due to minimal improvement over %d generations.\n", generation, patience)
				break
			}
		}

		// Adjust population size and mutation probability dynamically
		if generation%50 == 0 && generation > 0 {
			if avgFitnessChange < fitnessThreshold {
				if ga.PopulationSize < 1000 {
					ga.PopulationSize += 50
				}
				if ga.MutationProbability < 0.5 {
					ga.MutationProbability += 0.05
				}
			} else {
				if ga.PopulationSize > 100 {
					ga.PopulationSize -= 50
				}
				if ga.MutationProbability > 0.05 {
					ga.MutationProbability -= 0.05
				}
			}
		}

		if generation%10 == 0 {
			fmt.Printf("Generation %d: Best fitness = %15f, Avg fitness change = %15f\n", generation, ga.BestFitnessHistory[len(ga.BestFitnessHistory)-1], avgFitnessChange)
		}
	}
	return ga.Population[0]
}

// Utility functions

func contains(slice []int, item int) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

func reverse(s []int) {
	for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
		s[i], s[j] = s[j], s[i]
	}
}

// generateRandomCities creates N random cities.
func generateRandomCities(N int, xRange, yRange [2]float64) []City {
	cities := make([]City, N)
	for i := 0; i < N; i++ {
		name := fmt.Sprintf("City %d", i+1)
		x := xRange[0] + rand.Float64()*(xRange[1]-xRange[0])
		y := yRange[0] + rand.Float64()*(yRange[1]-yRange[0])
		cities[i] = City{Index: i, Name: name, X: x, Y: y}
	}
	return cities
}

// print the route through cities
func printRoute(cities []City, route []int) {
    fmt.Print("[")
	for i, idx := range route {
		fmt.Print(cities[idx].Name)
		if i < len(route) - 1 {
		    fmt.Print(" -> ")
		}
	}
fmt.Print("]")
fmt.Println()
}

func main() {
	rand.Seed(time.Now().UnixNano())
	fmt.Print("Enter 'UK12' or a value for N (<=100): ")
	var input string
	fmt.Scan(&input)
	start := time.Now()

	var cities []City // Declare cities outside of the conditional blocks

	// Check if input is "UK12"
	if input == "UK12" {
		var err error
		cities, err = loadCities("../TestData/uk12_name.csv", "../TestData/uk12_xy.csv")
		if err != nil {
			fmt.Println("Error loading cities:", err)
			return
		}
	} else {
		// If not "UK12", try to convert input to integer
		N, err := strconv.Atoi(input)
		if err != nil {
			fmt.Println("Invalid input. Please enter 'UK12' or a valid integer.")
			return
		}

		if N > 100 {
			fmt.Println("Please enter a value of N less than or equal to 100.")
			return
		}

		// Generate random cities
		cities = generateRandomCities(N, [2]float64{0, 100}, [2]float64{0, 100})
	}

	// Now `cities` is available for use in the GeneticAlgorithm
	ga := GeneticAlgorithm{
		Cities:              cities,
		PopulationSize:      5000,
		Generations:         1500,
		MutationProbability: 0.2,
	}

	ga.InitializePopulation()
	bestGenome := ga.RunEvolution(1e-15, 25)

	printRoute(cities, bestGenome.Route)
	fmt.Printf("Best distance: %.2f\n", bestGenome.Distance)
	fmt.Printf("Execution time: %s\n", time.Since(start))
}