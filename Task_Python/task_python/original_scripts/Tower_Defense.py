import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the clock
clock = pygame.time.Clock()

# Set up the tower class
class Tower:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.range = 100
        self.damage = 10

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.range, 2)
        pygame.draw.rect(screen, GREEN, (self.x - 10, self.y - 10, 20, 20))

# Set up the enemy class
class Enemy:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.health = 100
        self.speed = 2

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, 20, 20))

    def move(self):
        self.x += self.speed
        if self.x > WIDTH:
            self.x = 0
            self.y = random.randint(0, HEIGHT - 20)

# Set up the game variables
towers = []
enemies = []
score = 0
money = 100
multiplier = 1
weather = "Sunny"
chat_messages = []

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                towers.append(Tower(event.pos[0], event.pos[1]))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                chat_messages.append("Player: " + pygame.key.name(event.key - 32))
            else:
                chat_messages.append("Player: " + pygame.key.name(event.key))

    # Add enemies
    if random.random() < 0.05:
        enemies.append(Enemy(0, random.randint(0, HEIGHT - 20)))

    # Move enemies
    for enemy in enemies:
        enemy.move()
        if enemy.x > WIDTH:
            enemies.remove(enemy)
            score -= 10 * multiplier

    # Draw everything
    screen.fill(WHITE)
    for tower in towers:
        tower.draw()
    for enemy in enemies:
        enemy.draw()

    # Check for collisions
    for tower in towers:
        for enemy in enemies:
            if ((tower.x - enemy.x) ** 2 + (tower.y - enemy.y) ** 2) ** 0.5 < tower.range:
                enemy.health -= tower.damage / 60
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 10 * multiplier
                    money += 10 * multiplier
                    multiplier += 0.1

    # Update weather
    if random.random() < 0.01:
        weather = random.choice(["Sunny", "Rainy", "Windy"])
    if weather == "Rainy":
        for enemy in enemies:
            enemy.speed = 1
    else:
        for enemy in enemies:
            enemy.speed = 2

    # Draw score, money, and weather
    score_text = font.render(f'Score: {int(score)}', True, (0, 0, 0))
    money_text = font.render(f'Money: {int(money)}', True, (0, 0, 0))
    weather_text = font.render(f'Weather: {weather}', True, (0, 0, 0))
    multiplier_text = font.render(f'Multiplier: {int(multiplier)}x', True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(money_text, (10, 50))
    screen.blit(weather_text, (10, 90))
    screen.blit(multiplier_text, (10, 130))

    # Draw chat messages
    y = 170
    for message in chat_messages[-5:]:
        chat_text = font.render(message, True, (0, 0, 0))
        screen.blit(chat_text, (10, y))
        y += 40

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)