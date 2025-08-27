import os
import random
from collections import deque

import pygame

# ===== constants =====
CELL = 24
GRID_W, GRID_H = 24, 20
SCREEN_W, SCREEN_H = GRID_W * CELL, GRID_H * CELL

BG   = (18, 18, 18)
GRID = (40, 40, 40)
HEAD = (0, 200, 120)
BODY = (0, 150, 100)
FOOD = (220, 70, 90)
TEXT = (235, 235, 235)

STEP_MS = 120                    # one move per this many ms
MOVE_EVENT = pygame.USEREVENT + 1

SFX_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx", "game_over.ogg")

# ===== helpers =====
def draw_grid(surface):
    for x in range(GRID_W):
        pygame.draw.line(surface, GRID, (x * CELL, 0), (x * CELL, SCREEN_H))
    for y in range(GRID_H):
        pygame.draw.line(surface, GRID, (0, y * CELL), (SCREEN_W, y * CELL))

def draw_snake(surface, snake):
    for i, (gx, gy) in enumerate(snake):
        rect = pygame.Rect(gx * CELL, gy * CELL, CELL, CELL)
        color = HEAD if i == 0 else BODY
        radius = 7 if i == 0 else 5
        pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_food(surface, fx, fy):
    rect = pygame.Rect(fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4)
    pygame.draw.rect(surface, FOOD, rect, border_radius=6)

def set_direction(current_dir, requested):
    """Prevent 180° reversal."""
    dx, dy = current_dir
    rdx, rdy = requested
    if (rdx, rdy) == (-dx, -dy):
        return current_dir
    return requested

def random_empty_cell(occupied):
    while True:
        pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
        if pos not in occupied:
            return pos

# ===== main =====
def main():
    pygame.init()
    # audio (safe init)
    game_over_sound = None
    try:
        pygame.mixer.init()
        if os.path.isfile(SFX_PATH):
            game_over_sound = pygame.mixer.Sound(SFX_PATH)
    except Exception:
        game_over_sound = None  # audio optional

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Snake — food, growth, score, game over + sound")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=False)
    bigfont = pygame.font.SysFont("arial", 32, bold=True)

    def reset():
        start = (GRID_W // 2, GRID_H // 2)
        snake = deque([start, (start[0] - 1, start[1]), (start[0] - 2, start[1])])
        direction = (1, 0)
        next_direction = direction
        occupied = set(snake)
        food = random_empty_cell(occupied)
        score = 0
        return snake, direction, next_direction, food, score

    snake, direction, next_direction, food, score = reset()
    high_score = 0
    game_over = False
    played_sound = False

    pygame.time.set_timer(MOVE_EVENT, STEP_MS)
    running = True

    while running:
        # ---- events/input ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    next_direction = set_direction(direction, (-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    next_direction = set_direction(direction, (1, 0))
                elif event.key in (pygame.K_UP, pygame.K_w):
                    next_direction = set_direction(direction, (0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    next_direction = set_direction(direction, (0, 1))
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # restart
                    snake, direction, next_direction, food, score = reset()
                    game_over = False
                    played_sound = False

            elif event.type == MOVE_EVENT and not game_over:
                # move one cell
                direction = next_direction
                hx, hy = snake[0]
                dx, dy = direction
                nx, ny = hx + dx, hy + dy

                # wall collision -> game over
                if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H:
                    game_over = True

                # self collision -> game over
                elif (nx, ny) in snake:
                    game_over = True

                if game_over:
                    high_score = max(high_score, score)
                    if game_over_sound and not played_sound:
                        try:
                            game_over_sound.play()
                        except Exception:
                            pass
                    played_sound = True
                else:
                    # normal move
                    snake.appendleft((nx, ny))

                    # eat?
                    if (nx, ny) == food:
                        score += 1              # grow: do not pop tail
                        # respawn food
                        occupied = set(snake)
                        food = random_empty_cell(occupied)
                    else:
                        snake.pop()             # same length

        # ---- draw ----
        screen.fill(BG)
        draw_grid(screen)
        draw_snake(screen, snake)
        draw_food(screen, *food)

        # HUD
        hud = font.render(f"Score: {score}   High: {high_score}", True, TEXT)
        screen.blit(hud, (10, 8))

        if game_over:
            title = bigfont.render("Game Over", True, TEXT)
            sub = font.render("Press R to restart • Esc to quit", True, TEXT)
            trect = title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 14))
            srect = sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 18))
            screen.blit(title, trect)
            screen.blit(sub, srect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()




