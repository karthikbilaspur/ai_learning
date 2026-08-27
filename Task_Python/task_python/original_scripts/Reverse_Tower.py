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

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the clock
clock = pygame.time.Clock()

# Set up the sounds
pygame.mixer.init()
enemy_sound = pygame.mixer.Sound('enemy_sound.wav')
tower_sound = pygame.mixer.Sound('tower_sound.wav')
score_sound = pygame.mixer.Sound('score_sound.wav')
background_music = pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.play(-1)

# Set up the enemy class
class Enemy:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.speed = 2
        self.health = 100

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, 20, 20))

    def move(self):
        self.x += self.speed

# Set up the tower class
class Tower:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.range = 100
        self.damage = 10
        self.level = 1

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.range, 2)
        pygame.draw.rect(screen, GREEN, (self.x - 10, self.y - 10, 20, 20))

    def upgrade(self):
        self.level += 1
        self.range += 10
        self.damage += 5

# Set up the game variables
enemies = [Enemy(0, random.randint(0, HEIGHT - 20))]
towers = []
score = 0

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                towers.append(Tower(event.pos[0], event.pos[1]))
                tower_sound.play()
            elif event.button == 3:
                for tower in towers:
                    if ((tower.x - event.pos[0]) ** 2 + (tower.y - event.pos[1]) ** 2) ** 0.5 < tower.range:
                        tower.upgrade()

    # Move enemies
    for enemy in enemies:
        enemy.move()
        if enemy.x > WIDTH:
            enemies.remove(enemy)
            score -= 10

    # Add new enemies
    if random.random() < 0.05:
        enemies.append(Enemy(0, random.randint(0, HEIGHT - 20)))
        enemy_sound.play()

    # Check for collisions
    for tower in towers:
        for enemy in enemies:
            if ((tower.x - enemy.x) ** 2 + (tower.y - enemy.y) ** 2) ** 0.5 < tower.range:
                enemy.health -= tower.damage / 60
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 10
                    score_sound.play()

    # Draw everything
    screen.fill(WHITE)
    for enemy in enemies:
        enemy.draw()
    for tower in towers:
        tower.draw()
    score_text = font.render(f'Score: {int(score)}', True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)