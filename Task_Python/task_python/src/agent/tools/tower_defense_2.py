
import structlog, random, math
from typing import List

logger = structlog.get_logger()

# ---- YOUR ORIGINAL CLASSES (preserved, no pygame init at import) ----

class Tower:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.range = 100
        self.damage = 10
        self.level = 1

    def upgrade(self):
        self.level += 1
        self.range += 10
        self.damage += 5

class Enemy:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.speed = 2
        self.health = 100

    def move(self, width=800):
        self.x += self.speed
        if self.x > width:
            return True  # reached end
        return False

def simulate_tower_defense(towers_pos: List[dict], num_enemies: int = 20, width: int = 800, height: int = 600):
    towers = [Tower(t['x'], t['y']) for t in towers_pos]
    enemies = [Enemy(0, random.randint(0, height-20)) for _ in range(2)]
    score = 0
    money = 100
    multiplier = 1.0
    ticks = 0

    for _ in range(300):  # simulate 300 ticks
        ticks+=1
        if random.random() < 0.05 and len(enemies) < num_enemies:
            enemies.append(Enemy(0, random.randint(0, height-20)))

        to_remove = []
        for enemy in enemies:
            if enemy.move(width):
                to_remove.append(enemy)
                score -= 10 * multiplier

        for e in to_remove:
            if e in enemies:
                enemies.remove(e)

        for tower in towers:
            for enemy in list(enemies):
                dist = math.hypot(tower.x - enemy.x, tower.y - enemy.y)
                if dist < tower.range:
                    enemy.health -= tower.damage / 60
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        score += 10 * multiplier
                        money += 10 * multiplier
                        multiplier += 0.1
                        break

    return {
        "score": int(score),
        "money": int(money),
        "multiplier": round(multiplier,2),
        "towers": len(towers),
        "enemies_remaining": len(enemies),
        "ticks": ticks
    }

def simulate_reverse_tower(num_towers: int = 3):
    # Reverse Tower - enemies come from right, towers from left
    # Simplified simulation of your reverse_tower.py
    towers = [{"x": 100 + i*150, "y": 300} for i in range(num_towers)]
    return simulate_tower_defense(towers, num_enemies=15)

def run_full_pygame(mode: str = "tower_defense"):
    # This launches actual pygame window - for local dev only, not API
    import pygame, sys
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    towers = []
    enemies = []
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                towers.append(Tower(event.pos[0], event.pos[1]))

        if random.random() < 0.05:
            enemies.append(Enemy(0, random.randint(0, HEIGHT-20)))

        for enemy in list(enemies):
            if enemy.move(WIDTH):
                enemies.remove(enemy)
                score -= 10

        screen.fill((255,255,255))
        for tower in towers:
            pygame.draw.circle(screen, (0,255,0), (tower.x, tower.y), tower.range, 2)
            pygame.draw.rect(screen, (0,255,0), (tower.x-10, tower.y-10, 20, 20))
        for enemy in enemies:
            pygame.draw.rect(screen, (255,0,0), (enemy.x, enemy.y, 20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# ---- AGENT WRAPPERS ----
def run_defense(params: dict):
    logger.info("tool_start", tool="tower_defense", params=params)
    towers = params.get("towers", [{"x":100,"y":100},{"x":300,"y":300},{"x":500,"y":100}])
    num = int(params.get("num_enemies", 20))
    result = simulate_tower_defense(towers, num)
    return {"game": "tower_defense", **result}

def run_reverse(params: dict):
    logger.info("tool_start", tool="reverse_tower", params=params)
    num = int(params.get("num_towers", 3))
    result = simulate_reverse_tower(num)
    return {"game": "reverse_tower", **result}
