import pygame
import random
import math
import sys
import json
import threading
import urllib.request
import os
import shutil
import subprocess

pygame.init()
pygame.mouse.set_visible(False)

# ============================================================
# DRONE VS SPHERO - FIRST PERSON STYLE PROTOTYPE
# Controls:
#   WASD / Arrow keys = move/aim the drone
#   SPACE / Left mouse = shoot
#   1-5 = choose an upgrade
#   ESC = quit
# ============================================================

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone vs Sphero - Cybersecurity Prototype")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
SMALL = pygame.font.SysFont("arial", 19)
BIG = pygame.font.SysFont("arial", 42, bold=True)
TITLE = pygame.font.SysFont("arial", 58, bold=True)

# Colours
BLACK = (8, 12, 18)
WHITE = (240, 245, 250)
GREY = (120, 130, 145)
DARK_GREY = (35, 42, 52)
GREEN = (60, 220, 120)
RED = (235, 70, 70)
YELLOW = (245, 205, 65)
CYAN = (60, 210, 240)
BLUE = (80, 140, 245)
PURPLE = (180, 100, 240)
ORANGE = (245, 145, 55)

# ------------------------------------------------------------
# Game data
# ------------------------------------------------------------

LEVEL_HP = {
    1: 5,
    2: 8,
    3: 12,
    4: 16,
    5: 20,
    6: 25,
    7: 30,
    8: 36,
}

QUESTIONS = [
    {
        "question": "Which password is the strongest?",
        "answers": [
            "A) password123",
            "B) Oliver2026",
            "C) A long unique passphrase with mixed characters",
            "D) 12345678",
        ],
        "correct": 2,
    },
    {
        "question": "What is phishing?",
        "answers": [
            "A) A way to back up files",
            "B) A fake message designed to trick you into giving information",
            "C) A type of computer monitor",
            "D) A safe password manager",
        ],
        "correct": 1,
    },
    {
        "question": "What does MFA add to an account?",
        "answers": [
            "A) Multiple monitors",
            "B) Extra authentication factors",
            "C) More storage",
            "D) Faster internet",
        ],
        "correct": 1,
    },
    {
        "question": "What is malware?",
        "answers": [
            "A) Malicious software",
            "B) A secure website",
            "C) A backup device",
            "D) A type of keyboard",
        ],
        "correct": 0,
    },
    {
        "question": "What does encryption do?",
        "answers": [
            "A) Deletes every file",
            "B) Makes data unreadable without the appropriate key",
            "C) Makes Wi-Fi faster",
            "D) Turns off a computer",
        ],
        "correct": 1,
    },
    {
        "question": "You receive an unexpected email asking you to click a link urgently. What should you do?",
        "answers": [
            "A) Click it immediately",
            "B) Send your password",
            "C) Verify the message and sender before acting",
            "D) Forward it to everyone",
        ],
        "correct": 2,
    },
    {
        "question": "What is social engineering?",
        "answers": [
            "A) Designing social media apps",
            "B) Manipulating people into revealing information or taking an action",
            "C) Building a computer",
            "D) Encrypting a hard drive",
        ],
        "correct": 1,
    },
    {
        "question": "Why should software and operating systems be updated?",
        "answers": [
            "A) Updates can fix security vulnerabilities",
            "B) Updates always remove files",
            "C) Updates disable security",
            "D) Updates are only for appearance",
        ],
        "correct": 0,
    },
    {
        "question": "Which is a safer way to use public Wi-Fi?",
        "answers": [
            "A) Share passwords over public Wi-Fi",
            "B) Use secure connections and avoid sensitive activity on untrusted networks",
            "C) Turn off every security feature",
            "D) Use the same password everywhere",
        ],
        "correct": 1,
    },
    {
        "question": "What is a firewall mainly used for?",
        "answers": [
            "A) Controlling network traffic using security rules",
            "B) Cooling the computer",
            "C) Increasing screen brightness",
            "D) Creating passwords",
        ],
        "correct": 0,
    },
]

UPGRADES = [
    ("TARGET LOCK", "Automatically helps keep the crosshair on the Sphero."),
    ("RAPID FIRE", "Reduces the time between shots."),
    ("SHIELD", "Reduces damage taken from the Sphero."),
    ("DOUBLE SHOT", "A successful shot deals two damage."),
    ("AI SCAN", "Temporarily highlights the Sphero through the arena."),
    ("HEALTH +25", "Adds 25 to your maximum drone health."),
]

# ------------------------------------------------------------
# Weapons
# ------------------------------------------------------------
# Each weapon defines simple stats used by `Game.fire()`.
WEAPONS = [
    ("BASIC", {"damage": 1, "cooldown": 0.45, "aim_radius": 60, "desc": "Standard blaster."}),
    ("SHOTGUN", {"damage": 1, "pellets": 3, "cooldown": 0.7, "aim_radius": 80, "desc": "Fires multiple pellets in a spread."}),
    ("SNIPER", {"damage": 4, "cooldown": 1.2, "aim_radius": 35, "desc": "High damage, narrow aim."}),
    ("PIERCING", {"damage": 2, "cooldown": 0.9, "aim_radius": 60, "desc": "Deals extra score on hit."}),
]

# ------------------------------------------------------------
# Utility drawing functions
# ------------------------------------------------------------

def draw_text(text, font, colour, x, y, center=False):
    surf = font.render(text, True, colour)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)
    return rect


def draw_wrapped_text(text, font, colour, rect, line_gap=5):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= rect.width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    y = rect.top
    for line in lines:
        draw_text(line, font, colour, rect.left, y)
        y += font.get_height() + line_gap

    return y


def draw_bar(x, y, width, height, value, maximum, fill_colour, label):
    pygame.draw.rect(screen, DARK_GREY, (x, y, width, height), border_radius=5)
    ratio = 0 if maximum <= 0 else max(0, min(1, value / maximum))
    pygame.draw.rect(
        screen,
        fill_colour,
        (x, y, int(width * ratio), height),
        border_radius=5,
    )
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2, border_radius=5)
    draw_text(f"{label}: {max(0, int(value))}/{int(maximum)}",
              SMALL, WHITE, x + 8, y + 4)



# ------------------------------------------------------------
# Local Ollama AI - Sphero movement controller
# ------------------------------------------------------------
# Ollama runs locally. It does NOT control the game frame-by-frame;
# instead, it periodically chooses a movement behaviour/direction.
# The game adds increasing randomness at higher levels so the Sphero
# becomes harder to predict.
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


class OllamaMovementAI:
    def __init__(self):
        self.lock = threading.Lock()
        self.request_in_progress = False
        self.next_decision = 0.0
        self.direction = (1.0, 0.0)
        self.behaviour = "RANDOM"
        self.last_error = ""
        # Configurable: allow a mock mode driven by an env var for testing
        self.mock = os.environ.get("MOCK_OLLAMA", "0") == "1"
        self.ollama_url = os.environ.get("OLLAMA_URL", OLLAMA_URL)
        self.ollama_model = os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL)
        # Prefer local ollama CLI if available for more reliable, non-streaming JSON
        self.ollama_cli = shutil.which("ollama")
        # Also check a common Windows install location
        if not self.ollama_cli:
            possible = os.path.expandvars(r"%LocalAppData%\Programs\Ollama\ollama.exe")
            if os.path.exists(possible):
                self.ollama_cli = possible

    def request_decision(self, level, sphero_x, sphero_y,
                         drone_x, drone_y, current_vx, current_vy):
        """Ask local Ollama for the Sphero's next movement behaviour."""
        with self.lock:
            if self.request_in_progress:
                return
            self.request_in_progress = True

        prompt = f"""
You are the movement AI for a game called Drone vs Sphero.
You control the Sphero BOLT and must avoid the drone.

Current level: {level}
Sphero position: ({sphero_x:.0f}, {sphero_y:.0f})
Drone/crosshair position: ({drone_x:.0f}, {drone_y:.0f})
Current velocity: ({current_vx:.0f}, {current_vy:.0f})

Choose ONE movement behaviour:
RANDOM
CHASE
EVADE
LEFT
RIGHT
UP
DOWN

At higher levels, make the movement less predictable.
Return ONLY valid JSON in this exact format:
{{"behaviour":"RANDOM","x":0.0,"y":-1.0}}

x and y must each be between -1 and 1.
Do not include markdown or explanations.
"""

        def worker():
            try:
                # If mock mode is enabled, produce a deterministic/simple response
                if self.mock:
                    # Choose a behaviour based on distance: try to evade if close,
                    # otherwise randomly chase or wander.
                    dx = drone_x - sphero_x
                    dy = drone_y - sphero_y
                    dist = math.hypot(dx, dy)

                    if dist < 120:
                        behaviour = "EVADE"
                        angle = math.atan2(-dy, -dx)  # move away from drone
                    else:
                        behaviour = random.choice(["CHASE", "RANDOM"])
                        if behaviour == "CHASE":
                            angle = math.atan2(dy, dx)
                        else:
                            angle = random.uniform(0, math.tau)

                    x = math.cos(angle)
                    y = math.sin(angle)

                    # Normalize
                    length = math.hypot(x, y) or 1.0
                    x /= length
                    y /= length

                    with self.lock:
                        self.direction = (x, y)
                        self.behaviour = behaviour
                        self.last_error = "(mock)"
                    print(f"OLLAMA-MOCK -> behaviour={behaviour}, x={x:.2f}, y={y:.2f}")
                    return

                # If local ollama CLI is available, use it to get structured JSON
                if self.ollama_cli:
                    try:
                        proc = subprocess.run(
                            [self.ollama_cli, "run", self.ollama_model, "--format", "json", "--nowordwrap", prompt],
                            capture_output=True,
                            text=True,
                            timeout=6,
                        )
                        out = proc.stdout.strip()
                        if out:
                            try:
                                answer = json.loads(out)
                            except Exception:
                                # If CLI returned a bare JSON object without outer structure,
                                # try to extract an object substring.
                                import re
                                m = re.search(r"\{.*\}", out, re.DOTALL)
                                if m:
                                    try:
                                        answer = json.loads(m.group(0))
                                    except Exception:
                                        answer = {}
                        else:
                            answer = {}
                    except Exception as exc:
                        answer = {}
                        print("OLLAMA CLI error:", exc)

                else:
                    # Real Ollama HTTP request
                    # Use conservative sampling to encourage valid machine-readable output
                    request_options = {
                        "temperature": 0.2,
                        # Allow more tokens to reduce truncation likelihood
                        "num_predict": 150
                    }

                    data = json.dumps({
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "options": request_options,
                    }).encode("utf-8")

                    req = urllib.request.Request(
                        self.ollama_url,
                        data=data,
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )

                    # Attempt the request, with a small retry if parsing fails.
                    attempts = 2
                    result = None
                    for attempt in range(attempts):
                        with urllib.request.urlopen(req, timeout=8.0) as response:
                            raw = response.read().decode("utf-8")
                        try:
                            result = json.loads(raw)
                        except Exception:
                            # If parsing outer JSON fails, try once more.
                            result = None
                        if result is not None:
                            break
                        # short backoff before retry
                        import time
                        time.sleep(0.15)

                    # Be flexible about response formats. Ollama variants may return
                    # the payload under different keys or with nested choices.
                    inner = None
                    if isinstance(result, dict):
                        for key in ("response", "output", "text", "content"):
                            v = result.get(key)
                            if isinstance(v, str) and v.strip():
                                inner = v
                                break

                        if inner is None and "choices" in result:
                            try:
                                ch = result.get("choices")
                                if isinstance(ch, list) and ch:
                                    c0 = ch[0]
                                    for ck in ("message", "content", "text"):
                                        v = c0.get(ck) if isinstance(c0, dict) else None
                                        if isinstance(v, str) and v.strip():
                                            inner = v
                                            break
                                    if inner:
                                        pass
                            except Exception:
                                inner = None

                # If the outer result already directly contains behaviour/x/y,
                # accept it without an inner string.
                answer = {}
                if isinstance(result, dict) and all(k in result for k in ("behaviour", "x", "y")):
                    answer = {"behaviour": result.get("behaviour"), "x": result.get("x"), "y": result.get("y")}
                else:
                    if inner is None and isinstance(result, str):
                        inner = result

                    if inner is not None:
                        try:
                            answer = json.loads(inner)
                        except Exception:
                            # Try to extract a JSON object substring
                            import re
                            m = re.search(r"\{.*\}", inner, re.DOTALL)
                            if m:
                                try:
                                    answer = json.loads(m.group(0))
                                except Exception:
                                    answer = {}
                            else:
                                answer = {}

                behaviour = str(answer.get("behaviour", "RANDOM")).upper()
                try:
                    x = float(answer.get("x", 0))
                except Exception:
                    x = 0.0
                try:
                    y = float(answer.get("y", 0))
                except Exception:
                    y = 0.0

                if behaviour not in {
                    "RANDOM", "CHASE", "EVADE",
                    "LEFT", "RIGHT", "UP", "DOWN"
                }:
                    behaviour = "RANDOM"

                x = max(-1.0, min(1.0, x))
                y = max(-1.0, min(1.0, y))

                # If Ollama gives a named direction, use that direction.
                named = {
                    "LEFT": (-1.0, 0.0),
                    "RIGHT": (1.0, 0.0),
                    "UP": (0.0, -1.0),
                    "DOWN": (0.0, 1.0)
                }
                if behaviour in named:
                    x, y = named[behaviour]

                # Prevent a zero vector.
                if abs(x) + abs(y) < 0.05:
                    angle = random.uniform(0, math.tau)
                    x, y = math.cos(angle), math.sin(angle)

                length = math.hypot(x, y)
                x /= length
                y /= length

                with self.lock:
                    self.direction = (x, y)
                    self.behaviour = behaviour
                    self.last_error = ""

            except Exception as exc:
                with self.lock:
                    self.last_error = str(exc)
                print("OLLAMA request error:", exc)

            finally:
                with self.lock:
                    self.request_in_progress = False

        threading.Thread(target=worker, daemon=True).start()

    def get_direction(self):
        with self.lock:
            return self.direction, self.behaviour, self.last_error


# ------------------------------------------------------------
# Sphero
# ------------------------------------------------------------

EASY_BOSS_PATTERNS = [
    {"name": "DUAL ORB", "count": 2, "hp_bonus": 2, "orbit": 72, "speed": 0.9, "attack": "burst"},
    {"name": "BULWARK", "count": 2, "hp_bonus": 3, "orbit": 80, "speed": 0.8, "attack": "pulse"},
    {"name": "TRIAD", "count": 3, "hp_bonus": 3, "orbit": 84, "speed": 1.0, "attack": "shards"},
]

HARD_BOSS_PATTERNS = [
    {"name": "DUAL ORB", "count": 2, "hp_bonus": 4, "orbit": 82, "speed": 1.1, "attack": "burst"},
    {"name": "TRIAD", "count": 3, "hp_bonus": 5, "orbit": 94, "speed": 1.25, "attack": "shards"},
    {"name": "QUAD CORE", "count": 4, "hp_bonus": 6, "orbit": 108, "speed": 1.45, "attack": "storm"},
    {"name": "BULWARK", "count": 2, "hp_bonus": 8, "orbit": 92, "speed": 1.0, "attack": "pulse"},
    {"name": "BROOD", "count": 5, "hp_bonus": 9, "orbit": 126, "speed": 1.6, "attack": "burst"},
    {"name": "NEXUS", "count": 6, "hp_bonus": 11, "orbit": 140, "speed": 1.8, "attack": "storm"},
]

BOSS_PATTERNS = EASY_BOSS_PATTERNS + HARD_BOSS_PATTERNS


class Sphero:
    def __init__(self, level):
        self.level = level
        self.is_boss = level > 1
        self.boss_name = "SPHERO BOLT"
        self.parts = []
        self.projectiles = []
        self.attack_timer = random.uniform(1.0, 1.7)

        if self.is_boss:
            self._setup_boss()
        else:
            self._setup_regular()

    def _setup_regular(self):
        self.max_hp = LEVEL_HP.get(self.level, 36 + (self.level - 8) * 7)
        self.hp = self.max_hp

        self.x = random.uniform(-420, 420)
        self.y = random.uniform(-250, 250)

        self.vx = random.choice([-1, 1]) * random.uniform(45, 80)
        self.vy = random.choice([-1, 1]) * random.uniform(35, 70)

        self.base_speed = 75 + self.level * 17
        self.dodge_strength = min(0.90, 0.10 + self.level * 0.09)
        self.direction_timer = random.uniform(0.6, 1.5)
        self.dodge_timer = 0
        self.flash_timer = 0
        self.ai = OllamaMovementAI()
        self.ai_decision_timer = random.uniform(0.4, 1.0)
        self.parts = [{"x": self.x, "y": self.y, "radius": 24}]

    def _setup_boss(self):
        if self.level <= 5:
            pool = EASY_BOSS_PATTERNS
        else:
            pool = HARD_BOSS_PATTERNS
        self.pattern = random.choice(pool)
        self.boss_name = self.pattern["name"]
        self.count = self.pattern["count"]
        self.attack_style = self.pattern["attack"]

        if self.level <= 3:
            self.count = max(2, self.count - 1)
        elif self.level <= 5:
            self.count = max(2, min(self.count, 3))

        self.x = random.uniform(-300, 300)
        self.y = random.uniform(-180, 180)
        self.vx = random.choice([-1, 1]) * random.uniform(55, 85)
        self.vy = random.choice([-1, 1]) * random.uniform(45, 75)
        self.base_speed = 55 + self.level * 12
        self.dodge_strength = min(0.95, 0.18 + self.level * 0.06)
        self.flash_timer = 0

        self.parts = []
        part_base = 3 if self.level <= 3 else 4 if self.level <= 5 else 5
        for i in range(self.count):
            angle = (i / self.count) * math.tau + random.uniform(0.0, 0.7)
            part_hp = part_base + min(4, self.level // 3)
            self.parts.append({
                "angle": angle,
                "radius": self.pattern["orbit"] + random.uniform(-10, 15),
                "size": random.randint(17, 30),
                "x": self.x,
                "y": self.y,
                "hp": part_hp,
                "max_hp": part_hp,
                "alive": True,
            })

        self.max_hp = sum(part["max_hp"] for part in self.parts)
        self.hp = self.max_hp

    def _update_boss_positions(self, dt):
        dist = math.hypot(self.x, self.y)
        if dist > 20:
            pull = 38 + self.level * 7
            self.vx -= (self.x / dist) * pull * dt
            self.vy -= (self.y / dist) * pull * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        left, right = -260, 260
        top, bottom = -170, 170
        if self.x < left:
            self.x = left
            self.vx = abs(self.vx) * 0.9
        elif self.x > right:
            self.x = right
            self.vx = -abs(self.vx) * 0.9

        if self.y < top:
            self.y = top
            self.vy = abs(self.vy) * 0.9
        elif self.y > bottom:
            self.y = bottom
            self.vy = -abs(self.vy) * 0.9

        if abs(self.x) < 30:
            self.vx += random.choice([-1, 1]) * 12 * dt
        if abs(self.y) < 30:
            self.vy += random.choice([-1, 1]) * 12 * dt

        self.vx = max(-160, min(160, self.vx))
        self.vy = max(-140, min(140, self.vy))

        orbit_speed = (0.85 + self.level * 0.22) * self.pattern["speed"]
        alive_parts = []
        for i, part in enumerate(self.parts):
            if not part.get("alive", True):
                continue
            angle = part["angle"] + (dt * orbit_speed * (1.25 + i * 0.15))
            part["angle"] = angle
            part["x"] = self.x + math.cos(angle) * part["radius"]
            part["y"] = self.y + math.sin(angle) * part["radius"]
            alive_parts.append(part)
        self.parts = alive_parts

    def _spawn_boss_projectiles(self):
        if self.level < 2:
            return

        level_scale = max(0, self.level - 2)
        alive_parts = max(1, sum(1 for part in self.parts if part.get("alive", True)))
        lost_parts = max(0, self.count - alive_parts)

        if self.attack_style == "burst":
            shots = max(2, 4 + level_scale * 2 - lost_parts)
            spread = math.tau / shots
            speed = 95 + self.level * 14
            for i in range(shots):
                angle = i * spread + random.uniform(-0.2, 0.2)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 2.1 + max(0, 5 - self.level) * 0.25,
                    "radius": 7,
                    "kind": "burst",
                })

        elif self.attack_style == "shards":
            shots = max(3, 6 + level_scale * 3 - lost_parts)
            speed = 100 + self.level * 18
            for i in range(shots):
                angle = (i / shots) * math.tau + random.uniform(-0.12, 0.12)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 2.4 + max(0, 5 - self.level) * 0.3,
                    "radius": 6,
                    "kind": "shards",
                })

        elif self.attack_style == "storm":
            shots = max(4, 8 + level_scale * 4 - lost_parts)
            speed = 105 + self.level * 20
            for i in range(shots):
                angle = random.uniform(0, math.tau)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 2.7 + max(0, 5 - self.level) * 0.35,
                    "radius": 7,
                    "kind": "storm",
                })

        else:  # pulse
            shots = max(3, 5 + level_scale * 2 - lost_parts)
            speed = 85 + self.level * 16
            for i in range(shots):
                angle = (i / shots) * math.tau + math.pi / 2
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 3.0 + max(0, 5 - self.level) * 0.35,
                    "radius": 9,
                    "kind": "pulse",
                })

        if self.level >= 6:
            extra = max(0, min(12, 2 + self.level - 6) - lost_parts)
            for _ in range(extra):
                angle = random.uniform(0, math.tau)
                speed = 120 + self.level * 25
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 2.5,
                    "radius": 6,
                    "kind": "homing",
                })

    def update(self, dt, drone_x, drone_y, crosshair_x, crosshair_y):
        self.flash_timer = max(0, self.flash_timer - dt)

        if self.is_boss:
            self._update_boss_positions(dt)
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self._spawn_boss_projectiles()
                self.attack_timer = max(0.8, 2.4 - self.level * 0.16)

            for projectile in self.projectiles[:]:
                if projectile.get("kind") == "homing":
                    dx = drone_x - projectile["x"]
                    dy = drone_y - projectile["y"]
                    dist = max(1.0, math.hypot(dx, dy))
                    steer = (90 + self.level * 18) * dt
                    projectile["vx"] += (dx / dist) * steer
                    projectile["vy"] += (dy / dist) * steer
                    speed = math.hypot(projectile["vx"], projectile["vy"])
                    max_speed = 160 + self.level * 10
                    if speed > max_speed:
                        projectile["vx"] = (projectile["vx"] / speed) * max_speed
                        projectile["vy"] = (projectile["vy"] / speed) * max_speed

                projectile["x"] += projectile["vx"] * dt
                projectile["y"] += projectile["vy"] * dt
                projectile["life"] -= dt
                if projectile["life"] <= 0:
                    self.projectiles.remove(projectile)

            # Keep boss projectiles inside arena bounds.
            for projectile in self.projectiles:
                if projectile["x"] < -520 or projectile["x"] > 520:
                    projectile["vx"] *= -1
                if projectile["y"] < -330 or projectile["y"] > 330:
                    projectile["vy"] *= -1
            return

        self.direction_timer -= dt
        self.dodge_timer -= dt

        self.ai_decision_timer -= dt
        if self.ai_decision_timer <= 0:
            self.ai.request_decision(
                self.level,
                self.x,
                self.y,
                drone_x,
                drone_y,
                self.vx,
                self.vy
            )
            self.ai_decision_timer = max(
                0.25,
                random.uniform(0.9, 1.6) - self.level * 0.08
            )

        direction, behaviour, _ = self.ai.get_direction()
        ai_x, ai_y = direction

        randomness = min(0.85, 0.08 + self.level * 0.09)

        random_angle = random.uniform(0, math.tau)
        random_x = math.cos(random_angle)
        random_y = math.sin(random_angle)

        move_x = ai_x * (1.0 - randomness) + random_x * randomness
        move_y = ai_y * (1.0 - randomness) + random_y * randomness

        move_length = math.hypot(move_x, move_y)
        if move_length < 0.01:
            move_x, move_y = random_x, random_y
        else:
            move_x /= move_length
            move_y /= move_length

        speed = self.base_speed * random.uniform(
            0.65,
            1.10 + self.level * 0.025
        )

        self.vx = move_x * speed
        self.vy = move_y * speed

        dx = self.x - crosshair_x
        dy = self.y - crosshair_y
        distance_to_crosshair = math.hypot(dx, dy)

        dodge_radius = 100 + self.level * 8
        if distance_to_crosshair < dodge_radius and self.dodge_timer <= 0:
            if random.random() < self.dodge_strength:
                angle = math.atan2(dy, dx) + random.choice([-1, 1]) * math.pi / 2
                speed = self.base_speed * (1.1 + self.level * 0.035)
                self.vx = math.cos(angle) * speed
                self.vy = math.sin(angle) * speed
                self.dodge_timer = max(0.18, 0.75 - self.level * 0.045)

        self.x += self.vx * dt
        self.y += self.vy * dt

        left, right = -480, 480
        top, bottom = -285, 285

        if self.x < left:
            self.x = left
            self.vx = abs(self.vx)
        elif self.x > right:
            self.x = right
            self.vx = -abs(self.vx)

        if self.y < top:
            self.y = top
            self.vy = abs(self.vy)
        elif self.y > bottom:
            self.y = bottom
            self.vy = -abs(self.vy)

        self.parts = [{"x": self.x, "y": self.y, "radius": 22}]

    def hit(self, damage, target_part=None):
        if self.is_boss:
            if target_part is not None:
                target_part["hp"] -= damage
                if target_part["hp"] <= 0:
                    target_part["alive"] = False
                    self.parts = [part for part in self.parts if part.get("alive", True)]
                else:
                    target_part["alive"] = True
                self.flash_timer = 0.15
            else:
                for part in self.parts:
                    if part["alive"]:
                        target_part = part
                        break
                if target_part is not None:
                    target_part["hp"] -= damage
                    if target_part["hp"] <= 0:
                        target_part["alive"] = False
                        self.parts = [part for part in self.parts if part.get("alive", True)]
                    else:
                        target_part["alive"] = True
                    self.flash_timer = 0.15

            self.hp = sum(part["hp"] for part in self.parts if part["alive"])
        else:
            self.hp -= damage
            self.flash_timer = 0.15

    def is_dead(self):
        if self.is_boss:
            return not any(part["alive"] for part in self.parts)
        return self.hp <= 0


# ------------------------------------------------------------
# Main game class
# ------------------------------------------------------------

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "menu"
        self.level = 1
        # Menu selection: 0 = Computer Mode, 1 = Drone and SpheroBolt Mode
        self.menu_selection = 0
        self.mode = "computer"

        self.drone_max_hp = 100
        self.drone_hp = 100

        self.sphero = None
        self.time_left = 120.0

        # Simulated first-person camera orientation.
        self.look_x = 0.0
        self.look_y = 0.0
        self.aim_x = 0.0
        self.aim_y = 0.0
        self.move_x = 0.0
        self.move_y = 0.0

        self.shoot_cooldown = 0.0
        self.message = ""
        self.message_timer = 0.0

        self.questions_correct = 0
        self.question_mistakes = 0
        self.pending_health_penalty = 0
        self.current_question = None
        self.question_pool = []
        self.selected_answer = None
        self.question_feedback = ""

        self.upgrades = []
        self.available_upgrades = []
        self.selected_upgrade = None

        # Weapons: unlocked list and currently equipped weapon name
        self.unlocked_weapons = [WEAPONS[0][0]]  # BASIC unlocked by default
        self.equipped_weapon = WEAPONS[0][0]

        self.shield_active = False
        self.ai_scan_timer = 0.0

        self.shot_flash = 0.0
        self.damage_flash = 0.0

        self.score = 0

    def start_level(self):
        if self.pending_health_penalty > 0:
            self.drone_max_hp = max(40, self.drone_max_hp - self.pending_health_penalty)
            self.drone_hp = self.drone_max_hp
            self.pending_health_penalty = 0

        self.state = "playing"
        self.sphero = Sphero(self.level)
        self.time_left = 120.0
        self.shoot_cooldown = 0
        if self.pending_health_penalty > 0:
            self.message = f"LEVEL {self.level} - PENALTY: -{self.pending_health_penalty} HP"
        else:
            self.message = f"LEVEL {self.level} - HUNT THE SPHERO"
        self.message_timer = 2.4
        self.selected_upgrade = None
        self.shield_active = "SHIELD" in self.upgrades
        self.ai_scan_timer = 0
        self.look_x = 0.0
        self.look_y = 0.0
        self.aim_x = 0.0
        self.aim_y = 0.0

        # Reset player health at each level, while preserving maximum health.
        self.drone_hp = self.drone_max_hp

        # Apply weapon-specific cooldown if needed (ensure cooldown not negative)
        # (no-op here, kept for future extensibility)

    def start_questions(self):
        self.state = "questions"
        self.questions_correct = 0
        self.question_mistakes = 0
        self.selected_answer = None
        self.question_feedback = ""
        self.question_pool = random.sample(QUESTIONS, len(QUESTIONS))
        self.current_question = 0

    def next_question(self):
        self.selected_answer = None
        self.question_feedback = ""

    def question_answer(self, answer_index):
        if self.selected_answer is not None:
            return

        question = self.question_pool[self.current_question]
        self.selected_answer = answer_index

        if answer_index == question["correct"]:
            self.questions_correct += 1
            self.question_feedback = "CORRECT!"
            if self.questions_correct >= 3:
                self.pending_health_penalty = self.question_mistakes * 10
                self.state = "upgrade"
                self.choose_upgrades()
        else:
            self.question_mistakes += 1
            self.question_feedback = "INCORRECT - TRY AGAIN"

    def choose_upgrades(self):
        # Show all upgrades not already owned. If many are owned, show a selection
        # of remaining upgrades.
        remaining = [u for u in UPGRADES if u[0] not in self.upgrades]
        random.shuffle(remaining)
        self.available_upgrades = remaining[:5]

    def select_upgrade(self, index):
        if not (0 <= index < len(self.available_upgrades)):
            return

        name, description = self.available_upgrades[index]
        self.selected_upgrade = name

        if name not in self.upgrades:
            self.upgrades.append(name)

        # Some upgrades unlock weapons
        if name == "DOUBLE SHOT":
            # DOUBLE_SHOT gives a shotgun-like weapon
            if "SHOTGUN" not in self.unlocked_weapons:
                self.unlocked_weapons.append("SHOTGUN")
        if name == "TARGET LOCK":
            # TARGET_LOCK unlocks PIERCING
            if "PIERCING" not in self.unlocked_weapons:
                self.unlocked_weapons.append("PIERCING")
        if name == "RAPID FIRE":
            # RAPID FIRE unlocks BASIC improvements but also SNIPER for variety
            if "SNIPER" not in self.unlocked_weapons:
                self.unlocked_weapons.append("SNIPER")

        if name == "HEALTH +25":
            self.drone_max_hp += 25
            self.drone_hp = self.drone_max_hp

        self.state = "between_levels"
        self.message = f"UPGRADE EQUIPPED: {name}"
        self.message_timer = 2.0
        # After selecting upgrade, allow player to equip weapon before next level
        self.state = "equip_weapon"

    def fire(self):
        if self.state != "playing":
            return

        if self.shoot_cooldown > 0:
            return

        # Determine weapon stats from equipped weapon
        weapon = next((w for w in WEAPONS if w[0] == self.equipped_weapon), None)
        if weapon is None:
            weapon = WEAPONS[0]

        wname, wstats = weapon

        # Apply upgrades that affect cooldown/aim
        rapid = "RAPID FIRE" in self.upgrades
        base_cd = wstats.get("cooldown", 0.45)
        self.shoot_cooldown = max(0.05, (base_cd * (0.6 if rapid else 1.0)))
        self.shot_flash = 0.08

        # Aim radius: weapon base, modified by TARGET LOCK
        aim_radius = wstats.get("aim_radius", 60)
        if "TARGET LOCK" in self.upgrades:
            aim_radius = max(aim_radius, 115)

        # The cursor is the actual aiming reticle, so shot checks are based on
        # the mouse position translated into arena/world coordinates.
        if self.sphero.is_boss:
            target_parts = [part for part in self.sphero.parts if part["alive"]]
            part_to_hit = None
            best_distance = None
            for part in target_parts:
                dist = math.hypot(part["x"] - self.aim_x, part["y"] - self.aim_y)
                if dist <= aim_radius and (best_distance is None or dist < best_distance):
                    best_distance = dist
                    part_to_hit = part

            hit = part_to_hit is not None
            if hit:
                hit_part = part_to_hit
        else:
            distance = math.hypot(
                self.sphero.x - self.aim_x,
                self.sphero.y - self.aim_y
            )
            hit = distance <= aim_radius
            hit_part = None

        if hit:
            # Resolve damage based on weapon type
            if wname == "SHOTGUN":
                pellets = wstats.get("pellets", 3)
                hits = 0
                for _ in range(pellets):
                    # shotgun pellets have independent chance to hit based on spread
                    spread_chance = 0.55 + 0.1 * (self.level - 1)
                    if random.random() < spread_chance:
                        hits += 1
                damage = hits * wstats.get("damage", 1)
            else:
                damage = wstats.get("damage", 1)

            # Double-shot upgrade doubles damage if not shotgun (avoid stacking weirdness)
            if "DOUBLE SHOT" in self.upgrades and wname != "SHOTGUN":
                damage *= 2

            self.sphero.hit(damage, target_part=hit_part)

            # Score modifications
            score_mult = 1
            if wname == "PIERCING":
                score_mult = 1.5

            self.score += int(100 * damage * score_mult)
            self.message = "DIRECT HIT!"
            self.message_timer = 0.45

            if self.sphero.is_dead():
                self.score += self.level * 500
                self.start_questions()
        else:
            self.message = "MISS"
            self.message_timer = 0.25

    def update(self, dt):
        self.message_timer = max(0, self.message_timer - dt)
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.shot_flash = max(0, self.shot_flash - dt)
        self.damage_flash = max(0, self.damage_flash - dt)
        self.ai_scan_timer = max(0, self.ai_scan_timer - dt)

        if self.state == "playing":
            self.time_left -= dt

            # Move simulated first-person camera/aim.
            speed = 230
            self.look_x += self.move_x * speed * dt
            self.look_y += self.move_y * speed * dt

            self.look_x = max(-500, min(500, self.look_x))
            self.look_y = max(-305, min(305, self.look_y))

            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.aim_x = self.look_x + (mouse_x - WIDTH // 2) / 0.65
            self.aim_y = self.look_y + (mouse_y - HEIGHT // 2) / 0.55
            self.aim_x = max(-500, min(500, self.aim_x))
            self.aim_y = max(-305, min(305, self.aim_y))

            self.sphero.update(
                dt,
                0,
                0,
                self.aim_x,
                self.aim_y
            )

            for projectile in self.sphero.projectiles[:]:
                px = projectile["x"]
                py = projectile["y"]
                if math.hypot(px - self.aim_x, py - self.aim_y) < 18:
                    damage = max(1, 4 + self.level // 2)
                    if self.shield_active:
                        damage = max(1, damage // 2)
                    self.drone_hp -= damage
                    self.damage_flash = 0.18
                    self.sphero.projectiles.remove(projectile)
                    if self.drone_hp <= 0:
                        self.state = "game_over"
                        break

            # The Sphero can "attack" if it gets close to the cursor aim point.
            distance = math.hypot(self.sphero.x - self.aim_x,
                                  self.sphero.y - self.aim_y)

            attack_distance = 65 + self.level * 4
            if distance < attack_distance and random.random() < dt * (0.45 + self.level * 0.07):
                damage = max(1, 4 + self.level // 2)
                if self.shield_active:
                    damage = max(1, damage // 2)

                self.drone_hp -= damage
                self.damage_flash = 0.18

                if self.drone_hp <= 0:
                    self.state = "game_over"

            if self.time_left <= 0:
                self.time_left = 0
                self.state = "level_failed"

    def draw_background(self):
        # Fake first-person drone camera / arena.
        screen.fill((10, 16, 24))

        # Horizon.
        horizon = HEIGHT // 2 - 40
        pygame.draw.rect(screen, (19, 29, 38), (0, 0, WIDTH, horizon))
        pygame.draw.rect(screen, (28, 34, 35), (0, horizon, WIDTH, HEIGHT - horizon))

        # Perspective floor lines.
        centre_x = WIDTH // 2
        floor_y = horizon

        for offset in range(-700, 701, 100):
            pygame.draw.line(
                screen,
                (55, 62, 65),
                (centre_x, floor_y),
                (centre_x + offset, HEIGHT),
                1,
            )

        for y in [horizon + 40, horizon + 80, horizon + 130,
                  horizon + 195, horizon + 275]:
            pygame.draw.line(
                screen,
                (50, 57, 60),
                (0, y),
                (WIDTH, y),
                1,
            )

        # Arena side structures.
        pygame.draw.line(screen, (80, 90, 95), (70, horizon), (0, HEIGHT), 3)
        pygame.draw.line(screen, (80, 90, 95), (WIDTH - 70, horizon),
                         (WIDTH, HEIGHT), 3)

    def project_sphero(self):
        # Convert world difference from aim direction to screen position.
        dx = self.sphero.x - self.look_x
        dy = self.sphero.y - self.look_y

        # Scale into a first-person-ish display.
        sx = WIDTH // 2 + int(dx * 0.65)
        sy = HEIGHT // 2 + int(dy * 0.55)

        distance = max(40, math.hypot(dx, dy))
        radius = int(max(10, min(65, 19000 / distance)))

        return sx, sy, radius

    def draw_sphero(self):
        if self.sphero.is_boss:
            for part in self.sphero.parts:
                dx = part["x"] - self.look_x
                dy = part["y"] - self.look_y
                sx = WIDTH // 2 + int(dx * 0.65)
                sy = HEIGHT // 2 + int(dy * 0.55)
                radius = int(max(12, min(34, 19000 / max(40, math.hypot(dx, dy)))))

                if -150 < sx < WIDTH + 150 and -150 < sy < HEIGHT + 150:
                    if self.ai_scan_timer > 0:
                        pygame.draw.circle(screen, CYAN, (sx, sy), radius + 14, 4)

                    body_colour = RED if self.sphero.flash_timer <= 0 else WHITE
                    pygame.draw.circle(screen, (15, 15, 18), (sx + 4, sy + 5), radius + 2)
                    pygame.draw.circle(screen, body_colour, (sx, sy), radius)

            for projectile in self.sphero.projectiles:
                px = WIDTH // 2 + int((projectile["x"] - self.look_x) * 0.65)
                py = HEIGHT // 2 + int((projectile["y"] - self.look_y) * 0.55)
                if -80 < px < WIDTH + 80 and -80 < py < HEIGHT + 80:
                    kind = projectile.get("kind", "burst")
                    if kind == "homing":
                        colour = PURPLE
                        accent = CYAN
                    elif kind == "storm":
                        colour = CYAN
                        accent = BLUE
                    elif kind == "shards":
                        colour = YELLOW
                        accent = ORANGE
                    elif kind == "pulse":
                        colour = RED
                        accent = WHITE
                    else:
                        colour = ORANGE
                        accent = YELLOW
                    pygame.draw.circle(screen, colour, (px, py), projectile["radius"])
                    pygame.draw.circle(screen, accent, (px, py), max(2, projectile["radius"] // 2))

            draw_text(self.sphero.boss_name, SMALL, WHITE, WIDTH // 2, HEIGHT // 2 - 120, center=True)
            return

        sx, sy, radius = self.project_sphero()

        if -100 < sx < WIDTH + 100 and -100 < sy < HEIGHT + 100:
            if self.ai_scan_timer > 0:
                pygame.draw.circle(screen, CYAN, (sx, sy), radius + 18, 4)

            body_colour = RED if self.sphero.flash_timer <= 0 else WHITE

            pygame.draw.circle(screen, (15, 15, 18), (sx + 5, sy + 7), radius + 3)
            pygame.draw.circle(screen, body_colour, (sx, sy), radius)

            pygame.draw.arc(
                screen,
                CYAN,
                (sx - radius, sy - radius, radius * 2, radius * 2),
                0.2,
                math.pi * 1.3,
                max(2, radius // 7),
            )

            draw_text("SPHERO BOLT", SMALL, WHITE,
                      sx, sy - radius - 25, center=True)

    def draw_crosshair(self):
        cx, cy = pygame.mouse.get_pos()

        colour = GREEN
        if self.shot_flash > 0:
            colour = YELLOW

        size = 14
        gap = 7

        pygame.draw.line(screen, colour, (cx - size, cy), (cx - gap, cy), 3)
        pygame.draw.line(screen, colour, (cx + gap, cy), (cx + size, cy), 3)
        pygame.draw.line(screen, colour, (cx, cy - size), (cx, cy - gap), 3)
        pygame.draw.line(screen, colour, (cx, cy + gap), (cx, cy + size), 3)
        pygame.draw.circle(screen, colour, (cx, cy), 3)

    def draw_hud(self):
        # Top HUD.
        pygame.draw.rect(screen, (8, 12, 18), (0, 0, WIDTH, 75))
        pygame.draw.line(screen, GREY, (0, 74), (WIDTH, 74), 2)

        draw_text(f"LEVEL {self.level}", FONT, WHITE, 25, 18)

        mins = int(self.time_left) // 60
        secs = int(self.time_left) % 60
        timer_colour = RED if self.time_left <= 20 else WHITE
        draw_text(f"TIME {mins:02d}:{secs:02d}", FONT, timer_colour, 165, 18)

        draw_text(f"SCORE {self.score}", FONT, YELLOW, 350, 18)

        upgrade_text = ", ".join(self.upgrades) if self.upgrades else "NONE"
        draw_text("UPGRADES:", SMALL, WHITE, 590, 10)
        draw_text(upgrade_text[:48], SMALL, CYAN, 590, 38)
        # Weapon HUD
        draw_text("WEAPON:", SMALL, WHITE, 880, 10)
        draw_text(self.equipped_weapon, SMALL, ORANGE, 880, 38)

        # Bottom HUD.
        panel_y = HEIGHT - 105
        pygame.draw.rect(screen, (8, 12, 18), (0, panel_y, WIDTH, 105))
        pygame.draw.line(screen, GREY, (0, panel_y), (WIDTH, panel_y), 2)

        draw_bar(
            25, panel_y + 18, 270, 28,
            self.drone_hp, self.drone_max_hp,
            GREEN if self.drone_hp > self.drone_max_hp * 0.3 else RED,
            "DRONE HP",
        )

        draw_bar(
            320, panel_y + 18, 270, 28,
            self.sphero.hp, self.sphero.max_hp,
            RED, "SPHERO HP",
        )

        if self.sphero.is_boss:
            alive_parts = sum(1 for part in self.sphero.parts if part["alive"])
            draw_text(f"ENEMY: {self.sphero.boss_name}", SMALL, YELLOW, 610, panel_y + 15)
            draw_text(f"PARTS: {alive_parts}/{len(self.sphero.parts)}", SMALL, CYAN, 610, panel_y + 35)

        draw_text("WASD / ARROWS = MOVE/AIM", SMALL, WHITE, 25, panel_y + 62)
        draw_text("SPACE / LEFT CLICK = SHOOT", SMALL, WHITE, 300, panel_y + 62)

        status = "SHIELD ACTIVE" if self.shield_active else "SHIELD INACTIVE"
        draw_text(status, SMALL, CYAN if self.shield_active else GREY,
                  700, panel_y + 62)

        if self.ai_scan_timer > 0:
            draw_text("AI SCAN ACTIVE", SMALL, CYAN, 850, panel_y + 20)

        if self.sphero is not None:
            if self.sphero.is_boss:
                status = f"BOSS MODE: {self.sphero.attack_style.upper()}"
            else:
                _, ai_behaviour, ai_error = self.sphero.ai.get_direction()
                status = f"OLLAMA: {ai_behaviour}"
                if ai_error:
                    status = "OLLAMA: FALLBACK RANDOM"
            draw_text(status, SMALL, PURPLE, 700, panel_y + 82)

    def draw_message(self):
        if self.message_timer > 0 and self.message:
            draw_text(self.message, BIG, YELLOW,
                      WIDTH // 2, 105, center=True)

    def draw_menu(self):
        screen.fill(BLACK)

        draw_text("DRONE VS SPHERO", TITLE, CYAN, WIDTH // 2, 125, center=True)
        draw_text("CYBERSECURITY TRAINING PROTOTYPE", FONT, WHITE, WIDTH // 2, 185, center=True)

        box = pygame.Rect(180, 220, WIDTH - 360, 390)
        pygame.draw.rect(screen, DARK_GREY, box, border_radius=15)
        pygame.draw.rect(screen, CYAN, box, 2, border_radius=15)

        # Title inside the box
        title_y = box.y + 35
        draw_text("MISSION", BIG, YELLOW, WIDTH // 2, title_y, center=True)

        # Define mode options and compute layout to avoid overlap
        opts = [
            ("1. Computer Mode", "Regular base game (mouse + keyboard)"),
            ("2. Drone and SpheroBolt Mode", "Placeholder for real-world drone + Sphero integration")
        ]

        opt_h = 82
        spacing = 18
        total_h = len(opts) * opt_h + (len(opts) - 1) * spacing
        opt_y = box.y + 205

        # Mission text area between title and options with enough vertical room
        mission_top = title_y + 48
        mission_bottom = opt_y - 18
        mission_h = max(96, mission_bottom - mission_top)

        mission = (
            "Use the drone to find and hit the AI-controlled Sphero BOLT. "
            "Destroy it before the 2-minute timer ends. "
            "After each victory, answer 3 cybersecurity questions correctly "
            "to unlock an upgrade for the next level."
        )

        draw_wrapped_text(mission, FONT, WHITE, pygame.Rect(220, mission_top, WIDTH - 440, mission_h), 7)

        # Render options
        self._menu_option_rects = []
        for i, (title, desc) in enumerate(opts):
            w = 720
            h = opt_h
            x = WIDTH // 2 - w // 2
            y = opt_y + i * (h + spacing)
            rect = pygame.Rect(x, y, w, h)
            self._menu_option_rects.append((rect, i))

            # Drop shadow
            shadow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 100), (4, 4, w, h), border_radius=14)
            screen.blit(shadow, (x - 4, y - 4))

            # Background gradient (subtle)
            bg = pygame.Surface((w, h))
            top_col = (28, 34, 40)
            bot_col = (22, 26, 30)
            for row in range(h):
                t = row / max(1, h - 1)
                col = (
                    int(top_col[0] * (1 - t) + bot_col[0] * t),
                    int(top_col[1] * (1 - t) + bot_col[1] * t),
                    int(top_col[2] * (1 - t) + bot_col[2] * t),
                )
                pygame.draw.line(bg, col, (0, row), (w, row))

            mouse_over = getattr(self, "_menu_hover_index", None) == i
            if i == self.menu_selection or mouse_over:
                pygame.draw.rect(bg, (38, 56, 40), (0, 0, w, h), border_radius=14)
                screen.blit(bg, (x, y))
                border_col = GREEN if i == self.menu_selection else CYAN
                pygame.draw.rect(screen, border_col, rect, 4, border_radius=14)
            else:
                pygame.draw.rect(bg, (26, 32, 38), (0, 0, w, h), border_radius=14)
                screen.blit(bg, (x, y))
                pygame.draw.rect(screen, (45, 70, 90), rect, 2, border_radius=14)

            # Icon and texts
            icon_r = 28
            icon_cx = rect.x + 56
            icon_cy = rect.y + h // 2
            pygame.draw.circle(screen, (18, 24, 28), (icon_cx + 3, icon_cy + 3), icon_r + 3)
            pygame.draw.circle(screen, CYAN if i == self.menu_selection else GREY, (icon_cx, icon_cy), icon_r)
            draw_text("C" if i == 0 else "D", BIG, (8, 12, 18), icon_cx, icon_cy, center=True)

            draw_text(title, FONT, WHITE if (i == self.menu_selection or mouse_over) else (200, 210, 215), rect.x + 110, rect.y + 14)
            draw_text(desc, SMALL, (170, 178, 186), rect.x + 110, rect.y + 44)

        # Instructions below the mission box
        instr_y = box.y + box.height + 18
        draw_text("Press ENTER to start the selected mode", FONT, GREEN, WIDTH // 2, instr_y, center=True)
        draw_text("ESC = Quit | Use ARROW KEYS or 1-2 to select", SMALL, GREY, WIDTH // 2, instr_y + 30, center=True)

        # Show the current mouse aim as a visible reticle on the menu screen.
        self.draw_crosshair()

    def draw_questions(self):
        screen.fill((9, 14, 22))

        draw_text("CYBERSECURITY CHALLENGE", TITLE, CYAN,
                  WIDTH // 2, 65, center=True)
        draw_text(
            f"Correct answers: {self.questions_correct}/3",
            FONT,
            GREEN,
            WIDTH // 2,
            125,
            center=True,
        )

        q = self.question_pool[self.current_question]

        panel = pygame.Rect(100, 165, WIDTH - 200, 410)
        pygame.draw.rect(screen, DARK_GREY, panel, border_radius=15)
        pygame.draw.rect(screen, CYAN, panel, 2, border_radius=15)

        draw_wrapped_text(
            q["question"],
            BIG,
            WHITE,
            pygame.Rect(140, 200, WIDTH - 280, 90),
            8,
        )

        y = 300
        answer_rects = []

        for i, answer in enumerate(q["answers"]):
            rect = pygame.Rect(145, y, WIDTH - 290, 55)
            answer_rects.append(rect)

            colour = (50, 60, 72)
            border = GREY

            if self.selected_answer is not None:
                if i == q["correct"]:
                    colour = (30, 110, 65)
                    border = GREEN
                elif i == self.selected_answer:
                    colour = (130, 45, 45)
                    border = RED

            pygame.draw.rect(screen, colour, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            draw_text(answer, SMALL, WHITE, rect.x + 15, rect.y + 17)

            y += 65

        if self.question_feedback:
            feedback_colour = GREEN if self.questions_correct and self.selected_answer == q["correct"] else RED
            draw_text(
                self.question_feedback,
                FONT,
                feedback_colour,
                WIDTH // 2,
                605,
                center=True,
            )

            if self.selected_answer is not None:
                if self.selected_answer == q["correct"]:
                    if self.questions_correct < 3:
                        draw_text(
                            "Press ENTER for the next question",
                            SMALL,
                            WHITE,
                            WIDTH // 2,
                            640,
                            center=True,
                        )
                else:
                    draw_text(
                        "Press ENTER to try the question again",
                        SMALL,
                        WHITE,
                        WIDTH // 2,
                        640,
                        center=True,
                    )

        return answer_rects

    def equip_weapon_choice(self, index):
        # Equip by index in WEAPONS if owned
        if not (0 <= index < len(WEAPONS)):
            return
        name = WEAPONS[index][0]
        if name in self.unlocked_weapons:
            self.equipped_weapon = name
            self.message = f"EQUIPPED: {name}"
            self.message_timer = 1.4

    def draw_upgrade(self):
        screen.fill((10, 12, 20))

        penalty_text = ""
        if self.pending_health_penalty > 0:
            penalty_text = f"NEXT LEVEL PENALTY: -{self.pending_health_penalty} HP (10 HP per wrong answer)"

        draw_text("UPGRADE UNLOCKED", TITLE, YELLOW,
                  WIDTH // 2, 70, center=True)
        draw_text(
            "You answered 3 cybersecurity questions correctly.",
            FONT,
            WHITE,
            WIDTH // 2,
            135,
            center=True,
        )
        if penalty_text:
            draw_text(
                penalty_text,
                FONT,
                RED,
                WIDTH // 2,
                175,
                center=True,
            )
        draw_text(
            "Choose ONE upgrade for the next level:",
            FONT,
            CYAN,
            WIDTH // 2,
            210,
            center=True,
        )

        y = 245
        for i, (name, description) in enumerate(self.available_upgrades):
            rect = pygame.Rect(120, y, WIDTH - 240, 68)
            pygame.draw.rect(screen, DARK_GREY, rect, border_radius=10)
            pygame.draw.rect(screen, CYAN, rect, 2, border_radius=10)

            draw_text(f"{i + 1}", BIG, YELLOW, rect.x + 25, rect.y + 10)
            draw_text(name, FONT, WHITE, rect.x + 80, rect.y + 8)
            draw_text(description, SMALL, GREY, rect.x + 80, rect.y + 38)

            y += 78

        draw_text("Press 1-5 to choose", FONT, GREEN,
                  WIDTH // 2, 635, center=True)

    def draw_equip_screen(self):
        screen.fill((8, 10, 14))
        draw_text("EQUIP WEAPON", TITLE, CYAN, WIDTH // 2, 70, center=True)
        draw_text("Choose a weapon to equip for the next level:", FONT, WHITE, WIDTH // 2, 130, center=True)
        draw_text("LOCKED WEAPONS CANNOT BE USED UNTIL YOU UNLOCK THEM THROUGH UPGRADES.", SMALL, RED, WIDTH // 2, 160, center=True)

        y = 190
        for i, (name, stats) in enumerate(WEAPONS):
            owned = name in self.unlocked_weapons
            rect = pygame.Rect(140, y, WIDTH - 280, 68)
            pygame.draw.rect(screen, DARK_GREY if owned else (35, 35, 40), rect, border_radius=10)
            pygame.draw.rect(screen, CYAN if owned else GREY, rect, 2, border_radius=10)

            draw_text(f"{i + 1}", BIG, YELLOW, rect.x + 25, rect.y + 10)
            draw_text(name, FONT, WHITE if owned else GREY, rect.x + 80, rect.y + 8)
            draw_text(stats.get("desc", ""), SMALL, GREY, rect.x + 80, rect.y + 38)

            if owned:
                if name == self.equipped_weapon:
                    draw_text("EQUIPPED", SMALL, GREEN, rect.right - 120, rect.y + 22)
            else:
                draw_text("LOCKED", SMALL, RED, rect.right - 120, rect.y + 22)

            y += 78

        draw_text("Press 1-4 to equip unlocked weapons, ENTER to confirm, or ESC to skip", SMALL, GREY, WIDTH // 2, 620, center=True)
        # Build clickable rects so the main loop can handle mouse selection
        self._equip_option_rects = []
        y = 190
        for i, (name, stats) in enumerate(WEAPONS):
            rect = pygame.Rect(140, y, WIDTH - 280, 68)
            self._equip_option_rects.append((rect, i))
            y += 78

    def draw_between_levels(self):
        screen.fill(BLACK)

        if self.level >= 8:
            draw_text("MISSION COMPLETE", TITLE, GREEN,
                      WIDTH // 2, 145, center=True)
            draw_text("You defeated the Sphero BOLT.", BIG, WHITE,
                      WIDTH // 2, 230, center=True)
            draw_text(f"Final score: {self.score}", FONT, YELLOW,
                      WIDTH // 2, 290, center=True)
            draw_text("Press ENTER to return to the menu.", FONT, CYAN,
                      WIDTH // 2, 390, center=True)
            return

        draw_text(f"LEVEL {self.level} COMPLETE!", TITLE, GREEN,
                  WIDTH // 2, 130, center=True)

        if self.selected_upgrade:
            draw_text(
                f"Upgrade: {self.selected_upgrade}",
                BIG,
                CYAN,
                WIDTH // 2,
                220,
                center=True,
            )

        draw_text(
            f"Next: LEVEL {self.level + 1}",
            FONT,
            WHITE,
            WIDTH // 2,
            300,
            center=True,
        )
        draw_text(
            "The next boss may come as a dual orb, triad, quad core, or a barrage boss with extra health and screen hazards.",
            FONT,
            GREY,
            WIDTH // 2,
            345,
            center=True,
        )
        draw_text(
            "Press ENTER to start the next level.",
            FONT,
            GREEN,
            WIDTH // 2,
            440,
            center=True,
        )

        # Show equip UI instructions
        if self.unlocked_weapons:
            draw_text("Press TAB to equip weapon between levels", SMALL, GREY, WIDTH // 2, 490, center=True)

    def draw_failed(self):
        screen.fill((25, 8, 10))
        draw_text("TIME UP", TITLE, RED,
                  WIDTH // 2, 145, center=True)
        draw_text(
            f"You did not destroy the Sphero on Level {self.level}.",
            BIG,
            WHITE,
            WIDTH // 2,
            230,
            center=True,
        )
        draw_text(
            "Press ENTER to retry this level.",
            FONT,
            YELLOW,
            WIDTH // 2,
            335,
            center=True,
        )
        draw_text(
            "Press ESC to return to the menu.",
            SMALL,
            GREY,
            WIDTH // 2,
            380,
            center=True,
        )

    def draw_game_over(self):
        screen.fill((25, 8, 10))
        draw_text("DRONE DESTROYED", TITLE, RED,
                  WIDTH // 2, 145, center=True)
        draw_text(
            f"Level {self.level} failed.",
            BIG,
            WHITE,
            WIDTH // 2,
            230,
            center=True,
        )
        draw_text(
            "Press ENTER to retry this level.",
            FONT,
            YELLOW,
            WIDTH // 2,
            335,
            center=True,
        )
        draw_text(
            "Press ESC to return to the menu.",
            SMALL,
            GREY,
            WIDTH // 2,
            380,
            center=True,
        )

    def draw(self):
        if self.state == "menu":
            self.draw_menu()

        elif self.state == "drone_placeholder":
            # Simple placeholder screen for the unimplemented mode
            screen.fill((6, 10, 14))
            draw_text("DRONE & SPHEROBOLT MODE", TITLE, CYAN, WIDTH // 2, 140, center=True)
            draw_text("This mode will integrate real drones and Sphero BOLT hardware.", FONT, WHITE, WIDTH // 2, 220, center=True)
            draw_text("(Placeholder) Press ESC to return to menu or ENTER to go back to Computer Mode.", SMALL, GREY, WIDTH // 2, 300, center=True)

        elif self.state == "playing":
            self.draw_background()
            self.draw_sphero()
            self.draw_crosshair()
            self.draw_hud()
            self.draw_message()

            if self.damage_flash > 0:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 55))
                screen.blit(overlay, (0, 0))

        elif self.state == "questions":
            self.draw_questions()

        elif self.state == "upgrade":
            self.draw_upgrade()

        elif self.state == "between_levels":
            self.draw_between_levels()
        elif self.state == "equip_weapon":
            self.draw_equip_screen()

        elif self.state == "level_failed":
            self.draw_failed()

        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()


# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

game = Game()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    dt = min(dt, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game.state in ("level_failed", "game_over"):
                    game.state = "menu"
                else:
                    running = False

            elif game.state == "menu":
                # Navigate menu
                if event.key in (pygame.K_UP, pygame.K_w):
                    game.menu_selection = max(0, game.menu_selection - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    game.menu_selection = min(1, game.menu_selection + 1)
                elif event.key == pygame.K_1:
                    game.menu_selection = 0
                elif event.key == pygame.K_2:
                    game.menu_selection = 1
                elif event.key == pygame.K_RETURN:
                    # Start the selected mode
                    if game.menu_selection == 0:
                        game.mode = "computer"
                        game.level = 1
                        game.upgrades = []
                        game.drone_max_hp = 100
                        game.score = 0
                        game.start_level()
                    else:
                        game.mode = "drone_sphero"
                        game.state = "drone_placeholder"
                        game.message = "DRONE & SPHERO BOLT MODE (PLACEHOLDER)"
                        game.message_timer = 3.0

            elif game.state == "playing":
                if event.key == pygame.K_SPACE:
                    game.fire()

            elif game.state == "questions":
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    game.question_answer(event.key - pygame.K_1)

                elif event.key == pygame.K_RETURN:
                    if game.selected_answer is not None:
                        q = game.question_pool[game.current_question]

                        if game.selected_answer == q["correct"]:
                            if game.questions_correct < 3:
                                game.current_question += 1
                                game.next_question()
                        else:
                            game.next_question()

            elif game.state == "upgrade":
                if pygame.K_1 <= event.key <= pygame.K_5:
                    game.select_upgrade(event.key - pygame.K_1)

            elif game.state == "between_levels":
                if event.key == pygame.K_RETURN:
                    game.level += 1
                    game.start_level()
                elif event.key == pygame.K_TAB:
                    game.state = "equip_weapon"

            elif game.state == "equip_weapon":
                # Number keys equip, ENTER confirms (returns to between_levels), ESC cancels
                if pygame.K_1 <= event.key <= pygame.K_4:
                    idx = event.key - pygame.K_1
                    # give feedback if weapon locked
                    name = WEAPONS[idx][0] if 0 <= idx < len(WEAPONS) else None
                    if name and name in game.unlocked_weapons:
                        game.equip_weapon_choice(idx)
                    else:
                        game.message = "WEAPON LOCKED"
                        game.message_timer = 1.1
                elif event.key == pygame.K_RETURN:
                    game.state = "between_levels"
                elif event.key == pygame.K_ESCAPE:
                    game.state = "between_levels"

            elif game.state in ("level_failed", "game_over"):
                if event.key == pygame.K_RETURN:
                    game.start_level()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game.state == "playing":
                    game.fire()
                elif game.state == "equip_weapon":
                    if hasattr(game, "_equip_option_rects"):
                        mx, my = event.pos
                        for rect, idx in game._equip_option_rects:
                            if rect.collidepoint(mx, my):
                                game.equip_weapon_choice(idx)
                                break
                elif game.state == "menu":
                    # Allow clicking menu options
                    if hasattr(game, "_menu_option_rects"):
                        mx, my = event.pos
                        for rect, idx in game._menu_option_rects:
                            if rect.collidepoint(mx, my):
                                game.menu_selection = idx
                                # emulate Enter
                                if idx == 0:
                                    game.mode = "computer"
                                    game.level = 1
                                    game.upgrades = []
                                    game.drone_max_hp = 100
                                    game.score = 0
                                    game.start_level()
                                else:
                                    game.mode = "drone_sphero"
                                    game.state = "drone_placeholder"
                                    game.message = "DRONE & SPHERO BOLT MODE (PLACEHOLDER)"
                                    game.message_timer = 3.0
                                break

        elif event.type == pygame.MOUSEMOTION:
            if game.state == "playing":
                # Mouse movement changes the simulated camera aim.
                mx, my = event.rel
                game.look_x += mx * 1.4
                game.look_y += my * 1.1
                game.look_x = max(-500, min(500, game.look_x))
                game.look_y = max(-305, min(305, game.look_y))
            elif game.state == "menu":
                # Update hover index for menu options
                if hasattr(game, "_menu_option_rects"):
                    mx, my = event.pos
                    hover = None
                    for rect, idx in game._menu_option_rects:
                        if rect.collidepoint(mx, my):
                            hover = idx
                            break
                    game._menu_hover_index = hover

    # Continuous keyboard movement.
    keys = pygame.key.get_pressed()

    if game.state == "playing":
        game.move_x = 0
        game.move_y = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            game.move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            game.move_x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            game.move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            game.move_y += 1

        # AI Scan can be activated with Q for prototype testing.
        if keys[pygame.K_q] and "AI SCAN" in game.upgrades:
            game.ai_scan_timer = 2.5

    game.update(dt)
    game.draw()

pygame.quit()
sys.exit()
