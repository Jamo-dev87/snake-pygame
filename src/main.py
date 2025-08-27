import pygame
from collections import deque

# ===== constants =====
CELL = 24
GRID_W, GRID_H = 24, 20
SCREEN_W, SCREEN_H = GRID_W * CELL, GRID_H * CELL

BG   = (18, 18, 18)
GRID = (40, 40, 40)
HEAD = (0, 200, 120)
BODY = (0, 150, 100)

STEP_MS = 120                   # one move per this many ms
MOVE_EVENT = pygame.USEREVENT + 1

# ===== small helpers =====
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

def set_direction(current_dir, requested):
    """Prevent 180° reversal: can't go directly opposite."""
    dx, dy = current_dir
    rdx, rdy = requested
    if (rdx, rdy) == (-dx, -dy):
        return current_dir
    return requested

# ===== main =====
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Snake — Stage 5 (body + grid-step movement)")
    clock = pygame.time.Clock()

    # snake body as deque of (x, y); head is index 0
    start = (GRID_W // 2, GRID_H // 2)
    snake = deque([start, (start[0] - 1, start[1]), (start[0] - 2, start[1])])

    direction = (1, 0)        # start moving right
    next_direction = direction

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

            elif event.type == MOVE_EVENT:
                # move one grid cell
                direction = next_direction
                hx, hy = snake[0]
                dx, dy = direction
                nx, ny = hx + dx, hy + dy

                # temporary wall clamp (we'll add game-over later)
                nx = max(0, min(GRID_W - 1, nx))
                ny = max(0, min(GRID_H - 1, ny))

                # add new head, remove tail (constant length for now)
                snake.appendleft((nx, ny))
                snake.pop()

        # ---- draw ----
        screen.fill(BG)
        draw_grid(screen)
        draw_snake(screen, snake)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()



