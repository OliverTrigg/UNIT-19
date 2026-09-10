import pygame
import random
import math

pygame.init()

# ============================================================
# SETTINGS
# ============================================================

WIDTH, HEIGHT = 1100, 700
FPS = 60

ROWS = 5
COLS = 9

GRID_X = 180
GRID_Y = 125
CELL_W = 95
CELL_H = 95

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER DEFENSE")
clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (5, 8, 15)
DARK = (10, 15, 25)
PANEL = (15, 22, 35)

WHITE = (235, 245, 255)
CYAN = (30, 220, 255)
BLUE = (50, 120, 255)
GREEN = (50, 230, 110)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 40)
RED = (240, 55, 70)
PURPLE = (175, 70, 255)

GRID_1 = (18, 45, 48)
GRID_2 = (15, 37, 43)

# ============================================================
# FONTS
# ============================================================

font = pygame.font.SysFont("consolas", 20, bold=True)
small_font = pygame.font.SysFont("consolas", 14)
big_font = pygame.font.SysFont("consolas", 42, bold=True)
huge_font = pygame.font.SysFont("consolas", 58, bold=True)

# ============================================================
# GAME STATE
# ============================================================

energy = 150
network_health = 100

score = 0
wave = 1

game_over = False
victory = False

selected_plant = None

game_speed_multiplier = 1.0
powerup_damage_boost = 0.0
active_buff_text = ""
active_buff_timer = 0.0
active_buff_color = WHITE

spawn_timer = 0
wave_timer = 0

plants = []
threats = []
projectiles = []
particles = []
energy_orbs = []
floating_text = []

# ============================================================
# MENU STATE
# ============================================================

MENU = 0
MODE_SELECT = 1
LOADOUT = 2
GAME = 3

game_state = MENU

game_mode = "campaign"
menu_time = 0
menu_particles = []
menu_selected_plant = "firewall"
selected_loadout = []
loadout_scroll = 0
settings_menu_open = False

UPGRADES = {
    "health": {"name": "REINFORCED FIREWALL", "description": "+25 BASE NETWORK HEALTH", "color": GREEN},
    "energy": {"name": "EXTRA POWER CELLS", "description": "+50 STARTING ENERGY", "color": YELLOW},
    "damage": {"name": "OVERCHARGED DEFENSES", "description": "+20% DEFENSE DAMAGE", "color": RED},
}
selected_upgrades = []
UPGRADE_SELECT = 4
MAX_UPGRADES = 2
base_network_health = 100
max_network_health = 100
damage_upgrade_multiplier = 1.0

settings = {
    "default_2x": False,
    "keep_loadout": True,
    "hard_mode": False,
}

quiz_active = False
quiz_question = ""
quiz_choices = []
quiz_correct_index = 0
correct_quiz_count = 0

# ============================================================
# PLANT TYPES
# ============================================================

PLANT_TYPES = {

    "firewall": {
        "name": "FIREWALL",
        "cost": 75,
        "color": BLUE,
        "health": 180,
        "damage": 20,
        "cooldown": 1.2,
        "description": "Fires rapid shots at nearby threats and blocks intrusions early."
    },

    "monitor": {
        "name": "SOC MONITOR",
        "cost": 50,
        "color": GREEN,
        "health": 100,
        "damage": 0,
        "cooldown": 4,
        "description": "Generates extra energy over time to fuel the rest of your defense line."
    },

    "segment": {
        "name": "SEGMENTATION",
        "cost": 50,
        "color": ORANGE,
        "health": 300,
        "damage": 0,
        "cooldown": 0,
        "description": "A tough barrier that holds the line and absorbs heavy punishment."
    },

    "limiter": {
        "name": "RATE LIMITER",
        "cost": 100,
        "color": CYAN,
        "health": 120,
        "damage": 10,
        "cooldown": 0.6,
        "description": "A fast striker that keeps pressure on enemies before they reach the server."
    },

    "incident": {
        "name": "INCIDENT RESPONSE",
        "cost": 125,
        "color": PURPLE,
        "health": 100,
        "damage": 70,
        "cooldown": 5,
        "description": "A high-impact force unit that destroys stronger threats with powerful bursts."
    },

    "antivirus": {
        "name": "ANTIVIRUS",
        "cost": 90,
        "color": GREEN,
        "health": 140,
        "damage": 28,
        "cooldown": 1.0,
        "description": "Scans and scrubs malicious code before it reaches the gateway."
    },

    "patch": {
        "name": "PATCH MANAGER",
        "cost": 80,
        "color": CYAN,
        "health": 130,
        "damage": 18,
        "cooldown": 0.8,
        "description": "Applies quick software fixes and chokes off vulnerability spikes."
    },

    "siem": {
        "name": "SIEM NODE",
        "cost": 100,
        "color": (140, 200, 255),
        "health": 110,
        "damage": 0,
        "cooldown": 3.5,
        "description": "Monitors unusual events and produces a steady stream of energy."
    },

    "backup": {
        "name": "BACKUP GUARD",
        "cost": 85,
        "color": YELLOW,
        "health": 170,
        "damage": 0,
        "cooldown": 4.2,
        "description": "Restores damaged systems and keeps the defense line online."
    },

    "honeypot": {
        "name": "HONEYPOT",
        "cost": 110,
        "color": ORANGE,
        "health": 150,
        "damage": 16,
        "cooldown": 1.4,
        "description": "Lures attackers into decoy traps and slows their advance."
    },

    "ids": {
        "name": "IDS SENSOR",
        "cost": 120,
        "color": (90, 180, 255),
        "health": 120,
        "damage": 35,
        "cooldown": 1.6,
        "description": "Detects suspicious activity and delivers precise high-damage alerts."
    },

    "vpn": {
        "name": "VPN SHIELD",
        "cost": 95,
        "color": (120, 255, 180),
        "health": 220,
        "damage": 12,
        "cooldown": 1.1,
        "description": "Encrypts traffic and punches through nearby intrusions with steady fire."
    },

    "sandbox": {
        "name": "SANDBOX",
        "cost": 130,
        "color": PURPLE,
        "health": 200,
        "damage": 0,
        "cooldown": 5,
        "description": "Isolates threats in a safe environment and keeps the network stable."
    }
}

# ============================================================
# THREAT TYPES
# ============================================================

THREAT_TYPES = {

    "phishing": {
        "name": "PHISHING",
        "health": 80,
        "speed": 18,
        "damage": 12,
        "color": YELLOW,
        "reward": 15
    },

    "virus": {
        "name": "VIRUS",
        "health": 120,
        "speed": 15,
        "damage": 17,
        "color": (255, 110, 120),
        "reward": 20
    },

    "worm": {
        "name": "WORM",
        "health": 90,
        "speed": 26,
        "damage": 11,
        "color": (120, 255, 140),
        "reward": 14
    },

    "rootkit": {
        "name": "ROOTKIT",
        "health": 180,
        "speed": 10,
        "damage": 23,
        "color": (180, 130, 255),
        "reward": 32
    },

    "botnet": {
        "name": "BOTNET",
        "health": 150,
        "speed": 18,
        "damage": 20,
        "color": (255, 180, 70),
        "reward": 28
    },

    "ddos": {
        "name": "DDoS BOT",
        "health": 60,
        "speed": 28,
        "damage": 8,
        "color": ORANGE,
        "reward": 10
    },

    "ransomware": {
        "name": "RANSOMWARE",
        "health": 250,
        "speed": 8,
        "damage": 30,
        "color": PURPLE,
        "reward": 50
    },

    "boss": {
        "name": "BOSS",
        "health": 500,
        "speed": 6,
        "damage": 45,
        "color": RED,
        "reward": 120
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def draw_glow(surface, position, color, radius, strength=3):

    x, y = position

    for i in range(strength, 0, -1):

        r = radius + i * 6
        alpha = max(10, 45 - i * 8)

        glow = pygame.Surface(
            (r * 2, r * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (*color, alpha),
            (r, r),
            r
        )

        surface.blit(
            glow,
            (x - r, y - r)
        )


def draw_text(text, x, y, color=WHITE, f=font):

    image = f.render(text, True, color)
    screen.blit(image, (x, y))


def wrap_text(text, max_chars):

    words = text.split()
    lines = []
    current = ""

    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines or [text]


def add_particles(x, y, color, amount=12):

    for _ in range(amount):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            40,
            150
        )

        particles.append(
            Particle(
                x,
                y,
                color,
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
        )


def add_floating_text(text, x, y, color):

    floating_text.append(
        FloatingText(
            text,
            x,
            y,
            color
        )
    )


def get_antivirus_multiplier(threat_type):

    if threat_type in ("virus", "worm"):
        return 2.8
    if threat_type in ("rootkit", "botnet"):
        return 2.2
    if threat_type == "ransomware":
        return 1.6
    if threat_type == "ddos":
        return 1.4
    return 1.1


def grant_powerup(reward):

    global energy
    global network_health
    global max_network_health
    global base_network_health
    global powerup_damage_boost
    global active_buff_text
    global active_buff_timer
    global active_buff_color

    if reward == "damage":
        powerup_damage_boost = 10.0
        active_buff_text = "DAMAGE BOOST"
        active_buff_timer = 10.0
        active_buff_color = PURPLE
        add_floating_text(
            "DAMAGE BOOST 10s",
            WIDTH // 2 - 90,
            150,
            PURPLE
        )
        add_particles(
            WIDTH // 2,
            150,
            PURPLE,
            25
        )

    elif reward == "energy":
        energy += 50
        active_buff_text = "ENERGY BONUS +50"
        active_buff_timer = 3.0
        active_buff_color = YELLOW
        add_floating_text(
            "+50 ENERGY",
            WIDTH // 2 - 70,
            150,
            YELLOW
        )
        add_particles(
            WIDTH // 2,
            150,
            YELLOW,
            25
        )

    else:
        base_network_health += 25
        max_network_health = base_network_health
        network_health = min(max_network_health, network_health + 25)
        active_buff_text = "HEALTH BONUS +25"
        active_buff_timer = 3.0
        active_buff_color = GREEN
        add_floating_text(
            "+25 HEALTH",
            WIDTH // 2 - 70,
            150,
            GREEN
        )
        add_particles(
            WIDTH // 2,
            150,
            GREEN,
            25
        )


def grid_position(mouse_pos):

    mx, my = mouse_pos

    if (
        GRID_X <= mx <
        GRID_X + COLS * CELL_W
        and
        GRID_Y <= my <
        GRID_Y + ROWS * CELL_H
    ):

        col = int(
            (mx - GRID_X) / CELL_W
        )

        row = int(
            (my - GRID_Y) / CELL_H
        )

        return row, col

    return None


def occupied(row, col):

    return any(
        p.row == row and p.col == col
        for p in plants
    )


# ============================================================
# MENU PARTICLE
# ============================================================

class MenuParticle:

    def __init__(self):

        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

        self.speed = random.uniform(15, 50)

        self.size = random.randint(1, 3)

        self.alpha = random.randint(60, 180)

        self.color = random.choice([
            CYAN,
            BLUE,
            GREEN,
            PURPLE
        ])

    def update(self, dt):

        self.y -= self.speed * dt

        if self.y < -10:

            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)

    def draw(self):

        pygame.draw.circle(
            screen,
            self.color,
            (
                int(self.x),
                int(self.y)
            ),
            self.size
        )


# Create menu particles

for _ in range(90):

    menu_particles.append(
        MenuParticle()
    )


# ============================================================
# MENU BACKGROUND
# ============================================================

def draw_menu_background():

    screen.fill(BLACK)

    # Cyber grid

    grid_offset = int(menu_time * 20) % 40

    for x in range(
        -40,
        WIDTH + 40,
        40
    ):

        pygame.draw.line(
            screen,
            (8, 25, 35),
            (x, 0),
            (x, HEIGHT),
            1
        )

    for y in range(
        -40 + grid_offset,
        HEIGHT,
        40
    ):

        pygame.draw.line(
            screen,
            (8, 25, 35),
            (0, y),
            (WIDTH, y),
            1
        )

    # Horizontal moving scan line

    scan_y = int(
        (menu_time * 90) % HEIGHT
    )

    scan_surface = pygame.Surface(
        (WIDTH, 3),
        pygame.SRCALPHA
    )

    scan_surface.fill(
        (*CYAN, 35)
    )

    screen.blit(
        scan_surface,
        (0, scan_y)
    )

    # Particles

    for particle in menu_particles:

        particle.draw()


# ============================================================
# MENU BUTTON
# ============================================================

def draw_menu_button(
    rect,
    text,
    mouse_pos,
    active_color=CYAN
):

    hovered = rect.collidepoint(
        mouse_pos
    )

    if hovered:

        color = active_color

        draw_glow(
            screen,
            rect.center,
            active_color,
            35,
            3
        )

        fill_color = (
            20,
            65,
            75
        )

    else:

        color = (
            30,
            110,
            120
        )

        fill_color = (
            12,
            28,
            40
        )

    pygame.draw.rect(
        screen,
        fill_color,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        2,
        border_radius=8
    )

    image = big_font.render(
        text,
        True,
        WHITE
    )

    screen.blit(
        image,
        (
            rect.centerx -
            image.get_width() // 2,
            rect.centery -
            image.get_height() // 2
        )
    )

    return hovered


# ============================================================
# MAIN MENU
# ============================================================

CYBER_QUESTIONS = [
    {
        "question": "Which practice is best for protecting accounts from password theft?",
        "choices": [
            "Using a unique strong password and MFA",
            "Sharing passwords with teammates",
            "Saving passwords in plain text files",
            "Reusing the same password everywhere"
        ],
        "answer": 0
    },
    {
        "question": "What does MFA stand for?",
        "choices": [
            "Multiple File Access",
            "Multi-Factor Authentication",
            "Main Frame Access",
            "Manual Fraud Alert"
        ],
        "answer": 1
    },
    {
        "question": "What is the safest action when you receive an unexpected email link?",
        "choices": [
            "Open it immediately",
            "Delete it or verify it through a trusted source",
            "Forward it to everyone",
            "Click it to check if it is safe"
        ],
        "answer": 1
    },
    {
        "question": "Which of these is a common sign of a phishing attempt?",
        "choices": [
            "A trusted sender address with urgent pressure and suspicious links",
            "A calm message from a known colleague",
            "A normal software update alert",
            "A password manager reminder"
        ],
        "answer": 0
    },
    {
        "question": "What should you do before installing a downloaded attachment?",
        "choices": [
            "Scan it and confirm it is expected",
            "Open it right away to test it",
            "Send it to friends",
            "Save it to the desktop without checking"
        ],
        "answer": 0
    },
    {
        "question": "Which action helps reduce ransomware risk?",
        "choices": [
            "Backing up files regularly and patching systems",
            "Clicking every pop-up ad",
            "Disabling antivirus entirely",
            "Sharing admin credentials widely"
        ],
        "answer": 0
    },
    {
        "question": "What is the purpose of a firewall?",
        "choices": [
            "To block or filter unwanted network traffic",
            "To create a backup of all files",
            "To print cybersecurity reports",
            "To delete viruses from the CPU"
        ],
        "answer": 0
    },
    {
        "question": "What is the best response to a suspected malware alert?",
        "choices": [
            "Disconnect the device and report it", 
            "Ignore it and continue working",
            "Open the file to inspect it",
            "Share the alert with strangers"
        ],
        "answer": 0
    }
]


def start_quiz():

    global quiz_active
    global quiz_question
    global quiz_choices
    global quiz_correct_index

    question = random.choice(CYBER_QUESTIONS)
    quiz_active = True
    quiz_question = question["question"]
    quiz_choices = question["choices"]
    quiz_correct_index = question["answer"]


def draw_quiz():

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(WIDTH // 2 - 330, 120, 660, 440)
    pygame.draw.rect(screen, (15, 28, 38), panel, border_radius=18)
    pygame.draw.rect(screen, CYAN, panel, 2, border_radius=18)

    title = huge_font.render("CYBER CHALLENGE", True, CYAN)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

    question_text = font.render(quiz_question, True, WHITE)
    screen.blit(question_text, (WIDTH // 2 - question_text.get_width() // 2, 220))

    for i, choice in enumerate(quiz_choices):
        option_rect = pygame.Rect(WIDTH // 2 - 230, 270 + i * 70, 460, 52)
        hovered = option_rect.collidepoint(pygame.mouse.get_pos())
        fill = (20, 65, 75) if hovered else (15, 35, 45)
        border = CYAN if hovered else (80, 130, 145)
        pygame.draw.rect(screen, fill, option_rect, border_radius=10)
        pygame.draw.rect(screen, border, option_rect, 2, border_radius=10)

        text = small_font.render(f"{chr(65 + i)}. {choice}", True, WHITE)
        screen.blit(text, (option_rect.x + 18, option_rect.y + 16))

        if i == quiz_correct_index:
            pass

    hint = small_font.render("WRONG ANSWER: -25 HEALTH", True, RED)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 560))


def check_quiz_answer(index):

    global quiz_active
    global network_health
    global correct_quiz_count
    global game_state

    quiz_active = False

    if index != quiz_correct_index:
        network_health = max(0, network_health - 25)
        add_floating_text("-25 HEALTH", WIDTH // 2 - 60, 170, RED)
        add_particles(WIDTH // 2, 170, RED, 25)
        return

    correct_quiz_count += 1

    add_floating_text(
        f"CORRECT! {correct_quiz_count}/3",
        WIDTH // 2 - 70,
        170,
        GREEN
    )
    add_particles(WIDTH // 2, 170, GREEN, 18)

    if settings.get("hard_mode", False):
        if correct_quiz_count >= 3:
            correct_quiz_count = 0
            reward_choice = random.choice(["damage", "energy", "health"])
            grant_powerup(reward_choice)
        else:
            reward_choice = random.choice(["damage", "energy", "health"])
            grant_powerup(reward_choice)
    else:
        # Normal mode: let the player choose which upgrade they want.
        if correct_quiz_count >= 3:
            correct_quiz_count = 0
        game_state = UPGRADE_SELECT


def draw_settings_panel():

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(WIDTH // 2 - 260, 150, 520, 360)
    pygame.draw.rect(screen, (15, 28, 38), panel, border_radius=18)
    pygame.draw.rect(screen, CYAN, panel, 2, border_radius=18)

    title = huge_font.render("SETTINGS", True, CYAN)
    screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 20))

    toggle_y = panel.top + 110
    toggle_w = 220
    toggle_h = 46

    for key, label in [
        ("default_2x", "DEFAULT 2X SPEED"),
        ("keep_loadout", "KEEP LOADOUT"),
        ("hard_mode", "HARD MODE"),
    ]:
        rect = pygame.Rect(panel.centerx - toggle_w // 2, toggle_y, toggle_w, toggle_h)
        active = settings[key]
        fill = (22, 80, 70) if active else (18, 35, 48)
        border = GREEN if active else (100, 130, 150)
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        text = small_font.render(label, True, WHITE)
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2 + 1))

        toggle_y += 70

    close_rect = pygame.Rect(panel.centerx - 90, panel.bottom - 58, 180, 36)
    pygame.draw.rect(screen, (30, 45, 60), close_rect, border_radius=8)
    pygame.draw.rect(screen, CYAN, close_rect, 2, border_radius=8)
    close_text = small_font.render("CLOSE", True, WHITE)
    screen.blit(close_text, (close_rect.centerx - close_text.get_width() // 2, close_rect.centery - close_text.get_height() // 2 + 1))

    return close_rect


def draw_main_menu():

    draw_menu_background()

    if settings_menu_open:
        close_rect = draw_settings_panel()
        return start_rect if False else (None, None, close_rect)

    # Animated title

    pulse = (
        math.sin(menu_time * 3) * 3
    )

    title_y = 120 + int(pulse)

    draw_glow(
        screen,
        (
            WIDTH // 2,
            title_y + 30
        ),
        CYAN,
        80,
        4
    )

    title = huge_font.render(
        "CYBER DEFENSE",
        True,
        CYAN
    )

    screen.blit(
        title,
        (
            WIDTH // 2 -
            title.get_width() // 2,
            title_y
        )
    )

    # Subtitle

    subtitle = font.render(
        "DEFEND THE NETWORK",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2 -
            subtitle.get_width() // 2,
            200
        )
    )

    # Animated status

    dots = "." * (
        int(menu_time * 2) % 4
    )

    status = small_font.render(
        "SYSTEM STATUS: ONLINE" + dots,
        True,
        GREEN
    )

    screen.blit(
        status,
        (
            WIDTH // 2 -
            status.get_width() // 2,
            235
        )
    )

    # Buttons

    mouse_pos = pygame.mouse.get_pos()

    start_rect = pygame.Rect(
        WIDTH // 2 - 170,
        300,
        340,
        70
    )

    settings_rect = pygame.Rect(
        WIDTH // 2 - 170,
        390,
        340,
        60
    )

    quit_rect = pygame.Rect(
        WIDTH // 2 - 170,
        470,
        340,
        60
    )

    draw_menu_button(
        start_rect,
        "START GAME",
        mouse_pos,
        CYAN
    )

    draw_menu_button(
        settings_rect,
        "SETTINGS",
        mouse_pos,
        GREEN
    )

    draw_menu_button(
        quit_rect,
        "QUIT",
        mouse_pos,
        RED
    )

    # Instructions

    instruction = small_font.render(
        "DEFEND YOUR SERVER FROM CYBER THREATS",
        True,
        (100, 170, 185)
    )

    screen.blit(
        instruction,
        (
            WIDTH // 2 -
            instruction.get_width() // 2,
            560
        )
    )

    controls = small_font.render(
        "MOUSE: SELECT & PLACE DEFENSES     R: RESTART",
        True,
        (80, 130, 145)
    )

    screen.blit(
        controls,
        (
            WIDTH // 2 -
            controls.get_width() // 2,
            590
        )
    )

    # Version

    draw_text(
        "CYBER DEFENSE v1.0",
        20,
        HEIGHT - 30,
        (60, 100, 115),
        small_font
    )

    return start_rect, settings_rect, quit_rect


def draw_mode_select_menu():

    draw_menu_background()

    title = huge_font.render(
        "CHOOSE GAME MODE",
        True,
        CYAN
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            90
        )
    )

    subtitle = small_font.render(
        "PICK A MODE, THEN SELECT YOUR FIVE DEFENSE UNITS",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2 - subtitle.get_width() // 2,
            150
        )
    )

    mouse_pos = pygame.mouse.get_pos()

    campaign_rect = pygame.Rect(WIDTH // 2 - 310, 230, 260, 160)
    endless_rect = pygame.Rect(WIDTH // 2 + 50, 230, 260, 160)

    for rect, mode_key, title_text, desc_text in [
        (campaign_rect, "campaign", "10 WAVE MODE", "Classic survival. Defend the network through 10 escalating waves."),
        (endless_rect, "endless", "ENDLESS MODE", "Keep surviving as the threat count and difficulty never stop rising.")
    ]:
        active = game_mode == mode_key
        hovered = rect.collidepoint(mouse_pos)

        fill_color = (22, 72, 82) if active else ((18, 38, 50) if hovered else (12, 26, 38))
        border_color = CYAN if active else (70, 120, 140)

        pygame.draw.rect(screen, fill_color, rect, border_radius=12)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)

        mode_title = big_font.render(title_text, True, WHITE)
        screen.blit(mode_title, (rect.centerx - mode_title.get_width() // 2, rect.top + 20))

        desc_lines = []
        current = ""
        for word in desc_text.split():
            if len(current) + len(word) + 1 <= 24:
                current = f"{current} {word}".strip()
            else:
                desc_lines.append(current)
                current = word
        if current:
            desc_lines.append(current)

        for i, line in enumerate(desc_lines[:2]):
            line_text = small_font.render(line.upper(), True, (180, 220, 240))
            screen.blit(line_text, (rect.left + 12, rect.top + 82 + i * 18))

    back_rect = pygame.Rect(WIDTH // 2 - 170, 610, 340, 50)
    back_hover = back_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, (30, 45, 60) if back_hover else (15, 25, 35), back_rect, border_radius=8)
    pygame.draw.rect(screen, (120, 150, 160), back_rect, 2, border_radius=8)
    back_text = font.render("BACK TO MENU", True, WHITE)
    screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

    return campaign_rect, endless_rect, back_rect


def draw_upgrade_select_menu():
    screen.fill((6, 12, 22))
    draw_text("SELECT UPGRADES", WIDTH // 2 - 185, 55, CYAN, huge_font)
    draw_text(f"CHOOSE UP TO {MAX_UPGRADES} UPGRADES", WIDTH // 2 - 145, 120, (150, 200, 210), small_font)

    rects = []
    for index, (upgrade_key, data) in enumerate(UPGRADES.items()):
        y = 185 + index * 125
        rect = pygame.Rect(WIDTH // 2 - 310, y, 620, 95)
        rects.append((upgrade_key, rect))
        selected = upgrade_key in selected_upgrades
        pygame.draw.rect(screen, (18, 45, 55) if selected else (12, 25, 40), rect, border_radius=14)
        pygame.draw.rect(screen, data["color"] if selected else (70, 110, 130), rect, 3 if selected else 2, border_radius=14)
        draw_text(data["name"], rect.x + 25, rect.y + 18, data["color"], big_font)
        draw_text(data["description"], rect.x + 25, rect.y + 58, WHITE, small_font)
        draw_text("SELECTED" if selected else "CLICK TO SELECT", rect.right - 145, rect.y + 37, GREEN if selected else (150, 180, 190), small_font)

    continue_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT - 105, 230, 55)
    back_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 105, 230, 55)
    pygame.draw.rect(screen, (15, 70, 70), continue_rect, border_radius=12)
    pygame.draw.rect(screen, CYAN, continue_rect, 2, border_radius=12)
    pygame.draw.rect(screen, (35, 35, 50), back_rect, border_radius=12)
    pygame.draw.rect(screen, (130, 160, 180), back_rect, 2, border_radius=12)
    draw_text("CONTINUE", continue_rect.centerx - 52, continue_rect.centery - 12, WHITE, small_font)
    draw_text("BACK", back_rect.centerx - 25, back_rect.centery - 12, WHITE, small_font)
    return rects, continue_rect, back_rect


def draw_loadout_menu():

    global loadout_scroll

    draw_menu_background()

    title = huge_font.render(
        "SELECT YOUR FIVE UNITS",
        True,
        CYAN
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            60
        )
    )

    subtitle = small_font.render(
        "CHOOSE EXACTLY 5 DEFENSES TO BRING INTO BATTLE",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2 - subtitle.get_width() // 2,
            120
        )
    )

    count_text = font.render(
        f"SELECTED: {len(selected_loadout)}/5",
        True,
        YELLOW if len(selected_loadout) == 5 else WHITE
    )

    screen.blit(
        count_text,
        (
            WIDTH // 2 - count_text.get_width() // 2,
            150
        )
    )

    mouse_pos = pygame.mouse.get_pos()

    card_width = 220
    card_height = 120
    gap_x = 16
    gap_y = 10
    start_x = 120
    start_y = 180
    visible_top = 160
    visible_bottom = 500

    total_rows = (len(PLANT_TYPES) + 2) // 3
    max_scroll = max(0, start_y + total_rows * (card_height + gap_y) - visible_bottom)
    loadout_scroll = min(loadout_scroll, max_scroll)

    scroll_hint = small_font.render("SCROLL: MOUSE WHEEL / ARROWS", True, (120, 170, 190))
    screen.blit(scroll_hint, (WIDTH // 2 - scroll_hint.get_width() // 2, 165))

    for index, plant_type in enumerate(PLANT_TYPES):

        data = PLANT_TYPES[plant_type]

        col = index % 3
        row = index // 3

        rect = pygame.Rect(
            start_x + col * (card_width + gap_x),
            start_y - loadout_scroll + row * (card_height + gap_y),
            card_width,
            card_height
        )

        if rect.bottom < visible_top or rect.top > visible_bottom:
            continue

        selected = plant_type in selected_loadout
        hovered = rect.collidepoint(mouse_pos)

        if selected:
            fill_color = (20, 60, 70)
            border_color = CYAN
        elif hovered:
            fill_color = (18, 37, 48)
            border_color = (130, 220, 255)
        else:
            fill_color = (12, 28, 40)
            border_color = (40, 100, 115)

        pygame.draw.rect(screen, fill_color, rect, border_radius=10)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)

        icon_x = rect.left + 28
        icon_y = rect.top + 30

        if plant_type == "firewall":
            shield = [(icon_x, icon_y - 18), (icon_x + 16, icon_y - 11), (icon_x + 13, icon_y + 10), (icon_x, icon_y + 18), (icon_x - 13, icon_y + 10), (icon_x - 16, icon_y - 11)]
            pygame.draw.polygon(screen, data["color"], shield)
        elif plant_type == "monitor":
            pygame.draw.rect(screen, data["color"], (icon_x - 16, icon_y - 14, 32, 24), border_radius=4)
            pygame.draw.rect(screen, BLACK, (icon_x - 12, icon_y - 10, 24, 16))
            pygame.draw.line(screen, GREEN, (icon_x - 10, icon_y + 2), (icon_x - 3, icon_y - 5), 2)
            pygame.draw.line(screen, GREEN, (icon_x - 3, icon_y - 5), (icon_x + 8, icon_y + 7), 2)
        elif plant_type == "segment":
            pygame.draw.rect(screen, data["color"], (icon_x - 17, icon_y - 17, 34, 34), border_radius=4)
            pygame.draw.line(screen, WHITE, (icon_x - 14, icon_y), (icon_x + 14, icon_y), 2)
            pygame.draw.line(screen, WHITE, (icon_x - 14, icon_y + 8), (icon_x + 14, icon_y + 8), 2)
        elif plant_type == "limiter":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 16)
            pygame.draw.circle(screen, BLACK, (icon_x, icon_y), 11)
            pygame.draw.line(screen, CYAN, (icon_x, icon_y), (icon_x + 9, icon_y - 9), 3)
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y), 3)
        elif plant_type == "incident":
            pygame.draw.rect(screen, data["color"], (icon_x - 15, icon_y - 16, 30, 32), border_radius=6)
            pygame.draw.rect(screen, WHITE, (icon_x - 13, icon_y - 18, 26, 8), border_radius=3)
            pygame.draw.circle(screen, CYAN, (icon_x - 6, icon_y - 3), 4)
            pygame.draw.circle(screen, CYAN, (icon_x + 6, icon_y - 3), 4)
        elif plant_type == "antivirus":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 16)
            pygame.draw.line(screen, BLACK, (icon_x - 10, icon_y), (icon_x + 10, icon_y), 3)
            pygame.draw.line(screen, BLACK, (icon_x, icon_y - 10), (icon_x, icon_y + 10), 3)
        elif plant_type == "patch":
            pygame.draw.rect(screen, data["color"], (icon_x - 15, icon_y - 15, 30, 30), border_radius=5)
            pygame.draw.line(screen, WHITE, (icon_x - 7, icon_y), (icon_x - 1, icon_y + 7), 3)
            pygame.draw.line(screen, WHITE, (icon_x - 1, icon_y + 7), (icon_x + 11, icon_y - 8), 3)
        elif plant_type == "siem":
            pygame.draw.rect(screen, data["color"], (icon_x - 18, icon_y - 14, 36, 28), border_radius=5)
            pygame.draw.rect(screen, BLACK, (icon_x - 12, icon_y - 9, 24, 18))
            for offset in (-10, 0, 10):
                pygame.draw.line(screen, (140, 200, 255), (icon_x + offset, icon_y - 8), (icon_x + offset + 7, icon_y + 10), 2)
        elif plant_type == "backup":
            pygame.draw.rect(screen, data["color"], (icon_x - 15, icon_y - 15, 30, 30), border_radius=5)
            pygame.draw.rect(screen, WHITE, (icon_x - 7, icon_y - 7, 14, 14), border_radius=3)
            pygame.draw.line(screen, BLACK, (icon_x - 5, icon_y), (icon_x + 5, icon_y), 2)
        elif plant_type == "honeypot":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 14)
            pygame.draw.line(screen, WHITE, (icon_x, icon_y - 20), (icon_x, icon_y - 6), 3)
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y - 24), 3)
        elif plant_type == "ids":
            tri = [(icon_x, icon_y - 18), (icon_x + 15, icon_y + 14), (icon_x - 15, icon_y + 14)]
            pygame.draw.polygon(screen, data["color"], tri)
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y), 6)
        elif plant_type == "vpn":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 15)
            pygame.draw.circle(screen, BLACK, (icon_x, icon_y), 10)
            pygame.draw.line(screen, WHITE, (icon_x - 8, icon_y), (icon_x + 8, icon_y), 3)
        elif plant_type == "sandbox":
            sandbox_points = [(icon_x, icon_y - 18), (icon_x + 16, icon_y - 8), (icon_x + 16, icon_y + 10), (icon_x, icon_y + 20), (icon_x - 16, icon_y + 10), (icon_x - 16, icon_y - 8)]
            pygame.draw.polygon(screen, data["color"], sandbox_points)
            pygame.draw.line(screen, WHITE, (icon_x - 8, icon_y), (icon_x + 8, icon_y), 3)

        name_lines = wrap_text(data["name"], 11)
        for i, line in enumerate(name_lines[:2]):
            draw_text(line, rect.left + 52, rect.top + 12 + i * 14, WHITE, small_font)
        draw_text(f"{data['cost']} ENERGY", rect.left + 52, rect.top + 42, YELLOW, small_font)

        description = data["description"]
        for i, line in enumerate(wrap_text(description, 22)[:2]):
            draw_text(line.upper(), rect.left + 12, rect.top + 68 + i * 16, (160, 220, 230), small_font)

        if selected:
            draw_text("SELECTED", rect.left + 14, rect.bottom - 22, GREEN, small_font)
        elif len(selected_loadout) >= 5:
            draw_text("FULL", rect.left + 14, rect.bottom - 22, (180, 180, 180), small_font)

    begin_rect = pygame.Rect(WIDTH // 2 - 150, 560, 300, 38)
    begin_hover = begin_rect.collidepoint(mouse_pos)

    fill_color = (20, 65, 75) if begin_hover and len(selected_loadout) == 5 else (12, 28, 40)
    border_color = CYAN if len(selected_loadout) == 5 else (70, 100, 110)

    pygame.draw.rect(screen, fill_color, begin_rect, border_radius=8)
    pygame.draw.rect(screen, border_color, begin_rect, 2, border_radius=8)

    begin_text = font.render(
        "BEGIN BATTLE" if len(selected_loadout) == 5 else "SELECT 5 UNITS",
        True,
        WHITE
    )

    screen.blit(
        begin_text,
        (
            begin_rect.centerx - begin_text.get_width() // 2,
            begin_rect.centery - begin_text.get_height() // 2
        )
    )

    back_rect = pygame.Rect(WIDTH // 2 - 150, 610, 300, 32)
    back_hover = back_rect.collidepoint(mouse_pos)
    back_fill = (30, 45, 60) if back_hover else (15, 25, 35)

    pygame.draw.rect(screen, back_fill, back_rect, border_radius=8)
    pygame.draw.rect(screen, (120, 150, 160), back_rect, 2, border_radius=8)
    back_text = font.render("BACK TO MENU", True, WHITE)
    screen.blit(
        back_text,
        (
            back_rect.centerx - back_text.get_width() // 2,
            back_rect.centery - back_text.get_height() // 2
        )
    )

    return begin_rect, back_rect


# ============================================================
# HUD ICONS
# ============================================================

class HUDIcon:

    def __init__(self, x, y, icon_type):

        self.x = x
        self.y = y
        self.icon_type = icon_type

        self.animation = (
            random.random() * 10
        )

    def update(self, dt):

        self.animation += dt * 4

    def draw(self, value=100):

        pulse = (
            math.sin(self.animation) * 2
        )

        if self.icon_type == "energy":

            color = YELLOW

            draw_glow(
                screen,
                (
                    int(self.x),
                    int(self.y + pulse)
                ),
                color,
                15,
                2
            )

            pygame.draw.rect(
                screen,
                color,
                (
                    self.x - 17,
                    self.y - 13 + pulse,
                    30,
                    26
                ),
                2,
                border_radius=4
            )

            pygame.draw.rect(
                screen,
                color,
                (
                    self.x + 13,
                    self.y - 6 + pulse,
                    6,
                    12
                ),
                border_radius=2
            )

            bolt = [
                (
                    self.x + 1,
                    self.y - 10 + pulse
                ),
                (
                    self.x - 9,
                    self.y + 2 + pulse
                ),
                (
                    self.x - 1,
                    self.y + 2 + pulse
                ),
                (
                    self.x - 5,
                    self.y + 12 + pulse
                ),
                (
                    self.x + 10,
                    self.y - 4 + pulse
                ),
                (
                    self.x + 2,
                    self.y - 4 + pulse
                )
            ]

            pygame.draw.polygon(
                screen,
                color,
                bolt
            )

        elif self.icon_type == "health":

            if value > 60:
                color = GREEN
            elif value > 30:
                color = YELLOW
            else:
                color = RED

            draw_glow(
                screen,
                (
                    self.x,
                    self.y
                ),
                color,
                16,
                2
            )

            shield = [
                (
                    self.x,
                    self.y - 18
                ),
                (
                    self.x + 17,
                    self.y - 11
                ),
                (
                    self.x + 14,
                    self.y + 10
                ),
                (
                    self.x,
                    self.y + 20
                ),
                (
                    self.x - 14,
                    self.y + 10
                ),
                (
                    self.x - 17,
                    self.y - 11
                )
            ]

            pygame.draw.polygon(
                screen,
                color,
                shield
            )

            pygame.draw.polygon(
                screen,
                WHITE,
                shield,
                2
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    self.x,
                    self.y
                ),
                3
            )

            pygame.draw.line(
                screen,
                WHITE,
                (
                    self.x,
                    self.y
                ),
                (
                    self.x - 8,
                    self.y - 8
                ),
                2
            )

            pygame.draw.line(
                screen,
                WHITE,
                (
                    self.x,
                    self.y
                ),
                (
                    self.x + 8,
                    self.y - 8
                ),
                2
            )

            pulse_size = int(
                22 +
                math.sin(self.animation) * 4
            )

            pygame.draw.circle(
                screen,
                color,
                (
                    self.x,
                    self.y
                ),
                pulse_size,
                1
            )


energy_icon = HUDIcon(
    480,
    40,
    "energy"
)

health_icon = HUDIcon(
    630,
    40,
    "health"
)


# ============================================================
# PARTICLES
# ============================================================

class Particle:

    def __init__(
        self,
        x,
        y,
        color,
        vx,
        vy
    ):

        self.x = x
        self.y = y

        self.color = color

        self.vx = vx
        self.vy = vy

        self.life = random.uniform(
            0.3,
            0.8
        )

        self.max_life = self.life

        self.size = random.randint(
            2,
            5
        )

    def update(self, dt):

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vy += 80 * dt

        self.life -= dt

    def draw(self):

        if self.life <= 0:
            return

        alpha = int(
            255 *
            (
                self.life /
                self.max_life
            )
        )

        surface = pygame.Surface(
            (
                self.size * 4,
                self.size * 4
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surface,
            (
                *self.color,
                alpha
            ),
            (
                self.size * 2,
                self.size * 2
            ),
            self.size
        )

        screen.blit(
            surface,
            (
                int(
                    self.x -
                    self.size * 2
                ),
                int(
                    self.y -
                    self.size * 2
                )
            )
        )


# ============================================================
# FLOATING TEXT
# ============================================================

class FloatingText:

    def __init__(
        self,
        text,
        x,
        y,
        color
    ):

        self.text = text
        self.x = x
        self.y = y
        self.color = color

        self.life = 1.0

    def update(self, dt):

        self.y -= 30 * dt
        self.life -= dt

    def draw(self):

        if self.life <= 0:
            return

        image = small_font.render(
            self.text,
            True,
            self.color
        )

        screen.blit(
            image,
            (
                int(self.x),
                int(self.y)
            )
        )


# ============================================================
# ENERGY ORB
# ============================================================

class EnergyOrb:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.life = 7

        self.animation = (
            random.random() * 10
        )

    def update(self, dt):

        self.life -= dt

        self.animation += dt * 4

    def draw(self):

        offset = (
            math.sin(self.animation) *
            4
        )

        draw_glow(
            screen,
            (
                int(self.x),
                int(self.y + offset)
            ),
            YELLOW,
            12,
            3
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                int(self.x),
                int(self.y + offset)
            ),
            10
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x),
                int(self.y + offset)
            ),
            4
        )


# ============================================================
# PROJECTILE
# ============================================================

class Projectile:

    def __init__(
        self,
        x,
        y,
        damage,
        row
    ):

        self.x = x
        self.y = y

        self.damage = damage
        self.row = row

        self.speed = 360

        self.life = 3

    def update(self, dt):

        self.x += (
            self.speed * dt
        )

        self.life -= dt

    def draw(self):

        draw_glow(
            screen,
            (
                int(self.x),
                int(self.y)
            ),
            CYAN,
            8,
            2
        )

        pygame.draw.circle(
            screen,
            CYAN,
            (
                int(self.x),
                int(self.y)
            ),
            7
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            3
        )


# ============================================================
# PLANT
# ============================================================

class Plant:

    def __init__(
        self,
        row,
        col,
        plant_type
    ):

        self.row = row
        self.col = col
        self.type = plant_type

        data = PLANT_TYPES[
            plant_type
        ]

        self.x = (
            GRID_X +
            col * CELL_W +
            CELL_W // 2
        )

        self.y = (
            GRID_Y +
            row * CELL_H +
            CELL_H // 2
        )

        self.health = data["health"]

        self.max_health = data["health"]

        self.damage = data["damage"]

        self.cooldown = data["cooldown"]

        self.timer = (
            random.uniform(0, 1)
        )

        self.animation = (
            random.random() * 10
        )

        self.hit_flash = 0

    def update(self, dt):

        self.timer += dt

        self.animation += dt * 3

        self.hit_flash -= dt

        if powerup_damage_boost > 0:
            self.timer += dt * 0.25

        if self.type == "antivirus":

            if self.timer >= self.cooldown:

                target = None
                for threat in threats:
                    if threat.row == self.row and threat.x > self.x and threat.x - self.x < 220:
                        if target is None or threat.x > target.x:
                            target = threat

                if target:
                    bonus_multiplier = get_antivirus_multiplier(target.type)
                    target.health -= self.damage * bonus_multiplier
                    target.hit_flash = 0.12
                    add_particles(self.x + 30, self.y, GREEN, 10)
                    add_floating_text(f"{int(self.damage * bonus_multiplier)}", target.x, target.y - 24, GREEN)
                    self.timer = 0

        elif self.type == "monitor":

            if self.timer >= self.cooldown:

                global energy

                energy += 20

                energy_orbs.append(
                    EnergyOrb(
                        self.x,
                        self.y - 35
                    )
                )

                add_floating_text(
                    "+20 ENERGY",
                    self.x - 35,
                    self.y - 55,
                    YELLOW
                )

                self.timer = 0

        elif self.damage > 0:

            if self.timer >= self.cooldown:

                enemy_present = any(
                    t.row == self.row
                    and
                    t.x > self.x
                    for t in threats
                )

                if enemy_present:

                    projectile_damage = self.damage
                    if powerup_damage_boost > 0:
                        projectile_damage *= 2

                    projectiles.append(
                        Projectile(
                            self.x + 35,
                            self.y,
                            projectile_damage,
                            self.row
                        )
                    )

                    add_particles(
                        self.x + 30,
                        self.y,
                        PLANT_TYPES[
                            self.type
                        ]["color"],
                        5
                    )

                    self.timer = 0

    def draw(self):

        data = PLANT_TYPES[
            self.type
        ]

        color = data["color"]

        bob = (
            math.sin(
                self.animation
            ) * 2
        )

        x = int(self.x)
        y = int(self.y + bob)

        pygame.draw.ellipse(
            screen,
            (5, 10, 15),
            (
                x - 32,
                y + 28,
                64,
                15
            )
        )

        draw_glow(
            screen,
            (x, y),
            color,
            25,
            2
        )

        if self.hit_flash > 0:
            color = WHITE

        if self.type == "firewall":

            shield = [
                (x, y - 32),
                (x + 27, y - 20),
                (x + 23, y + 18),
                (x, y + 34),
                (x - 23, y + 18),
                (x - 27, y - 20)
            ]

            pygame.draw.polygon(
                screen,
                color,
                shield
            )

            pygame.draw.polygon(
                screen,
                WHITE,
                shield,
                2
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 10,
                    y - 2,
                    20,
                    17
                ),
                border_radius=3
            )

            pygame.draw.arc(
                screen,
                WHITE,
                (
                    x - 7,
                    y - 13,
                    14,
                    17
                ),
                math.pi,
                math.pi * 2,
                3
            )

        elif self.type == "monitor":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 32,
                    y - 27,
                    64,
                    48
                ),
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                BLACK,
                (
                    x - 25,
                    y - 20,
                    50,
                    34
                )
            )

            points = [
                (x - 20, y + 5),
                (x - 10, y - 5),
                (x, y + 2),
                (x + 8, y - 13),
                (x + 20, y - 2)
            ]

            pygame.draw.lines(
                screen,
                GREEN,
                False,
                points,
                3
            )

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 5,
                    y + 21,
                    10,
                    12
                )
            )

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 18,
                    y + 31,
                    36,
                    5
                )
            )

        elif self.type == "antivirus":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                28
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (x, y),
                18
            )

            pygame.draw.line(
                screen,
                GREEN,
                (x - 11, y),
                (x + 11, y),
                4
            )

            pygame.draw.line(
                screen,
                GREEN,
                (x, y - 11),
                (x, y + 11),
                4
            )

        elif self.type == "patch":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 24,
                    y - 24,
                    48,
                    48
                ),
                border_radius=8
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x - 10, y),
                (x - 2, y + 8),
                4
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x - 2, y + 8),
                (x + 14, y - 12),
                4
            )

        elif self.type == "siem":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 30,
                    y - 26,
                    60,
                    52
                ),
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                BLACK,
                (
                    x - 22,
                    y - 18,
                    44,
                    36
                )
            )

            for offset in (-16, 0, 16):
                pygame.draw.line(
                    screen,
                    (140, 200, 255),
                    (x + offset, y - 12),
                    (x + offset + 10, y + 12),
                    2
                )

        elif self.type == "backup":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 20,
                    y - 20,
                    40,
                    40
                ),
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 10,
                    y - 10,
                    20,
                    20
                ),
                border_radius=4
            )

            pygame.draw.line(
                screen,
                BLACK,
                (x - 6, y),
                (x + 6, y),
                3
            )

        elif self.type == "honeypot":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                24
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x, y - 28),
                (x, y - 8),
                3
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (x, y - 32),
                4
            )

        elif self.type == "ids":

            tri = [
                (x, y - 30),
                (x + 26, y + 20),
                (x - 26, y + 20)
            ]
            pygame.draw.polygon(screen, color, tri)
            pygame.draw.circle(screen, WHITE, (x, y), 8)
            pygame.draw.line(screen, BLACK, (x - 6, y), (x + 6, y), 2)
            pygame.draw.line(screen, BLACK, (x, y - 6), (x, y + 6), 2)

        elif self.type == "vpn":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                30
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (x, y),
                20
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x - 12, y),
                (x + 12, y),
                3
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x, y - 12),
                (x, y + 12),
                3
            )

        elif self.type == "sandbox":

            pygame.draw.polygon(
                screen,
                color,
                [
                    (x, y - 30),
                    (x + 27, y - 10),
                    (x + 27, y + 20),
                    (x, y + 35),
                    (x - 27, y + 20),
                    (x - 27, y - 10)
                ]
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x - 11, y - 4),
                (x + 11, y - 4),
                3
            )

        elif self.type == "segment":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 35,
                    y - 32,
                    70,
                    64
                ),
                border_radius=5
            )

            for yy in [-10, 12]:

                pygame.draw.line(
                    screen,
                    WHITE,
                    (
                        x - 35,
                        y + yy
                    ),
                    (
                        x + 35,
                        y + yy
                    ),
                    2
                )

        elif self.type == "limiter":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                32
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (x, y),
                23
            )

            pygame.draw.line(
                screen,
                CYAN,
                (x, y),
                (
                    x + 16,
                    y - 15
                ),
                5
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (x, y),
                5
            )

        elif self.type == "incident":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 27,
                    y - 28,
                    54,
                    55
                ),
                border_radius=9
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 23,
                    y - 32,
                    46,
                    10
                ),
                border_radius=4
            )

            pygame.draw.circle(
                screen,
                CYAN,
                (
                    x - 10,
                    y - 5
                ),
                6
            )

            pygame.draw.circle(
                screen,
                CYAN,
                (
                    x + 10,
                    y - 5
                ),
                6
            )

        ratio = max(
            self.health /
            self.max_health,
            0
        )

        pygame.draw.rect(
            screen,
            (70, 15, 20),
            (
                x - 32,
                y + 42,
                64,
                6
            ),
            border_radius=3
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                x - 32,
                y + 42,
                int(64 * ratio),
                6
            ),
            border_radius=3
        )


# ============================================================
# THREAT
# ============================================================

class Threat:

    def __init__(
        self,
        row,
        threat_type
    ):

        self.row = row
        self.type = threat_type

        data = THREAT_TYPES[
            threat_type
        ]

        self.x = WIDTH + 40

        self.y = (
            GRID_Y +
            row * CELL_H +
            CELL_H // 2
        )

        self.health = data["health"]

        self.max_health = data["health"]

        hard_mode_bonus = 1.35 if settings.get("hard_mode", False) else 1.0
        self.speed = (
            data["speed"] *
            (
                1 +
                wave * 0.04
            ) *
            hard_mode_bonus
        )

        self.damage = data["damage"] * hard_mode_bonus * (1 + wave * 0.03)

        self.reward = data["reward"]

        self.attack_timer = 0

        self.animation = (
            random.random() * 10
        )

        self.hit_flash = 0

    def update(self, dt):

        self.animation += dt * 4

        self.attack_timer += dt

        self.hit_flash -= dt

        target = None

        possible_targets = [
            p for p in plants
            if
            p.row == self.row
            and
            p.x < self.x
            and
            self.x - p.x < 48
        ]

        if possible_targets:

            target = max(
                possible_targets,
                key=lambda p: p.x
            )

        if target:

            if self.attack_timer >= 1:

                target.health -= (
                    self.damage
                )

                target.hit_flash = 0.15

                add_particles(
                    target.x,
                    target.y,
                    RED,
                    6
                )

                self.attack_timer = 0

        else:

            self.x -= (
                self.speed * dt
            )

        # ====================================================
        # BASE DAMAGE
        # ====================================================
        #
        # Every enemy that reaches the base now deals exactly
        # 25 damage to network health.
        #
        # ====================================================

        if self.x < GRID_X - 35:

            global network_health

            network_health -= 25

            add_floating_text(
                "-25 NETWORK",
                GRID_X - 80,
                self.y - 45,
                RED
            )

            add_particles(
                GRID_X - 35,
                self.y,
                RED,
                20
            )

            # Remove the enemy immediately so it doesn't
            # repeatedly damage the base every frame.

            if self in threats:

                threats.remove(self)

    def draw(self):

        data = THREAT_TYPES[
            self.type
        ]

        color = data["color"]

        bob = (
            math.sin(
                self.animation
            ) * 3
        )

        x = int(self.x)
        y = int(self.y + bob)

        pygame.draw.ellipse(
            screen,
            (5, 10, 15),
            (
                x - 32,
                y + 27,
                64,
                15
            )
        )

        draw_glow(
            screen,
            (x, y),
            color,
            22,
            2
        )

        if self.hit_flash > 0:
            color = WHITE

        if self.type == "phishing":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                27
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (
                    x - 9,
                    y - 6
                ),
                4
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (
                    x + 9,
                    y - 6
                ),
                4
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 13,
                    y + 7,
                    26,
                    17
                ),
                2
            )

        elif self.type == "virus":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                28
            )

            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = x + int(math.cos(rad) * 22)
                y1 = y + int(math.sin(rad) * 22)
                x2 = x + int(math.cos(rad) * 34)
                y2 = y + int(math.sin(rad) * 34)
                pygame.draw.line(screen, (255, 230, 230), (x1, y1), (x2, y2), 4)

            pygame.draw.circle(screen, WHITE, (x - 9, y - 5), 6)
            pygame.draw.circle(screen, WHITE, (x + 9, y - 5), 6)

        elif self.type == "worm":

            body_segments = [(-18, 0), (-6, -8), (10, -2), (24, 0), (10, 8), (-6, 6)]
            for i, (dx, dy) in enumerate(body_segments):
                segment_x = x + dx
                segment_y = y + dy
                radius = 12 if i % 2 == 0 else 10
                pygame.draw.circle(screen, color, (segment_x, segment_y), radius)
            pygame.draw.line(screen, WHITE, (x - 17, y), (x + 25, y), 3)

        elif self.type == "rootkit":

            pygame.draw.polygon(screen, color, [(x, y - 28), (x + 24, y), (x, y + 28), (x - 24, y)])
            pygame.draw.circle(screen, BLACK, (x, y), 9)
            pygame.draw.line(screen, WHITE, (x - 12, y), (x + 12, y), 3)

        elif self.type == "botnet":

            pygame.draw.circle(screen, color, (x, y), 24)
            for dx, dy in [(-22, -16), (22, -14), (-22, 18), (22, 17)]:
                pygame.draw.circle(screen, (255, 220, 120), (x + dx, y + dy), 9)
                pygame.draw.line(screen, WHITE, (x, y), (x + dx, y + dy), 2)
            pygame.draw.circle(screen, BLACK, (x, y), 7)

        elif self.type == "ddos":

            pygame.draw.rect(
                screen,
                color,
                (
                    x - 27,
                    y - 25,
                    54,
                    50
                ),
                border_radius=8
            )

            pygame.draw.line(
                screen,
                WHITE,
                (
                    x,
                    y - 25
                ),
                (
                    x,
                    y - 40
                ),
                3
            )

            pygame.draw.circle(
                screen,
                RED,
                (
                    x,
                    y - 43
                ),
                5
            )

            pygame.draw.rect(
                screen,
                BLACK,
                (
                    x - 17,
                    y - 10,
                    11,
                    11
                )
            )

            pygame.draw.rect(
                screen,
                BLACK,
                (
                    x + 6,
                    y - 10,
                    11,
                    11
                )
            )

        elif self.type == "ransomware":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                31
            )

            pygame.draw.polygon(
                screen,
                color,
                [
                    (x - 20, y - 20),
                    (x - 36, y - 38),
                    (x - 10, y - 28)
                ]
            )

            pygame.draw.polygon(
                screen,
                color,
                [
                    (x + 20, y - 20),
                    (x + 36, y - 38),
                    (x + 10, y - 28)
                ]
            )

            pygame.draw.rect(
                screen,
                YELLOW,
                (
                    x - 13,
                    y - 2,
                    26,
                    20
                ),
                border_radius=3
            )

            pygame.draw.arc(
                screen,
                YELLOW,
                (
                    x - 9,
                    y - 15,
                    18,
                    20
                ),
                math.pi,
                math.pi * 2,
                4
            )

        elif self.type == "boss":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                36
            )

            pygame.draw.circle(
                screen,
                BLACK,
                (x, y),
                22
            )

            pygame.draw.line(
                screen,
                WHITE,
                (x - 12, y - 8),
                (x + 12, y - 8),
                4
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (x - 18, y + 10, 36, 8),
                border_radius=3
            )

            pygame.draw.circle(
                screen,
                YELLOW,
                (x, y - 30),
                7
            )

        ratio = max(
            self.health /
            self.max_health,
            0
        )

        pygame.draw.rect(
            screen,
            (80, 15, 20),
            (
                x - 32,
                y - 46,
                64,
                6
            ),
            border_radius=3
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                x - 32,
                y - 46,
                int(64 * ratio),
                6
            ),
            border_radius=3
        )

        label = small_font.render(
            data["name"],
            True,
            WHITE
        )

        screen.blit(
            label,
            (
                x -
                label.get_width() // 2,
                y + 35
            )
        )

        if self.type == "boss":
            boss_label = small_font.render("BOSS", True, RED)
            screen.blit(boss_label, (x - boss_label.get_width() // 2, y + 46))


# ============================================================
# SPAWN THREATS
# ============================================================

def spawn_threat():

    extra_spawns = 1
    if settings.get("hard_mode", False):
        extra_spawns += 1
        if wave >= 4:
            extra_spawns += 1

    if wave % 5 == 0:
        base_types = ["boss"]
    elif wave <= 2:
        base_types = ["phishing", "virus", "worm", "ddos"]
    elif wave <= 5:
        base_types = ["phishing", "virus", "worm", "rootkit", "botnet", "ddos", "ransomware"]
    else:
        base_types = ["phishing", "virus", "worm", "rootkit", "botnet", "ddos", "ransomware"]

    for _ in range(extra_spawns):
        if wave % 5 == 0:
            threat_type = "boss"
        elif wave > 5 and settings.get("hard_mode", False):
            threat_type = random.choices(
                base_types,
                weights=[20, 24, 18, 14, 14, 20, 10],
            )[0]
        else:
            threat_type = random.choice(base_types)

        row = random.randint(0, ROWS - 1)

        threats.append(
            Threat(
                row,
                threat_type
            )
        )


# ============================================================
# BACKGROUND
# ============================================================

def draw_background():

    screen.fill(BLACK)

    for x in range(
        0,
        WIDTH,
        40
    ):

        pygame.draw.line(
            screen,
            (8, 25, 35),
            (x, 0),
            (x, HEIGHT),
            1
        )

    for y in range(
        0,
        HEIGHT,
        40
    ):

        pygame.draw.line(
            screen,
            (8, 25, 35),
            (0, y),
            (WIDTH, y),
            1
        )


# ============================================================
# NETWORK GRID
# ============================================================

def draw_grid():

    mouse_pos = pygame.mouse.get_pos()
    hovered_position = grid_position(mouse_pos)
    active_target = None

    if selected_plant and hovered_position is not None:
        row, col = hovered_position
        if 0 <= row < ROWS and 0 <= col < COLS:
            data = PLANT_TYPES[selected_plant]
            can_place = (not occupied(row, col) and energy >= data["cost"])
            active_target = (row, col, can_place)

    for row in range(ROWS):

        for col in range(COLS):

            x = (
                GRID_X +
                col * CELL_W
            )

            y = (
                GRID_Y +
                row * CELL_H
            )

            if (
                row + col
            ) % 2 == 0:

                color = GRID_1

            else:

                color = GRID_2

            pygame.draw.rect(
                screen,
                color,
                (
                    x,
                    y,
                    CELL_W,
                    CELL_H
                )
            )

            if active_target and active_target[0] == row and active_target[1] == col:
                highlight = (40, 220, 120) if active_target[2] else (220, 60, 70)
                overlay = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
                overlay.fill((highlight[0], highlight[1], highlight[2], 110))
                screen.blit(overlay, (x, y))

            pygame.draw.rect(
                screen,
                (30, 90, 95),
                (
                    x,
                    y,
                    CELL_W,
                    CELL_H
                ),
                1
            )


# ============================================================
# SERVER
# ============================================================

def draw_server():

    x = GRID_X - 100
    y = GRID_Y

    width = 70

    height = (
        ROWS * CELL_H
    )

    draw_glow(
        screen,
        (
            x + width // 2,
            y + height // 2
        ),
        CYAN,
        25,
        2
    )

    pygame.draw.rect(
        screen,
        (25, 55, 75),
        (
            x,
            y,
            width,
            height
        ),
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            x,
            y,
            width,
            height
        ),
        2,
        border_radius=8
    )

    for i in range(5):

        yy = (
            y +
            25 +
            i * 75
        )

        pygame.draw.rect(
            screen,
            BLACK,
            (
                x + 10,
                yy,
                50,
                45
            ),
            border_radius=4
        )

        for j in range(3):

            pygame.draw.circle(
                screen,
                GREEN
                if j != 1
                else CYAN,
                (
                    x + 18 +
                    j * 14,
                    yy + 34
                ),
                3
            )

    label = small_font.render(
        "SERVER",
        True,
        CYAN
    )

    screen.blit(
        label,
        (
            x - 3,
            y - 22
        )
    )


# ============================================================
# SIDEBAR
# ============================================================

def draw_sidebar():

    pygame.draw.rect(
        screen,
        PANEL,
        (
            0,
            0,
            160,
            HEIGHT
        )
    )

    pygame.draw.line(
        screen,
        CYAN,
        (
            158,
            0
        ),
        (
            158,
            HEIGHT
        ),
        2
    )

    draw_text(
        "DEFENSE",
        20,
        20,
        CYAN
    )

    types = selected_loadout[:] if selected_loadout else list(PLANT_TYPES.keys())

    for i, plant_type in enumerate(
        types
    ):

        data = PLANT_TYPES[
            plant_type
        ]

        y = (
            70 +
            i * 105
        )

        selected = (
            selected_plant ==
            plant_type
        )

        if selected:

            pygame.draw.rect(
                screen,
                (25, 70, 80),
                (
                    8,
                    y - 5,
                    142,
                    90
                ),
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                CYAN,
                (
                    8,
                    y - 5,
                    142,
                    90
                ),
                2,
                border_radius=8
            )

        icon_x = 32
        icon_y = y + 32

        if plant_type == "firewall":
            shield = [(icon_x, icon_y - 18), (icon_x + 16, icon_y - 11), (icon_x + 13, icon_y + 10), (icon_x, icon_y + 18), (icon_x - 13, icon_y + 10), (icon_x - 16, icon_y - 11)]
            pygame.draw.polygon(screen, data["color"], shield)
        elif plant_type == "monitor":
            pygame.draw.rect(screen, data["color"], (icon_x - 16, icon_y - 14, 32, 24), border_radius=4)
            pygame.draw.rect(screen, BLACK, (icon_x - 12, icon_y - 10, 24, 16))
            pygame.draw.line(screen, GREEN, (icon_x - 10, icon_y + 2), (icon_x - 3, icon_y - 5), 2)
            pygame.draw.line(screen, GREEN, (icon_x - 3, icon_y - 5), (icon_x + 8, icon_y + 7), 2)
        elif plant_type == "segment":
            pygame.draw.rect(screen, data["color"], (icon_x - 17, icon_y - 17, 34, 34), border_radius=4)
            pygame.draw.line(screen, WHITE, (icon_x - 14, icon_y), (icon_x + 14, icon_y), 2)
            pygame.draw.line(screen, WHITE, (icon_x - 14, icon_y + 8), (icon_x + 14, icon_y + 8), 2)
        elif plant_type == "limiter":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 16)
            pygame.draw.circle(screen, BLACK, (icon_x, icon_y), 11)
            pygame.draw.line(screen, CYAN, (icon_x, icon_y), (icon_x + 9, icon_y - 9), 3)
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y), 3)
        elif plant_type == "incident":
            pygame.draw.rect(screen, data["color"], (icon_x - 15, icon_y - 16, 30, 32), border_radius=6)
            pygame.draw.rect(screen, WHITE, (icon_x - 13, icon_y - 18, 26, 8), border_radius=3)
            pygame.draw.circle(screen, CYAN, (icon_x - 6, icon_y - 3), 4)
            pygame.draw.circle(screen, CYAN, (icon_x + 6, icon_y - 3), 4)
        elif plant_type == "antivirus":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 16)
            pygame.draw.line(screen, BLACK, (icon_x - 10, icon_y), (icon_x + 10, icon_y), 3)
            pygame.draw.line(screen, BLACK, (icon_x, icon_y - 10), (icon_x, icon_y + 10), 3)
        elif plant_type == "patch":
            pygame.draw.rect(screen, data["color"], (icon_x - 15, icon_y - 15, 30, 30), border_radius=5)
            pygame.draw.line(screen, WHITE, (icon_x - 7, icon_y), (icon_x - 1, icon_y + 7), 3)
            pygame.draw.line(screen, WHITE, (icon_x - 1, icon_y + 7), (icon_x + 11, icon_y - 8), 3)
        elif plant_type == "siem":
            pygame.draw.rect(screen, data["color"], (icon_x - 18, icon_y - 14, 36, 28), border_radius=5)
            pygame.draw.rect(screen, BLACK, (icon_x - 12, icon_y - 9, 24, 18))
            for offset in (-10, 0, 10):
                pygame.draw.line(screen, (140, 200, 255), (icon_x + offset, icon_y - 8), (icon_x + offset + 7, icon_y + 10), 2)
        elif plant_type == "backup":
            pygame.draw.rect(screen, data["color"], (icon_x - 15, icon_y - 15, 30, 30), border_radius=5)
            pygame.draw.rect(screen, WHITE, (icon_x - 7, icon_y - 7, 14, 14), border_radius=3)
            pygame.draw.line(screen, BLACK, (icon_x - 5, icon_y), (icon_x + 5, icon_y), 2)
        elif plant_type == "honeypot":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 14)
            pygame.draw.line(screen, WHITE, (icon_x, icon_y - 20), (icon_x, icon_y - 6), 3)
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y - 24), 3)
        elif plant_type == "ids":
            tri = [(icon_x, icon_y - 18), (icon_x + 15, icon_y + 14), (icon_x - 15, icon_y + 14)]
            pygame.draw.polygon(screen, data["color"], tri)
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y), 6)
        elif plant_type == "vpn":
            pygame.draw.circle(screen, data["color"], (icon_x, icon_y), 15)
            pygame.draw.circle(screen, BLACK, (icon_x, icon_y), 10)
            pygame.draw.line(screen, WHITE, (icon_x - 8, icon_y), (icon_x + 8, icon_y), 3)
        elif plant_type == "sandbox":
            sandbox_points = [(icon_x, icon_y - 18), (icon_x + 16, icon_y - 8), (icon_x + 16, icon_y + 10), (icon_x, icon_y + 20), (icon_x - 16, icon_y + 10), (icon_x - 16, icon_y - 8)]
            pygame.draw.polygon(screen, data["color"], sandbox_points)
            pygame.draw.line(screen, WHITE, (icon_x - 8, icon_y), (icon_x + 8, icon_y), 3)

        name_lines = wrap_text(data["name"], 11)
        for i, line in enumerate(name_lines[:2]):
            draw_text(line, 58, y + 8 + i * 12, WHITE, small_font)

        draw_text(
            f"{data['cost']} E",
            58,
            y + 30,
            YELLOW,
            small_font
        )

        if energy >= data["cost"]:

            draw_text(
                "READY",
                58,
                y + 52,
                GREEN,
                small_font
            )

        else:

            draw_text(
                "LOW ENERGY",
                58,
                y + 52,
                RED,
                small_font
            )


# ============================================================
# TOP BAR
# ============================================================

def draw_top_bar():

    pygame.draw.rect(
        screen,
        (10, 18, 30),
        (
            160,
            0,
            WIDTH - 160,
            90
        )
    )

    pygame.draw.line(
        screen,
        CYAN,
        (
            160,
            88
        ),
        (
            WIDTH,
            88
        ),
        2
    )

    draw_text(
        "CYBER DEFENSE",
        185,
        12,
        CYAN,
        big_font
    )

    energy_icon.draw()

    draw_text(
        f"{int(energy)}",
        505,
        27,
        YELLOW
    )

    health_icon.draw(
        network_health
    )

    if network_health > 60:

        health_color = GREEN

    elif network_health > 30:

        health_color = YELLOW

    else:

        health_color = RED

    draw_text(
        f"{int(network_health)}/{int(max_network_health)}",
        655,
        27,
        health_color
    )

    draw_text(
        f"SCORE  {score}",
        835,
        27,
        WHITE
    )

    wave_label = f"WAVE  {wave}" if game_mode == "endless" else f"WAVE  {wave}/10"
    draw_text(
        wave_label,
        970,
        27,
        ORANGE
    )

    return None


# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    global energy
    global network_health
    global score
    global wave
    global base_network_health
    global max_network_health
    global damage_upgrade_multiplier

    global game_over
    global victory

    global selected_plant
    global game_speed_multiplier

    global spawn_timer
    global wave_timer

    base_network_health = 100 + (25 if "health" in selected_upgrades else 0)
    max_network_health = base_network_health
    damage_upgrade_multiplier = 1.20 if "damage" in selected_upgrades else 1.0

    energy = 150 + (50 if "energy" in selected_upgrades else 0)

    network_health = base_network_health

    score = 0
    wave = 1

    game_over = False
    victory = False

    selected_plant = None
    game_speed_multiplier = 1.0

    spawn_timer = 0
    wave_timer = 0

    plants.clear()
    threats.clear()
    projectiles.clear()
    particles.clear()
    energy_orbs.clear()
    floating_text.clear()


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(FPS) / 1000

    # ========================================================
    # MENU
    # ========================================================

    if game_state in (MENU, MODE_SELECT, LOADOUT):

        menu_time += dt

        for particle in menu_particles:

            particle.update(dt)

    if game_state == MENU:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    selected_loadout.clear()
                    game_state = MODE_SELECT

                elif event.key == pygame.K_ESCAPE:

                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_pos = pygame.mouse.get_pos()

                    if settings_menu_open:
                        close_rect = draw_settings_panel()
                        if close_rect.collidepoint(mouse_pos):
                            settings_menu_open = False
                        else:
                            panel = pygame.Rect(WIDTH // 2 - 260, 150, 520, 360)
                            toggle_y = panel.top + 110
                            for key in ["default_2x", "keep_loadout", "hard_mode"]:
                                rect = pygame.Rect(panel.centerx - 110, toggle_y, 220, 46)
                                if rect.collidepoint(mouse_pos):
                                    settings[key] = not settings[key]
                                    break
                                toggle_y += 70
                        continue

                    start_rect = pygame.Rect(
                        WIDTH // 2 - 170,
                        300,
                        340,
                        70
                    )

                    settings_rect = pygame.Rect(
                        WIDTH // 2 - 170,
                        390,
                        340,
                        60
                    )

                    quit_rect = pygame.Rect(
                        WIDTH // 2 - 170,
                        470,
                        340,
                        60
                    )

                    if start_rect.collidepoint(
                        mouse_pos
                    ):

                        if not settings["keep_loadout"]:
                            selected_loadout.clear()
                        game_state = MODE_SELECT

                    elif settings_rect.collidepoint(mouse_pos):
                        settings_menu_open = True

                    elif quit_rect.collidepoint(
                        mouse_pos
                    ):

                        running = False

        draw_main_menu()

        pygame.display.flip()

        continue

    if game_state == MODE_SELECT:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    game_state = MENU

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_pos = pygame.mouse.get_pos()
                    campaign_rect, endless_rect, back_rect = draw_mode_select_menu()

                    if campaign_rect.collidepoint(mouse_pos):
                        game_mode = "campaign"
                        if not settings["keep_loadout"]:
                            selected_loadout.clear()
                        selected_upgrades.clear()
                        game_state = LOADOUT

                    elif endless_rect.collidepoint(mouse_pos):
                        game_mode = "endless"
                        if not settings["keep_loadout"]:
                            selected_loadout.clear()
                        selected_upgrades.clear()
                        game_state = LOADOUT

                    elif back_rect.collidepoint(mouse_pos):
                        game_state = MENU

        draw_mode_select_menu()
        pygame.display.flip()
        continue

    if game_state == UPGRADE_SELECT:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = GAME
                elif event.key == pygame.K_RETURN:
                    game_state = GAME

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                upgrade_rects, continue_rect, back_rect = draw_upgrade_select_menu()

                for upgrade_key, rect in upgrade_rects:
                    if rect.collidepoint(mouse_pos):

                        if upgrade_key in selected_upgrades:
                            selected_upgrades.remove(upgrade_key)

                            # Remove an upgrade if the player changes their mind.
                            if upgrade_key == "health":
                                base_network_health = 100 + (25 if "health" in selected_upgrades else 0)
                                max_network_health = base_network_health
                                network_health = min(network_health, max_network_health)
                            elif upgrade_key == "energy":
                                energy = max(0, energy - 50)
                            elif upgrade_key == "damage":
                                damage_upgrade_multiplier = 1.0

                        elif len(selected_upgrades) < MAX_UPGRADES:
                            selected_upgrades.append(upgrade_key)

                            if upgrade_key == "health":
                                base_network_health = 100 + (25 if "health" in selected_upgrades else 0)
                                max_network_health = base_network_health
                                network_health = min(network_health + 25, max_network_health)
                                add_floating_text("+25 BASE HEALTH", WIDTH // 2 - 85, 170, GREEN)
                            elif upgrade_key == "energy":
                                energy += 50
                                add_floating_text("+50 ENERGY", WIDTH // 2 - 65, 170, YELLOW)
                            elif upgrade_key == "damage":
                                damage_upgrade_multiplier = 1.20
                                add_floating_text("+20% DAMAGE", WIDTH // 2 - 70, 170, RED)

                        break

                if continue_rect.collidepoint(mouse_pos):
                    game_state = GAME
                elif back_rect.collidepoint(mouse_pos):
                    game_state = GAME

        draw_upgrade_select_menu()
        pygame.display.flip()
        continue

    if game_state == LOADOUT:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    selected_loadout.clear()
                    game_state = MENU

                elif event.key in (pygame.K_UP, pygame.K_PAGEUP):
                    loadout_scroll = max(0, loadout_scroll - 30)

                elif event.key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
                    loadout_scroll += 30

            if event.type == pygame.MOUSEWHEEL:
                loadout_scroll = max(0, loadout_scroll - event.y * 30)

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_pos = pygame.mouse.get_pos()
                    begin_rect, back_rect = draw_loadout_menu()

                    for index, plant_type in enumerate(PLANT_TYPES):

                        col = index % 3
                        row = index // 3
                        rect = pygame.Rect(
                            120 + col * 250,
                            180 - loadout_scroll + row * 130,
                            220,
                            120
                        )

                        if rect.bottom < 160 or rect.top > 560:
                            continue

                        if rect.collidepoint(mouse_pos):

                            if plant_type in selected_loadout:
                                selected_loadout.remove(plant_type)
                            else:
                                if len(selected_loadout) < 5:
                                    selected_loadout.append(plant_type)
                            break

                    if begin_rect.collidepoint(mouse_pos) and len(selected_loadout) == 5:

                        reset_game()
                        selected_plant = selected_loadout[0]
                        game_state = GAME

                    elif back_rect.collidepoint(mouse_pos):

                        selected_loadout.clear()
                        game_state = MENU

        draw_loadout_menu()
        pygame.display.flip()
        continue

    if quiz_active:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    for i, choice in enumerate(quiz_choices):
                        rect = pygame.Rect(WIDTH // 2 - 230, 270 + i * 70, 460, 52)
                        if rect.collidepoint(mouse_pos):
                            check_quiz_answer(i)
                            break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    check_quiz_answer(-1)

        draw_background()
        draw_grid()
        draw_server()
        for plant in plants:
            plant.draw()
        for threat in threats:
            threat.draw()
        for projectile in projectiles:
            projectile.draw()
        for orb in energy_orbs:
            orb.draw()
        for particle in particles:
            particle.draw()
        for text in floating_text:
            text.draw()
        draw_sidebar()
        draw_top_bar()
        draw_quiz()
        pygame.display.flip()
        continue

    # ========================================================
    # GAME EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_over or victory:

                reset_game()

                continue

            mx, my = pygame.mouse.get_pos()
            speed_button_rect = pygame.Rect(WIDTH - 190, HEIGHT - 60, 160, 42)

            if speed_button_rect.collidepoint((mx, my)):
                game_speed_multiplier = 2.0 if game_speed_multiplier == 1.0 else 1.0
                continue

            if mx < 160 and my > 60:

                index = (
                    my - 65
                ) // 105

                types = selected_loadout[:] if selected_loadout else list(PLANT_TYPES.keys())

                if (
                    0 <= index <
                    len(types)
                ):

                    selected_plant = (
                        types[index]
                    )

            else:

                position = grid_position(
                    (
                        mx,
                        my
                    )
                )

                if (
                    position
                    and
                    selected_plant
                ):

                    row, col = position

                    data = PLANT_TYPES[
                        selected_plant
                    ]

                    if (
                        not occupied(
                            row,
                            col
                        )
                        and
                        energy >=
                        data["cost"]
                    ):

                        plants.append(
                            Plant(
                                row,
                                col,
                                selected_plant
                            )
                        )

                        energy -= (
                            data["cost"]
                        )

                        add_particles(
                            GRID_X +
                            col * CELL_W +
                            CELL_W // 2,

                            GRID_Y +
                            row * CELL_H +
                            CELL_H // 2,

                            data["color"],

                            15
                        )

                    elif (
                        energy <
                        data["cost"]
                    ):

                        add_floating_text(
                            "NOT ENOUGH ENERGY",
                            mx - 70,
                            my,
                            RED
                        )

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:

                reset_game()

            if event.key == pygame.K_ESCAPE:

                game_state = MENU

                selected_plant = None

    # ========================================================
    # UPDATE GAME
    # ========================================================

    if not game_over and not victory:

        if settings["default_2x"] and game_state == GAME and game_speed_multiplier == 1.0:
            game_speed_multiplier = 2.0

        speed_dt = dt * game_speed_multiplier

        if active_buff_timer > 0:
            active_buff_timer = max(0, active_buff_timer - speed_dt)

        if powerup_damage_boost > 0:
            powerup_damage_boost = max(0, powerup_damage_boost - speed_dt)
            if active_buff_text == "DAMAGE BOOST":
                active_buff_timer = powerup_damage_boost
            if powerup_damage_boost <= 0:
                active_buff_text = ""
                active_buff_timer = 0

        energy_icon.update(dt)
        health_icon.update(dt)

        wave_timer += speed_dt
        spawn_timer += speed_dt

        spawn_interval = max(
            0.65,
            2.5 -
            wave * 0.13
        )

        if (
            spawn_timer >=
            spawn_interval
        ):

            spawn_threat()

            spawn_timer = 0

        if wave_timer >= 25:

            if game_mode == "campaign":
                if wave >= 10:
                    victory = True
                    wave_timer = 0
                    add_floating_text(
                        "CAMPAIGN CLEARED",
                        WIDTH // 2 - 100,
                        105,
                        GREEN
                    )
                else:
                    wave += 1
                    wave_timer = 0
                    add_floating_text(
                        f"WAVE {wave}",
                        WIDTH // 2 - 30,
                        105,
                        CYAN
                    )
                    if wave % 2 == 0:
                        start_quiz()
            else:
                wave += 1
                wave_timer = 0
                add_floating_text(
                    f"WAVE {wave}",
                    WIDTH // 2 - 30,
                    105,
                    CYAN
                )
                if wave % 2 == 0:
                    start_quiz()

        # Plants

        for plant in plants:

            plant.update(speed_dt)

        # Threats

        for threat in threats[:]:

            threat.update(speed_dt)

        # Projectiles

        for projectile in projectiles[:]:

            projectile.update(speed_dt)

            for threat in threats[:]:

                if (
                    projectile.row ==
                    threat.row
                    and
                    abs(
                        projectile.x -
                        threat.x
                    ) < 27
                ):

                    threat.health -= (
                        projectile.damage * damage_upgrade_multiplier
                    )

                    threat.hit_flash = 0.12

                    add_particles(
                        threat.x,
                        threat.y,
                        THREAT_TYPES[
                            threat.type
                        ]["color"],
                        8
                    )

                    if projectile in projectiles:

                        projectiles.remove(
                            projectile
                        )

                    if threat.health <= 0:

                        reward = (
                            threat.reward
                        )

                        score += reward

                        energy += 15

                        add_floating_text(
                            f"+{reward}",
                            threat.x,
                            threat.y - 45,
                            GREEN
                        )

                        add_floating_text(
                            "+5 ENERGY",
                            threat.x + 25,
                            threat.y - 70,
                            YELLOW
                        )

                        add_particles(
                            threat.x,
                            threat.y,
                            THREAT_TYPES[
                                threat.type
                            ]["color"],
                            25
                        )

                        if threat in threats:

                            threats.remove(
                                threat
                            )

                    break

        # Dead plants

        for plant in plants[:]:

            if plant.health <= 0:

                add_particles(
                    plant.x,
                    plant.y,
                    RED,
                    20
                )

                plants.remove(
                    plant
                )

        # Projectiles

        projectiles[:] = [

            p for p in projectiles

            if
            p.x < WIDTH
            and
            p.life > 0
        ]

        # Energy orbs

        for orb in energy_orbs:

            orb.update(speed_dt)

        energy_orbs[:] = [

            orb
            for orb in energy_orbs

            if orb.life > 0
        ]

        # Particles

        for particle in particles:

            particle.update(speed_dt)

        particles[:] = [

            p
            for p in particles

            if p.life > 0
        ]

        # Floating text

        for text in floating_text:

            text.update(speed_dt)

        floating_text[:] = [

            t
            for t in floating_text

            if t.life > 0
        ]

        # Network destroyed

        if network_health <= 0:

            network_health = 0

            game_over = True

    if quiz_active:
        continue

    # ========================================================
    # DRAW GAME
    # ========================================================

    draw_background()

    draw_grid()

    draw_server()

    for plant in plants:

        plant.draw()

    for threat in threats:

        threat.draw()

    for projectile in projectiles:

        projectile.draw()

    for orb in energy_orbs:

        orb.draw()

    for particle in particles:

        particle.draw()

    for text in floating_text:

        text.draw()

    draw_sidebar()

    draw_top_bar()

    speed_button_rect = pygame.Rect(WIDTH - 190, HEIGHT - 60, 160, 42)
    speed_active = game_speed_multiplier > 1
    button_fill = (18, 80, 70) if speed_active else (25, 35, 50)
    button_border = GREEN if speed_active else (90, 120, 140)

    pygame.draw.rect(screen, button_fill, speed_button_rect, border_radius=10)
    pygame.draw.rect(screen, button_border, speed_button_rect, 2, border_radius=10)

    speed_text = small_font.render("2X SPEED", True, WHITE if speed_active else (180, 210, 220))
    screen.blit(speed_text, (speed_button_rect.centerx - speed_text.get_width() // 2, speed_button_rect.centery - speed_text.get_height() // 2 + 1))

    if active_buff_timer > 0 and active_buff_text:
        buff_panel = pygame.Rect(WIDTH // 2 - 170, HEIGHT - 80, 340, 34)
        pygame.draw.rect(screen, (10, 18, 30), buff_panel, border_radius=10)
        pygame.draw.rect(screen, active_buff_color, buff_panel, 2, border_radius=10)

        buff_label = small_font.render(
            f"{active_buff_text}  {active_buff_timer:.1f}s",
            True,
            WHITE
        )
        screen.blit(
            buff_label,
            (
                buff_panel.centerx - buff_label.get_width() // 2,
                buff_panel.centery - buff_label.get_height() // 2 + 1
            )
        )

    draw_text(
        "SELECT DEFENSE  >  CLICK NETWORK CELL",
        GRID_X,
        HEIGHT - 35,
        (130, 180, 190),
        small_font
    )

    # ========================================================
    # GAME OVER
    # ========================================================

    if game_over:

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 190)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            "NETWORK BREACHED",
            WIDTH // 2 - 250,
            250,
            RED,
            huge_font
        )

        draw_text(
            f"FINAL SCORE: {score}",
            WIDTH // 2 - 120,
            330,
            WHITE
        )

        draw_text(
            "CLICK OR PRESS R TO RESTART",
            WIDTH // 2 - 180,
            380,
            YELLOW
        )

    # ========================================================
    # VICTORY
    # ========================================================

    if victory:

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            "NETWORK SECURED",
            WIDTH // 2 - 250,
            250,
            GREEN,
            huge_font
        )

        draw_text(
            f"FINAL SCORE: {score}",
            WIDTH // 2 - 120,
            330,
            WHITE
        )

        draw_text(
            "CLICK OR PRESS R TO PLAY AGAIN",
            WIDTH // 2 - 190,
            380,
            YELLOW
        )

    pygame.display.flip()

pygame.quit()