"""
Project: HCASA Mission 1 - QuadraControl Symphony
Status: FINAL ULTIMATE 
Features: Spatial Audio, HUD, GPS, Shadow, Scanlines, NSOE, Smart Flight Tag
"""
import pygame
import math
import os
import sys
import random

# --- CONFIGURATION SYSTÈME ---
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# 1. Initialisation
pygame.init()
pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HCASA Mission 1: QuadraControl Symphony | Tactical Radar System | Bertold & Loic")
# Polices
font_hud = pygame.font.SysFont("Consolas", 14) 
font_gps = pygame.font.SysFont("Consolas", 12) 
font_title = pygame.font.SysFont("Arial", 16, bold=True)
font_warn = pygame.font.SysFont("Arial Black", 12)
font_compass = pygame.font.SysFont("Impact", 22) 
font_tag = pygame.font.SysFont("Consolas", 10, bold=True)

# 2. Chargement Sons
sound_files = ["bas_droite.mp3", "bas_gauche.mp3","haut_droite.mp3","haut_gauche.mp3"]
channels = [] 
sound_names = ["CH-A", "CH-B", "CH-C", "CH-D"]

for file in sound_files:
    if os.path.exists(file):
        try:
            s = pygame.mixer.Sound(file)
            chan = s.play(loops=-1)
            chan.set_volume(0.0)
            channels.append(chan)
        except: pass

# 3. Images
avion_img = None
shadow_img = None
if os.path.exists("avion.png"):
    try:
        avion_img = pygame.image.load("avion.png").convert_alpha()
        avion_img = pygame.transform.scale(avion_img, (45, 45))
        shadow_img = avion_img.copy()
        shadow_img.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        shadow_img.set_alpha(150) 
    except: pass

# --- VARIABLES ---
trainee_fumee = [] 
shockwaves = []
last_mouse_pos = pygame.mouse.get_pos()
angle = 0 
is_muted = False 
radar_angle = 0 
lock_anim_angle = 0 

corners = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
wave_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255), (255, 255, 0)]

# Texture CRT (Scanlines)
crt_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 3):
    pygame.draw.line(crt_surface, (0, 0, 0, 80), (0, y), (WIDTH, y), 1)

def get_volume(pos_avion, pos_coin, max_dist):
    dist = math.hypot(pos_avion[0] - pos_coin[0], pos_avion[1] - pos_coin[1])
    return max(0.0, 1.0 - (dist / (max_dist * 0.8)))**2

def get_gps(mouse_x, mouse_y):
    lat = 55.0 - (mouse_y / HEIGHT * 8.0)
    lon = 6.0 + (mouse_x / WIDTH * 9.0)
    return lat, lon

# --- CALCULS DE VOL ---
def calculate_flight_data(mouse_pos, last_pos):
    dx = mouse_pos[0] - last_pos[0]
    dy = mouse_pos[1] - last_pos[1]
    speed_px = math.hypot(dx, dy)
    knots = int(speed_px * 15) 
    altitude = int((HEIGHT - mouse_pos[1]) * 65) 
    if altitude < 0: altitude = 0
    return knots, altitude

# --- RADAR OVERLAY ---
def draw_radar_overlay(surface):
    grid_color = (20, 50, 20) 
    center = (WIDTH//2, HEIGHT//2)
    
    for x in range(0, WIDTH, 100): pygame.draw.line(surface, grid_color, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 100): pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y), 1)
    for r in range(100, 500, 100): pygame.draw.circle(surface, (30, 80, 30), center, r, 1)
    
    pygame.draw.line(surface, (50, 200, 50), (center[0]-10, center[1]), (center[0]+10, center[1]), 1)
    pygame.draw.line(surface, (50, 200, 50), (center[0], center[1]-10), (center[0], center[1]+10), 1)

    compass_color = (100, 200, 100) 
    txt_n = font_compass.render("N", True, compass_color)
    surface.blit(txt_n, (center[0] - txt_n.get_width()//2, 20))
    txt_o = font_compass.render("O", True, compass_color)
    surface.blit(txt_o, (20, center[1] - txt_o.get_height()//2))
    txt_e = font_compass.render("E", True, compass_color)
    surface.blit(txt_e, (WIDTH - 40, center[1] - txt_e.get_height()//2))
    txt_s = font_compass.render("S", True, compass_color)
    surface.blit(txt_s, (center[0] - txt_s.get_width()//2, HEIGHT - 210))

# --- NOUVEAU : DESSIN ÉTIQUETTE INTELLIGENTE (Direction Centre) ---
def draw_flight_tag(surface, pos, speed, alt):
    color = (200, 255, 200)
    
    # Centre de l'écran
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # Vecteur direction vers le centre (Centre - Avion)
    dir_x = center_x - pos[0]
    dir_y = center_y - pos[1]
    
    # Distance pour normaliser
    distance = math.hypot(dir_x, dir_y)
    
    # Longueur de la ligne de l'étiquette
    line_length = 60
    
    # Calcul du point final (tag_end)
    if distance > 0:
        # Normalisation et multiplication par la longueur
        offset_x = (dir_x / distance) * line_length
        offset_y = (dir_y / distance) * line_length
    else:
        # Si on est pile au centre (cas rare), on décale par défaut
        offset_x, offset_y = 50, 50
        
    tag_end = (pos[0] + offset_x, pos[1] + offset_y)
    
    # Dessin de la ligne
    pygame.draw.line(surface, color, pos, tag_end, 1)
    # Petit rond au bout de la ligne
    pygame.draw.circle(surface, color, (int(tag_end[0]), int(tag_end[1])), 2)
    
    # Textes
    lines = [
        "AF1042",           
        f"A:{alt:03d}",     
        f"S:{speed}kt"      
    ]
    
    # Ajustement position texte pour ne pas chevaucher la ligne
    # Si on pointe vers la gauche, on décale le texte un peu plus à gauche
    text_offset_x = 5
    if offset_x < 0: text_offset_x = -45 # Décalage inverse si on pointe vers la gauche
        
    for i, line in enumerate(lines):
        txt = font_tag.render(line, True, color)
        # On ajoute un petit fond noir semi-transparent pour la lisibilité
        bg_rect = txt.get_rect(topleft=(tag_end[0] + text_offset_x, tag_end[1] - 15 + (i * 10)))
        surf_bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        surf_bg.fill((0,0,0,150))
        surface.blit(surf_bg, bg_rect.topleft)
        
        surface.blit(txt, bg_rect.topleft)

# --- FAISCEAU RADAR ---
def draw_radar_sweep(surface, angle):
    center = (WIDTH//2, HEIGHT//2)
    length = 600
    for i in range(25): 
        theta = math.radians(angle - i)
        alpha = 255 - (i * 10) 
        if alpha < 0: alpha = 0
        end_x = center[0] + length * math.cos(theta)
        end_y = center[1] - length * math.sin(theta)
        beam_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        color = (0, 255, 0, alpha//3)
        pygame.draw.line(beam_surf, color, center, (end_x, end_y), 4)
        surface.blit(beam_surf, (0,0))
    rad = math.radians(angle)
    ex = center[0] + length * math.cos(rad)
    ey = center[1] - length * math.sin(rad)
    pygame.draw.line(surface, (150, 255, 150), center, (ex, ey), 2)

# --- HUD (CENTRÉ) ---
def draw_hud(surface, volumes, mouse_pos):
    hud_width = 290
    hud_height = 180
    start_x = (WIDTH - hud_width) // 2 
    start_y = HEIGHT - 190

    overlay = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 10, 0, 240), overlay.get_rect(), border_radius=20)
    pygame.draw.rect(overlay, (40, 120, 40), overlay.get_rect(), 2, border_radius=20)
    surface.blit(overlay, (start_x, start_y))
    
    title = font_title.render("SIGNAL ANALYSIS", True, (120, 255, 120))
    surface.blit(title, (start_x + 75, start_y + 10))
    
    lat, lon = get_gps(mouse_pos[0], mouse_pos[1])
    gps_surf = font_gps.render(f"POS: {lat:.4f}N {lon:.4f}E", True, (0, 255, 255))
    surface.blit(gps_surf, (start_x + 70, start_y + 30))
    
    for i, vol in enumerate(volumes):
        current_y = start_y + 60 + (i * 20)
        text = font_hud.render(f"{sound_names[i]}: {int(vol*100):>3}%", True, (150, 255, 150))
        surface.blit(text, (start_x + 20, current_y))
        bar_x = start_x + 130
        bar_w = int(vol * 130)
        pygame.draw.rect(surface, wave_colors[i], (bar_x, current_y + 5, bar_w, 6))
        pygame.draw.rect(surface, (50, 100, 50), (bar_x, current_y + 5, 130, 6), 1)

    col = (255, 50, 50) if is_muted else (50, 255, 50)
    txt = "MUTED" if is_muted else "ON"
    info = font_hud.render(f"SND:{txt} | [R] RESET | [ESC]", True, col)
    surface.blit(info, (start_x + 35, start_y + 150))

# --- TARGET LOCK ---
def draw_target_lock(surface, pos, is_locked):
    if is_locked:
        size = 60
        rect_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, (255, 0, 0), (0, 0, size, size), 2)
        rotated_surf = pygame.transform.rotate(rect_surf, lock_anim_angle)
        rect = rotated_surf.get_rect(center=pos)
        surface.blit(rotated_surf, rect.topleft)
        
        if (pygame.time.get_ticks() // 200) % 2 == 0:
            txt = font_warn.render("TARGET LOCKED", True, (255, 50, 50))
            txt_rect = txt.get_rect(center=(pos[0], pos[1] - 45))
            surface.blit(txt, txt_rect)


# --- BOUCLE PRINCIPALE ---
running = True
clock = pygame.time.Clock()
max_distance = math.hypot(WIDTH, HEIGHT)

while running:
    mouse_pos = pygame.mouse.get_pos()
    current_volumes = [0.0, 0.0, 0.0, 0.0] 
    
    # Calcul des données de vol (Vitesse / Alt)
    speed_knots, altitude_ft = calculate_flight_data(mouse_pos, last_mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key == pygame.K_m: is_muted = not is_muted
            if event.key == pygame.K_r: pygame.mouse.set_pos(WIDTH//2, HEIGHT//2)

    # 1. CALCUL AUDIO
    max_vol_found = 0.0
    if len(channels) == 4:
        for i in range(4):
            vol = get_volume(mouse_pos, corners[i], max_distance)
            final_vol = 0.0 if is_muted else vol
            channels[i].set_volume(final_vol)
            current_volumes[i] = final_vol 
            if vol > max_vol_found: max_vol_found = vol 
            if not is_muted and vol > 0.6 and random.randint(0, 20) == 0:
                shockwaves.append({'pos': corners[i], 'radius': 10, 'alpha': 255, 'color': wave_colors[i]})

    # 2. DESSIN FOND
    screen.fill((5, 15, 5)) 
    draw_radar_overlay(screen)
    
    # 3. HUD (Centré)
    draw_hud(screen, current_volumes, mouse_pos)

    # 4. BALAYAGE
    radar_angle = (radar_angle + 3) % 360
    draw_radar_sweep(screen, radar_angle)

    # 5. ONDES
    for wave in shockwaves[:]:
        wave['radius'] += 4
        wave['alpha'] -= 4
        if wave['alpha'] <= 0: shockwaves.remove(wave)
        else:
            s = pygame.Surface((wave['radius']*2, wave['radius']*2), pygame.SRCALPHA)
            color_with_alpha = (*wave['color'], wave['alpha'])
            pygame.draw.circle(s, color_with_alpha, (wave['radius'], wave['radius']), wave['radius'], 3)
            screen.blit(s, (wave['pos'][0] - wave['radius'], wave['pos'][1] - wave['radius']))

    # 6. FUMÉE
    trainee_fumee.append({'pos': list(mouse_pos), 'alpha': 255, 'size': 5})
    if len(trainee_fumee) > 40: trainee_fumee.pop(0)
    for p in trainee_fumee:
        p['alpha'] -= 6
        p['size'] += 0.1
        if p['alpha'] > 0:
            smoke_surf = pygame.Surface((int(p['size']*2), int(p['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surf, (150, 180, 150, int(p['alpha'])), (int(p['size']), int(p['size'])), int(p['size']))
            screen.blit(smoke_surf, (p['pos'][0] - p['size'], p['pos'][1] - p['size']))

    # 7. AVION & LOCK
    dx = mouse_pos[0] - last_mouse_pos[0]
    dy = mouse_pos[1] - last_mouse_pos[1]
    if abs(dx) > 0 or abs(dy) > 0:
        angle = math.degrees(math.atan2(-dy, dx)) 
    
    lock_anim_angle = (lock_anim_angle + 5) % 360
    draw_target_lock(screen, mouse_pos, max_vol_found > 0.85)

    if avion_img and shadow_img:
        rotated_shadow = pygame.transform.rotate(shadow_img, angle)
        shadow_rect = rotated_shadow.get_rect(center=(mouse_pos[0]+15, mouse_pos[1]+15))
        screen.blit(rotated_shadow, shadow_rect.topleft)
        rotated_avion = pygame.transform.rotate(avion_img, angle)
        new_rect = rotated_avion.get_rect(center=mouse_pos)
        screen.blit(rotated_avion, new_rect.topleft)
    else:
        pygame.draw.circle(screen, (0, 255, 0), mouse_pos, 15)

    # 8. ETIQUETTE DE VOL (Pointant vers le centre)
    draw_flight_tag(screen, mouse_pos, speed_knots, altitude_ft)

    # 9. SCANLINES
    screen.blit(crt_surface, (0,0))
    
    last_mouse_pos = mouse_pos

    pygame.display.flip()
    clock.tick(60)
pygame.quit()