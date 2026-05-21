import pygame
import math
import random
import sys
import os
import wave
import struct

# --- SYSTÈME DE DÉBOGAGE ET INITIALISATION DE PYGAME ---
pygame.init()
pygame.font.init()

# Initialisation du mixer audio en mono 22050 Hz pour un style rétro
pygame.mixer.init(frequency=22050, size=-16, channels=1)

def generate_audio_assets():
    import os
    import wave
    import struct
    import math
    import random

    os.makedirs("assets", exist_ok=True)
    sample_rate = 22050

    def write_wav(filename, samples):
        path = os.path.join("assets", filename)
        if os.path.exists(path):
            return
        
        # Clamp and pack samples
        clamped = [int(max(-32768, min(32767, s))) for s in samples]
        packed = struct.pack(f"<{len(clamped)}h", *clamped)
        
        with wave.open(path, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            w.writeframes(packed)

    # 1. SFX HIT ("boom" croustillant rétro)
    # Mélange d'une onde carrée balayant vers le bas et de bruit blanc avec extinction rapide
    hit_samples = []
    num_samples_hit = int(0.25 * sample_rate)
    for i in range(num_samples_hit):
        t = i / sample_rate
        freq = 150 - (150 - 30) * (t / 0.25)
        phase = 2 * math.pi * (150 * t - 240 * t * t)
        sq = 0.7 * math.exp(-12 * t) * (1.0 if math.sin(phase) > 0 else -1.0)
        ns = 0.7 * math.exp(-40 * t) * random.uniform(-1.0, 1.0)
        hit_samples.append((sq + ns) * 32767)
    write_wav("sfx_hit.wav", hit_samples)

    # 2. SFX SWORD ("swoosh" de l'épée dans l'air)
    # Bruit blanc avec extinction rapide et une onde carrée descendante
    sword_samples = []
    num_samples_sword = int(0.20 * sample_rate)
    for i in range(num_samples_sword):
        t = i / sample_rate
        phase = 2 * math.pi * (800 * t - 1625 * t * t)
        sq = 0.3 * math.exp(-15 * t) * (1.0 if math.sin(phase) > 0 else -1.0)
        ns = 0.8 * math.exp(-15 * t) * random.uniform(-1.0, 1.0)
        sword_samples.append((sq + ns) * 32767)
    write_wav("sfx_sword.wav", sword_samples)

    # 3. SFX HURT ("screamer" métallique lors des blessures)
    # Onde carrée avec vibrato rapide
    hurt_samples = []
    num_samples_hurt = int(0.20 * sample_rate)
    for i in range(num_samples_hurt):
        t = i / sample_rate
        phase = 2 * math.pi * 350 * t - 3.75 * math.cos(80 * math.pi * t)
        sq = 0.7 * math.exp(-18 * t) * (1.0 if math.sin(phase) > 0 else -1.0)
        ns = 0.3 * math.exp(-30 * t) * random.uniform(-1.0, 1.0)
        hurt_samples.append((sq + ns) * 32767)
    write_wav("sfx_hurt.wav", hurt_samples)

    # 4. SFX DEFEAT (mélodie triste descendante)
    # Suite de 4 notes tristes sur onde carrée
    defeat_samples = []
    notes_def = [261.63, 207.65, 196.00, 174.61] # Do4, Sol#3, Sol3, Fa3
    phase = 0.0
    for i in range(int(0.8 * sample_rate)):
        t_total = i / sample_rate
        note_idx = int(t_total / 0.2)
        if note_idx > 3: note_idx = 3
        freq = notes_def[note_idx]
        
        t_note = (i % int(0.2 * sample_rate)) / sample_rate
        env = 0.6 * math.exp(-8 * t_note)
        
        phase += 2 * math.pi * freq / sample_rate
        sq = 1.0 if math.sin(phase) > 0 else -1.0
        defeat_samples.append(sq * env * 32767)
    write_wav("sfx_defeat.wav", defeat_samples)

    # 5. SFX VICTORY (fanfare triomphante ascendante)
    # Suite de 4 notes sur ondes triangulaires
    victory_samples = []
    notes_vic = [261.63, 329.63, 392.00, 523.25] # Do4, Mi4, Sol4, Do5
    phase = 0.0
    for i in range(int(0.6 * sample_rate)):
        t_total = i / sample_rate
        note_idx = int(t_total / 0.15)
        if note_idx > 3: note_idx = 3
        freq = notes_vic[note_idx]
        
        t_note = (i % int(0.15 * sample_rate)) / sample_rate
        env = 0.5 * math.exp(-5 * t_note)
        
        phase += 2 * math.pi * freq / sample_rate
        tri = 4.0 * abs((phase % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
        victory_samples.append(tri * env * 32767)
    write_wav("sfx_victory.wav", victory_samples)

    # 6. MUSIC LOOP (musique d'ambiance tendue de 8s)
    # Mélodie onde carrée + Basse onde triangulaire
    music_samples = []
    bass_notes = [
        55.00, 55.00, 55.00, 55.00, 55.00, 55.00, 55.00, 55.00, # A2
        65.41, 65.41, 65.41, 65.41, 65.41, 65.41, 65.41, 65.41, # C3
        73.42, 73.42, 73.42, 73.42, 73.42, 73.42, 73.42, 73.42, # D3
        82.41, 82.41, 82.41, 82.41, 82.41, 82.41, 82.41, 82.41, # E3
    ]
    melody_notes = [
        440.00, 493.88, 523.25, 659.25, # A4, Si4, Do5, Mi5
        587.33, 523.25, 493.88, 415.30, # Ré5, Do5, Si4, Sol#4
    ]

    phase_bass = 0.0
    phase_mel = 0.0
    step_duration = 0.25

    for i in range(int(8.0 * sample_rate)):
        t = i / sample_rate
        
        step_idx = int(t / step_duration)
        if step_idx > 31: step_idx = 31
        
        mel_idx = int(t / 1.0)
        if mel_idx > 7: mel_idx = 7
        
        t_step = t % step_duration
        t_note = t % 1.0
        
        # Basse (Triangle)
        freq_bass = bass_notes[step_idx]
        phase_bass += 2 * math.pi * freq_bass / sample_rate
        tri_bass = 4.0 * abs((phase_bass % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
        env_bass = 0.45 * math.exp(-12 * t_step)
        bass_val = tri_bass * env_bass

        # Mélodie (Square)
        freq_mel = melody_notes[mel_idx]
        phase_mel += 2 * math.pi * freq_mel / sample_rate
        sq_mel = 1.0 if math.sin(phase_mel) > 0 else -1.0
        env_mel = 0.25 * math.exp(-1.5 * t_note)
        mel_val = sq_mel * env_mel
        
        music_samples.append((bass_val + mel_val) * 32767)
    
    write_wav("music.wav", music_samples)

# Générer et charger les ressources audio
generate_audio_assets()

sfx_hit = pygame.mixer.Sound(os.path.join("assets", "sfx_hit.wav"))
sfx_sword = pygame.mixer.Sound(os.path.join("assets", "sfx_sword.wav"))
sfx_hurt = pygame.mixer.Sound(os.path.join("assets", "sfx_hurt.wav"))
sfx_victory = pygame.mixer.Sound(os.path.join("assets", "sfx_victory.wav"))
sfx_defeat = pygame.mixer.Sound(os.path.join("assets", "sfx_defeat.wav"))

# --- SYSTÈME DE CONTRÔLE DU VOLUME MASTER ---
master_volume = 0.5
volume_indicator_timer = 0.0

def apply_volume():
    sfx_hit.set_volume(master_volume)
    sfx_sword.set_volume(master_volume)
    sfx_hurt.set_volume(master_volume)
    sfx_victory.set_volume(master_volume)
    sfx_defeat.set_volume(master_volume)
    pygame.mixer.music.set_volume(master_volume)

apply_volume()

# --- CONFIGURATION DE LA FENÊTRE ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Le Dernier Survivant")

# Charger une police système
try:
    font_title = pygame.font.SysFont("Outfit", 64, bold=True)
    font_subtitle = pygame.font.SysFont("Outfit", 24)
    font_hud_label = pygame.font.SysFont("Outfit", 14, bold=True)
    font_hud_value = pygame.font.SysFont("Outfit", 28, bold=True)
    font_body = pygame.font.SysFont("Outfit", 16)
except:
    font_title = pygame.font.SysFont("Arial", 60, bold=True)
    font_subtitle = pygame.font.SysFont("Arial", 22)
    font_hud_label = pygame.font.SysFont("Arial", 12, bold=True)
    font_hud_value = pygame.font.SysFont("Arial", 24, bold=True)
    font_body = pygame.font.SysFont("Arial", 16)

# --- CONSTANTES DU JEU ---
TILE_SIZE = 80
MAP_COLS = 25
MAP_ROWS = 20
MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE

# --- PLAN DE LA CARTE ---
MAP_LAYOUT = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,0,'E',0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,0,'X',0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,1,0,'M',0,1,0,1,1,1,1,1,1,1,1,0,1,1],
    [1,0,1,0,0,0,1,0,1,1,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1],
    [1,0,1,0,1,1,1,0,0,0,0,0,0,0,1,0,'M',0,'M',0,0,1,0,0,1],
    [1,0,1,0,1,0,0,0,1,1,0,1,1,0,1,1,1,1,1,1,0,1,1,0,1],
    [1,0,0,0,1,0,'M',0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,1,0,1],
    [1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,1,0,1,1,0,'W',0,1,0,1,1,0,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,0,'M',0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,'M',0,0,0,0,1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# --- FONCTIONS DE DESSIN DE LUEUR NÉON ---
def draw_glow_line(surface, start, end, color=(255, 255, 255), width=2, glow_color=(255, 255, 255)):
    # Lueur large très transparente
    g1 = (glow_color[0] // 6, glow_color[1] // 6, glow_color[2] // 6)
    g2 = (glow_color[0] // 2, glow_color[1] // 2, glow_color[2] // 2)
    pygame.draw.line(surface, g1, start, end, width + 6)
    pygame.draw.line(surface, g2, start, end, width + 2)
    # Cœur blanc éclatant
    pygame.draw.line(surface, color, start, end, width)

def draw_glow_circle(surface, center, radius, color=(255, 255, 255), width=2, glow_color=(255, 255, 255)):
    g1 = (glow_color[0] // 6, glow_color[1] // 6, glow_color[2] // 6)
    g2 = (glow_color[0] // 2, glow_color[1] // 2, glow_color[2] // 2)
    if width <= 0:
        # Cercle plein
        pygame.draw.circle(surface, g1, center, radius + 4)
        pygame.draw.circle(surface, g2, center, radius + 1)
        pygame.draw.circle(surface, color, center, radius)
    else:
        # Contour du cercle
        pygame.draw.circle(surface, g1, center, radius, width + 4)
        pygame.draw.circle(surface, g2, center, radius, width + 1)
        pygame.draw.circle(surface, color, center, radius, width)

# --- CLASSE DE LA CAMÉRA ---
class Camera:
    def __init__(self):
        self.x = 0;
        self.y = 0;

    def update(self, target_x, target_y):
        ideal_x = target_x - SCREEN_WIDTH / 2
        ideal_y = target_y - SCREEN_HEIGHT / 2

        if SCREEN_WIDTH >= MAP_WIDTH:
            self.x = (MAP_WIDTH - SCREEN_WIDTH) / 2
        else:
            self.x = max(0, min(ideal_x, MAP_WIDTH - SCREEN_WIDTH))

        if SCREEN_HEIGHT >= MAP_HEIGHT:
            self.y = (MAP_HEIGHT - SCREEN_HEIGHT) / 2
        else:
            self.y = max(0, min(ideal_y, MAP_HEIGHT - SCREEN_HEIGHT))

    def to_screen(self, world_x, world_y):
        return int(world_x - self.x), int(world_y - self.y)

    def to_world(self, screen_x, screen_y):
        return int(screen_x + self.x), int(screen_y + self.y)

camera = Camera()

# --- CLASSE DES PARTICULES ---
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, decay, is_line=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.decay = decay
        self.is_line = is_line

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= self.decay * dt * 60

    def draw(self, surface, cam):
        if self.life <= 0: return
        screen_x, screen_y = cam.to_screen(self.x, self.y)
        alpha = max(0, min(255, int((self.life / self.max_life) * 255)))
        
        # Pour dessiner des particules semi-transparentes avec lueur en Pygame :
        # On utilise une petite surface temporaire avec canal Alpha
        size_int = max(1, int(self.size))
        p_surf = pygame.Surface((size_int * 4, size_int * 4), pygame.SRCALPHA)
        col = (self.color[0], self.color[1], self.color[2], alpha)
        
        if self.is_line:
            vx_len = int(self.vx * 0.2)
            vy_len = int(self.vy * 0.2)
            pygame.draw.line(surface, col, (screen_x, screen_y), (screen_x - vx_len, screen_y - vy_len), size_int)
        else:
            pygame.draw.circle(p_surf, col, (size_int * 2, size_int * 2), size_int)
            surface.blit(p_surf, (screen_x - size_int * 2, screen_y - size_int * 2))

particles = []

def spawn_impact_particles(x, y, count, color=(255,255,255)):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(1, 4)
        life = 1.0
        decay = random.uniform(0.02, 0.05)
        particles.append(Particle(x, y, vx, vy, color, size, life, decay, random.random() > 0.5))

def spawn_trail_particles(x, y, count, color=(150, 150, 150)):
    for _ in range(count):
        vx = random.uniform(-0.25, 0.25)
        vy = random.uniform(-0.25, 0.25)
        size = random.uniform(1, 3)
        life = 0.5
        decay = 0.04
        particles.append(Particle(x, y, vx, vy, color, size, life, decay))

# --- SYSTEME DE SECOUSSE D'ECRAN ---
screen_shake_timer = 0
screen_shake_intensity = 0

def trigger_screen_shake(intensity, duration):
    global screen_shake_timer, screen_shake_intensity
    screen_shake_intensity = intensity
    screen_shake_timer = duration

# --- MURS & COLLISIONS ---
class Wall:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, cam):
        screen_x, screen_y = cam.to_screen(self.rect.x, self.rect.y)
        draw_glow_line(surface, (screen_x, screen_y), (screen_x + self.rect.w, screen_y), (255,255,255), 2)
        draw_glow_line(surface, (screen_x, screen_y + self.rect.h), (screen_x + self.rect.w, screen_y + self.rect.h), (255,255,255), 2)
        draw_glow_line(surface, (screen_x, screen_y), (screen_x, screen_y + self.rect.h), (255,255,255), 2)
        draw_glow_line(surface, (screen_x + self.rect.w, screen_y), (screen_x + self.rect.w, screen_y + self.rect.h), (255,255,255), 2)

walls = []

def check_aabb_collision(cx, cy, r, rx, ry, rw, rh):
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    dist_x = cx - closest_x
    dist_y = cy - closest_y
    return (dist_x * dist_x + dist_y * dist_y) < (r * r)

def handle_wall_collisions(entity_x, entity_y, radius):
    new_x = entity_x
    new_y = entity_y

    # 1. Résoudre l'axe X (collisions principalement horizontales)
    for wall in walls:
        if check_aabb_collision(new_x, entity_y, radius, wall.rect.x, wall.rect.y, wall.rect.w, wall.rect.h):
            closest_x = max(wall.rect.x, min(new_x, wall.rect.x + wall.rect.w))
            closest_y = max(wall.rect.y, min(entity_y, wall.rect.y + wall.rect.h))
            
            pen_x = radius - abs(new_x - closest_x)
            pen_y = radius - abs(entity_y - closest_y)
            
            # Si la pénétration sur Y est plus faible, c'est une collision de type sol/plafond,
            # on refuse donc tout déplacement correctif sur l'axe X.
            if pen_y < pen_x:
                continue

            wall_center_x = wall.rect.x + wall.rect.w / 2
            if entity_x < wall_center_x:
                new_x = wall.rect.x - radius
            else:
                new_x = wall.rect.x + wall.rect.w + radius

    # 2. Résoudre l'axe Y (collisions principalement verticales)
    for wall in walls:
        if check_aabb_collision(new_x, new_y, radius, wall.rect.x, wall.rect.y, wall.rect.w, wall.rect.h):
            closest_x = max(wall.rect.x, min(new_x, wall.rect.x + wall.rect.w))
            closest_y = max(wall.rect.y, min(new_y, wall.rect.y + wall.rect.h))
            
            pen_x = radius - abs(new_x - closest_x)
            pen_y = radius - abs(new_y - closest_y)
            
            # Si la pénétration sur X est plus faible, c'est une collision de type mur latéral,
            # on refuse donc tout déplacement correctif sur l'axe Y.
            if pen_x < pen_y:
                continue

            wall_center_y = wall.rect.y + wall.rect.h / 2
            if entity_y < wall_center_y:
                new_y = wall.rect.y - radius
            else:
                new_y = wall.rect.y + wall.rect.h + radius

    return new_x, new_y

# --- EPEE A RAMASSER ---
class WeaponItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.hover_time = 0
        self.picked_up = False

    def update(self, dt, player):
        if self.picked_up: return
        self.hover_time += dt * 3
        
        dist = math.hypot(self.x - player.x, self.y - player.y)
        if dist < player.radius + self.radius:
            self.picked_up = True
            player.has_sword = True
            player.objective = "ELIMINER LES MUTANTS ET S'ECHAPPER"
            spawn_impact_particles(self.x, self.y, 25, (255,255,255))
            trigger_screen_shake(4, 0.2)

    def draw(self, surface, cam):
        if self.picked_up: return
        screen_x, screen_y = cam.to_screen(self.x, self.y)
        y_offset = int(math.sin(self.hover_time) * 6)
        
        # Dessin de l'épée inclinée
        ang = -math.pi / 4
        # Points de l'épée locaux
        # Lame
        l1 = (0, y_offset)
        l2 = (int(math.cos(ang - math.pi/2) * 18), y_offset + int(math.sin(ang - math.pi/2) * 18))
        # Garde
        g1 = (int(math.cos(ang) * -6 + math.cos(ang - math.pi/2) * 5), y_offset + int(math.sin(ang) * -6 + math.sin(ang - math.pi/2) * 5))
        g2 = (int(math.cos(ang) * 6 + math.cos(ang - math.pi/2) * 5), y_offset + int(math.sin(ang) * 6 + math.sin(ang - math.pi/2) * 5))
        # Poignée
        p1 = (int(math.cos(ang - math.pi/2) * 5), y_offset + int(math.sin(ang - math.pi/2) * 5))
        p2 = (int(math.cos(ang - math.pi/2) * -3), y_offset + int(math.sin(ang - math.pi/2) * -3))

        draw_glow_line(surface, (screen_x + l1[0], screen_y + l1[1]), (screen_x + l2[0], screen_y + l2[1]), (255,255,255), 2)
        draw_glow_line(surface, (screen_x + g1[0], screen_y + g1[1]), (screen_x + g2[0], screen_y + g2[1]), (255,255,255), 2)
        draw_glow_line(surface, (screen_x + p1[0], screen_y + p1[1]), (screen_x + p2[0], screen_y + p2[1]), (255,255,255), 2)
        
        # Halo de lueur autour
        draw_glow_circle(surface, (screen_x, screen_y - 8 + y_offset), 16, (255,255,255,30), 1, (255,255,255))

sword_item = None

# --- PORTAIL DE SORTIE ---
class ExitPortal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 35
        self.angle = 0

    def update(self, dt, player, game_state_callback):
        self.angle += dt * 1.5
        
        if random.random() < 0.15:
            a = random.uniform(0, math.pi * 2)
            r = random.uniform(0, self.radius)
            px = self.x + math.cos(a) * r
            py = self.y + math.sin(a) * r
            particles.append(Particle(px, py, 0, -random.uniform(0.5, 1.0), (255,255,255), random.uniform(1, 2), 0.8, 0.03))

        dist = math.hypot(self.x - player.x, self.y - player.y)
        if dist < player.radius + self.radius - 10:
            spawn_impact_particles(self.x, self.y, 40, (255,255,255))
            sfx_victory.play()
            pygame.mixer.music.stop()
            game_state_callback("VICTORY")

    def draw(self, surface, cam):
        screen_pos = cam.to_screen(self.x, self.y)
        
        # Anneau extérieur
        draw_glow_circle(surface, screen_pos, self.radius, (255,255,255), 2, (255,255,255))
        # Anneau intérieur
        draw_glow_circle(surface, screen_pos, self.radius - 10, (200,200,200), 1, (200,200,200))
        # Noyau
        core_r = int(6 + math.sin(self.angle * 4) * 2)
        draw_glow_circle(surface, screen_pos, core_r, (255,255,255), 0, (255,255,255))

        # Rayons décoratifs
        for i in range(4):
            a = self.angle + (i * math.pi / 2)
            s_pt = (screen_pos[0] + int(math.cos(a) * (self.radius + 5)), screen_pos[1] + int(math.sin(a) * (self.radius + 5)))
            e_pt = (screen_pos[0] + int(math.cos(a) * (self.radius + 12)), screen_pos[1] + int(math.sin(a) * (self.radius + 12)))
            draw_glow_line(surface, s_pt, e_pt, (255,255,255,100), 1)

exit_portal = None

# --- JOUEUR ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 16
        self.speed = 220
        
        self.max_hp = 100
        self.hp = 100
        self.has_sword = False
        self.objective = "EXPLORER ET SURVIVRE"
        
        self.look_angle = 0
        self.run_cycle = 0
        self.is_moving = False
        self.bob_time = 0
        self.is_dead = False
        
        self.punch_left_timer = 0
        self.punch_right_timer = 0
        self.punch_duration = 0.15
        self.punch_side = "left"
        self.sword_swing_timer = 0
        self.sword_swing_duration = 0.25
        self.sword_swing_side = 1
        
        self.invuln_timer = 0
        self.lantern_active = True
        self.death_timer = 0.0

    def update(self, dt, keys, mouse_world, click_left, click_right):
        if self.is_dead:
            self.death_timer += dt
            if self.death_timer >= 1.5:
                set_game_state("GAMEOVER")
            return

        # Décrémenter les timers
        if self.punch_left_timer > 0: self.punch_left_timer -= dt
        if self.punch_right_timer > 0: self.punch_right_timer -= dt
        if self.sword_swing_timer > 0: self.sword_swing_timer -= dt
        if self.invuln_timer > 0: self.invuln_timer -= dt

        # Déplacements
        move_x = 0
        move_y = 0

        if keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP]: move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_y += 1
        if keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT]: move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += 1

        if move_x != 0 or move_y != 0:
            length = math.hypot(move_x, move_y)
            dx = (move_x / length) * self.speed * dt
            dy = (move_y / length) * self.speed * dt
            self.x += dx
            self.y += dy
            self.is_moving = True
            self.run_cycle += dt * 14
            
            if random.random() < 0.15:
                spawn_trail_particles(self.x, self.y + 15, 1, (100,100,100))
        else:
            self.is_moving = False
            self.bob_time += dt * 3.5

        # Collisions
        self.x, self.y = handle_wall_collisions(self.x, self.y, self.radius)

        # Orientation
        self.look_angle = math.atan2(mouse_world[1] - (self.y - 15), mouse_world[0] - self.x)

        # Attaque
        if click_left or click_right:
            if self.has_sword:
                if self.sword_swing_timer <= 0:
                    self.sword_swing_timer = self.sword_swing_duration
                    self.sword_swing_side = -self.sword_swing_side
                    self.perform_sword_attack()
            else:
                if self.punch_left_timer <= 0 and self.punch_right_timer <= 0:
                    if self.punch_side == "left":
                        self.punch_left_timer = self.punch_duration
                        self.punch_side = "right"
                        self.perform_fist_punch("left")
                    else:
                        self.punch_right_timer = self.punch_duration
                        self.punch_side = "left"
                        self.perform_fist_punch("right")

    def perform_fist_punch(self, side):
        punch_dist = 32
        impact_x = self.x + math.cos(self.look_angle) * punch_dist
        impact_y = (self.y - 15) + math.sin(self.look_angle) * punch_dist
        
        spawn_impact_particles(impact_x, impact_y, 4, (255,255,255))
        
        hit = False
        for enemy in enemies:
            dist = math.hypot(enemy.x - impact_x, enemy.y - impact_y)
            if dist < enemy.radius + 10:
                enemy.take_damage(15, self.x, self.y)
                hit = True
        if hit:
            trigger_screen_shake(2, 0.1)
            sfx_hit.play()

    def perform_sword_attack(self):
        sfx_sword.play()
        sweep_range = 65
        sweep_angle = math.pi * 0.8
        start_arc = self.look_angle - (sweep_angle / 2) * self.sword_swing_side
        
        # Créer des particules en arc
        for i in range(7):
            a = start_arc + (sweep_angle * (i / 6.0)) * self.sword_swing_side
            px = self.x + math.cos(a) * sweep_range
            py = (self.y - 15) + math.sin(a) * sweep_range
            particles.append(Particle(px, py, math.cos(a)*2, math.sin(a)*2, (255,255,255), 2, 0.3, 0.05))

        hit = False
        for enemy in enemies:
            angle_to_enemy = math.atan2(enemy.y - (self.y - 15), enemy.x - self.x)
            diff_angle = angle_to_enemy - self.look_angle
            
            while diff_angle < -math.pi: diff_angle += math.pi * 2
            while diff_angle > math.pi: diff_angle -= math.pi * 2

            dist = math.hypot(enemy.x - self.x, enemy.y - (self.y - 15))
            if dist < sweep_range + enemy.radius and abs(diff_angle) < sweep_angle / 2:
                enemy.take_damage(40, self.x, self.y)
                hit = True
        if hit:
            trigger_screen_shake(4, 0.12)
            sfx_hit.play()

    def take_damage(self, amount, source_x, source_y):
        if self.is_dead or self.invuln_timer > 0: return

        self.hp = max(0, self.hp - amount)
        self.invuln_timer = 0.5
        
        # Recul
        angle = math.atan2(self.y - source_y, self.x - source_x)
        self.x += math.cos(angle) * 20
        self.y += math.sin(angle) * 20
        self.x, self.y = handle_wall_collisions(self.x, self.y, self.radius)

        trigger_screen_shake(8, 0.25)
        spawn_impact_particles(self.x, self.y - 15, 15, (255, 51, 51))

        if self.hp <= 0:
            self.is_dead = True
            spawn_impact_particles(self.x, self.y - 15, 35, (255, 51, 51))
            sfx_defeat.play()
            pygame.mixer.music.stop()
        else:
            sfx_hurt.play()

    def draw(self, surface, cam):
        if self.is_dead: return

        screen_pos = cam.to_screen(self.x, self.y)
        
        # Couleurs de rendu
        color = (255, 255, 255)
        glow_color = (255, 255, 255)
        if self.invuln_timer > 0:
            if int(pygame.time.get_ticks() / 50) % 2 == 0:
                color = (255, 51, 51)
                glow_color = (255, 51, 51)

        # Respiration / oscillations
        bob = 0 if self.is_moving else math.sin(self.bob_time) * 1.2
        
        foot_height_y = screen_pos[1]
        hips_y = screen_pos[1] - 18 + int(bob)
        neck_y = screen_pos[1] - 36 + int(bob)
        head_y = screen_pos[1] - 46 + int(bob)
        
        # Jambes
        if self.is_moving:
            left_angle = self.run_cycle
            right_angle = self.run_cycle + math.pi
            
            left_foot = (screen_pos[0] + int(math.sin(left_angle) * 12), foot_height_y - int(max(0, math.cos(left_angle) * 4)))
            right_foot = (screen_pos[0] + int(math.sin(right_angle) * 12), foot_height_y - int(max(0, math.cos(right_angle) * 4)))
        else:
            left_foot = (screen_pos[0] - 6, foot_height_y)
            right_foot = (screen_pos[0] + 6, foot_height_y)

        # Jambe gauche
        draw_glow_line(surface, (screen_pos[0] - 3, hips_y), left_foot, color, 2, glow_color)
        # Jambe droite
        draw_glow_line(surface, (screen_pos[0] + 3, hips_y), right_foot, color, 2, glow_color)
        # Tronc
        draw_glow_line(surface, (screen_pos[0], hips_y), (screen_pos[0], neck_y), color, 3, glow_color)
        # Tête
        draw_glow_circle(surface, (screen_pos[0], head_y), 7, color, 2, glow_color)

        # Regard (yeux néons)
        eye_dist = 3.5
        eye_offset = 0.4
        le_x = screen_pos[0] + int(math.cos(self.look_angle - eye_offset) * eye_dist)
        le_y = head_y + int(math.sin(self.look_angle - eye_offset) * eye_dist)
        re_x = screen_pos[0] + int(math.cos(self.look_angle + eye_offset) * eye_dist)
        re_y = head_y + int(math.sin(self.look_angle + eye_offset) * eye_dist)
        
        pygame.draw.circle(surface, (255,255,255), (le_x, le_y), 1)
        pygame.draw.circle(surface, (255,255,255), (re_x, re_y), 1)

        # Épaules
        shoulder_l = (screen_pos[0] - 4, neck_y + 2)
        shoulder_r = (screen_pos[0] + 4, neck_y + 2)
        arm_length = 16

        if self.has_sword:
            # Rendu avec épée
            if self.sword_swing_timer > 0:
                pct = (self.sword_swing_duration - self.sword_swing_timer) / self.sword_swing_duration
                swing_angle = self.look_angle + (-math.pi / 2 + math.pi * pct) * self.sword_swing_side
                
                hand = (screen_pos[0] + int(math.cos(swing_angle) * arm_length), neck_y + int(math.sin(swing_angle) * arm_length))
                
                draw_glow_line(surface, shoulder_l, hand, color, 2, glow_color)
                draw_glow_line(surface, shoulder_r, hand, color, 2, glow_color)

                # Dessiner l'épée swing
                sw_ang = swing_angle + math.pi/4 * self.sword_swing_side
                blade_tip = (hand[0] + int(math.cos(sw_ang - math.pi/2) * 32), hand[1] + int(math.sin(sw_ang - math.pi/2) * 32))
                g_l = (hand[0] + int(math.cos(sw_ang) * -9 + math.cos(sw_ang - math.pi/2) * 8), hand[1] + int(math.sin(sw_ang) * -9 + math.sin(sw_ang - math.pi/2) * 8))
                g_r = (hand[0] + int(math.cos(sw_ang) * 9 + math.cos(sw_ang - math.pi/2) * 8), hand[1] + int(math.sin(sw_ang) * 9 + math.sin(sw_ang - math.pi/2) * 8))
                pom_pt = (hand[0] + int(math.cos(sw_ang - math.pi/2) * -7), hand[1] + int(math.sin(sw_ang - math.pi/2) * -7))

                draw_glow_line(surface, hand, blade_tip, (255,255,255), 3)
                draw_glow_line(surface, g_l, g_r, (255,255,255), 2)
                draw_glow_line(surface, hand, pom_pt, (255,255,255), 2)
            else:
                # Épée en garde passive
                guard_angle = self.look_angle - 0.5
                hand = (screen_pos[0] + int(math.cos(guard_angle) * (arm_length - 2)), neck_y + int(math.sin(guard_angle) * (arm_length - 2)))
                draw_glow_line(surface, shoulder_l, hand, color, 2, glow_color)
                draw_glow_line(surface, shoulder_r, hand, color, 2, glow_color)

                sw_ang = self.look_angle + 0.3
                blade_tip = (hand[0] + int(math.cos(sw_ang - math.pi/2) * 28), hand[1] + int(math.sin(sw_ang - math.pi/2) * 28))
                g_l = (hand[0] + int(math.cos(sw_ang) * -7 + math.cos(sw_ang - math.pi/2) * 5), hand[1] + int(math.sin(sw_ang) * -7 + math.sin(sw_ang - math.pi/2) * 5))
                g_r = (hand[0] + int(math.cos(sw_ang) * 7 + math.cos(sw_ang - math.pi/2) * 5), hand[1] + int(math.sin(sw_ang) * 7 + math.sin(sw_ang - math.pi/2) * 5))
                pom_pt = (hand[0] + int(math.cos(sw_ang - math.pi/2) * -5), hand[1] + int(math.sin(sw_ang - math.pi/2) * -5))

                draw_glow_line(surface, hand, blade_tip, (255,255,255), 2)
                draw_glow_line(surface, g_l, g_r, (255,255,255), 2)
                draw_glow_line(surface, hand, pom_pt, (255,255,255), 2)
        else:
            # Combat mains nues
            # Bras gauche
            if self.punch_left_timer > 0:
                pct = self.punch_left_timer / self.punch_duration
                ext = arm_length + int(math.sin(pct * math.pi) * 16)
                hand_l = (shoulder_l[0] + int(math.cos(self.look_angle - 0.3) * ext), neck_y + int(math.sin(self.look_angle - 0.3) * ext))
            else:
                hand_l = (shoulder_l[0] + int(math.cos(self.look_angle - 0.6) * (arm_length - 4)), neck_y + int(math.sin(self.look_angle - 0.6) * (arm_length - 4)))

            # Bras droit
            if self.punch_right_timer > 0:
                pct = self.punch_right_timer / self.punch_duration
                ext = arm_length + int(math.sin(pct * math.pi) * 16)
                hand_r = (shoulder_r[0] + int(math.cos(self.look_angle + 0.3) * ext), neck_y + int(math.sin(self.look_angle + 0.3) * ext))
            else:
                hand_r = (shoulder_r[0] + int(math.cos(self.look_angle + 0.6) * (arm_length - 4)), neck_y + int(math.sin(self.look_angle + 0.6) * (arm_length - 4)))

            draw_glow_line(surface, shoulder_l, hand_l, color, 2, glow_color)
            draw_glow_line(surface, shoulder_r, hand_r, color, 2, glow_color)
            pygame.draw.circle(surface, color, hand_l, 2)
            pygame.draw.circle(surface, color, hand_r, 2)

player = None

# --- ENNEMI (MUTANT FIL DE FER) ---
class Enemy:
    def __init__(self, x, y, is_boss=False):
        self.x = x
        self.y = y
        self.is_boss = is_boss
        
        self.radius = 28 if is_boss else 15
        self.speed = 100 if is_boss else 125
        self.max_hp = 200 if is_boss else 35
        self.hp = self.max_hp
        
        self.state = "SLEEPING" # SLEEPING, ALERT, CHASING, STUNNED
        self.look_angle = random.uniform(0, math.pi * 2)
        self.detection_radius = 280 if is_boss else 200
        
        self.walk_cycle = random.uniform(0, 100)
        self.stun_timer = 0
        self.bob_time = random.uniform(0, 100)
        self.swipe_timer = 0
        self.swipe_duration = 0.2

    def update(self, dt, player_obj):
        if player_obj.is_dead: return

        if self.stun_timer > 0:
            self.stun_timer -= dt
            if self.stun_timer <= 0: self.state = "CHASING"
        if self.swipe_timer > 0: self.swipe_timer -= dt

        if self.state == "STUNNED":
            if random.random() < 0.2:
                spawn_trail_particles(self.x, self.y + 10, 1, (255, 51, 51))
            self.x, self.y = handle_wall_collisions(self.x, self.y, self.radius)
            return

        dist = math.hypot(player_obj.x - self.x, player_obj.y - self.y)

        if self.state == "SLEEPING":
            detect_range = self.detection_radius if player_obj.lantern_active else self.detection_radius * 0.4
            if dist < detect_range:
                self.state = "ALERT"
                self.stun_timer = 0.4
                spawn_impact_particles(self.x, self.y - 25, 6, (255, 51, 51))
                trigger_screen_shake(1.5, 0.1)
            self.bob_time += dt * 2
        elif self.state == "ALERT":
            self.look_angle = math.atan2(player_obj.y - self.y, player_obj.x - self.x)
            if self.stun_timer <= 0:
                self.state = "CHASING"
        elif self.state == "CHASING":
            self.look_angle = math.atan2(player_obj.y - self.y, player_obj.x - self.x)
            
            vx = math.cos(self.look_angle) * self.speed * dt
            vy = math.sin(self.look_angle) * self.speed * dt
            self.x += vx
            self.y += vy
            self.walk_cycle += dt * (8 if self.is_boss else 14)

            self.x, self.y = handle_wall_collisions(self.x, self.y, self.radius)

            # Frapper si au contact
            atk_range = self.radius + player_obj.radius + 8
            if dist < atk_range:
                if self.swipe_timer <= 0:
                    self.swipe_timer = self.swipe_duration
                    player_obj.take_damage(25 if self.is_boss else 12, self.x, self.y)

    def take_damage(self, amount, source_x, source_y):
        self.hp -= amount
        self.state = "STUNNED"
        self.stun_timer = 0.25
        
        # Recul
        angle = math.atan2(self.y - source_y, self.x - source_x)
        knock = 15 if self.is_boss else 35
        self.x += math.cos(angle) * knock
        self.y += math.sin(angle) * knock
        self.x, self.y = handle_wall_collisions(self.x, self.y, self.radius)

        spawn_impact_particles(self.x, self.y - 12, 10, (150, 0, 0))
        spawn_impact_particles(self.x, self.y - 12, 5, (255, 51, 51))

        if self.hp <= 0:
            spawn_impact_particles(self.x, self.y - 12, 45 if self.is_boss else 20, (150, 0, 0))
            spawn_impact_particles(self.x, self.y - 12, 20 if self.is_boss else 10, (255, 255, 255))
            if self in enemies:
                enemies.remove(self)
            trigger_screen_shake(7 if self.is_boss else 3, 0.15)

    def draw(self, surface, cam):
        screen_pos = cam.to_screen(self.x, self.y)
        
        color = (255, 60, 60)
        glow_color = (255, 60, 60)
        width = 3 if self.is_boss else 2
        
        if self.state == "STUNNED":
            color = (255, 255, 255)
            glow_color = (255, 255, 255)

        # Dessiner le squelette bossu muté
        is_chasing = (self.state == "CHASING")
        bob = math.sin(self.walk_cycle * 0.8 if is_chasing else self.bob_time) * (2.0 if self.is_boss else 1.5)
        
        ground_y = screen_pos[1]
        hips_y = ground_y - (25 if self.is_boss else 12) + int(bob)
        
        # Tête projetée vers l'avant
        forward_x = int(math.cos(self.look_angle) * (15 if self.is_boss else 8))
        forward_y = int(math.sin(self.look_angle) * (5 if self.is_boss else 2))
        
        neck_x = screen_pos[0] + forward_x
        neck_y = ground_y - (45 if self.is_boss else 24) + int(bob) + forward_y
        
        head_x = neck_x + int(math.cos(self.look_angle) * (10 if self.is_boss else 6))
        head_y = neck_y - (10 if self.is_boss else 6)

        # Jambes difformes
        if is_chasing:
            left_angle = self.walk_cycle
            right_angle = self.walk_cycle + math.pi + 0.5
            
            l_foot = (screen_pos[0] + int(math.sin(left_angle) * (16 if self.is_boss else 9)), ground_y - int(max(0, math.cos(left_angle) * 6)))
            r_foot = (screen_pos[0] + int(math.sin(right_angle) * (14 if self.is_boss else 8)), ground_y - int(max(0, math.cos(right_angle) * 5)))
        else:
            l_foot = (screen_pos[0] - (12 if self.is_boss else 5), ground_y)
            r_foot = (screen_pos[0] + (12 if self.is_boss else 5), ground_y)

        # Tracé des jambes
        knee_l = ((screen_pos[0] - 4 + l_foot[0]) // 2 - (6 if self.is_boss else 3), (hips_y + l_foot[1]) // 2)
        draw_glow_line(surface, (screen_pos[0] - 3, hips_y), knee_l, color, width, glow_color)
        draw_glow_line(surface, knee_l, l_foot, color, width, glow_color)

        knee_r = ((screen_pos[0] + 4 + r_foot[0]) // 2 + (6 if self.is_boss else 3), (hips_y + r_foot[1]) // 2)
        draw_glow_line(surface, (screen_pos[0] + 3, hips_y), knee_r, color, width, glow_color)
        draw_glow_line(surface, knee_r, r_foot, color, width, glow_color)

        # Spine courbée
        pygame.draw.line(surface, color, (screen_pos[0], hips_y), (neck_x, neck_y), width)
        # Tête
        draw_glow_circle(surface, (head_x, head_y), 11 if self.is_boss else 5, color, width, glow_color)

        # Oeil cyclope rouge
        if self.state != "SLEEPING":
            eye_x = head_x + int(math.cos(self.look_angle) * (7 if self.is_boss else 3))
            eye_y = head_y + int(math.sin(self.look_angle) * (7 if self.is_boss else 3))
            pygame.draw.circle(surface, (255, 0, 0), (eye_x, eye_y), 3 if self.is_boss else 1.5)

        # Bras longs flasques
        arm_length = 32 if self.is_boss else 16
        if self.swipe_timer > 0:
            pct = self.swipe_timer / self.swipe_duration
            ext = arm_length + int(math.sin(pct * math.pi) * (20 if self.is_boss else 10))
            hand_l = (neck_x + int(math.cos(self.look_angle - 0.2) * ext), neck_y + int(math.sin(self.look_angle - 0.2) * ext))
            hand_r = (neck_x + int(math.cos(self.look_angle + 0.2) * ext), neck_y + int(math.sin(self.look_angle + 0.2) * ext))
        else:
            hand_l = (neck_x - (15 if self.is_boss else 6) + int(math.cos(self.look_angle + 0.3) * (arm_length * 0.6)), neck_y + (20 if self.is_boss else 12) + int(math.sin(self.look_angle + 0.3) * (arm_length * 0.4)))
            hand_r = (neck_x + (15 if self.is_boss else 6) + int(math.cos(self.look_angle - 0.3) * (arm_length * 0.6)), neck_y + (22 if self.is_boss else 13) + int(math.sin(self.look_angle - 0.3) * (arm_length * 0.4)))

        draw_glow_line(surface, (neck_x - 3, neck_y + 2), hand_l, color, width, glow_color)
        draw_glow_line(surface, (neck_x + 3, neck_y + 2), hand_r, color, width, glow_color)

        # Griffes blanches acérées au bout
        for i in range(3):
            spread = (i - 1) * 3
            ang_l = self.look_angle + 0.2
            grif_l = (hand_l[0] + int(math.cos(ang_l)*4 + spread*math.cos(ang_l+math.pi/2)*0.3), hand_l[1] + int(math.sin(ang_l)*4 + spread*math.sin(ang_l+math.pi/2)*0.3))
            pygame.draw.line(surface, (255,255,255), hand_l, grif_l, 1)

            ang_r = self.look_angle - 0.2
            grif_r = (hand_r[0] + int(math.cos(ang_r)*4 + spread*math.cos(ang_r-math.pi/2)*0.3), hand_r[1] + int(math.sin(ang_r)*4 + spread*math.sin(ang_r-math.pi/2)*0.3))
            pygame.draw.line(surface, (255,255,255), hand_r, grif_r, 1)

        # Petite barre de vie
        if self.hp < self.max_hp:
            bar_w = 40 if self.is_boss else 20
            bar_h = 3
            bx = screen_pos[0] - bar_w // 2
            by = head_y - 12
            pygame.draw.rect(surface, (30,30,30), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, (255,51,51), (bx, by, int(bar_w * (self.hp / self.max_hp)), bar_h))
            pygame.draw.rect(surface, (100,100,100), (bx, by, bar_w, bar_h), 1)

enemies = []

# --- CONSTRUCTIONS DES ELEMENTS DU JEU ---
def build_map():
    global spawn_point, exit_portal, sword_item, enemies, walls
    walls = []
    enemies = []
    exit_portal = None
    sword_item = None

    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            tile = MAP_LAYOUT[r][c]
            x = c * TILE_SIZE
            y = r * TILE_SIZE

            if tile == 1:
                walls.append(Wall(x, y, TILE_SIZE, TILE_SIZE))
            else:
                if tile == 'E':
                    spawn_point = (x + TILE_SIZE // 2, y + TILE_SIZE // 2 + 15)
                elif tile == 'X':
                    exit_portal = ExitPortal(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                elif tile == 'W':
                    sword_item = WeaponItem(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                elif tile == 'M':
                    enemies.append(Enemy(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

    if exit_portal:
        enemies.append(Enemy(exit_portal.x - 120, exit_portal.y, True))

# --- RENDU DE LA CARTE FIL DE FER ---
def draw_wireframe_map(surface, cam):
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            if MAP_LAYOUT[r][c] != 1: continue

            x = c * TILE_SIZE
            y = r * TILE_SIZE
            screen_x, screen_y = cam.to_screen(x, y)

            # Dessin de chaque contour blanc uniquement s'il touche un espace vide
            if r > 0 and MAP_LAYOUT[r-1][c] != 1:
                draw_glow_line(surface, (screen_x, screen_y), (screen_x + TILE_SIZE, screen_y), (255,255,255), 2)
            if r < MAP_ROWS - 1 and MAP_LAYOUT[r+1][c] != 1:
                draw_glow_line(surface, (screen_x, screen_y + TILE_SIZE), (screen_x + TILE_SIZE, screen_y + TILE_SIZE), (255,255,255), 2)
            if c > 0 and MAP_LAYOUT[r][c-1] != 1:
                draw_glow_line(surface, (screen_x, screen_y), (screen_x, screen_y + TILE_SIZE), (255,255,255), 2)
            if c < MAP_COLS - 1 and MAP_LAYOUT[r][c+1] != 1:
                draw_glow_line(surface, (screen_x + TILE_SIZE, screen_y), (screen_x + TILE_SIZE, screen_y + TILE_SIZE), (255,255,255), 2)

# --- EFFET D'OBSCURITE DYNAMIQUE MULTIPLY BLIT ---
def draw_lantern_light(surface, cam, player_obj):
    # Création du masque d'obscurité
    dark_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    dark_mask.fill((10, 10, 10)) # Niveau d'obscurité (10,10,10 = presque noir total)
    
    # Dessiner la lanterne autour du joueur
    p_screen = cam.to_screen(player_obj.x, player_obj.y - 15)
    
    if player_obj.lantern_active:
        # Lueur vacillante
        time_sec = pygame.time.get_ticks() * 0.001
        flicker = math.sin(time_sec * 25) * 3 + math.cos(time_sec * 40) * 1.5 + random.uniform(-1, 1)
        radius = max(80, int(220 + flicker))
        
        # Dessiner un cercle de lumière doux radial par dégradé concentrique
        # On dessine du blanc au centre vers le noir aux bords, qui sera multiplié
        for r in range(radius, 0, -8):
            alpha = int(255 * (1.0 - (r / radius) ** 1.8))
            pygame.draw.circle(dark_mask, (alpha, alpha, alpha), p_screen, r)
    else:
        # Lanterne éteinte : micro-halo
        pygame.draw.circle(dark_mask, (255, 255, 255), p_screen, 40)

    # Multiplier le masque sur l'écran
    surface.blit(dark_mask, (0, 0), special_flags=pygame.BLEND_MULT)

# --- RECTANGLE BOUTON INTERACTIF EN PYGAME ---
class PygameButton:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x - w//2, y - h//2, w, h)
        self.text = text
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = (255, 255, 255) if self.is_hovered else (150, 150, 150)
        width = 2 if self.is_hovered else 1
        
        # Fond translucide
        card_bg = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        card_bg.fill((10, 10, 10, 200))
        surface.blit(card_bg, (self.rect.x, self.rect.y))

        # Tracé néon
        draw_glow_line(surface, (self.rect.x, self.rect.y), (self.rect.x + self.rect.w, self.rect.y), color, width)
        draw_glow_line(surface, (self.rect.x, self.rect.y + self.rect.h), (self.rect.x + self.rect.w, self.rect.y + self.rect.h), color, width)
        draw_glow_line(surface, (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + self.rect.h), color, width)
        draw_glow_line(surface, (self.rect.x + self.rect.w, self.rect.y), (self.rect.x + self.rect.w, self.rect.y + self.rect.h), color, width)
        
        # Texte
        text_surf = font_subtitle.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

# --- ETAT DU JEU ---
game_state = "MENU" # MENU, PLAYING, GAMEOVER, VICTORY
fullscreen = False

# --- BOUTONS ---
btn_start = PygameButton(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 160, 320, 50, "COMMENCER L'EXPLORATION")
btn_restart = PygameButton(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80, 250, 50, "RECOMMENCER")
btn_next = PygameButton(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80, 300, 50, "CONTINUER L'AVENTURE")

def set_game_state(new_state):
    global game_state, player, particles
    game_state = new_state
    if new_state == "PLAYING":
        build_map()
        player = Player(spawn_point[0], spawn_point[1])
        particles = []
        trigger_screen_shake(3, 0.15)
        try:
            pygame.mixer.music.load(os.path.join("assets", "music.wav"))
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Erreur de chargement de la musique:", e)

# --- DESSINER DES ÉCRANS DE MENU (GLASSMORPHISM EFFECT) ---
def draw_menu_card(surface, title, subtitle, story_lines, btn_to_draw):
    # Rendu d'une carte floue translucide
    card_w = 640
    card_h = 440
    card_x = (SCREEN_WIDTH - card_w) // 2
    card_y = (SCREEN_HEIGHT - card_h) // 2

    # Fond de carte sombre translucide
    card_bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    card_bg.fill((10, 10, 10, 230))
    surface.blit(card_bg, (card_x, card_y))

    # Liseré de contour néon
    draw_glow_line(surface, (card_x, card_y), (card_x + card_w, card_y), (255, 255, 255), 1)
    draw_glow_line(surface, (card_x, card_y + card_h), (card_x + card_w, card_y + card_h), (255, 255, 255), 1)
    draw_glow_line(surface, (card_x, card_y), (card_x, card_y + card_h), (255, 255, 255), 1)
    draw_glow_line(surface, (card_x + card_w, card_y), (card_x + card_w, card_y + card_h), (255, 255, 255), 1)

    # Titre
    t_surf = font_title.render(title, True, (255,255,255))
    t_rect = t_surf.get_rect(center=(SCREEN_WIDTH//2, card_y + 50))
    surface.blit(t_surf, t_rect)

    # Sous-titre
    sub_surf = font_subtitle.render(subtitle, True, (200, 200, 200))
    sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH//2, card_y + 100))
    surface.blit(sub_surf, sub_rect)

    # Texte de l'histoire
    curr_y = card_y + 150
    for line in story_lines:
        story_surf = font_body.render(line, True, (230, 230, 230))
        story_rect = story_surf.get_rect(center=(SCREEN_WIDTH//2, curr_y))
        surface.blit(story_surf, story_rect)
        curr_y += 24

    # Bouton
    btn_to_draw.draw(surface)

# --- BOUCLE PRINCIPALE ---
clock = pygame.time.Clock()
running = True

while running:
    # 1. TEMPS ET SECCOUSSE
    dt = clock.tick(60) / 1000.0
    
    shake_x = 0
    shake_y = 0
    if screen_shake_timer > 0:
        screen_shake_timer -= dt
        shake_x = random.randint(-int(screen_shake_intensity), int(screen_shake_intensity))
        shake_y = random.randint(-int(screen_shake_intensity), int(screen_shake_intensity))
        if screen_shake_timer <= 0:
            screen_shake_intensity = 0

    if volume_indicator_timer > 0:
        volume_indicator_timer -= dt

    # 2. GESTION DES EVENEMENTS (INPUTS)
    mouse_pos = pygame.mouse.get_pos()
    mouse_world = camera.to_world(mouse_pos[0], mouse_pos[1])
    click_l = False
    click_r = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            elif event.key == pygame.K_f:
                if game_state == "PLAYING" and player:
                    player.lantern_active = not player.lantern_active
                    spawn_impact_particles(player.x, player.y - 20, 5, (200, 200, 200))
            elif event.key == pygame.K_r:
                if game_state in ["PLAYING", "GAMEOVER", "VICTORY"]:
                    set_game_state("PLAYING")
            elif event.key in [pygame.K_KP_PLUS, pygame.K_PLUS, pygame.K_EQUALS]:
                master_volume = min(1.0, master_volume + 0.1)
                apply_volume()
                volume_indicator_timer = 1.5
            elif event.key in [pygame.K_KP_MINUS, pygame.K_MINUS]:
                master_volume = max(0.0, master_volume - 0.1)
                apply_volume()
                volume_indicator_timer = 1.5
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click_l = True
                if game_state == "MENU" and btn_start.is_hovered:
                    set_game_state("PLAYING")
                elif game_state == "GAMEOVER" and btn_restart.is_hovered:
                    set_game_state("PLAYING")
                elif game_state == "VICTORY" and btn_next.is_hovered:
                    set_game_state("PLAYING")
            elif event.button == 3:
                click_r = True

    # 3. MISE A JOUR DES ACTIONS EN JEU
    if game_state == "PLAYING" and player:
        keys = pygame.key.get_pressed()
        player.update(dt, keys, mouse_world, click_l, click_r)
        camera.update(player.x, player.y)

        # Update Ennemis
        for enemy in enemies:
            enemy.update(dt, player)

        # Update Items
        if sword_item: sword_item.update(dt, player)
        if exit_portal: exit_portal.update(dt, player, set_game_state)

        # Update Particules
        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.life > 0]
    
    # Mettre à jour les boutons selon le survol de la souris
    if game_state == "MENU":
        btn_start.update(mouse_pos)
    elif game_state == "GAMEOVER":
        btn_restart.update(mouse_pos)
    elif game_state == "VICTORY":
        btn_next.update(mouse_pos)

    # 4. RENDU VISUEL (DESSIN)
    # Fond d'écran noir absolu
    screen.fill((0, 0, 0))

    # Surface virtuelle de jeu (avec décalage de tremblement)
    game_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_surf.fill((0, 0, 0))

    # Dessiner la carte vectorielle
    draw_wireframe_map(game_surf, camera)

    # Dessiner l'épée
    if sword_item: sword_item.draw(game_surf, camera)
    
    # Dessiner le portail
    if exit_portal: exit_portal.draw(game_surf, camera)

    # Dessiner les particules
    for p in particles:
        p.draw(game_surf, camera)

    # Dessiner les mutants
    for enemy in enemies:
        enemy.draw(game_surf, camera)

    # Dessiner le joueur
    if player: player.draw(game_surf, camera)

    # Appliquer l'effet de lanterne
    if game_state == "PLAYING" and player:
        draw_lantern_light(game_surf, camera, player)

    # Blitter la scène de jeu sur l'écran final avec le décalage du screen shake
    screen.blit(game_surf, (shake_x, shake_y))

    # 5. DESSINER LES MENUS / HUD SUR L'ECRAN FINAL
    if game_state == "PLAYING" and player:
        # HUD minimaliste en haut à gauche
        # Barre de vie blanche
        pygame.draw.rect(screen, (50,50,50), (30, 30, 250, 10), border_radius=5)
        hp_w = int(250 * (player.hp / player.max_hp))
        if hp_w > 0:
            # Lueur rouge si bas en PV, blanc sinon
            bar_col = (255, 51, 51) if player.hp < 30 else (255, 255, 255)
            pygame.draw.rect(screen, bar_col, (30, 30, hp_w, 10), border_radius=5)
        
        # Libellé HUD
        lbl_surf = font_hud_label.render("SANTÉ (ESPRIT)", True, (150,150,150))
        screen.blit(lbl_surf, (30, 12))

        # Objectif
        obj_lbl = font_hud_label.render("OBJECTIF", True, (150,150,150))
        screen.blit(obj_lbl, (30, 52))
        obj_surf = font_hud_value.render(player.objective, True, (255,255,255))
        screen.blit(obj_surf, (30, 68))

        # Instructions bas gauche
        inst_surf1 = font_hud_label.render("[ZQSD / WASD / FLÈCHES] SE DÉPLACER", True, (100,100,100))
        inst_surf2 = font_hud_label.render("[SOURIS] VISER  |  [CLICS GAUCHE/DROIT] COUPS DE POING/ÉPÉE", True, (100,100,100))
        inst_surf3 = font_hud_label.render("[F] LANTERNE  |  [R] RECOMMENCER  |  [KP+/-] VOLUME  |  [F11] PLEIN ÉCRAN", True, (100,100,100))
        screen.blit(inst_surf1, (30, SCREEN_HEIGHT - 75))
        screen.blit(inst_surf2, (30, SCREEN_HEIGHT - 55))
        screen.blit(inst_surf3, (30, SCREEN_HEIGHT - 35))

        # Rendre le curseur néon blanc
        pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 4, 1)
        pygame.draw.line(screen, (255, 255, 255), (mouse_pos[0] - 8, mouse_pos[1]), (mouse_pos[0] - 5, mouse_pos[1]))
        pygame.draw.line(screen, (255, 255, 255), (mouse_pos[0] + 5, mouse_pos[1]), (mouse_pos[0] + 8, mouse_pos[1]))
        pygame.draw.line(screen, (255, 255, 255), (mouse_pos[0], mouse_pos[1] - 8), (mouse_pos[0], mouse_pos[1] - 5))
        pygame.draw.line(screen, (255, 255, 255), (mouse_pos[0], mouse_pos[1] + 5), (mouse_pos[0], mouse_pos[1] + 8))

    elif game_state == "MENU":
        story_text = [
            "Le monde s'est effondré en une nuit.",
            "Une force invisible, \"La Chute\", a vidé les humains de leur âme,",
            "les transformant en mutants violents qui errent dans l'obscurité.",
            "",
            "Vous vous réveillez seul dans les ruines de votre maison.",
            "Vous n'avez aucune arme. Juste vos poings, et une lanterne faiblissante.",
            "Trouvez la sortie pour survivre. Mais restez sur vos gardes...",
            "Vous n'êtes peut-être plus tout à fait humain vous-même."
        ]
        draw_menu_card(screen, "LA CHUTE", "LE DERNIER SURVIVANT", story_text, btn_start)
        
    elif game_state == "GAMEOVER":
        gameover_text = [
            "La Chute a fini par consumer votre esprit.",
            "Vos forces vous ont abandonné au plus profond des ruines.",
            "",
            "Appuyez sur [R] ou cliquez ci-dessous pour recommencer."
        ]
        # Texte en rouge pour l'écran de mort
        draw_menu_card(screen, "VOUS AVEZ SUCCOMBÉ", "Votre âme a rejoint les ruines", gameover_text, btn_restart)

    elif game_state == "VICTORY":
        victory_text = [
            "Vous avez franchi le portail de résonance mystique.",
            "Pour l'instant... vous survivez.",
            "",
            "Les symboles mystérieux peints sur le sol confirment ce",
            "que vous redoutiez : ce n'est que le début d'un voyage",
            "bien plus vaste et terrifiant au cœur du cataclysme.",
            "",
            "Appuyez sur [R] ou cliquez ci-dessous pour continuer."
        ]
        draw_menu_card(screen, "SORTIE ATTEINTE", "Le premier pas vers la vérité", victory_text, btn_next)

    # Mettre à jour l'écran physique
    if volume_indicator_timer > 0:
        # Dimensions de l'indicateur de volume (translucide avec lueur néon)
        val_w = 240
        val_h = 65
        val_x = SCREEN_WIDTH - val_w - 30
        val_y = 30
        
        # Facteur de fondu (fade-out)
        alpha_factor = min(1.0, volume_indicator_timer / 0.3)
        bg_alpha = int(220 * alpha_factor)
        
        # Couleurs adaptées au fondu
        text_color = (int(255 * alpha_factor), int(255 * alpha_factor), int(255 * alpha_factor))
        border_color = (int(255 * alpha_factor), int(255 * alpha_factor), int(255 * alpha_factor))
        gray_color = (int(150 * alpha_factor), int(150 * alpha_factor), int(150 * alpha_factor))
        bar_bg_color = (int(40 * alpha_factor), int(40 * alpha_factor), int(40 * alpha_factor))
        
        # Fond translucide
        bg_surface = pygame.Surface((val_w, val_h), pygame.SRCALPHA)
        bg_surface.fill((10, 10, 10, bg_alpha))
        screen.blit(bg_surface, (val_x, val_y))
        
        # Liseré de contour néon
        draw_glow_line(screen, (val_x, val_y), (val_x + val_w, val_y), border_color, 1, border_color)
        draw_glow_line(screen, (val_x, val_y + val_h), (val_x + val_w, val_y + val_h), border_color, 1, border_color)
        draw_glow_line(screen, (val_x, val_y), (val_x, val_y + val_h), border_color, 1, border_color)
        draw_glow_line(screen, (val_x + val_w, val_y), (val_x + val_w, val_y + val_h), border_color, 1, border_color)
        
        # Textes (Libellé et Pourcentage)
        vol_pct = int(master_volume * 100)
        vol_lbl = font_hud_label.render("VOLUME MASTER", True, gray_color)
        screen.blit(vol_lbl, (val_x + 15, val_y + 12))
        
        vol_val = font_hud_value.render(f"{vol_pct}%", True, text_color)
        val_rect = vol_val.get_rect()
        val_rect.right = val_x + val_w - 15
        val_rect.top = val_y + 5
        screen.blit(vol_val, val_rect)
        
        # Barre de progression du volume
        pygame.draw.rect(screen, bar_bg_color, (val_x + 15, val_y + 42, 210, 8), border_radius=4)
        fill_w = int(210 * master_volume)
        if fill_w > 0:
            pygame.draw.rect(screen, text_color, (val_x + 15, val_y + 42, fill_w, 8), border_radius=4)

    pygame.display.flip()

# --- FERMETURE DE PYGAME ---
pygame.quit()
sys.exit()
