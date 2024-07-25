import random
import tkinter as tk
from tkinter import ttk
import pygame

# Genetic Algorithm Functions
def initialize_population(pop_size, gene_length):
    return [''.join(random.choice('01') for _ in range(gene_length)) for _ in range(pop_size)]

def fitness(individual, target):
    return sum(1 for i in range(len(individual)) if individual[i] == target[i])

def selection(population, fitness_scores):
    total_fitness = sum(fitness_scores)
    probabilities = [f / total_fitness for f in fitness_scores]
    return random.choices(population, weights=probabilities, k=len(population))

def crossover(parent1, parent2, gene_length):
    crossover_point = random.randint(1, gene_length - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

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

def predator(population, predator_rate):
    num_predators = int(predator_rate * len(population))
    population = random.sample(population, len(population) - num_predators)
    return population

def disaster(population, disaster_rate):
    num_survivors = int((1 - disaster_rate) * len(population))
    population = random.sample(population, num_survivors)
    return population

def genetic_algorithm(gui_callback, visual_callback, pop_size, gene_length, target, max_generations, mutation_rate, elite_size, predator_rate, disaster_rate, mutation_type):
    population = initialize_population(pop_size, gene_length)
    best_fitness = 0
    best_individual = None

    for generation in range(max_generations):
        fitness_scores = [fitness(individual, target) for individual in population]
        best_index = fitness_scores.index(max(fitness_scores))
        if fitness_scores[best_index] > best_fitness:
            best_fitness = fitness_scores[best_index]
            best_individual = population[best_index]

        gui_callback(f"Generation {generation}, Best fitness: {best_fitness}, Individual: {best_individual}")
        visual_callback(fitness_scores)

        if best_fitness == gene_length:
            break

        elite = elitism(population, fitness_scores, elite_size)
        population = selection(population, fitness_scores)
        offspring = []
        for _ in range(len(population) // 2):
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2, gene_length)
            offspring.append(mutation(child1, mutation_rate, mutation_type, gene_length))
            offspring.append(mutation(child2, mutation_rate, mutation_type, gene_length))
        population = elite + offspring

        if random.random() < predator_rate:
            population = predator(population, predator_rate)
        if random.random() < disaster_rate:
            population = disaster(population, disaster_rate)

    return best_individual, best_fitness

# Pygame Visualization
class PygameVisualizer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = None

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Genetic Algorithm Visualizer")
    
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

# GUI
class GeneticAlgorithmGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genetic Algorithm Simulator")
        self.geometry("800x600")
        self.visualizer = PygameVisualizer()

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
        
        # Mutation type dropdown
        tk.Label(self, text="Mutation Type:").grid(row=8, column=0, pady=5, sticky="e")
        self.mutation_type_var = tk.StringVar()
        self.mutation_type_var.set("bit_flip")
        self.mutation_type_menu = ttk.Combobox(self, textvariable=self.mutation_type_var, values=["bit_flip", "inversion", "random_set"])
        self.mutation_type_menu.grid(row=8, column=1, pady=5, sticky="w")
        self.create_tooltip(self.mutation_type_menu, "The type of mutation applied to individuals.")

        # Start button
        self.start_button = ttk.Button(self, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=9, column=0, columnspan=2, pady=20)
        
        # Output text box
        self.output_text = tk.Text(self, wrap="word", height=20, width=80)
        self.output_text.grid(row=10, column=0, columnspan=2, pady=20)

    def create_labeled_entry(self, label_text, row, tooltip_text):
        tk.Label(self, text=label_text).grid(row=row, column=0, pady=5, sticky="e")
        entry = ttk.Entry(self)
        entry.grid(row=row, column=1, pady=5, sticky="w")
        setattr(self, label_text.replace(" ", "_").lower()[:-1], entry)
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
            mutation_type = self.mutation_type_var.get()

            if pop_size <= 0 or gene_length <= 0 or max_generations <= 0 or mutation_rate < 0 or elite_size < 0 or predator_rate < 0 or disaster_rate < 0:
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
                mutation_type
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
