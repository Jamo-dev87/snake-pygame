import pygame

# ===== constants =====
CELL = 24
GRID_W, GRID_H = 24, 20
SCREEN_W, SCREEN_H = GRID_W * CELL, GRID_H * CELL

BG   = (18, 18, 18)
GRID = (40, 40, 40)
HEAD = (0, 200, 120)

# move one cell every N milliseconds (snake pace)
STEP_MS = 120
MOVE_EVENT = pygame.USEREVENT + 1  # a custom timer event

# ===== setup =====
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake - Stage 4 (grid-step movement)")
clock = pygame.time.Clock()

# snake head position on the grid
head_x, head_y = 10, 10

# current direction and “buffered” direction
direction = (1, 0)       # start moving right (dx, dy)
next_direction = (1, 0)  # keys update this; applied on each step tick

def draw_grid(surface):
    for x in range(GRID_W):
        pygame.draw.line(surface, GRID, (x * CELL, 0), (x * CELL, SCREEN_H))
    for y in range(GRID_H):
        pygame.draw.line(surface, GRID, (0, y * CELL), (SCREEN_W, y * CELL))

def draw_head(surface, gx, gy):
    rect = pygame.Rect(gx * CELL, gy * CELL, CELL, CELL)
    pygame.draw.rect(surface, HEAD, rect, border_radius=6)

def set_direction(dx, dy):
    """Update next_direction but prevent instant 180° reversals."""
    global next_direction, direction
    if (-dx, -dy) == direction:
        return
    next_direction = (dx, dy)

# fire MOVE_EVENT every STEP_MS ms
pygame.time.set_timer(MOVE_EVENT, STEP_MS)

running = True
while running:
    # --- events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):   set_direction(-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d): set_direction( 1, 0)
            elif event.key in (pygame.K_UP, pygame.K_w):    set_direction( 0,-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):  set_direction( 0, 1)
            elif event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == MOVE_EVENT:
            # apply buffered direction exactly once per “tick”
            direction = next_direction
            dx, dy = direction
            head_x += dx
            head_y += dy

            # keep in-bounds for now (we’ll add game over later)
            head_x = max(0, min(GRID_W - 1, head_x))
            head_y = max(0, min(GRID_H - 1, head_y))

    # --- draw ---
    screen.fill(BG)
    draw_grid(screen)
    draw_head(screen, head_x, head_y)
    pygame.display.flip()

    clock.tick(60)  # display refresh rate; movement is controlled by MOVE_EVENT

pygame.quit()


