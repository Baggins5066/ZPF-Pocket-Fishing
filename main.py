import pygame
import random
import sys

# --- Game Config ---
WIDTH, HEIGHT = 800, 450
FPS = 60
FONT_NAME = 'arial'

# Fish types: name, price, weight
FISH_TYPES = [
    {'name': 'Bluegill', 'price': 1, 'weight': 7},
    {'name': 'Crappie', 'price': 2, 'weight': 5},
    {'name': 'Catfish', 'price': 2, 'weight': 5},
    {'name': 'Smallmouth bass', 'price': 5, 'weight': 2},
    {'name': 'Largemouth bass', 'price': 7, 'weight': 1}
]

# Colors
WHITE = (255,255,255)
LIGHT_BLUE = (136,255,255)
RED = (255,170,170)
BG_COLOR = (42,61,85)
BUTTON_COLOR = (68,68,255)

# --- Assets (placeholder) ---
PLAYER_IMG = pygame.Surface((32,32))
PLAYER_IMG.fill((200,200,255))
FISH_IMG = pygame.Surface((32,16))
FISH_IMG.fill((100,255,100))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pocket Fishing')
clock = pygame.time.Clock()
font = pygame.font.SysFont(FONT_NAME, 18)

# --- Game State ---
player_y = HEIGHT//4
is_casting = False
inventory = {f['name']: 0 for f in FISH_TYPES}
result_text = ''
result_alpha = 0
result_pos = (0,0)
result_color = LIGHT_BLUE
result_dir = -1
fade_timer = 0

# --- UI ---
def draw_backpack_btn():
    pygame.draw.rect(screen, BUTTON_COLOR, (10, HEIGHT//2-28, 56, 56), border_radius=16)
    pygame.draw.circle(screen, WHITE, (38, HEIGHT//2-6), 11)
    badge_text = font.render(str(sum(inventory.values())), True, BUTTON_COLOR)
    screen.blit(badge_text, (30, HEIGHT//2-14))
    # Backpack icon (placeholder)
    pygame.draw.rect(screen, (120,120,255), (18, HEIGHT//2-18, 32, 32), border_radius=8)

def draw_cast_btn(disabled):
    color = (180,180,180) if disabled else BUTTON_COLOR
    pygame.draw.rect(screen, color, (WIDTH//2-60, 20, 120, 40), border_radius=12)
    txt = font.render('Cast', True, WHITE)
    screen.blit(txt, (WIDTH//2-22, 30))

def draw_total_value():
    total = sum(inventory[f['name']] * f['price'] for f in FISH_TYPES)
    txt = font.render(f'Total Value: ${total}', True, WHITE)
    screen.blit(txt, (10, HEIGHT//2+36))

def draw_inventory_modal():
    modal_w, modal_h = 240, 320
    x, y = 76, HEIGHT//2-modal_h//2
    pygame.draw.rect(screen, (51,51,51), (x, y, modal_w, modal_h), border_radius=14)
    grid_x, grid_y = x+16, y+48
    has_items = False
    for i, f in enumerate(FISH_TYPES):
        count = inventory[f['name']]
        if count <= 0: continue
        has_items = True
        item_rect = pygame.Rect(grid_x, grid_y+i*56, 48, 48)
        pygame.draw.rect(screen, (100,255,100), item_rect, border_radius=8)
        badge = font.render(str(count), True, BUTTON_COLOR)
        screen.blit(badge, (grid_x+32, grid_y+i*56+32))
        name_txt = font.render(f['name'], True, WHITE)
        screen.blit(name_txt, (grid_x+56, grid_y+i*56+12))
    if not has_items:
        empty_txt = font.render('Inventory is empty', True, (170,170,170))
        screen.blit(empty_txt, (x+32, y+modal_h//2))

def weighted_random_fish():
    total_weight = sum(f['weight'] for f in FISH_TYPES)
    rand = random.uniform(0, total_weight)
    for f in FISH_TYPES:
        if rand < f['weight']:
            return f
        rand -= f['weight']
    return None

show_inventory = False
cast_btn_disabled = False

# --- Main Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Backpack button
            if 10 <= mx <= 66 and HEIGHT//2-28 <= my <= HEIGHT//2+28:
                show_inventory = not show_inventory
            # Cast button
            if not cast_btn_disabled and WIDTH//2-60 <= mx <= WIDTH//2+60 and 20 <= my <= 60:
                is_casting = True
                cast_btn_disabled = True
                # Animate rod down
                player_y = HEIGHT//2
                fade_timer = pygame.time.get_ticks() + random.randint(1000,5000)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                show_inventory = False

    # Animate rod up after wait
    if is_casting and pygame.time.get_ticks() > fade_timer > 0:
        player_y = HEIGHT//4
        is_casting = False
        cast_btn_disabled = False
        # Reveal catch
        selected_fish = weighted_random_fish()
        caught = selected_fish and random.random() < 0.7
        if caught:
            inventory[selected_fish['name']] += 1
            result_text = f"1+ {selected_fish['name']}"
            result_color = LIGHT_BLUE
            result_dir = -1
        else:
            result_text = "Nothing..."
            result_color = RED
            result_dir = 1
        result_alpha = 255
        result_pos = (WIDTH//2-140, player_y+16)
        fade_timer = pygame.time.get_ticks() + 2200

    # Fade result text
    if result_alpha > 0:
        result_pos = (result_pos[0], result_pos[1] + result_dir)
        txt = font.render(result_text, True, result_color)
        txt.set_alpha(result_alpha)
        screen.blit(txt, result_pos)
        result_alpha = max(0, result_alpha - 4)

    screen.fill(BG_COLOR)
    # Draw player
    screen.blit(PLAYER_IMG, (WIDTH//2-16, player_y-16))
    # Draw UI
    draw_backpack_btn()
    draw_cast_btn(cast_btn_disabled)
    draw_total_value()
    if show_inventory:
        draw_inventory_modal()
    pygame.display.flip()
    clock.tick(FPS)
