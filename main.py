import pygame
import random
import math
import sys

pygame.init()
# Hide the system cursor — we draw a custom cursor instead
pygame.mouse.set_visible(False)

# ============================================================
# IoT DEFENDER: SMART CITY SHIELD — VERSION 2
# One-file Pygame prototype
#
# Controls:
#   Mouse / arrow keys  = move cursor
#   SPACE / left click  = select
#   1-8                 = quick-select devices
#   ESC                 = menu
#
# The game is deliberately built so a joystick/button can be
# added later without redesigning the gameplay.
# ============================================================

WIDTH, HEIGHT = 1200, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IoT Defender: Smart City Shield")
clock = pygame.time.Clock()

# Fonts
F_SMALL = pygame.font.Font(None, 22)
F_BODY = pygame.font.Font(None, 28)
F_MED = pygame.font.Font(None, 36)
F_BIG = pygame.font.Font(None, 52)
F_TITLE = pygame.font.Font(None, 76)

# Palette
BG = (7, 10, 24)
PANEL = (15, 22, 44)
PANEL2 = (21, 31, 59)
GRID = (34, 47, 78)
WHITE = (240, 245, 255)
MUTED = (150, 164, 195)
CYAN = (55, 220, 255)
GREEN = (70, 235, 150)
RED = (255, 70, 92)
YELLOW = (255, 211, 75)
PURPLE = (170, 110, 255)
ORANGE = (255, 145, 70)

# Game states
MENU, HOW, GAME, QUIZ, RESULT = range(5)
state = MENU

# Device definitions
devices = [
    ("SMART LIGHT", "LIGHT", CYAN),
    ("TRAFFIC CONTROL", "TRAFFIC", GREEN),
    ("CCTV CAMERA", "CAMERA", PURPLE),
    ("WATER SENSOR", "WATER", CYAN),
    ("SMART HOME", "HOME", ORANGE),
    ("CONNECTED BUS", "BUS", YELLOW),
    ("EMERGENCY SPEAKER", "SPEAKER", RED),
    ("AIR SENSOR", "AIR", GREEN),
]

device_rects = []
for i in range(8):
    col = i % 4
    row = i // 4
    x = 42 + col * 286
    y = 205 + row * 210
    device_rects.append(pygame.Rect(x, y, 250, 175))

attack_types = [
    ("MALWARE", "ISOLATE", RED),
    ("WEAK PASSWORD", "CHANGE PASSWORD", YELLOW),
    ("OUTDATED FIRMWARE", "PATCH DEVICE", CYAN),
    ("UNKNOWN DEVICE", "BLOCK DEVICE", PURPLE),
    ("PHISHING", "REPORT ATTACK", ORANGE),
]

# Runtime
score = 0
shield = 100
combo = 0
best_combo = 0
level = 1
threats = {}            # device index -> attack tuple
secured = set()
threat_active_at = {}   # device index -> ms when threat becomes actively draining
threat_drain = {}       # device index -> drain per second
stealth_threats = {}    # device index -> (active_at_ms, attack_tuple, drain_per_sec)
data_events = {}       # device index -> expiry timestamp (ms)
last_data_spawn = 0
data_spawn_interval = 900  # ms (more frequent)
message = "SYSTEM ONLINE — scan the city network."
message_colour = CYAN
mission_start = 0
last_spawn = 0
spawn_interval = 3.0
base_time = 75          # base time for current level/round (seconds)
level_start = 0        # timestamp when current level started
last_level = 1
mission_failed = False
failure_reason = ""
time_left = 75
cursor = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
particles = []
flash_until = 0
flash_colour = RED

# Quiz
quiz_index = 0
quiz_message = ""
quiz_message_colour = WHITE
quiz_questions = [
    (
        "A CCTV camera has not received a security update for 3 years. What is safest?",
        ["Install the official security update.", "Ignore all updates.", "Download a random update.", "Share the admin password."],
        0,
    ),
    (
        "A smart-home device uses the password '123456'. What should you do?",
        ["Keep it because it is easy.", "Change it to a strong, unique password.", "Post it online.", "Use it on every account."],
        1,
    ),
    (
        "An unknown IoT device suddenly appears on the network. What is a good first response?",
        ["Give it admin access.", "Connect more devices.", "Isolate/report it and investigate.", "Ignore it."],
        2,
    ),
]

# ============================================================
# Drawing helpers
# ============================================================

def text(txt, font, colour, pos, center=False):
    s = font.render(txt, True, colour)
    r = s.get_rect(center=pos) if center else s.get_rect(topleft=pos)
    screen.blit(s, r)
    return r

def panel(rect, fill=PANEL, outline=GRID, radius=16):
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, outline, rect, 2, border_radius=radius)

def button(rect, label, accent=CYAN):
    pygame.draw.rect(screen, PANEL2, rect, border_radius=12)
    pygame.draw.rect(screen, accent, rect, 2, border_radius=12)
    text(label, F_BODY, WHITE, rect.center, True)

def add_particles(pos, colour, count=16):
    for _ in range(count):
        a = random.random() * math.tau
        speed = random.uniform(40, 180)
        particles.append([
            pygame.Vector2(pos),
            pygame.Vector2(math.cos(a) * speed, math.sin(a) * speed),
            random.uniform(.25, .7),
            colour,
        ])

def update_particles(dt):
    for p in particles[:]:
        p[0] += p[1] * dt
        p[1] *= 0.94
        p[2] -= dt
        if p[2] <= 0:
            particles.remove(p)

def draw_particles():
    for pos, vel, life, colour in particles:
        pygame.draw.circle(screen, colour, (int(pos.x), int(pos.y)), max(1, int(5 * life)))

def set_message(msg, colour=WHITE):
    global message, message_colour
    message = msg
    message_colour = colour

def reset_game():
    global score, shield, combo, best_combo, level
    global threats, secured, mission_start, last_spawn
    global spawn_interval, time_left, cursor, particles
    global base_time, level_start, last_level, mission_failed, failure_reason

    score = 0
    shield = 100
    combo = 0
    best_combo = 0
    level = 1
    threats = {}
    secured = set()
    particles = []
    cursor = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

    mission_start = pygame.time.get_ticks()
    last_spawn = mission_start
    spawn_interval = 3.0
    base_time = 75
    level_start = mission_start
    last_level = 1
    mission_failed = False
    failure_reason = ""
    time_left = base_time
    set_message("SYSTEM ONLINE — protect every connected device.", CYAN)

def create_threat(now):
    # Avoid spawning a threat where a benign data event is currently present
    available = [i for i in range(8) if i not in threats and i not in secured and i not in data_events and i not in stealth_threats]
    if not available:
        # Once everything has been secured, reset secured devices so
        # later levels can continue generating gameplay.
        secured.clear()
        available = list(range(8))

    if not available:
        return

    i = random.choice(available)
    attack = random.choice(attack_types)
    threats[i] = attack
    # threat becomes dangerous after a short grace period
    # Activate faster: 0.8–1.5 seconds
    active_in = random.randint(800, 1500)
    threat_active_at[i] = now + active_in
    # drain rate scales with level
    threat_drain[i] = 4 + level * 3


def create_stealth_threat(now):
    # Create a hidden harmful rootkit-style threat that doesn't visibly change the device
    available = [i for i in range(8) if i not in threats and i not in secured and i not in data_events and i not in stealth_threats]
    if not available:
        return
    i = random.choice(available)
    attack = random.choice(attack_types)
    # Stealth activates quickly: ~1–2 seconds
    active_in = random.randint(1000, 2000)
    drain = 6 + level * 4
    stealth_threats[i] = (now + active_in, attack, drain)

def create_data_event(now):
    """Spawn a benign data event on a random available device."""
    available = [i for i in range(8) if i not in threats and i not in data_events and i not in secured]
    if not available:
        return
    i = random.choice(available)
    duration = random.randint(800, 2200)
    # Pick a misleading label from attack types so the benign packet looks suspicious
    label = random.choice([t[0] for t in attack_types])
    data_events[i] = (now + duration, label)

def secure_target(i):
    global score, shield, combo, best_combo, level

    if i in threats:
        # If this device had a deceptive data event, remove it when we handle the real threat
        data_events.pop(i, None)
        attack_name, solution, colour = threats.pop(i)
        secured.add(i)
        combo += 1
        best_combo = max(best_combo, combo)

        bonus = 100 + (combo - 1) * 25
        score += bonus

        device_center = device_rects[i].center
        add_particles(device_center, GREEN, 24)

        if combo >= 3:
            set_message(f"THREAT NEUTRALISED — {solution} — COMBO x{combo}! +{bonus}", GREEN)
        else:
            set_message(f"{attack_name} STOPPED — {solution} — +{bonus}", GREEN)

        # Level up every 4 secured devices
        new_level = 1 + len([x for x in secured]) // 4
        if new_level > level:
            level = min(5, new_level)
            set_message(f"LEVEL {level} — ATTACKS ARE GETTING FASTER!", YELLOW)
        return True

    # Safe device clicked: penalty
    combo = 0
    shield = max(0, shield - 10)
    score = max(0, score - 30)
    add_particles(device_rects[i].center, RED, 12)
    set_message("WRONG TARGET — that device was healthy. -10 SHIELD", RED)
    return False


def secure_stealth(i):
    """Handle securing a stealth/rootkit threat."""
    global score, shield, combo, best_combo
    if i in stealth_threats:
        _, attack, _ = stealth_threats.pop(i)
        secured.add(i)
        combo += 1
        best_combo = max(best_combo, combo)
        bonus = 80 + (combo - 1) * 20
        score += bonus
        add_particles(device_rects[i].center, GREEN, 28)
        set_message(f"ROOTKIT REMOVED — ISOLATE {attack[0]} — +{bonus}", GREEN)
        return True
    return False

def start_quiz():
    global state, quiz_index, quiz_message
    quiz_index = 0
    quiz_message = ""
    state = QUIZ

# ============================================================
# Menu
# ============================================================

def draw_menu():
    screen.fill(BG)

    # Decorative city
    for x in range(0, WIDTH, 80):
        h = random.Random(x).randint(35, 110)
        pygame.draw.rect(screen, (12, 18, 38), (x, HEIGHT - h, 65, h))
        for wy in range(HEIGHT - h + 15, HEIGHT - 10, 18):
            pygame.draw.rect(screen, (25, 40, 68), (x + 10, wy, 8, 6))

    text("IoT", F_BIG, CYAN, (WIDTH // 2 - 160, 100), True)
    text("DEFENDER", F_TITLE, WHITE, (WIDTH // 2 + 90, 100), True)
    text("SMART CITY SHIELD", F_MED, YELLOW, (WIDTH // 2, 160), True)
    text("CONNECT  •  DETECT  •  DEFEND", F_BODY, MUTED, (WIDTH // 2, 198), True)

    panel(pygame.Rect(255, 250, 690, 220))
    text("YOUR MISSION", F_MED, CYAN, (WIDTH // 2, 285), True)
    text("Protect the city's connected IoT network", F_BODY, WHITE, (WIDTH // 2, 330), True)
    text("Find cyber threats before they damage", F_BODY, WHITE, (WIDTH // 2, 365), True)
    text("critical smart-city services.", F_BODY, WHITE, (WIDTH // 2, 397), True)

    start = pygame.Rect(WIDTH // 2 - 170, 500, 340, 62)
    button(start, "START MISSION", CYAN)

    how = pygame.Rect(WIDTH // 2 - 170, 580, 340, 52)
    button(how, "HOW TO PLAY", PURPLE)

    text("Pygame prototype • designed for ages 8–18", F_SMALL, MUTED, (WIDTH // 2, 680), True)
    return start, how

def draw_how():
    screen.fill(BG)
    text("HOW TO PLAY", F_TITLE, CYAN, (WIDTH // 2, 80), True)

    panel(pygame.Rect(130, 140, 940, 455))

    steps = [
        ("01", "SCAN", "Watch the connected IoT devices."),
        ("02", "DETECT", "Red devices have been compromised."),
        ("03", "DEFEND", "Select a threat to apply the correct defence."),
        ("04", "COMBO", "Secure threats quickly to earn bigger bonuses."),
        ("05", "SURVIVE", "Do not let the City Shield reach zero."),
        ("06", "LEARN", "Finish the cyber-awareness challenge."),
    ]

    y = 175
    for num, title, desc in steps:
        text(num, F_MED, YELLOW, (175, y))
        text(title, F_BODY, CYAN, (235, y))
        text(desc, F_BODY, WHITE, (385, y))
        y += 62

    text("Keyboard: Arrow keys move the cursor • SPACE selects", F_SMALL, MUTED, (WIDTH // 2, 625), True)
    back = pygame.Rect(WIDTH // 2 - 130, 660, 260, 48)
    button(back, "BACK", PURPLE)
    return back

# ============================================================
# Game screen
# ============================================================

def draw_device(i):
    rect = device_rects[i]
    name, icon, base_colour = devices[i]

    if i in threats:
        attack_name, solution, attack_colour = threats[i]
        fill = (48, 18, 32)
        outline = RED
        status = "⚠ THREAT"
        status_colour = RED
    elif i in data_events and i not in threats:
        expiry, fake_label = data_events[i]
        # Render the benign data to look almost identical to a real threat
        attack_name = fake_label
        fill = (48, 18, 32)
        outline = RED
        status = "⚠ SUSPICIOUS"
        status_colour = RED
    elif i in secured:
        fill = (16, 48, 43)
        outline = GREEN
        status = "✓ SECURED"
        status_colour = GREEN
    else:
        fill = PANEL
        outline = base_colour
        status = "● ONLINE"
        status_colour = GREEN

    pygame.draw.rect(screen, fill, rect, border_radius=15)
    pygame.draw.rect(screen, outline, rect, 3, border_radius=15)

    # Device icon drawn as a simple stylised terminal symbol
    icon_box = pygame.Rect(rect.centerx - 45, rect.y + 18, 90, 50)
    pygame.draw.rect(screen, (8, 13, 28), icon_box, border_radius=10)
    pygame.draw.rect(screen, outline, icon_box, 2, border_radius=10)
    text(icon[:3], F_MED, outline, icon_box.center, True)

    text(name, F_BODY, WHITE, (rect.centerx, rect.y + 84), True)
    text(status, F_SMALL, status_colour, (rect.centerx, rect.y + 113), True)

    if i in threats:
        text(attack_name, F_SMALL, YELLOW, (rect.centerx, rect.y + 142), True)
    elif i in secured:
        text("SECURITY ACTIVE", F_SMALL, GREEN, (rect.centerx, rect.y + 142), True)
    else:
        text("MONITORING", F_SMALL, MUTED, (rect.centerx, rect.y + 142), True)

    # (data events render above as deceptive threats)

def draw_game():
    screen.fill(BG)

    # Top bar
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 112))
    pygame.draw.line(screen, GRID, (0, 111), (WIDTH, 111), 2)

    text("🛡 IoT DEFENDER", F_MED, CYAN, (30, 24))
    text(f"SCORE  {score}", F_BODY, WHITE, (320, 31))
    text(f"COMBO  x{combo}", F_BODY, YELLOW if combo else MUTED, (490, 31))
    text(f"LEVEL  {level}", F_BODY, PURPLE, (650, 31))
    text(f"THREATS {len(threats)}", F_BODY, WHITE, (800, 31))

    # Shield
    text("CITY SHIELD", F_SMALL, MUTED, (960, 16))
    pygame.draw.rect(screen, (40, 45, 62), (960, 43, 205, 18), border_radius=8)
    shield_w = int(205 * shield / 100)
    shield_colour = GREEN if shield > 55 else YELLOW if shield > 25 else RED
    pygame.draw.rect(screen, shield_colour, (960, 43, shield_w, 18), border_radius=8)
    text(f"{shield}%", F_SMALL, shield_colour, (1170, 40), True)

    # Message panel
    panel(pygame.Rect(30, 125, 1140, 54), PANEL2, GRID)
    text(message, F_BODY, message_colour, (WIDTH // 2, 152), True)

    # Devices
    for i in range(8):
        draw_device(i)

    # (cursor is drawn globally now)

    # Bottom legend
    text("ARROWS: MOVE", F_SMALL, MUTED, (30, 730))
    text("SPACE / CLICK: DEFEND", F_SMALL, CYAN, (190, 730))
    text("1–8: QUICK SELECT", F_SMALL, MUTED, (455, 730))
    text("RED = THREAT", F_SMALL, RED, (700, 730))
    text("GREEN = SECURED", F_SMALL, GREEN, (900, 730))

# ============================================================
# Quiz
# ============================================================

def draw_quiz():
    screen.fill(BG)

    text("CYBER CHALLENGE", F_TITLE, CYAN, (WIDTH // 2, 70), True)
    text(f"Question {quiz_index + 1} / {len(quiz_questions)}", F_BODY, MUTED, (WIDTH // 2, 125), True)

    q, answers, correct = quiz_questions[quiz_index]

    panel(pygame.Rect(100, 165, 1000, 125))
    # Basic word wrapping
    words = q.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if F_BODY.size(test)[0] > 900:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)

    yy = 205
    for line in lines:
        text(line, F_BODY, WHITE, (WIDTH // 2, yy), True)
        yy += 32

    rects = []
    y = 330
    for i, ans in enumerate(answers):
        r = pygame.Rect(180, y, 840, 62)
        accent = GREEN if quiz_message and i == correct else PANEL2
        button(r, f"{i + 1}. {ans}", accent)
        rects.append(r)
        y += 75

    if quiz_message:
        text(quiz_message, F_BODY, quiz_message_colour, (WIDTH // 2, 670), True)
    else:
        text("Choose the safest response.", F_SMALL, MUTED, (WIDTH // 2, 670), True)

    return rects

# ============================================================
# Result
# ============================================================

def draw_result():
    screen.fill(BG)

    # Show failure or success header
    if mission_failed:
        text("MISSION FAILED", F_TITLE, RED, (WIDTH // 2, 95), True)
        text(failure_reason, F_MED, RED, (WIDTH // 2, 150), True)
    else:
        text("MISSION COMPLETE", F_TITLE, CYAN, (WIDTH // 2, 95), True)
    text("FINAL SCORE", F_MED, MUTED, (WIDTH // 2, 180), True)
    text(str(score), F_TITLE, YELLOW, (WIDTH // 2, 245), True)

    if score >= 1200:
        rank = "CYBER CHAMPION"
        colour = GREEN
    elif score >= 800:
        rank = "NETWORK DEFENDER"
        colour = CYAN
    else:
        rank = "ROOKIE DEFENDER"
        colour = YELLOW

    text(rank, F_BIG, colour, (WIDTH // 2, 330), True)
    text(f"Best combo: x{best_combo}", F_BODY, WHITE, (WIDTH // 2, 390), True)
    text(f"Final city shield: {shield}%", F_BODY, WHITE, (WIDTH // 2, 425), True)

    # Achievement cards (only on success)
    if not mission_failed:
        achievements = [
            ("IoT AWARE", "Protected connected devices"),
            ("FAST RESPONSE", "Stopped active threats"),
            ("CYBER SMART", "Completed the quiz"),
        ]

        x = 150
        for title, desc in achievements:
            r = pygame.Rect(x, 470, 280, 100)
            panel(r, PANEL, GRID)
            text("✓ " + title, F_BODY, GREEN, (r.centerx, r.y + 28), True)
            text(desc, F_SMALL, MUTED, (r.centerx, r.y + 63), True)
            x += 310

    replay = pygame.Rect(WIDTH // 2 - 170, 610, 340, 52)
    button(replay, "PLAY AGAIN", CYAN)

    menu = pygame.Rect(WIDTH // 2 - 170, 675, 340, 45)
    button(menu, "MAIN MENU", PURPLE)

    return replay, menu

# ============================================================
# Main loop
# ============================================================

reset_game()

running = True

while running:
    dt = clock.tick(60) / 1000.0
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keep our custom cursor in sync with the mouse
        if event.type == pygame.MOUSEMOTION:
            cursor.xy = event.pos

        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                start, how = draw_menu()
                if start.collidepoint(event.pos):
                    reset_game()
                    state = GAME
                elif how.collidepoint(event.pos):
                    state = HOW

        elif state == HOW:
            if event.type == pygame.MOUSEBUTTONDOWN:
                back = draw_how()
                if back.collidepoint(event.pos):
                    state = MENU

        elif state == GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse directly selects a device
                for i, rect in enumerate(device_rects):
                    if rect.collidepoint(event.pos):
                        cursor.xy = rect.center
                        # Prioritise visible threats, then stealth threats, then deceptive data
                        if i in threats:
                            secure_target(i)
                        elif i in stealth_threats:
                            secure_stealth(i)
                        elif i in data_events:
                            # Mishandling a benign data packet is now fatal
                            data_events.pop(i, None)
                            add_particles(rect.center, RED, 32)
                            mission_failed = True
                            failure_reason = "MISHANDLED DATA"
                            set_message("MISCLASSIFIED PACKET — MISSION FAILED", RED)
                            state = RESULT
                        else:
                            # Normal interaction (safe device)
                            secure_target(i)
                        break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = MENU

                # Quick-select
                if pygame.K_1 <= event.key <= pygame.K_8:
                    secure_target(event.key - pygame.K_1)

                if event.key == pygame.K_SPACE:
                    # Select whichever device is under the cursor
                    for i, rect in enumerate(device_rects):
                        if rect.collidepoint((int(cursor.x), int(cursor.y))):
                            secure_target(i)
                            break

        elif state == QUIZ:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = MENU

                elif pygame.K_1 <= event.key <= pygame.K_4:
                    answer = event.key - pygame.K_1
                    q, answers, correct = quiz_questions[quiz_index]

                    if answer == correct:
                        score += 200
                        quiz_message = "CORRECT! +200 POINTS"
                        quiz_message_colour = GREEN
                    else:
                        shield = max(0, shield - 10)
                        quiz_message = "NOT THE SAFEST CHOICE. -10 SHIELD"
                        quiz_message_colour = RED

                    pygame.time.set_timer(pygame.USEREVENT + 1, 700)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(draw_quiz()):
                    if r.collidepoint(event.pos):
                        q, answers, correct = quiz_questions[quiz_index]

                        if i == correct:
                            score += 200
                            quiz_message = "CORRECT! +200 POINTS"
                            quiz_message_colour = GREEN
                        else:
                            shield = max(0, shield - 10)
                            quiz_message = "NOT THE SAFEST CHOICE. -10 SHIELD"
                            quiz_message_colour = RED

                        pygame.time.set_timer(pygame.USEREVENT + 1, 700)

            if event.type == pygame.USEREVENT + 1:
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                quiz_index += 1
                quiz_message = ""

                if quiz_index >= len(quiz_questions):
                    state = RESULT

        elif state == RESULT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                replay, menu = draw_result()

                if replay.collidepoint(event.pos):
                    reset_game()
                    state = GAME

                elif menu.collidepoint(event.pos):
                    state = MENU

    # --------------------------------------------------------
    # Game update
    # --------------------------------------------------------

    if state == GAME:
        elapsed_total = (now - mission_start) / 1000

        # Make levels ramp faster: based on secured count and some elapsed time
        level = min(5, 1 + len(secured) // 3 + int(elapsed_total // 12))

        # Increase difficulty: faster spawns at higher levels
        spawn_interval = max(0.4, 1.8 - level * 0.25)

        if now - last_spawn >= spawn_interval * 1000:
            create_threat(now)
            last_spawn = now

        # Spawn benign data events frequently and quickly
        if now - last_data_spawn >= data_spawn_interval:
            create_data_event(now)
            # jitter next spawn
            last_data_spawn = now + random.randint(300, 900)

        # Occasionally spawn stealth rootkit threats
        if random.random() < 0.06:
            create_stealth_threat(now)

        # Remove expired data events
        for di in list(data_events.keys()):
            expiry_label = data_events.get(di)
            if not expiry_label:
                continue
            expiry = expiry_label[0]
            if expiry <= now:
                data_events.pop(di, None)

        # Move cursor with keyboard
        keys = pygame.key.get_pressed()
        speed = 420

        if keys[pygame.K_LEFT]:
            cursor.x -= speed * dt
        if keys[pygame.K_RIGHT]:
            cursor.x += speed * dt
        if keys[pygame.K_UP]:
            cursor.y -= speed * dt
        if keys[pygame.K_DOWN]:
            cursor.y += speed * dt

        cursor.x = max(15, min(WIDTH - 15, cursor.x))
        cursor.y = max(120, min(700, cursor.y))
        # Threats that are not handled quickly will start draining the shield
        for ti in list(threats.keys()):
            active_at = threat_active_at.get(ti, 0)
            if now >= active_at:
                drain = threat_drain.get(ti, 6)
                shield = max(0, shield - int(drain * dt))
                # subtle warning message (occasional)
                if random.random() < 0.01:
                    set_message("THREAT IS ACTIVE — CITY SHIELD IS BEING DRAINED!", RED)

        # Stealth threats silently drain when active
        for si, info in list(stealth_threats.items()):
            active_at, attack, drain = info
            if now >= active_at:
                shield = max(0, shield - int(drain * dt))
                # stealth events almost never give a hint
                if random.random() < 0.002:
                    set_message("SUSPICIOUS ACTIVITY DETECTED — investigate devices.", MUTED)

        # No time-based loss; player loses by depleting shield or mishandling data
        if shield <= 0:
            mission_failed = True
            failure_reason = "SHIELD DEPLETED"
            state = RESULT

    update_particles(dt)

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    if state == MENU:
        draw_menu()
    elif state == HOW:
        draw_how()
    elif state == GAME:
        draw_game()
    elif state == QUIZ:
        draw_quiz()
    elif state == RESULT:
        draw_result()

    # Draw custom cursor on top of all screens
    cursor_radius = 16
    pygame.draw.circle(screen, CYAN, (int(cursor.x), int(cursor.y)), cursor_radius, 2)
    pygame.draw.line(screen, CYAN, (int(cursor.x) - 24, int(cursor.y)), (int(cursor.x) + 24, int(cursor.y)), 1)
    pygame.draw.line(screen, CYAN, (int(cursor.x), int(cursor.y) - 24), (int(cursor.x), int(cursor.y) + 24), 1)

    draw_particles()
    pygame.display.flip()

pygame.quit()
sys.exit()
