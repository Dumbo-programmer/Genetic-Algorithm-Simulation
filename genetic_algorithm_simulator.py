import random

# Constants
POP_SIZE = 100000000000000
GENE_LENGTH = 20
TARGET = '10101010101010101010'
MAX_GENERATIONS = 1000
MUTATION_RATE = 0.01
ELITE_SIZE = 5
PREDATOR_RATE = 0.5
DISASTER_RATE = 0.2
MUTATION_TYPE = 'bit_flip'  # 'bit_flip', 'inversion', 'random_set'


# Functions
def initialize_population(pop_size, gene_length):
    return [''.join(random.choice('01') for _ in range(gene_length)) for _ in range(pop_size)]

def fitness(individual, target):
    return sum(1 for i in range(len(individual)) if individual[i] == target[i])

def selection(population, fitness_scores):
    total_fitness = sum(fitness_scores)
    probabilities = [f / total_fitness for f in fitness_scores]
    return random.choices(population, weights=probabilities, k=POP_SIZE)

def crossover(parent1, parent2):
    crossover_point = random.randint(1, GENE_LENGTH - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutation(individual, mutation_rate, mutation_type):
    if random.random() < mutation_rate:
        if mutation_type == 'bit_flip':
            index = random.randint(0, GENE_LENGTH - 1)
            individual = individual[:index] + str(1 - int(individual[index])) + individual[index + 1:]
        elif mutation_type == 'inversion':
            start, end = sorted(random.sample(range(GENE_LENGTH), 2))
            individual = individual[:start] + individual[start:end][::-1] + individual[end:]
        elif mutation_type == 'random_set':
            individual = ''.join(random.choice('01') for _ in range(GENE_LENGTH))
    return individual

def elitism(population, fitness_scores, elite_size):
    elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_size]
    elite = [population[i] for i in elite_indices]
    return elite

def predator(population, predator_rate):
    num_predators = int(predator_rate * POP_SIZE)
    population = random.sample(population, POP_SIZE - num_predators)
    return population

def disaster(population, disaster_rate):
    num_survivors = int((1 - disaster_rate) * POP_SIZE)
    population = random.sample(population, num_survivors)
    return population

def genetic_algorithm():
    population = initialize_population(POP_SIZE, GENE_LENGTH)
    best_fitness = 0
    best_individual = None

    for generation in range(MAX_GENERATIONS):
        fitness_scores = [fitness(individual, TARGET) for individual in population]
        best_index = fitness_scores.index(max(fitness_scores))
        if fitness_scores[best_index] > best_fitness:
            best_fitness = fitness_scores[best_index]
            best_individual = population[best_index]
        print(f"Generation {generation}, Best fitness: {best_fitness}, Individual: {best_individual}")

        if best_fitness == GENE_LENGTH:
            break

        elite = elitism(population, fitness_scores, ELITE_SIZE)
        population = selection(population, fitness_scores)
        offspring = []
        for _ in range(POP_SIZE // 2):
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2)
            offspring.append(mutation(child1, MUTATION_RATE, MUTATION_TYPE))
            offspring.append(mutation(child2, MUTATION_RATE, MUTATION_TYPE))
        population = elite + offspring

        if random.random() < PREDATOR_RATE:
            population = predator(population, PREDATOR_RATE)
        if random.random() < DISASTER_RATE:
            population = disaster(population, DISASTER_RATE)

    return best_individual, best_fitness

if __name__ == "__main__":
    best_individual, best_fitness = genetic_algorithm()
    print("Final best individual:", best_individual)
    print("Final best fitness:", best_fitness)
