import random
import tkinter as tk
from tkinter import ttk
import pygame
import logging

logging.basicConfig(filename='genetic_algorithm.log', level=logging.INFO)

# Genetic Algorithm Functions
def initialize_population(pop_size, gene_length, gene_type='binary'):
    if gene_type == 'binary':
        return [''.join(random.choice('01') for _ in range(gene_length)) for _ in range(pop_size)]
    elif gene_type == 'nucleotide':
        return [''.join(random.choice('ATCG') for _ in range(gene_length)) for _ in range(pop_size)]
    elif gene_type == 'amino_acid':
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        return [''.join(random.choice(amino_acids) for _ in range(gene_length)) for _ in range(pop_size)]

def fitness(individual, target):
    if len(individual) != len(target):
        raise ValueError("Individual and target lengths must match")
    return sum(1 for i in range(len(individual)) if individual[i] == target[i])

def adaptive_mutation_rate(generation, max_generations):
    return max(0.01, 0.1 * (1 - generation / max_generations))

def selection(population, fitness_scores):
    total_fitness = sum(fitness_scores)
    probabilities = [f / total_fitness for f in fitness_scores]
    return random.choices(population, weights=probabilities, k=len(population))

def crossover(parent1, parent2, gene_length):
    crossover_point = random.randint(1, gene_length - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def communalism(population1, population2, community_benefit, target, mutation_rate, mutation_type, gene_length):
    for i in range(len(population1)):
        if random.random() < community_benefit:
            fitness1 = fitness(population1[i], target)
            fitness2 = fitness(random.choice(population2), target)
            population1[i] = mutation(population1[i], mutation_rate, mutation_type, gene_length)
    return population1

def mutualism(population1, population2, mutualism_rate, gene_length, target, mutation_rate, mutation_type):
    interactions = int(mutualism_rate * len(population1))
    for _ in range(interactions):
        individual1 = random.choice(population1)
        individual2 = random.choice(population2)
        if fitness(individual1, target) < fitness(individual2, target):
            population1.append(mutation(individual1, mutation_rate, mutation_type, gene_length))
    return population1

def mutation(individual, mutation_rate, mutation_type, gene_length, gene_type='binary'):
    if random.random() < mutation_rate:
        if gene_type == 'binary':
            if mutation_type == 'bit_flip':
                index = random.randint(0, gene_length - 1)
                individual = individual[:index] + str(1 - int(individual[index])) + individual[index + 1:]
            elif mutation_type == 'inversion':
                start, end = sorted(random.sample(range(gene_length), 2))
                individual = individual[:start] + individual[start:end][::-1] + individual[end:]
            elif mutation_type == 'random_set':
                individual = ''.join(random.choice('01') for _ in range(gene_length))
        elif gene_type == 'nucleotide':
            if mutation_type == 'substitution':
                index = random.randint(0, gene_length - 1)
                nucleotides = 'ATCG'
                new_nucleotide = random.choice(nucleotides.replace(individual[index], ''))
                individual = individual[:index] + new_nucleotide + individual[index + 1:]
            elif mutation_type == 'inversion':
                start, end = sorted(random.sample(range(gene_length), 2))
                individual = individual[:start] + individual[start:end][::-1] + individual[end:]
            elif mutation_type == 'random_set':
                individual = ''.join(random.choice('ATCG') for _ in range(gene_length))
        elif gene_type == 'amino_acid':
            if mutation_type == 'substitution':
                index = random.randint(0, gene_length - 1)
                amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
                new_amino_acid = random.choice(amino_acids.replace(individual[index], ''))
                individual = individual[:index] + new_amino_acid + individual[index + 1:]
            elif mutation_type == 'inversion':
                start, end = sorted(random.sample(range(gene_length), 2))
                individual = individual[:start] + individual[start:end][::-1] + individual[end:]
            elif mutation_type == 'random_set':
                amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
                individual = ''.join(random.choice(amino_acids) for _ in range(gene_length))
    return individual

def elitism(population, fitness_scores, elite_size):
    elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_size]
    elite = [population[i] for i in elite_indices]
    return elite

def adjust_population(population, max_size, min_size):
    if not population:
        return initialize_population(max_size, 1)

    gene_length = len(population[0])
    if len(population) > max_size:
        population = random.sample(population, max_size)
    elif len(population) < min_size:
        additional_individuals = initialize_population(min_size - len(population), gene_length)
        population += additional_individuals
    return population

def tournament_selection(population, fitness_scores, tournament_size=5):
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(list(zip(population, fitness_scores)), tournament_size)
        winner = max(tournament, key=lambda x: x[1])[0]
        selected.append(winner)
    return selected

def predator(population, predator_rate):
    num_predators = int(predator_rate * len(population))
    population = random.sample(population, len(population) - num_predators)
    return population

def disaster(population, disaster_rate):
    num_survivors = int((1 - disaster_rate) * len(population))
    population = random.sample(population, num_survivors)
    return population

def genetic_algorithm(gui_callback, visual_callback, pop_size, gene_length, target, max_generations, mutation_rate, elite_size, predator_rate, disaster_rate, mutation_type, gene_type, num_species=1, mutualism_rate=0.0, community_benefit=0.0):
    population = initialize_population(pop_size, gene_length, gene_type)  
    best_fitness = 0
    best_individual = None

    for generation in range(max_generations):
        current_mutation_rate = adaptive_mutation_rate(generation, max_generations)
        fitness_scores = [fitness(individual, target) for individual in population]
        
        best_index = fitness_scores.index(max(fitness_scores))
        if fitness_scores[best_index] > best_fitness:
            best_fitness = fitness_scores[best_index]
            best_individual = population[best_index]

        log_message = f"Generation {generation}, Best fitness: {best_fitness}, Individual: {best_individual}"
        logging.info(log_message)
        gui_callback(log_message)
        visual_callback(fitness_scores)

        if best_fitness == gene_length:
            break

        elite = elitism(population, fitness_scores, elite_size)
        population = tournament_selection(population, fitness_scores)
        offspring = []
        for _ in range(len(population) // 2):
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2, gene_length)
            offspring.append(mutation(child1, current_mutation_rate, mutation_type, gene_length))
            offspring.append(mutation(child2, current_mutation_rate, mutation_type, gene_length))
        
        population = elite + offspring
        population = adjust_population(population, pop_size, pop_size // 2)

        if mutualism_rate > 0:
            population = mutualism(population, population, mutualism_rate, gene_length, target, current_mutation_rate, mutation_type)

        if community_benefit > 0:
            population = communalism(population, population, community_benefit, target, current_mutation_rate, mutation_type, gene_length)

        population = predator(population, predator_rate)
        population = disaster(population, disaster_rate)

    return best_individual, best_fitness

class InteractivePygameVisualizer:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Genetic Algorithm Visualization')
        self.running = True
        self.font = pygame.font.SysFont(None, 24)
        self.colors = {'black': (0, 0, 0), 'white': (255, 255, 255)}

    def update(self, fitness_scores):
        self.screen.fill(self.colors['black'])
        max_fitness = max(fitness_scores, default=1)
        for i, score in enumerate(fitness_scores):
            color = (255, 0, 0) if score == max_fitness else (0, 255, 0)
            pygame.draw.rect(self.screen, color, (10 + i * 10, self.height - score * 10, 5, score * 10))
        pygame.display.flip()

    def close(self):
        pygame.quit()

    def run(self, fitness_scores):
        self.update(fitness_scores)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def interact(self):
        while self.running:
            self.run([])
            pygame.time.wait(100)

class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Genetic Algorithm Simulation")

        self.pop_size = tk.IntVar(value=100)
        self.gene_length = tk.IntVar(value=10)
        self.target = tk.StringVar(value="1111111111")
        self.max_generations = tk.IntVar(value=100)
        self.mutation_rate = tk.DoubleVar(value=0.01)
        self.elite_size = tk.IntVar(value=5)
        self.predator_rate = tk.DoubleVar(value=0.1)
        self.disaster_rate = tk.DoubleVar(value=0.1)
        self.mutation_type = tk.StringVar(value="bit_flip")
        self.gene_type = tk.StringVar(value="binary")
        self.num_species = tk.IntVar(value=1)
        self.mutualism_rate = tk.DoubleVar(value=0.0)
        self.community_benefit = tk.DoubleVar(value=0.0)

        self.create_widgets()

    def create_widgets(self):
        # Create and place widgets here
        ttk.Label(self.master, text="Population Size:").grid(row=0, column=0)
        ttk.Entry(self.master, textvariable=self.pop_size).grid(row=0, column=1)
        ttk.Label(self.master, text="Gene Length:").grid(row=1, column=0)
        ttk.Entry(self.master, textvariable=self.gene_length).grid(row=1, column=1)
        ttk.Label(self.master, text="Target:").grid(row=2, column=0)
        ttk.Entry(self.master, textvariable=self.target).grid(row=2, column=1)
        ttk.Label(self.master, text="Max Generations:").grid(row=3, column=0)
        ttk.Entry(self.master, textvariable=self.max_generations).grid(row=3, column=1)
        ttk.Label(self.master, text="Mutation Rate:").grid(row=4, column=0)
        ttk.Entry(self.master, textvariable=self.mutation_rate).grid(row=4, column=1)
        ttk.Label(self.master, text="Elite Size:").grid(row=5, column=0)
        ttk.Entry(self.master, textvariable=self.elite_size).grid(row=5, column=1)
        ttk.Label(self.master, text="Predator Rate:").grid(row=6, column=0)
        ttk.Entry(self.master, textvariable=self.predator_rate).grid(row=6, column=1)
        ttk.Label(self.master, text="Disaster Rate:").grid(row=7, column=0)
        ttk.Entry(self.master, textvariable=self.disaster_rate).grid(row=7, column=1)
        ttk.Label(self.master, text="Mutation Type:").grid(row=8, column=0)
        self.mutation_type_menu = tk.OptionMenu(self.master, self.mutation_type, "bit_flip", "inversion", "random_set")
        self.mutation_type_menu.grid(row=8, column=1)
        ttk.Label(self.master, text="Gene Type:").grid(row=9, column=0)
        self.gene_type_menu = tk.OptionMenu(self.master, self.gene_type, "binary", "nucleotide", "amino_acid")
        self.gene_type_menu.grid(row=9, column=1)
        ttk.Label(self.master, text="Number of Species:").grid(row=10, column=0)
        ttk.Entry(self.master, textvariable=self.num_species).grid(row=10, column=1)
        ttk.Label(self.master, text="Mutualism Rate:").grid(row=11, column=0)
        ttk.Entry(self.master, textvariable=self.mutualism_rate).grid(row=11, column=1)
        ttk.Label(self.master, text="Community Benefit:").grid(row=12, column=0)
        ttk.Entry(self.master, textvariable=self.community_benefit).grid(row=12, column=1)

        ttk.Button(self.master, text="Start Simulation", command=self.start_simulation).grid(row=13, column=0, columnspan=2)

        self.log_text = tk.Text(self.master, height=10, width=50)
        self.log_text.grid(row=14, column=0, columnspan=2)

    def update_log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.yview(tk.END)

    def start_simulation(self):
        try:
            pop_size = self.pop_size.get()
            gene_length = self.gene_length.get()
            target = self.target.get()
            max_generations = self.max_generations.get()
            mutation_rate = self.mutation_rate.get()
            elite_size = self.elite_size.get()
            predator_rate = self.predator_rate.get()
            disaster_rate = self.disaster_rate.get()
            mutation_type = self.mutation_type.get()
            gene_type = self.gene_type.get()
            num_species = self.num_species.get()
            mutualism_rate = self.mutualism_rate.get()
            community_benefit = self.community_benefit.get()

            if not target:
                raise ValueError("Target must be provided")

            visualizer = InteractivePygameVisualizer()
            def gui_callback(message):
                self.update_log(message)
            def visual_callback(fitness_scores):
                visualizer.update(fitness_scores)
            best_individual, best_fitness = genetic_algorithm(
                gui_callback, visual_callback, pop_size, gene_length, target, max_generations, mutation_rate, elite_size,
                predator_rate, disaster_rate, mutation_type, gene_type, num_species, mutualism_rate, community_benefit
            )
            visualizer.close()
            self.update_log(f"Best individual: {best_individual} with fitness: {best_fitness}")
        except Exception as e:
            self.update_log(f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()