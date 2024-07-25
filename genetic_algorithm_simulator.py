import random
import tkinter as tk
from tkinter import ttk
import pygame
import logging

logging.basicConfig(filename='genetic_algorithm.log', level=logging.INFO)

# Genetic Algorithm Functions
def initialize_population(pop_size, gene_length):
    return [''.join(random.choice('01') for _ in range(gene_length)) for _ in range(pop_size)]

def fitness(individual, target):
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


def communalism(population1, population2, community_benefit, gene_length):
    for i in range(len(population1)):
        if random.random() < community_benefit:  # Use community_benefit
            fitness1 = fitness(population1[i], TARGET)
            fitness2 = fitness(random.choice(population2), TARGET)
            # Benefit from communalism
            population1[i] = mutation(population1[i], MUTATION_RATE, MUTATION_TYPE, gene_length)
    return population1
def mutualism(population1, population2, mutualism_rate, gene_length):
    interactions = int(mutualism_rate * len(population1))
    for _ in range(interactions):
        individual1 = random.choice(population1)
        individual2 = random.choice(population2)
        if fitness(individual1, TARGET) < fitness(individual2, TARGET):
            # Benefit from mutualism
            population1.append(mutation(individual1, MUTATION_RATE, MUTATION_TYPE, gene_length))
    return population1
def mutation(individual, mutation_rate, mutation_type, gene_length):
    if random.random() < mutation_rate:
        if mutation_type == 'bit_flip':
            index = random.randint(0, gene_length - 1)
            individual = individual[:index] + str(1 - int(individual[index])) + individual[index + 1:]
        elif mutation_type == 'inversion':
            start, end = sorted(random.sample(range(gene_length), 2))
            individual = individual[:start] + individual[start:end][::-1] + individual[end:]
        elif mutation_type == 'random_set':
            individual = ''.join(random.choice('01') for _ in range(gene_length))
    return individual

def elitism(population, fitness_scores, elite_size):
    elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_size]
    elite = [population[i] for i in elite_indices]
    return elite

def adjust_population(population, max_size, min_size):
    if len(population) > max_size:
        population = random.sample(population, max_size)
    elif len(population) < min_size:
        additional_individuals = initialize_population(min_size - len(population), len(population[0]))
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

def genetic_algorithm(gui_callback, visual_callback, pop_size, gene_length, target, max_generations, mutation_rate, elite_size, predator_rate, disaster_rate, mutation_type, custom_fitness=None, num_species=1, mutualism_rate=0.0, community_benefit=0.0):
    population = initialize_population(pop_size, gene_length)
    best_fitness = 0
    best_individual = None

    for generation in range(max_generations):
        current_mutation_rate = adaptive_mutation_rate(generation, max_generations)
        if custom_fitness:
            fitness_scores = [custom_fitness(individual) for individual in population]
        else:
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

        if num_species > 1:
            # Apply communalism and mutualism if multiple species are involved
            population = communalism(population, population, community_benefit, target, current_mutation_rate, mutation_type, gene_length)
            population = mutualism(population, population, mutualism_rate, gene_length, target, current_mutation_rate, mutation_type)

        if random.random() < predator_rate:
            population = predator(population, predator_rate)
        if random.random() < disaster_rate:
            population = disaster(population, disaster_rate)

        population = adjust_population(population, max_size=pop_size, min_size=pop_size//2)

    return best_individual, best_fitness

# Pygame Visualization
class InteractivePygameVisualizer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = None
        self.running = True

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Interactive Genetic Algorithm Visualizer")

    def stop(self):
        pygame.quit()

    def draw(self, fitness_scores):
        self.screen.fill((0, 0, 0))
        max_fitness = max(fitness_scores)
        bar_width = self.width // len(fitness_scores)
        for i, fitness in enumerate(fitness_scores):
            bar_height = (fitness / max_fitness) * self.height if max_fitness > 0 else 0
            pygame.draw.rect(self.screen, (0, 255, 0), (i * bar_width, self.height - bar_height, bar_width, bar_height))
        pygame.display.flip()

        # Event handling for interactivity
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

# GUI
class GeneticAlgorithmGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genetic Algorithm Simulator")
        self.geometry("800x600")
        self.visualizer = InteractivePygameVisualizer()  # Use InteractivePygameVisualizer instead

        self.create_widgets()

    def create_widgets(self):
        # Create input fields for parameters with tooltips
        self.create_labeled_entry("Population Size:", 0, "The number of individuals in the population.")
        self.create_labeled_entry("Gene Length:", 1, "The length of the gene (number of bits).")
        self.create_labeled_entry("Target:", 2, "The target gene to be evolved.")
        self.create_labeled_entry("Max Generations:", 3, "The maximum number of generations to run the simulation.")
        self.create_labeled_entry("Mutation Rate:", 4, "The probability of a mutation occurring in an individual.")
        self.create_labeled_entry("Elite Size:", 5, "The number of top individuals preserved without mutation.")
        self.create_labeled_entry("Predator Rate:", 6, "The proportion of the population removed by the predator mechanism.")
        self.create_labeled_entry("Disaster Rate:", 7, "The proportion of the population removed by natural disasters.")
        self.create_labeled_entry("Number of Species:", 8, "The number of different species in the simulation.")
        self.create_labeled_entry("Mutualism Rate:", 9, "The interaction rate between species where they benefit from cooperation.")
        self.create_labeled_entry("Community Benefit:", 10, "The fitness boost from communal interactions.")

        # Mutation type dropdown
        tk.Label(self, text="Mutation Type:").grid(row=11, column=0, pady=5, sticky="e")
        self.mutation_type_var = tk.StringVar()
        self.mutation_type_var.set("bit_flip")
        self.mutation_type_menu = ttk.Combobox(self, textvariable=self.mutation_type_var, values=["bit_flip", "inversion", "random_set"])
        self.mutation_type_menu.grid(row=11, column=1, pady=5, sticky="w")
        self.create_tooltip(self.mutation_type_menu, "The type of mutation applied to individuals.")

        # Start button
        self.start_button = ttk.Button(self, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=12, column=0, columnspan=2, pady=20)

        # Output text box
        self.output_text = tk.Text(self, wrap="word", height=20, width=80)
        self.output_text.grid(row=13, column=0, columnspan=2, pady=20)

    def create_labeled_entry(self, label_text, row, tooltip_text):
        tk.Label(self, text=label_text).grid(row=row, column=0, pady=5, sticky="e")
        entry = ttk.Entry(self)
        entry.grid(row=row, column=1, pady=5, sticky="w")
        setattr(self, label_text.replace(" ", "_").lower()[:-1], entry)  # Store the entry widget
        self.create_tooltip(entry, tooltip_text)

    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.wm_overrideredirect(True)
        label = ttk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1, wraplength=200)
        label.pack()

        def on_enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def on_leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def start_simulation(self):
        # Input validation
        try:
            pop_size = int(self.population_size.get())
            gene_length = int(self.gene_length.get())
            target = self.target.get()
            max_generations = int(self.max_generations.get())
            mutation_rate = float(self.mutation_rate.get())
            elite_size = int(self.elite_size.get())
            predator_rate = float(self.predator_rate.get())
            disaster_rate = float(self.disaster_rate.get())
            num_species = int(self.num_species.get())  # Ensure num_species exists
            mutualism_rate = float(self.mutualism_rate.get())
            community_benefit = float(self.community_benefit.get())
            mutation_type = self.mutation_type_var.get()

            if pop_size <= 0 or gene_length <= 0 or max_generations <= 0 or mutation_rate < 0 or elite_size < 0 or predator_rate < 0 or disaster_rate < 0 or num_species <= 0 or mutualism_rate < 0 or community_benefit < 0:
                raise ValueError("All values must be positive.")
            if not all(bit in "01" for bit in target):
                raise ValueError("Target must be a binary string.")
            if len(target) != gene_length:
                raise ValueError("Target length must match gene length.")

        except ValueError as e:
         self.update_output(f"Invalid input: {e}")
         return

        self.start_button.config(state=tk.DISABLED)
        self.visualizer.start()
        self.update_output("Starting simulation...")

    def run_genetic_algorithm():
        best_individual, best_fitness = genetic_algorithm(
            self.update_output,
            self.visualizer.draw,
            pop_size,
            gene_length,
            target,
            max_generations,
            mutation_rate,
            elite_size,
            predator_rate,
            disaster_rate,
            mutation_type,
            num_species,
            mutualism_rate,
            community_benefit
        )
        self.update_output(f"\nFinal best individual: {best_individual}")
        self.update_output(f"Final best fitness: {best_fitness}")
        self.start_button.config(state=tk.NORMAL)
        self.visualizer.stop()

        self.after(100, run_genetic_algorithm)   
        
    
    def update_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.update()

if __name__ == "__main__":
    app = GeneticAlgorithmGUI()
    app.mainloop()
