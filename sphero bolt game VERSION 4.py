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
import importlib
import time

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
                result = None
                inner = None
                answer = {}

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


class RealSpheroBoltController:
    """Optional adapter for controlling a real Sphero BOLT using the same AI decisions.

    This stays completely opt-in. If the real device is not present, or the SDK is not
    installed, the game continues to behave exactly as before.
    """

    def __init__(self, enabled=False, bolt_name=None):
        self.enabled = bool(enabled)
        self.bolt_name = bolt_name or os.environ.get("REAL_SPHERO_NAME", "Sphero Bolt")
        self.device = None
        self.connected = False
        self.last_error = ""
        self.last_heading = 0
        self.last_speed = 0
        self.last_updated = 0.0

    def connect(self):
        if not self.enabled:
            return False

        if self.connected and self.device is not None:
            return True

        try:
            sdk = None
            for module_name in ("sphero_sdk", "sphero", "spherov2", "spheroedu"):
                try:
                    sdk = importlib.import_module(module_name)
                    break
                except Exception:
                    continue

            if sdk is None:
                self.last_error = "No Sphero SDK found. Install the Sphero Python library on the Raspberry Pi."
                return False

            device_factory = None
            for attr in ("SpheroBolt", "Sphero", "SpheroEduAPI", "SpheroDevice"):
                candidate = getattr(sdk, attr, None)
                if candidate is not None:
                    device_factory = candidate
                    break

            if device_factory is None:
                self.last_error = "Sphero Python SDK is installed, but no supported device class was found."
                return False

            self.device = device_factory()

            connect_fn = getattr(self.device, "connect", None) or getattr(self.device, "open", None)
            if connect_fn is None:
                self.last_error = "Connected Sphero object does not expose a connect/open method."
                return False

            connect_fn()
            self.connected = True
            self.last_error = ""
            return True

        except Exception as exc:
            self.connected = False
            self.last_error = str(exc)
            print(f"REAL SPHERO connect error: {exc}")
            return False

    def _drive(self, speed_percent, heading_deg):
        if self.device is None:
            return False

        heading_deg = int(max(0, min(359, heading_deg)))
        speed_percent = int(max(0, min(100, speed_percent)))

        try:
            drive_with_heading = getattr(self.device, "drive_with_heading", None)
            if callable(drive_with_heading):
                drive_with_heading(speed_percent, heading_deg, 0)
                self.last_heading = heading_deg
                self.last_speed = speed_percent
                return True

            drive = getattr(self.device, "drive", None)
            if callable(drive):
                drive(speed_percent, heading_deg)
                self.last_heading = heading_deg
                self.last_speed = speed_percent
                return True

            set_speed = getattr(self.device, "set_speed", None)
            set_heading = getattr(self.device, "set_heading", None)
            if callable(set_speed) and callable(set_heading):
                set_heading(heading_deg)
                set_speed(speed_percent)
                self.last_heading = heading_deg
                self.last_speed = speed_percent
                return True

            self.last_error = "Sphero SDK object does not expose a compatible drive method."
            return False

        except Exception as exc:
            self.last_error = str(exc)
            print(f"REAL SPHERO drive error: {exc}")
            return False

    def apply_move(self, move_x, move_y, level, behaviour="RANDOM"):
        if not self.enabled:
            return False

        if not self.connected:
            if not self.connect():
                return False

        magnitude = math.hypot(move_x, move_y)
        if magnitude < 0.01:
            move_x, move_y = 1.0, 0.0
            magnitude = 1.0

        move_x /= magnitude
        move_y /= magnitude

        heading = math.degrees(math.atan2(move_y, move_x))
        if heading < 0:
            heading += 360.0

        randomness = 0.12 + level * 0.06
        if behaviour in {"RANDOM", "CHASE", "EVADE"}:
            randomness += 0.08

        if random.random() < randomness:
            angle_jitter = random.uniform(-30, 30)
            heading += angle_jitter
            if heading < 0:
                heading += 360.0
            elif heading >= 360.0:
                heading -= 360.0

        base_speed = 18 + level * 4
        if behaviour == "EVADE":
            base_speed += 12
        elif behaviour == "CHASE":
            base_speed += 8
        elif behaviour == "RANDOM":
            base_speed += 6

        speed_percent = max(15, min(100, int(base_speed + random.uniform(-5, 10))))

        self.last_updated = time.monotonic()
        return self._drive(speed_percent, heading)


class OllamaDroneAI:
    def __init__(self):
        self.lock = threading.Lock()
        self.request_in_progress = False
        self.last_error = ""
        self.move_x = 0.0
        self.move_y = 0.0
        self.aim_x = 0.0
        self.aim_y = 0.0
        self.shoot = False
        self.scan = False
        self.next_decision = 0.0
        self.mock = os.environ.get("MOCK_OLLAMA", "0") == "1"
        self.ollama_url = os.environ.get("OLLAMA_URL", OLLAMA_URL)
        self.ollama_model = os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL)
        self.ollama_cli = shutil.which("ollama")
        if not self.ollama_cli:
            possible = os.path.expandvars(r"%LocalAppData%\Programs\Ollama\ollama.exe")
            if os.path.exists(possible):
                self.ollama_cli = possible

    def request_decision(self, level, sphero_x, sphero_y, drone_x, drone_y,
                         time_left, hp, max_hp, aim_x, aim_y):
        with self.lock:
            if self.request_in_progress:
                return
            self.request_in_progress = True

        prompt = f"""
You are the drone pilot AI for a game called Drone vs Sphero.
You control the drone fighter and must destroy the Sphero BOLT.

Current level: {level}
Time left: {time_left:.1f}s
Drone HP: {hp:.0f}/{max_hp:.0f}
Sphero position: ({sphero_x:.0f}, {sphero_y:.0f})
Drone position: ({drone_x:.0f}, {drone_y:.0f})
Current aim target: ({aim_x:.0f}, {aim_y:.0f})

Return ONLY valid JSON in this exact format:
{{"move_x":0.0,"move_y":0.0,"aim_x":0.0,"aim_y":0.0,"shoot":false,"scan":false}}

Rules:
- move_x and move_y must be between -1 and 1.
- aim_x and aim_y are relative offsets from the drone centre in the arena.
- shoot should be true when the Sphero is in line of sight and close enough.
- scan should be true if the Sphero is hidden or if you need to reveal it.
- Prefer repositioning to a safe flank while keeping the aim on the Sphero.
Do not include markdown or explanations.
"""

        def worker():
            try:
                if self.mock:
                    dx = sphero_x - drone_x
                    dy = sphero_y - drone_y
                    dist = math.hypot(dx, dy) or 1.0
                    move_x = max(-1.0, min(1.0, dx / (dist * 1.8)))
                    move_y = max(-1.0, min(1.0, dy / (dist * 1.8)))
                    shoot = dist < 200
                    scan = dist > 260 and time_left < 80
                    with self.lock:
                        self.move_x = move_x
                        self.move_y = move_y
                        self.aim_x = dx * 0.35
                        self.aim_y = dy * 0.35
                        self.shoot = shoot
                        self.scan = scan
                        self.last_error = "(mock)"
                    return

                answer = {}
                if self.ollama_cli:
                    try:
                        proc = subprocess.run(
                            [self.ollama_cli, "run", self.ollama_model, "--format", "json", "--nowordwrap", prompt],
                            capture_output=True,
                            text=True,
                            timeout=6,
                        )
                        raw = proc.stdout.strip()
                        if raw:
                            try:
                                answer = json.loads(raw)
                            except Exception:
                                import re
                                m = re.search(r"\{.*\}", raw, re.DOTALL)
                                if m:
                                    try:
                                        answer = json.loads(m.group(0))
                                    except Exception:
                                        answer = {}
                    except Exception as exc:
                        answer = {}
                        print("OLLAMA drone CLI error:", exc)
                else:
                    data = json.dumps({
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.25, "num_predict": 150},
                    }).encode("utf-8")
                    req = urllib.request.Request(
                        self.ollama_url,
                        data=data,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    result = None
                    try:
                        with urllib.request.urlopen(req, timeout=8.0) as response:
                            raw = response.read().decode("utf-8")
                        result = json.loads(raw)
                    except Exception:
                        result = None

                    if isinstance(result, dict):
                        if all(k in result for k in ("move_x", "move_y", "aim_x", "aim_y", "shoot", "scan")):
                            answer = {
                                "move_x": result.get("move_x"),
                                "move_y": result.get("move_y"),
                                "aim_x": result.get("aim_x"),
                                "aim_y": result.get("aim_y"),
                                "shoot": bool(result.get("shoot", False)),
                                "scan": bool(result.get("scan", False)),
                            }
                        else:
                            inner = None
                            for key in ("response", "output", "text", "content"):
                                v = result.get(key)
                                if isinstance(v, str) and v.strip():
                                    inner = v
                                    break
                            if inner:
                                try:
                                    answer = json.loads(inner)
                                except Exception:
                                    import re
                                    m = re.search(r"\{.*\}", inner, re.DOTALL)
                                    if m:
                                        try:
                                            answer = json.loads(m.group(0))
                                        except Exception:
                                            answer = {}

                move_x = float(answer.get("move_x", 0.0))
                move_y = float(answer.get("move_y", 0.0))
                aim_x = float(answer.get("aim_x", 0.0))
                aim_y = float(answer.get("aim_y", 0.0))
                shoot = bool(answer.get("shoot", False))
                scan = bool(answer.get("scan", False))

                move_x = max(-1.0, min(1.0, move_x))
                move_y = max(-1.0, min(1.0, move_y))
                aim_x = max(-500.0, min(500.0, aim_x))
                aim_y = max(-305.0, min(305.0, aim_y))

                with self.lock:
                    self.move_x = move_x
                    self.move_y = move_y
                    self.aim_x = aim_x
                    self.aim_y = aim_y
                    self.shoot = shoot
                    self.scan = scan
                    self.last_error = ""
            except Exception as exc:
                with self.lock:
                    self.last_error = str(exc)
                print("OLLAMA drone request error:", exc)
            finally:
                with self.lock:
                    self.request_in_progress = False

        threading.Thread(target=worker, daemon=True).start()

    def get_controls(self):
        with self.lock:
            return self.move_x, self.move_y, self.aim_x, self.aim_y, self.shoot, self.scan, self.last_error

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

        self.real_bolt = RealSpheroBoltController(
            enabled=os.environ.get("REAL_SPHERO_BOLT", "0") == "1",
            bolt_name=os.environ.get("REAL_SPHERO_NAME", "Sphero Bolt"),
        )

        if self.real_bolt.enabled:
            self.real_bolt.connect()

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
        # Keep the progression consistent from Level 1 onward. The old formula
        # gave Level 1 a noticeably different dodge/randomness curve than the
        # rest of the run, which made the reticle-dodge behaviour feel off.
        level_progression = max(0, self.level - 1)
        self.dodge_strength = min(0.90, 0.18 + level_progression * 0.08)
        self.direction_timer = random.uniform(0.6, 1.5)
        self.dodge_timer = 0
        self.flash_timer = 0
        self.ai = OllamaMovementAI()
        self.ai_decision_timer = random.uniform(0.4, 1.0)
        self.parts = [{"x": self.x, "y": self.y, "radius": 24}]

    def _setup_boss(self):
        if self.level >= 99:
            self.pattern = {"name": "CORE SPHERO", "count": 3, "hp_bonus": 3, "orbit": 78, "speed": 0.9, "attack": "pulse"}
            self.boss_name = "CORE SPHERO"
            self.count = 3
            self.attack_style = "pulse"
        else:
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
        if self.level >= 99:
            part_base = 2
            orbit_bonus = 12
        else:
            part_base = 3 if self.level <= 3 else 4 if self.level <= 5 else 5
            orbit_bonus = 0
        for i in range(self.count):
            angle = (i / self.count) * math.tau + random.uniform(0.0, 0.7)
            part_hp = part_base + min(4, self.level // 3) if self.level < 99 else 4
            self.parts.append({
                "angle": angle,
                "radius": self.pattern["orbit"] + orbit_bonus + random.uniform(-10, 15),
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

        if self.level >= 99:
            level_scale = 0
            lost_parts = max(0, lost_parts - 1)

        if self.attack_style == "burst":
            shots = max(2, 4 + level_scale * 2 - lost_parts)
            if self.level >= 99:
                shots = max(2, shots - 1)
            spread = math.tau / shots
            speed = (95 + self.level * 14) * 0.74 if self.level >= 99 else 95 + self.level * 14
            for i in range(shots):
                angle = i * spread + random.uniform(-0.2, 0.2)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 2.4 + max(0, 5 - self.level) * 0.25,
                    "radius": 7,
                    "kind": "burst",
                })

        elif self.attack_style == "shards":
            shots = max(3, 6 + level_scale * 3 - lost_parts)
            if self.level >= 99:
                shots = max(3, shots - 2)
            speed = (100 + self.level * 18) * 0.75 if self.level >= 99 else 100 + self.level * 18
            for i in range(shots):
                angle = (i / shots) * math.tau + random.uniform(-0.12, 0.12)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 2.7 + max(0, 5 - self.level) * 0.3,
                    "radius": 6,
                    "kind": "shards",
                })

        elif self.attack_style == "storm":
            shots = max(4, 8 + level_scale * 4 - lost_parts)
            if self.level >= 99:
                shots = max(4, shots - 3)
            speed = (105 + self.level * 20) * 0.72 if self.level >= 99 else 105 + self.level * 20
            for i in range(shots):
                angle = random.uniform(0, math.tau)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 3.0 + max(0, 5 - self.level) * 0.35,
                    "radius": 7,
                    "kind": "storm",
                })

        else:  # pulse
            shots = max(3, 5 + level_scale * 2 - lost_parts)
            if self.level >= 99:
                shots = max(3, shots - 2)
            speed = (85 + self.level * 16) * 0.7 if self.level >= 99 else 85 + self.level * 16
            for i in range(shots):
                angle = (i / shots) * math.tau + math.pi / 2
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 3.3 + max(0, 5 - self.level) * 0.35,
                    "radius": 9,
                    "kind": "pulse",
                })

        if self.level >= 6 and self.level < 99:
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
                if self.level >= 99:
                    self.attack_timer = max(1.0, 2.9 - self.level * 0.0)
                else:
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

        # Use a single progression curve from Level 1 upward so the Sphero's
        # movement and crosshair-dodging feel stable and in line with the rest of
        # the level ramp instead of jumping abruptly at the first level.
        randomness = min(0.85, 0.18 + max(0, self.level - 1) * 0.08)

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

        if self.real_bolt.enabled:
            self.real_bolt.apply_move(move_x, move_y, self.level, behaviour)

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
        self.menu_selection = 0
        self.game_mode = "computer"
        self.drone_camera_source = os.environ.get("DRONE_CAMERA_URL") or os.environ.get("DRONE_CAMERA_DEVICE") or ""
        self.drone_camera = None
        self.drone_camera_available = False
        self.drone_camera_error = ""
        self.drone_camera_frame = None

        self.drone_max_hp = 100
        self.drone_hp = 100

        self.final_boss_unlocked = False
        self.final_boss_defeated = False

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
        self.pending_level_heal = 0
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
        self.cinematic_timer = 0.0
        self.background_phase = 0.0
        self.agentic_ollama = os.environ.get("AGENTIC_OLLAMA", "0") == "1"
        self.drone_ai = OllamaDroneAI()
        self.drone_agent_timer = 0.0

        self.score = 0
        self._menu_hover_index = None
        self._upgrade_hover_index = None
        self._equip_hover_index = None
        self._question_hover_index = None

    def enemy_damage(self):
        """Keep boss pressure threatening but reasonable."""
        capped_level = min(self.level, 12)
        base = 2 + capped_level // 3
        if self.level == 99:
            return max(1, base - 1)
        return max(1, base)

    def set_menu_mode(self, index):
        options = ["computer"]
        if 0 <= index < len(options):
            self.menu_selection = index
            self.game_mode = options[index]
            self.drone_camera_error = ""

    def _init_drone_camera(self):
        self.drone_camera_available = False
        self.drone_camera_frame = None
        self.drone_camera_error = ""

        if not self.drone_camera_source:
            self.drone_camera_error = "Real drone camera not connected."
            return

        try:
            import cv2
            self.drone_camera = cv2.VideoCapture(self.drone_camera_source)
            if self.drone_camera is None or not self.drone_camera.isOpened():
                self.drone_camera = None
                self.drone_camera_error = "Real drone camera device could not be opened."
                return
            self.drone_camera_available = True
        except Exception as exc:
            self.drone_camera = None
            self.drone_camera_error = f"Camera setup failed: {exc}"

    def update_drone_camera_preview(self):
        if self.game_mode != "real_drone" or self.drone_camera is None:
            self.drone_camera_frame = None
            return

        try:
            import cv2
            ok, frame = self.drone_camera.read()
            if not ok or frame is None:
                self.drone_camera_frame = None
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.drone_camera_frame = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
        except Exception:
            self.drone_camera_frame = None

    def start_selected_mode(self):
        self.game_mode = ["computer"][self.menu_selection]
        self.level = 1
        self.upgrades = []
        self.final_boss_unlocked = False
        self.final_boss_defeated = False
        self.drone_max_hp = 100
        self.score = 0
        self.start_level()

    def start_level(self):
        # Wrong-answer penalties are applied immediately and permanently when a
        # question is missed, so there is no delayed level-start deduction.
        self.pending_health_penalty = 0

        # Carry the player's current health forward, then apply the level-clear
        # bonus once before the next level begins.
        if self.pending_level_heal > 0:
            self.drone_hp = min(self.drone_max_hp, self.drone_hp + self.pending_level_heal)
            self.pending_level_heal = 0

        self.state = "playing"
        self.sphero = Sphero(self.level)
        self.time_left = 120.0
        self.shoot_cooldown = 0
        self.message = f"LEVEL {self.level} - HUNT THE SPHERO"
        self.message_timer = 2.4
        self.selected_upgrade = None
        self.shield_active = "SHIELD" in self.upgrades
        self.ai_scan_timer = 0
        self.look_x = 0.0
        self.look_y = 0.0
        self.aim_x = 0.0
        self.aim_y = 0.0

        # Keep the player's remaining health instead of resetting to full every level.

        # Apply weapon-specific cooldown if needed (ensure cooldown not negative)
        # (no-op here, kept for future extensibility)

    def start_final_boss(self):
        self.final_boss_unlocked = True
        self.level = 99
        self.state = "playing"
        self.sphero = Sphero(99)
        self.time_left = 180.0
        self.shoot_cooldown = 0
        self.message = "FINAL BOSS - CORE SPHERO"
        self.message_timer = 2.8
        self.selected_upgrade = None
        self.shield_active = "SHIELD" in self.upgrades
        self.ai_scan_timer = 0
        self.cinematic_timer = 2.8
        self.look_x = 0.0
        self.look_y = 0.0
        self.aim_x = 0.0
        self.aim_y = 0.0
        # Preserve current HP for the final boss rather than resetting to full.

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
                self.pending_health_penalty = 0
                self.state = "upgrade"
                self.choose_upgrades()
        else:
            self.question_mistakes += 1
            self.pending_health_penalty = 0
            self.drone_max_hp = max(40, self.drone_max_hp - 10)
            self.drone_hp = min(self.drone_hp, self.drone_max_hp)
            self.question_feedback = "INCORRECT - MAX HP -10 (PERMANENT)"

    def choose_upgrades(self):
        # Show all upgrades not already owned. If many are owned, show a selection
        # of remaining upgrades.
        remaining = [u for u in UPGRADES if u[0] not in self.upgrades]
        random.shuffle(remaining)
        self.available_upgrades = remaining[:5]

        if not self.available_upgrades:
            self.final_boss_unlocked = True
            self.state = "between_levels"
            self.message = "ALL UPGRADES UNLOCKED! FINAL BOSS READY"
            self.message_timer = 2.5

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

        if len(self.upgrades) >= len(UPGRADES):
            self.final_boss_unlocked = True
            self.state = "between_levels"
            self.message = "ALL UPGRADES ACQUIRED! FINAL BOSS UNLOCKED"
            self.message_timer = 2.5
            return

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
                self.pending_level_heal = 10
                if self.final_boss_unlocked and self.level == 99:
                    self.final_boss_defeated = True
                    self.state = "win_screen"
                    self.message = "FINAL BOSS DEFEATED!"
                    self.message_timer = 2.0
                else:
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
        self.cinematic_timer = max(0, self.cinematic_timer - dt)
        self.background_phase += dt

        if self.state == "playing":
            self.time_left -= dt

            if self.agentic_ollama:
                self.drone_agent_timer -= dt
                if self.drone_agent_timer <= 0:
                    self.drone_ai.request_decision(
                        self.level,
                        self.sphero.x,
                        self.sphero.y,
                        self.look_x,
                        self.look_y,
                        self.time_left,
                        self.drone_hp,
                        self.drone_max_hp,
                        self.aim_x,
                        self.aim_y,
                    )
                    self.drone_agent_timer = 0.35

                move_x, move_y, aim_x, aim_y, shoot, scan, _ = self.drone_ai.get_controls()
                self.move_x = max(-1.0, min(1.0, move_x))
                self.move_y = max(-1.0, min(1.0, move_y))
                if scan and "AI SCAN" in self.upgrades:
                    self.ai_scan_timer = max(self.ai_scan_timer, 2.0)

                self.look_x += self.move_x * 230 * dt
                self.look_y += self.move_y * 230 * dt
                self.look_x = max(-500, min(500, self.look_x))
                self.look_y = max(-305, min(305, self.look_y))

                self.aim_x = self.look_x + aim_x
                self.aim_y = self.look_y + aim_y
                self.aim_x = max(-500, min(500, self.aim_x))
                self.aim_y = max(-305, min(305, self.aim_y))

                if shoot and self.shoot_cooldown <= 0:
                    self.fire()
            else:
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
                    damage = self.enemy_damage()
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
                damage = self.enemy_damage()
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
        # Subtle sci-fi arena backdrop with calmer motion.
        t = self.background_phase
        horizon = HEIGHT // 2 - 35

        screen.fill((10, 16, 24))
        pygame.draw.rect(screen, (18, 26, 36), (0, 0, WIDTH, horizon))
        pygame.draw.rect(screen, (26, 32, 38), (0, horizon, WIDTH, HEIGHT - horizon))

        glow_band = pygame.Surface((WIDTH, horizon), pygame.SRCALPHA)
        pygame.draw.rect(glow_band, (70, 145, 255, 18), (0, 0, WIDTH, horizon))
        screen.blit(glow_band, (0, 0))

        scan_offset = int((t * 90) % 100)
        for y in range(0, horizon, 18):
            yy = (y + scan_offset) % (horizon + 20)
            pygame.draw.line(screen, (30, 42, 58), (0, yy), (WIDTH, yy), 1)

        centre_x = WIDTH // 2
        floor_y = horizon
        for offset in range(-700, 701, 100):
            pygame.draw.line(
                screen,
                (44, 50, 58),
                (centre_x, floor_y),
                (centre_x + offset, HEIGHT),
                1,
            )

        for y in [horizon + 40, horizon + 100, horizon + 180, horizon + 270]:
            line_surf = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            line_surf.fill((30, 38, 45, 110))
            screen.blit(line_surf, (0, y))

        for x_edge, side in ((70, -1), (WIDTH - 70, 1)):
            pygame.draw.line(screen, (92, 100, 110), (x_edge, horizon), (x_edge + side * 25, HEIGHT), 2)

        for i in range(8):
            px = (i * 120 + int(t * 18)) % WIDTH
            py = ((i * 59 + int(t * 28)) % (HEIGHT - 80)) + 20
            pygame.draw.circle(screen, (80, 180, 255) if i % 2 == 0 else (120, 230, 180), (px, py), 2)

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
        pulse = 1.0 + 0.08 * math.sin(self.background_phase * 8)
        if self.sphero.is_boss:
            intro_scale = 1.0 + max(0, (2.8 - self.cinematic_timer)) * 0.12 if self.level == 99 else 1.0
            for part in self.sphero.parts:
                dx = part["x"] - self.look_x
                dy = part["y"] - self.look_y
                sx = WIDTH // 2 + int(dx * 0.65)
                sy = HEIGHT // 2 + int(dy * 0.55)
                radius = int(max(12, min(34, 19000 / max(40, math.hypot(dx, dy))))) * int(intro_scale)

                if -150 < sx < WIDTH + 150 and -150 < sy < HEIGHT + 150:
                    aura_r = int(radius * 1.35 * pulse)
                    pygame.draw.circle(screen, (80, 170, 255), (sx, sy), aura_r, 2)
                    if self.ai_scan_timer > 0:
                        pygame.draw.circle(screen, CYAN, (sx, sy), radius + 12, 3)

                    if self.cinematic_timer > 0 and self.level == 99:
                        pygame.draw.circle(screen, (255, 170, 80), (sx, sy), radius + 12, 2)

                    body_colour = RED if self.sphero.flash_timer <= 0 else WHITE
                    pygame.draw.circle(screen, (15, 15, 18), (sx + 3, sy + 4), radius + 2)
                    pygame.draw.circle(screen, body_colour, (sx, sy), radius)
                    pygame.draw.arc(screen, (130, 200, 255), (sx - radius, sy - radius, radius * 2, radius * 2), 0.2, math.pi * 1.3, max(2, radius // 8))

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
                pygame.draw.circle(screen, CYAN, (sx, sy), radius + 12, 3)

            body_colour = RED if self.sphero.flash_timer <= 0 else WHITE
            aura_r = int(radius * 1.3 * pulse)
            pygame.draw.circle(screen, (80, 170, 255), (sx, sy), aura_r, 2)

            pygame.draw.circle(screen, (15, 15, 18), (sx + 3, sy + 4), radius + 2)
            pygame.draw.circle(screen, body_colour, (sx, sy), radius)

            pygame.draw.arc(
                screen,
                CYAN,
                (sx - radius, sy - radius, radius * 2, radius * 2),
                0.2,
                math.pi * 1.3,
                max(2, radius // 8),
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

    def draw_menu_cursor(self):
        x, y = pygame.mouse.get_pos()
        if self.state == "questions":
            cursor_colour = GREEN
        elif self.state == "upgrade":
            cursor_colour = CYAN
        else:
            cursor_colour = ORANGE
        outline = (15, 22, 30)

        points = [
            (x, y),
            (x + 20, y + 14),
            (x + 12, y + 14),
            (x + 22, y + 42),
            (x + 11, y + 30),
            (x + 7, y + 58),
            (x + 2, y + 46),
            (x + 4, y + 20),
        ]

        pygame.draw.polygon(screen, outline, points, 0)
        pygame.draw.polygon(screen, cursor_colour, [(px, py) for px, py in points], 0)
        pygame.draw.line(screen, (255, 255, 255), (x + 1, y + 2), (x + 9, y + 10), 2)

    def draw_hud(self):
        # Top HUD with layered cyber panels.
        top_panel = pygame.Rect(0, 0, WIDTH, 80)
        pygame.draw.rect(screen, (10, 18, 26), top_panel)
        pygame.draw.rect(screen, (32, 175, 255), (0, 78, WIDTH, 2))
        pygame.draw.rect(screen, (255, 120, 80), (0, 80, WIDTH, 1))

        level_label = "FINAL BOSS" if self.level == 99 else f"LEVEL {self.level}"
        draw_text(level_label, FONT, WHITE, 25, 18)

        mins = int(self.time_left) // 60
        secs = int(self.time_left) % 60
        timer_colour = RED if self.time_left <= 20 else WHITE
        draw_text(f"TIME {mins:02d}:{secs:02d}", FONT, timer_colour, 165, 18)

        draw_text(f"SCORE {self.score}", FONT, YELLOW, 350, 18)

        upgrade_text = ", ".join(self.upgrades) if self.upgrades else "NONE"
        draw_text("UPGRADES:", SMALL, WHITE, 590, 10)
        draw_text(upgrade_text[:48], SMALL, CYAN, 590, 38)
        draw_text("WEAPON:", SMALL, WHITE, 880, 10)
        draw_text(self.equipped_weapon, SMALL, ORANGE, 880, 38)

        # Bottom HUD.
        panel_y = HEIGHT - 105
        pygame.draw.rect(screen, (8, 14, 22), (0, panel_y, WIDTH, 105))
        pygame.draw.line(screen, (90, 200, 255), (0, panel_y), (WIDTH, panel_y), 2)

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

    def draw_drone_camera_preview(self):
        if self.game_mode != "real_drone":
            return

        panel = pygame.Rect(WIDTH - 360, 20, 330, 220)
        pygame.draw.rect(screen, DARK_GREY, panel, border_radius=14)
        pygame.draw.rect(screen, CYAN, panel, 2, border_radius=14)
        draw_text("DRONE CAMERA", SMALL, WHITE, panel.x + 12, panel.y + 12)

        if self.drone_camera_frame is not None:
            frame = pygame.transform.smoothscale(self.drone_camera_frame, (290, 165))
            screen.blit(frame, (panel.x + 20, panel.y + 38))
        else:
            draw_text("NO REAL DRONE CONNECTED", SMALL, RED, panel.centerx, panel.centery, center=True)
            if self.drone_camera_error:
                draw_text(self.drone_camera_error[:42], SMALL, YELLOW, panel.centerx, panel.centery + 24, center=True)

    def draw_menu(self):
        screen.fill(BLACK)

        draw_text("DRONE VS SPHERO", TITLE, CYAN, WIDTH // 2, 125, center=True)
        draw_text("CYBERSECURITY TRAINING PROTOTYPE", FONT, WHITE, WIDTH // 2, 185, center=True)

        box = pygame.Rect(180, 220, WIDTH - 360, 390)
        pygame.draw.rect(screen, DARK_GREY, box, border_radius=15)
        pygame.draw.rect(screen, CYAN, box, 2, border_radius=15)

        title_y = box.y + 35
        draw_text("MISSION", BIG, YELLOW, WIDTH // 2, title_y, center=True)

        opts = [
            ("1. Computer Mode", "Regular base game (mouse + keyboard)"),
        ]

        opt_h = 68
        spacing = 12
        opt_y = box.y + 205

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

        self._menu_option_rects = []
        for i, (title, desc) in enumerate(opts):
            w = 720
            h = opt_h
            x = WIDTH // 2 - w // 2
            y = opt_y + i * (h + spacing)
            rect = pygame.Rect(x, y, w, h)
            self._menu_option_rects.append((rect, i))

            shadow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 100), (4, 4, w, h), border_radius=14)
            screen.blit(shadow, (x - 4, y - 4))

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

            icon_r = 22
            icon_cx = rect.x + 46
            icon_cy = rect.y + h // 2
            pygame.draw.circle(screen, (18, 24, 28), (icon_cx + 3, icon_cy + 3), icon_r + 3)
            pygame.draw.circle(screen, CYAN if i == self.menu_selection else GREY, (icon_cx, icon_cy), icon_r)
            draw_text(str(i + 1), SMALL, (8, 12, 18), icon_cx, icon_cy, center=True)

            draw_text(title, FONT, WHITE if (i == self.menu_selection or mouse_over) else (200, 210, 215), rect.x + 92, rect.y + 10)
            draw_text(desc, SMALL, (170, 178, 186), rect.x + 92, rect.y + 38)

        instr_y = box.y + box.height + 18
        draw_text("Press ENTER to start the selected mode", FONT, GREEN, WIDTH // 2, instr_y, center=True)
        draw_text("Use W/S or up/down to switch mode", SMALL, GREY, WIDTH // 2, instr_y + 30, center=True)
        if self.drone_camera_error:
            draw_text(self.drone_camera_error[:64], SMALL, RED, WIDTH // 2, instr_y + 54, center=True)

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
        self._question_answer_rects = []

        for i, answer in enumerate(q["answers"]):
            rect = pygame.Rect(145, y, WIDTH - 290, 55)
            answer_rects.append(rect)
            self._question_answer_rects.append((rect, i))

            hovered = getattr(self, "_question_hover_index", None) == i
            colour = (50, 60, 72)
            border = GREY

            if self.selected_answer is not None:
                if i == q["correct"]:
                    colour = (30, 110, 65)
                    border = GREEN
                elif i == self.selected_answer:
                    colour = (130, 45, 45)
                    border = RED
            elif hovered:
                colour = (58, 78, 98)
                border = CYAN

            pygame.draw.rect(screen, colour, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            draw_text(answer, SMALL, WHITE, rect.x + 15, rect.y + 17)

            y += 65

        self.draw_menu_cursor()

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

        penalty_text = "WRONG ANSWERS COST 10 MAX HP PERMANENTLY"

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

        self._upgrade_option_rects = []
        y = 245
        for i, (name, description) in enumerate(self.available_upgrades):
            rect = pygame.Rect(120, y, WIDTH - 240, 68)
            self._upgrade_option_rects.append((rect, i))

            hovered = getattr(self, "_upgrade_hover_index", None) == i
            fill = (55, 66, 84) if hovered else DARK_GREY
            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, CYAN if hovered else (90, 110, 130), rect, 2, border_radius=10)

            draw_text(f"{i + 1}", BIG, YELLOW, rect.x + 25, rect.y + 10)
            draw_text(name, FONT, WHITE, rect.x + 80, rect.y + 8)
            draw_text(description, SMALL, GREY, rect.x + 80, rect.y + 38)

            y += 78

        draw_text("Click an upgrade or press 1-5 to choose", FONT, GREEN,
                  WIDTH // 2, 635, center=True)
        self.draw_menu_cursor()

    def draw_equip_screen(self):
        screen.fill((8, 10, 14))
        draw_text("EQUIP WEAPON", TITLE, CYAN, WIDTH // 2, 70, center=True)
        draw_text("Choose a weapon to equip for the next level:", FONT, WHITE, WIDTH // 2, 130, center=True)
        draw_text("LOCKED WEAPONS CANNOT BE USED UNTIL YOU UNLOCK THEM THROUGH UPGRADES.", SMALL, RED, WIDTH // 2, 160, center=True)

        self._equip_option_rects = []
        y = 190
        for i, (name, stats) in enumerate(WEAPONS):
            owned = name in self.unlocked_weapons
            rect = pygame.Rect(140, y, WIDTH - 280, 68)
            self._equip_option_rects.append((rect, i))

            hovered = getattr(self, "_equip_hover_index", None) == i
            fill = (58, 75, 96) if hovered and owned else (DARK_GREY if owned else (35, 35, 40))
            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, CYAN if (owned and hovered) else (CYAN if owned else GREY), rect, 2, border_radius=10)

            draw_text(f"{i + 1}", BIG, YELLOW, rect.x + 25, rect.y + 10)
            draw_text(name, FONT, WHITE if owned else GREY, rect.x + 80, rect.y + 8)
            draw_text(stats.get("desc", ""), SMALL, GREY, rect.x + 80, rect.y + 38)

            if owned:
                if name == self.equipped_weapon:
                    draw_text("EQUIPPED", SMALL, GREEN, rect.right - 120, rect.y + 22)
            else:
                draw_text("LOCKED", SMALL, RED, rect.right - 120, rect.y + 22)

            y += 78

        draw_text("Click a weapon or press 1-4 to equip unlocked weapons, ENTER to confirm, or ESC to skip", SMALL, GREY, WIDTH // 2, 620, center=True)
        self.draw_menu_cursor()

    def draw_between_levels(self):
        screen.fill(BLACK)

        if self.final_boss_unlocked and not self.final_boss_defeated:
            draw_text("FINAL BOSS READY", TITLE, RED,
                      WIDTH // 2, 145, center=True)
            draw_text("All upgrades acquired. The Core Sphero has awakened.", BIG, WHITE,
                      WIDTH // 2, 230, center=True)
            draw_text("Press ENTER to face the final boss.", FONT, CYAN,
                      WIDTH // 2, 330, center=True)
            draw_text("Fight with your fully upgraded defence suite.", SMALL, GREY,
                      WIDTH // 2, 380, center=True)
            return

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

    def draw_win_screen(self):
        screen.fill((8, 18, 16))
        draw_text("YOU WIN!", TITLE, GREEN,
                  WIDTH // 2, 150, center=True)
        draw_text("The Core Sphero has been defeated.", BIG, WHITE,
                  WIDTH // 2, 235, center=True)
        draw_text(f"Final score: {self.score}", FONT, YELLOW,
                  WIDTH // 2, 300, center=True)
        draw_text("All cybersecurity upgrades were secured.", FONT, CYAN,
                  WIDTH // 2, 355, center=True)
        draw_text("Press ENTER to return to the menu.", FONT, GREEN,
                  WIDTH // 2, 430, center=True)

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

        elif self.state == "playing":
            self.update_drone_camera_preview()
            self.draw_background()
            if self.game_mode == "real_drone":
                self.draw_drone_camera_preview()
            if self.cinematic_timer > 0 and self.sphero and self.sphero.is_boss:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                alpha = int(120 * (self.cinematic_timer / 2.8))
                overlay.fill((255, 120, 40, alpha))
                screen.blit(overlay, (0, 0))
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

        elif self.state == "win_screen":
            self.draw_win_screen()

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
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    game.set_menu_mode(0)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    game.set_menu_mode(0)
                elif event.key == pygame.K_RETURN:
                    game.start_selected_mode()

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
                    if game.final_boss_unlocked and not game.final_boss_defeated:
                        game.start_final_boss()
                    else:
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

            elif game.state == "win_screen":
                if event.key == pygame.K_RETURN:
                    game.reset()
                    game.state = "menu"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game.state == "playing":
                    game.fire()
                elif game.state == "questions":
                    if hasattr(game, "_question_answer_rects"):
                        mx, my = event.pos
                        for rect, idx in game._question_answer_rects:
                            if rect.collidepoint(mx, my):
                                game.question_answer(idx)
                                break
                elif game.state == "upgrade":
                    if hasattr(game, "_upgrade_option_rects"):
                        mx, my = event.pos
                        for rect, idx in game._upgrade_option_rects:
                            if rect.collidepoint(mx, my):
                                game.select_upgrade(idx)
                                break
                elif game.state == "equip_weapon":
                    if hasattr(game, "_equip_option_rects"):
                        mx, my = event.pos
                        for rect, idx in game._equip_option_rects:
                            if rect.collidepoint(mx, my):
                                game.equip_weapon_choice(idx)
                                break
                elif game.state == "menu":
                    if hasattr(game, "_menu_option_rects"):
                        mx, my = event.pos
                        for rect, idx in game._menu_option_rects:
                            if rect.collidepoint(mx, my):
                                game.set_menu_mode(idx)
                                game.start_selected_mode()
                                break

        elif event.type == pygame.MOUSEMOTION:
            if game.state == "playing":
                if not game.agentic_ollama:
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
            elif game.state == "questions":
                if hasattr(game, "_question_answer_rects"):
                    mx, my = event.pos
                    hover = None
                    for rect, idx in game._question_answer_rects:
                        if rect.collidepoint(mx, my):
                            hover = idx
                            break
                    game._question_hover_index = hover
            elif game.state == "upgrade":
                if hasattr(game, "_upgrade_option_rects"):
                    mx, my = event.pos
                    hover = None
                    for rect, idx in game._upgrade_option_rects:
                        if rect.collidepoint(mx, my):
                            hover = idx
                            break
                    game._upgrade_hover_index = hover
            elif game.state == "equip_weapon":
                if hasattr(game, "_equip_option_rects"):
                    mx, my = event.pos
                    hover = None
                    for rect, idx in game._equip_option_rects:
                        if rect.collidepoint(mx, my):
                            hover = idx
                            break
                    game._equip_hover_index = hover

    # Continuous keyboard movement.
    keys = pygame.key.get_pressed()

    if game.state == "playing":
        if not game.agentic_ollama:
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

