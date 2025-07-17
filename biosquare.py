# Add mutation tracking and visualization (fixed)
import pygame
import random
import os
import csv
import matplotlib.pyplot as plt

MAX_DEERS = 150
MAX_WOLVES = 100
square = 1000
screen = pygame.display.set_mode((square,square))

mutation_stats = {
    "step": [],
    "mutation_count": [],
    "mutation_rate_actual": [],
    "mutation_speed_avg": [],
    "mutation_sight_avg": []
}

mutation_counter = 0
mutation_speed_total = 0
mutation_sight_total = 0
mutation_events = 0

def reset_mutation_stats():
    global mutation_counter, mutation_speed_total, mutation_sight_total, mutation_events
    mutation_counter = 0
    mutation_speed_total = 0
    mutation_sight_total = 0
    mutation_events = 0

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

def mutate_trait(value, mutation_rate=0.3, mutation_strength=0.5):
    global mutation_counter, mutation_speed_total, mutation_sight_total, mutation_events
    if random.random() < mutation_rate:
        mutation_counter += 1
        delta = random.uniform(-mutation_strength, mutation_strength)
        mutation_events += 1
        if value < 50:  # speed typically ~10-20
            mutation_speed_total += abs(delta)
        else:           # sight typically ~150-300
            mutation_sight_total += abs(delta)
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

    def reproduce(self):
        return Deer(
            color=self.color,
            sight=mutate_trait(self.sight),
            speed=mutate_trait(self.speed),
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

    def reproduce(self):
        return Wolf(
            color=self.color,
            sight=mutate_trait(self.sight),
            speed=mutate_trait(self.speed),
            lifespan=self.lifespan,
            generation=self.generation + 1
        )

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

        # Log mutation stats
        mutation_stats["step"].append(step)
        mutation_stats["mutation_count"].append(mutation_counter)
        mutation_stats["mutation_rate_actual"].append(mutation_counter / max(1, len(new_deers)*2))
        mutation_stats["mutation_speed_avg"].append(mutation_speed_total / max(1, mutation_events))
        mutation_stats["mutation_sight_avg"].append(mutation_sight_total / max(1, mutation_events))

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

# Save mutation plot
mutation_folder = "/Users/yeriming/Downloads/Biosquare/Mutation"
mutation_path = get_file(mutation_folder, base_name="mutation_plot", extension=".png")

plt.figure()
plt.plot(mutation_stats["step"], mutation_stats["mutation_rate_actual"], label="Mutation Rate")
plt.plot(mutation_stats["step"], mutation_stats["mutation_speed_avg"], label="Avg Speed Mutation")
plt.plot(mutation_stats["step"], mutation_stats["mutation_sight_avg"], label="Avg Sight Mutation")
plt.xlabel("Step")
plt.ylabel("Mutation Metric")
plt.title("Mutation Trends Over Time")
plt.legend()
plt.grid(True)
plt.savefig(mutation_path)
print(f"Saved mutation plot to: {mutation_path}")

pygame.quit()