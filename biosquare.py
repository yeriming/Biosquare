# Add mutation tracking and visualization (fixed)
import pygame
import random
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

MAX_DEERS = 150
MAX_WOLVES = 100
square = 1000
screen = pygame.display.set_mode((square,square))

# Mutation tracking per species
# Records number of mutations and average mutation strength per step.
mutation_stats = {
    "step": [],
    "deer_mutation_count": [],
    "deer_mutation_rate": [],
    "deer_mutation_speed_avg": [],
    "deer_mutation_sight_avg": [],
    "wolf_mutation_count": [],
    "wolf_mutation_rate": [],
    "wolf_mutation_speed_avg": [],
    "wolf_mutation_sight_avg": []
}

deer_mutation_counter = 0
wolf_mutation_counter = 0
deer_mutation_speed_total = 0
deer_mutation_sight_total = 0
deer_mutation_events = 0
wolf_mutation_speed_total = 0
wolf_mutation_sight_total = 0
wolf_mutation_events = 0

def reset_mutation_stats():
    global deer_mutation_counter, wolf_mutation_counter
    global deer_mutation_speed_total, deer_mutation_sight_total, deer_mutation_events
    global wolf_mutation_speed_total, wolf_mutation_sight_total, wolf_mutation_events
    deer_mutation_counter = 0
    wolf_mutation_counter = 0
    deer_mutation_speed_total = 0
    deer_mutation_sight_total = 0
    deer_mutation_events = 0
    wolf_mutation_speed_total = 0
    wolf_mutation_sight_total = 0
    wolf_mutation_events = 0

class Animal():
    def __init__(self, sight, speed, lifespan, generation=0, color='black', position=None):
        self.sight = sight
        self.speed = speed
        self.steps = 0
        self.direction = self.get_random_direction()
        self.lifespan = lifespan if lifespan is not None else 100
        self.color = color
        self.position = position if position else self.get_random_position()
        self.generation = generation

    def get_modular_position(self):
        if self.position.x < 0: self.position.x += square
        if self.position.x > square: self.position.x -= square
        if self.position.y < 0: self.position.y += square
        if self.position.y > square: self.position.y -= square

    def get_random_position(self):
        return pygame.Vector2(random.random()*square, random.random()*square)

    def get_random_direction(self):
        x = random.randint(-1, 1)
        y = random.randint(-1, 1)
        direction = pygame.Vector2(x, y)
        if direction.length() > 0.0:
            direction = direction.normalize()
        return direction

    def get_animals_in_sight(self, animals):
        return [a for a in animals if a != self and self.position.distance_to(a.position) < self.sight]

    def get_closest_animal(self, animals):
        return min((a for a in animals if a != self), key=lambda a: self.position.distance_to(a.position), default=None)

    def draw(self):
        pygame.draw.circle(screen, self.color, self.position, 10)

# This function introduces a mutation into a genetic trait such as speed or sight.
# Mutations occur with a certain probability (mutation rate) and change the trait by a small random amount (mutation strength).
# The change is sampled from a normal distribution to allow both small increases and decreases.
# This models how biological mutations introduce random variation in real populations.
# If no mutation occurs (based on chance), the original trait value is returned unchanged.
def mutate_trait(value, species, trait_type, mutation_rate=0.3, mutation_strength=0.5):
    global deer_mutation_counter, wolf_mutation_counter
    global deer_mutation_speed_total, deer_mutation_sight_total, deer_mutation_events
    global wolf_mutation_speed_total, wolf_mutation_sight_total, wolf_mutation_events

    if random.random() < mutation_rate:
        delta = random.uniform(-mutation_strength, mutation_strength)
        if species == 'deer':
            deer_mutation_counter += 1
            deer_mutation_events += 1
            if trait_type == 'speed':
                deer_mutation_speed_total += abs(delta)
            elif trait_type == 'sight':
                deer_mutation_sight_total += abs(delta)
        elif species == 'wolf':
            wolf_mutation_counter += 1
            wolf_mutation_events += 1
            if trait_type == 'speed':
                wolf_mutation_speed_total += abs(delta)
            elif trait_type == 'sight':
                wolf_mutation_sight_total += abs(delta)
        return max(0.1, value + delta)
    return value

def get_file(folder, base_name="file", extension=".txt"):
    os.makedirs(folder, exist_ok=True)
    i = 1
    while True:
        filename = f"{base_name}_{i}{extension}"
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            return path
        i += 1

class Deer(Animal):
    def move(self):
        self.steps += 1
        wolves_in_sight = self.get_animals_in_sight(wolves)
        if wolves_in_sight:
            self.set_flee_direction(wolves_in_sight)
        else:
            self.set_wander_direction()
        self.position += self.speed * self.direction
        self.get_modular_position()

    def set_flee_direction(self, predators):
        direction = pygame.Vector2(0, 0)
        for predator in predators:
            metric = self.position.distance_to(predator.position)
            direction += (self.position - predator.position) / metric
        self.direction = direction

    def set_wander_direction(self):
        if random.random() > 0.4:
            self.direction = self.get_random_direction()

# Deer reproduce if they have survived a certain number of steps without being caught.
# The offspring inherits the parent's traits (speed and sight), with a chance for mutation.
# This simulates trait inheritance and the accumulation of advantageous variations over time.
# A new Deer object is returned and added to the population in the main loop.
    def reproduce(self):
        return Deer(
            color=self.color,
            sight=mutate_trait(self.sight, 'deer', 'sight'),
            speed=mutate_trait(self.speed, 'deer', 'speed'),
            lifespan=self.lifespan,
            generation=self.generation + 1
        )

class Wolf(Animal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hunts = 0

    def move(self):
        self.steps += 1
        deers_in_sight = self.get_animals_in_sight(deers)
        if deers_in_sight:
            self.set_chase_direction(deers_in_sight)
        else:
            self.set_wander_direction()
        self.position += self.speed * self.direction
        self.get_modular_position()

    def set_chase_direction(self, preys):
        closest = self.get_closest_animal(preys)
        if closest:
            direction = closest.position - self.position
            if direction.length() > 0:
                self.direction = direction.normalize()

    def set_wander_direction(self):
        if random.random() > 0.6:
            self.direction = self.get_random_direction()

# Wolves can reproduce if they have survived long enough and hunted successfully.
# Reproduction creates a new wolf with inherited traits (speed and sight), possibly mutated.
# This models natural selection by allowing only the fittest individuals to pass on their genes.
# The new wolf is returned as an object to be added to the population.
    def reproduce(self):
        return Wolf(
            color=self.color,
            sight=mutate_trait(self.sight, 'wolf', 'sight'),
            speed=mutate_trait(self.speed, 'wolf', 'speed'),
            lifespan=self.lifespan,
            generation=self.generation + 1
        )

# This dictionary keeps track of population-level statistics across simulation steps.
# For each time step, we record:
# - The number of wolves and deer alive
# - The average speed and sight for each species
# This data helps visualize evolutionary trends over time (e.g., if speed increases).
def log_population_stats(step, deers, wolves, log_list):
    def avg(attr, animals):
        return sum(getattr(a, attr) for a in animals) / len(animals) if animals else 0
    log_list.append({
        "step": step,
        "deer_count": len(deers),
        "deer_speed_avg": avg("speed", deers),
        "deer_sight_avg": avg("sight", deers),
        "deer_fitness_avg": avg("speed", deers) + avg("sight", deers),
        "deer_generation_avg": avg("generation", deers),
        "wolf_count": len(wolves),
        "wolf_speed_avg": avg("speed", wolves),
        "wolf_sight_avg": avg("sight", wolves),
        "wolf_fitness_avg": avg("speed", wolves) + avg("sight", wolves),
        "wolf_generation_avg": avg("generation", wolves)
    })

log = []
deers = [Deer(color='brown', sight=random.uniform(150, 200), speed=random.uniform(10, 15), lifespan=100) for _ in range(60)]
wolves = [Wolf(color='grey', sight=random.uniform(250, 300), speed=random.uniform(15, 20), lifespan=100) for _ in range(20)]

running = True
step = 0
max_steps = 500

# At each simulation step, wolves and deer are updated:
# - Wolves that meet survival and hunting criteria may reproduce
# - Deer that survive long enough may reproduce as well
# Offspring inherit their parent's traits with possible mutations
# All mutation events are counted and summarized for statistical analysis

# After updating the population, we record:
# - Total population counts
# - Trait averages
# - Mutation counts and averages
# These records are stored for visualization in the final dashboard.
while running and step < max_steps:
    screen.fill('white')

    for deer in deers:
        deer.move()
        deer.draw()

    for wolf in wolves[:]:
        wolf.move()
        wolf.draw()
        closest = wolf.get_closest_animal(deers)
        if closest and wolf.position.distance_to(closest.position) < wolf.speed * 1.5:
            if closest in deers:
                deers.remove(closest)
                wolf.hunts += 1
                wolf.steps = 0
        if wolf.hunts >= 1 and wolf.steps >= wolf.lifespan // 4:
            if len(wolves) < MAX_WOLVES:
                wolves.append(wolf.reproduce())
        if wolf.steps >= wolf.lifespan:
            wolves.remove(wolf)

    if step % 10 == 0:
        reset_mutation_stats()
        deers = sorted(deers, key=lambda d: d.speed + d.sight, reverse=True)
        top_deers = [d for d in deers[:len(deers)//3] if d.steps >= 10]
        new_deers = []
        for parent in top_deers:
            if len(deers) + len(new_deers) < MAX_DEERS:
                new_deers.append(parent.reproduce())
        deers.extend(new_deers)

        # This dictionary records mutation activity during the simulation.
        # For each step, we log:
        # - How many mutations occurred
        # - What percentage of the population mutated
        # - The average size of the mutations for each trait (speed, sight)
        # This allows students to analyze the role of mutation in evolution with actual data.
        mutation_stats["step"].append(step)

        mutation_stats["deer_mutation_count"].append(deer_mutation_counter)
        mutation_stats["deer_mutation_rate"].append(deer_mutation_counter / max(1, len(new_deers) * 2))
        mutation_stats["deer_mutation_speed_avg"].append(deer_mutation_speed_total / max(1, deer_mutation_events))
        mutation_stats["deer_mutation_sight_avg"].append(deer_mutation_sight_total / max(1, deer_mutation_events))

        mutation_stats["wolf_mutation_count"].append(wolf_mutation_counter)
        mutation_stats["wolf_mutation_rate"].append(wolf_mutation_counter / max(1, len(wolves)))
        mutation_stats["wolf_mutation_speed_avg"].append(wolf_mutation_speed_total / max(1, wolf_mutation_events))
        mutation_stats["wolf_mutation_sight_avg"].append(
            wolf_mutation_sight_total / wolf_mutation_events if wolf_mutation_events > 0 else np.nan
        )

    if len(wolves) > len(deers) * 2:
        wolves = wolves[:len(deers)*2]
    if len(deers) > len(wolves) * 4:
        if len(wolves) < MAX_WOLVES:
            wolves.append(Wolf(color='grey', sight=random.uniform(250, 300), speed=random.uniform(15, 20), lifespan=100))

    pygame.display.flip()
    pygame.time.wait(200)

    log_population_stats(step, deers, wolves, log)
    step += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# ---------------- SAVE SECTION ---------------- #

# 1. Save CSV log
output_folder = "/Users/yeriming/Downloads/Biosquare/Log"
file_path = get_file(output_folder)

if log:
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=log[0].keys())
        writer.writeheader()
        writer.writerows(log)
    print(f"Saved log to {file_path}")
else:
    print("Not saved")

# 2. Save Visualization for separate mutation metrics
mutation_plot_folder = "/Users/yeriming/Downloads/Biosquare/Mutation"
mutation_plot_path = get_file(mutation_plot_folder, base_name="mutation_plot", extension=".png")

plt.figure()
plt.plot(mutation_stats["step"], mutation_stats["deer_mutation_speed_avg"], label="Deer Speed Mutation", linestyle='-')
plt.plot(mutation_stats["step"], mutation_stats["deer_mutation_sight_avg"], label="Deer Sight Mutation", linestyle='--')
plt.plot(mutation_stats["step"], mutation_stats["wolf_mutation_speed_avg"], label="Wolf Speed Mutation", linestyle='-')
plt.plot(mutation_stats["step"], mutation_stats["wolf_mutation_sight_avg"], label="Wolf Sight Mutation", linestyle='--')
plt.xlabel("Step")
plt.ylabel("Avg Mutation Magnitude")
plt.title("Species Mutation Averages Over Time")
plt.legend()
plt.grid(True)
plt.savefig(mutation_plot_path)
print(f"Saved mutation plot to: {mutation_plot_path}")


# 3. Save dashboard (population + traits + mutation)
steps = [row["step"] for row in log]

dashboard_folder = "/Users/yeriming/Downloads/Biosquare/Dashboard"
dashboard_path = get_file(dashboard_folder, base_name="evolution_dashboard", extension=".png")

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

axs[0, 0].plot(steps, [row["deer_count"] for row in log], label="Deer Count", color='sienna')
axs[0, 0].plot(steps, [row["wolf_count"] for row in log], label="Wolf Count", color='gray')
axs[0, 0].set_title("Population Over Time")
axs[0, 0].set_xlabel("Step")
axs[0, 0].set_ylabel("Count")
axs[0, 0].legend()
axs[0, 0].grid(True)

# Deer traits with twin y-axis
axs[0, 1].clear()
ax1 = axs[0, 1]
ax1.set_xlabel("Step")
ax1.set_ylabel("Deer Speed", color='tab:blue')
ax1.plot(steps, [row["deer_speed_avg"] for row in log], color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel("Deer Sight", color='tab:orange')
ax2.plot(steps, [row["deer_sight_avg"] for row in log], color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:orange')
ax1.set_title("Deer Trait Evolution")

# Wolf traits with twin y-axis
axs[1, 0].clear()
ax1 = axs[1, 0]
ax1.set_xlabel("Step")
ax1.set_ylabel("Wolf Speed", color='tab:purple')
ax1.plot(steps, [row["wolf_speed_avg"] for row in log], color='tab:purple')
ax1.tick_params(axis='y', labelcolor='tab:purple')

ax2 = ax1.twinx()
ax2.set_ylabel("Wolf Sight", color='tab:green')
ax2.plot(steps, [row["wolf_sight_avg"] for row in log], color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')
ax1.set_title("Wolf Trait Evolution")

if all(k in mutation_stats for k in [
    "step",
    "deer_mutation_rate", "deer_mutation_speed_avg", "deer_mutation_sight_avg",
    "wolf_mutation_rate", "wolf_mutation_speed_avg", "wolf_mutation_sight_avg"
]):
    axs[1, 1].plot(mutation_stats["step"], mutation_stats["deer_mutation_rate"], label="Deer Mutation Rate", color='tab:red')
    axs[1, 1].plot(mutation_stats["step"], mutation_stats["deer_mutation_speed_avg"], label="Deer Speed Mutation", color='tab:pink')
    axs[1, 1].plot(mutation_stats["step"], mutation_stats["deer_mutation_sight_avg"], label="Deer Sight Mutation", color='tab:cyan')
    axs[1, 1].plot(mutation_stats["step"], mutation_stats["wolf_mutation_rate"], label="Wolf Mutation Rate", color='tab:olive')
    axs[1, 1].plot(mutation_stats["step"], mutation_stats["wolf_mutation_speed_avg"], label="Wolf Speed Mutation", color='tab:blue')
    axs[1, 1].plot(mutation_stats["step"], mutation_stats["wolf_mutation_sight_avg"], label="Wolf Sight Mutation", color='tab:orange')
    axs[1, 1].set_title("Mutation Trends")
    axs[1, 1].set_xlabel("Step")
    axs[1, 1].set_ylabel("Mutation Value")
    axs[1, 1].legend()
    axs[1, 1].grid(True)
else:
    axs[1, 1].text(0.5, 0.5, "Mutation data missing", ha='center', va='center', transform=axs[1, 1].transAxes)
    axs[1, 1].set_title("Mutation Trends")
    axs[1, 1].axis('off')

fig.suptitle("Evolution Dashboard", fontsize=16)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(dashboard_path)
print(f"Saved dashboard plot to: {dashboard_path}")

pygame.quit()