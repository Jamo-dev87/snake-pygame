import os
import random
from collections import deque
import pygame

# =========================
# CONFIG
# =========================
CELL = 28
GRID_W, GRID_H = 22, 18
SCREEN_W, SCREEN_H = GRID_W * CELL, GRID_H * CELL

BG_TOP    = (15, 16, 22)
BG_BOTTOM = (12, 12, 18)
TEXT      = (235, 235, 235)

PURPLE_BODY = (120, 50, 200)
PURPLE_HEAD = (150, 70, 230)
STEM_GREEN  = (70, 175, 80)

PEACH_L     = (255, 160, 150)
PEACH_R     = (255, 175, 120)
PEACH_LINE  = (215, 120, 140)
LEAF_GREEN  = (85, 190, 95)

STEP_MS      = 110
MOVE_EVENT   = pygame.USEREVENT + 1
EDGE_MARGIN  = 1

ASSETS_DIR   = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
IMG_EGGPLANT = os.path.join(ASSETS_DIR, "img", "eggplant.png")
IMG_PEACH    = os.path.join(ASSETS_DIR, "img", "peach.png")
SFX_GAMEOVER = os.path.join(ASSETS_DIR, "sfx", "game_over.ogg")

# =========================
# UTILS
# =========================
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def grid_to_center(gx: float, gy: float) -> tuple[int, int]:
    return int((gx + 0.5) * CELL), int((gy + 0.5) * CELL)

def random_empty_cell(occupied: set[tuple[int, int]], margin: int) -> tuple[int, int]:
    xs = range(margin, GRID_W - margin)
    ys = range(margin, GRID_H - margin)
    while True:
        pos = (random.choice(xs), random.choice(ys))
        if pos not in occupied:
            return pos

def load_image(path: str, size: int):
    try:
        if os.path.isfile(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (size, size))
    except Exception:
        pass
    return None

# =========================
# RENDERING
# =========================
def draw_bg(surface: pygame.Surface):
    surface.fill(BG_BOTTOM)
    h = surface.get_height()
    band = pygame.Surface((surface.get_width(), 2), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(lerp(BG_TOP[0], BG_BOTTOM[0], t))
        g = int(lerp(BG_TOP[1], BG_BOTTOM[1], t))
        b = int(lerp(BG_TOP[2], BG_BOTTOM[2], t))
        band.fill((r, g, b))
        surface.blit(band, (0, y))

def draw_peach(surface: pygame.Surface, center: tuple[int, int], img: pygame.Surface | None):
    if img:
        surface.blit(img, img.get_rect(center=center))
        return
    cx, cy = center
    r = int(CELL * 0.42)
    pygame.draw.circle(surface, PEACH_L, (cx - r // 2, cy), r)
    pygame.draw.circle(surface, PEACH_R, (cx + r // 2, cy), r)
    pygame.draw.line(surface, PEACH_LINE, (cx, cy - r), (cx, cy + r), 2)
    leaf = [(cx + r // 2, cy - r - 2),
            (cx + r // 2 + 8, cy - r - 6),
            (cx + r // 2 + 3, cy - r - 12)]
    pygame.draw.polygon(surface, LEAF_GREEN, leaf)

def draw_eggplant_snake(surface: pygame.Surface, points: list[tuple[float, float]],
                        head_dir: tuple[int, int], head_img: pygame.Surface | None):
    if len(points) < 2:
        return
    width = int(CELL * 0.76)
    for i in range(len(points) - 1, 0, -1):
        pygame.draw.line(surface, PURPLE_BODY, points[i], points[i - 1], width)
    radius = width // 2
    for p in points:
        pygame.draw.circle(surface, PURPLE_BODY, (int(p[0]), int(p[1])), radius)

    hx, hy = points[0]
    if head_img:
        dx, dy = head_dir
        angle = 0
        if   (dx, dy) == (1, 0):  angle = 0
        elif (dx, dy) == (-1, 0): angle = 180
        elif (dx, dy) == (0, -1): angle = 90
        elif (dx, dy) == (0, 1):  angle = -90
        sprite = pygame.transform.rotate(head_img, angle)
        surface.blit(sprite, sprite.get_rect(center=(int(hx), int(hy))))
    else:
        pygame.draw.circle(surface, PURPLE_HEAD, (int(hx), int(hy)), int(CELL * 0.48))
        dx, dy = head_dir
        stem_w = max(6, CELL // 6)
        stem_h = max(6, CELL // 6)
        if   (dx, dy) == (1, 0):  stem_rect = (int(hx + CELL*0.35), int(hy - stem_h/2), stem_w, stem_h)
        elif (dx, dy) == (-1, 0): stem_rect = (int(hx - CELL*0.35) - stem_w, int(hy - stem_h/2), stem_w, stem_h)
        elif (dx, dy) == (0, -1): stem_rect = (int(hx - stem_w/2), int(hy - CELL*0.35) - stem_h, stem_w, stem_h)
        else:                     stem_rect = (int(hx - stem_w/2), int(hy + CELL*0.35), stem_w, stem_h)
        pygame.draw.rect(surface, STEM_GREEN, stem_rect, border_radius=4)

# =========================
# GAME
# =========================
def main():
    pygame.init()
    pygame.display.set_caption("Orchard Serpent — Pygame")

    game_over_sound = None
    try:
        pygame.mixer.init()
        if os.path.isfile(SFX_GAMEOVER):
            game_over_sound = pygame.mixer.Sound(SFX_GAMEOVER)
    except Exception:
        pass

    eggplant_img = load_image(IMG_EGGPLANT, CELL)
    peach_img    = load_image(IMG_PEACH, CELL)

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("arial", 18)
    big    = pygame.font.SysFont("arial", 32, bold=True)

    def reset():
        start = (GRID_W // 2, GRID_H // 2)
        s = deque([start, (start[0]-1, start[1]), (start[0]-2, start[1])])
        d = (1, 0)
        nd = d
        f = random_empty_cell(set(s), EDGE_MARGIN)
        sc = 0
        return s, d, nd, f, sc

    snake, direction, next_dir, food, score = reset()
    high = 0
    game_over = False
    last_step_ms = pygame.time.get_ticks()   # <- correct
    prev_snake = list(snake)

    pygame.time.set_timer(MOVE_EVENT, STEP_MS)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    nd = (-1, 0)
                    next_dir = nd if nd != (-direction[0], -direction[1]) else next_dir
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    nd = (1, 0)
                    next_dir = nd if nd != (-direction[0], -direction[1]) else next_dir
                elif event.key in (pygame.K_UP, pygame.K_w):
                    nd = (0, -1)
                    next_dir = nd if nd != (-direction[0], -direction[1]) else next_dir
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    nd = (0, 1)
                    next_dir = nd if nd != (-direction[0], -direction[1]) else next_dir
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # ---- FIXED: use pygame.time.get_ticks() (dot), not time_get_ticks() ----
                    snake, direction, next_dir, food, score = reset()
                    game_over = False
                    prev_snake = list(snake)
                    last_step_ms = pygame.time.get_ticks()  # <- correct
                    # (timer already running; no need to reset)

            elif event.type == MOVE_EVENT and not game_over:
                prev_snake = list(snake)
                direction = next_dir
                hx, hy = snake[0]
                dx, dy = direction
                nx, ny = hx + dx, hy + dy

                if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H or (nx, ny) in snake:
                    game_over = True
                    high = max(high, score)
                    if game_over_sound:
                        try: game_over_sound.play()
                        except Exception: pass
                else:
                    snake.appendleft((nx, ny))
                    if (nx, ny) == food:
                        score += 1
                        food = random_empty_cell(set(snake), EDGE_MARGIN)
                    else:
                        snake.pop()
                last_step_ms = pygame.time.get_ticks()

        # ----- render with interpolation -----
        now = pygame.time.get_ticks()
        t = max(0.0, min(1.0, (now - last_step_ms) / STEP_MS))

        render_pts = []
        for i in range(len(snake)):
            a = prev_snake[i] if i < len(prev_snake) else snake[i]
            b = snake[i]
            gx = lerp(a[0], b[0], t)
            gy = lerp(a[1], b[1], t)
            render_pts.append(grid_to_center(gx, gy))

        draw_bg(screen)
        draw_peach(screen, grid_to_center(food[0], food[1]), peach_img)
        draw_eggplant_snake(screen, render_pts, direction, eggplant_img)

        hud = font.render(f"Score: {score}   High: {high}", True, TEXT)
        screen.blit(hud, (12, 8))

        if game_over:
            title = big.render("Game Over", True, TEXT)
            sub   = font.render("Press R to restart • Esc to quit", True, TEXT)
            screen.blit(title, title.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 14)))
            screen.blit(sub,   sub.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 18)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()


