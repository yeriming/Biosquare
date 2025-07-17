import pygame
import random

class Animal():
    def __init__(self, sight, speed, lifespan, color='black', position=None):
        self.sight = sight
        self.steps = 0
        self.speed = speed
        self.direction = self.get_random_direction()        
        self.lifespan = lifespan
        self.color = color
        self.position = position
        if position is None:
            self.position = self.get_random_position()

    def get_modular_position(self):
        if self.position.x < 0: 
            self.position.x += square
        if self.position.x > square:
            self.position.x -= square
        if self.position.y < 0:
            self.position.y += square
        if self.position.y > square:
            self.position.y -= square

    def get_random_position(self):
        x = random.random()*square
        y = random.random()*square
        position = pygame.Vector2(x,y)
        return position

    def get_random_direction(self):
        x = random.randint(-1, 1)
        y = random.randint(-1, 1)
        direction = pygame.Vector2(x,y)
        if direction.length() > 0.0:
            direction = direction.normalize()
        return direction

    def get_animals_in_sight(self, animals):
        animals_in_sight = []
        for animal in animals:
            if self.position.distance_to(animal.position) < self.sight:
                animals_in_sight.append(animal)
        return animals_in_sight

    def get_closest_animal(self, animals):
        distances = []
        for animal in animals:
            distances.append(self.position.distance_to(animal.position))
        closest_animal = animals[distances.index(min(distances))]
        return closest_animal

    def draw(self):
        pygame.draw.circle(screen, self.color, self.position, 10)

def mutate_trait(value, mutation_rate=0.1, mutation_strength=0.1):
    """
    Applies random mutation to a given trait.
    Returns the modified value or original depending on mutation rate.
    """
    if random.random() < mutation_rate:
        return value + random.uniform(-mutation_strength, mutation_strength)
    return value

class Deer(Animal):
    def move(self):
        wolves_in_sight = self.get_animals_in_sight(wolves)
        if len(wolves_in_sight) > 0:
            self.set_flee_direction(wolves_in_sight)
            self.position += self.speed*self.direction
        else:
            self.set_wander_direction()
            self.position += self.speed*self.direction
        self.get_modular_position()

    def set_flee_direction(self, predators):
        direction = pygame.Vector2(0, 0)
        for predator in predators:
            metric = self.position.distance_to(predator.position)
            direction += (self.position - predator.position)/metric
        self.direction = direction

    def set_wander_direction(self):
        if random.random() > 0.4:
            self.direction = self.get_random_direction()

    def reproduce(self):
        """
        Returns a new Deer with mutated traits based on this one's attributes.
        """
        return Deer(
            color=self.color,
            sight=mutate_trait(self.sight),
            speed=mutate_trait(self.speed),
            lifespan=self.lifespan
        )

class Wolf(Animal):
    def move(self):
        self.steps += 1
        deers_in_sight = self.get_animals_in_sight(deers)
        if len(deers_in_sight) > 0:
            self.set_chase_direction(deers_in_sight)
            self.position += self.speed*self.direction
        else:
            self.set_wander_direction()
            self.position += self.speed*self.direction

    def set_chase_direction(self, preys):
        prey = self.get_closest_animal(preys)
        direction = prey.position - self.position
        if direction.length() > 0.0:
            direction = direction.normalize()
        self.direction = direction

    def set_wander_direction(self):
        if random.random() > 0.6:
            self.direction = self.get_random_direction()

    def reproduce(self):
        """
        Returns a new Wolf with mutated traits based on this one's attributes.
        """
        return Wolf(
            color=self.color,
            sight=mutate_trait(self.sight),
            speed=mutate_trait(self.speed),
            lifespan=self.lifespan
        )

pygame.init()

square = 1000
screen = pygame.display.set_mode((square,square))

number_deers = 10
deers = []

number_wolves = 4
wolves = []
for n in range(number_wolves):
    wolves.append(Wolf(color='grey', sight=300, speed=15, lifespan=100))

running = True
while running:
    screen.fill('white')

    while len(deers) < number_deers:
        parent = random.choice(deers)
        deers.append(parent.reproduce())

    for deer in deers:
        deer.move()
        deer.draw()
        
    for wolf in wolves:
        wolf.move()
        wolf.draw()
        closest_deer = wolf.get_closest_animal(deers)
        if wolf.position.distance_to(closest_deer.position) < 20:
            deers.remove(closest_deer)
            wolf.steps = 0
            wolves.append(wolf.reproduce())
        if wolf.steps == wolf.lifespan:
            wolves.remove(wolf)

    if len(wolves) == 0:
        running = False

    pygame.display.flip()
    pygame.time.wait(1000) # milliseconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
