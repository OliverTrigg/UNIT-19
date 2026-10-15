# Drone vs Sphero: AI Security Demo Setup Guide

This project is a local AI security prototype that combines:
- a Python game arena
- a Sphero Bolt enemy
- Ollama-powered decision-making
- optional real hardware integration
- a human-controlled drone workflow for a more realistic demonstration

The goal is to build a system where the Sphero behaves like an autonomous device that reacts to threat level, difficulty, and the drone’s position, while the drone tries to hunt it in a cyber-security style game.

---

## What this project contains

The project has three important layers:

1. Simulation layer
   - the game world is rendered in Pygame
   - the Sphero and drone are represented visually
   - the game runs even without hardware

2. Ollama AI layer
   - the Sphero uses local AI to choose behaviour
   - the drone can also receive AI guidance
   - decisions are based on level, difficulty, threat distance, and timing

3. Hardware integration layer
   - the real Sphero Bolt can be connected as an optional physical target
   - a real drone can be included later, but the simplest setup is to keep the drone human-controlled with the Pi acting as mission coordinator

---

## Core setup path

This is the easiest way to build the system in a safe order:

1. Get the simulation working first
2. Add Ollama locally
3. Test the AI decision loop in mock mode
4. Plug in a real Sphero Bolt only when the software is stable
5. Add the human-controlled drone as the final stage

This avoids rewiring the whole project after it is already working.

---

## Step 1: Install the software requirements

On your main development machine or Raspberry Pi:

```bash
pip install pygame
```

You also need:
- Python 3.10+
- Ollama installed locally
- a valid model such as llama3.2

Install and pull the model:

```bash
ollama pull llama3.2
```

Check that Ollama is running locally:

```bash
ollama list
```

---

## Step 2: Run the project in simulation mode

The project already supports a pure simulation mode without any physical hardware.

From the project folder:

```bash
python "sphero bolt game VERSION 3.py"
```

To enable AI behaviour in simulation mode:

```bash
$env:AGENTIC_OLLAMA = "1"
python "sphero bolt game VERSION 3.py"
```

To test without a live model connection:

```bash
$env:MOCK_OLLAMA = "1"
$env:AGENTIC_OLLAMA = "1"
python "sphero bolt game VERSION 3.py"
```

This is the best first test because it lets you verify the game flow, the AI logic, and the difficulty scaling before adding hardware.

---

## Step 3: Understand the AI behaviour

The Sphero uses Ollama to decide movement based on:
- current level
- Sphero position
- drone position
- velocity
- distance to the target
- difficulty scaling

The AI decides behaviours such as:
- RANDOM
- CHASE
- EVADE
- LEFT
- RIGHT
- UP
- DOWN

At higher levels, the movement becomes less predictable and more chaotic, which helps the gameplay feel more like a real enemy device that is adapting to a threat.

---

## Step 4: Add the real Sphero Bolt (optional)

Once the simulation is stable, you can enable real hardware control.

On the Raspberry Pi (or whichever machine is connected to the Sphero), set:

```bash
$env:REAL_SPHERO_BOLT = "1"
$env:REAL_SPHERO_NAME = "Sphero Bolt"
$env:AGENTIC_OLLAMA = "1"
python "sphero bolt game VERSION 3.py"
```

This makes the project try to connect to a physical Sphero Bolt and move it using the same AI logic that is used in the simulated version.

Important:
- this is optional
- it should be enabled only when the Sphero is connected and working
- the project still includes a fallback to the simulation when real hardware is not available

---

## Step 5: Connect the real Sphero properly

The Sphero Bolt needs the proper Python library and a working Bluetooth or serial connection depending on your setup.

Checklist:
- Sphero is charged
- the device is in range
- the API library is installed on the Pi
- the Bluetooth adapter is available
- the script is launched from the environment that can access the hardware

If the device cannot be opened or no SDK is found, the code will simply stay in fallback mode and the simulation continues without crashing.

This is designed to be safe and non-destructive.

---

## Step 6: Decide how the drone fits in

There are 3 realistic ways to do this.

### Option A: Human-controlled drone, Pi as AI coordinator
Best for a Raspberry Pi 4.

- the drone uses its own remote/headset controls
- the Pi manages the game logic and Sphero AI
- the operator flies the drone toward the Sphero based on what the game and AI say
- the Pi does not need to fully control the drone flight stack

This is the simplest and safest way.

### Option B: Drone remote sends high-level commands only

- the Pi decides whether the drone should pursue, flank, retreat, or scan
- the remote or headset executes those basic instructions
- the Pi acts as the tactical decision engine

### Option C: Full autonomous drone control

This is possible, but not recommended as the first version on a Pi 4.

It would require:
- real-time tracking
- camera processing
- flight stabilization
- extra sensors or compute power
- a much more complex control system

This is a later-stage upgrade, not the basic connection path.

---

## Step 7: Recommended final architecture

For a project like this, the best architecture is:

- Raspberry Pi 4: mission coordinator, game state, Sphero logic, Ollama decisions
- Sphero Bolt: target device or real enemy bot
- Drone remote/headset: actual flight control
- Optional camera: used only for live tracking or high-level target detection

This keeps the Pi load manageable while still giving the project a realistic AI/security demo feel.

---

## Step 8: Add live tracking only after the base system works

Once the simulation and real Sphero path are stable, you can add live tracking.

Recommended order:
1. test with the simulation
2. connect a real Sphero
3. add a single camera or marker tracker
4. only then feed live target positions into the game logic

Do not start with heavy computer vision. Start small.

A good first version is:
- one visible marker on the Sphero
- one simple colour marker or fiducial detection system
- only x/y position reporting from the camera
- all other decisions still handled by game logic or Ollama

---

## Step 9: Keep the project split into modes

This project works best when it is clearly separated into modes:

- Simulation mode
- Mock AI mode
- Real Sphero mode
- Drone-assisted mode
- Full tracking mode

This helps you debug each layer separately.

Example:
- if simulation works, but real Sphero does not, the problem is hardware or SDK-related
- if the simulation works and AI works, but the drone does not react, the problem is control logic
- if everything works but motion is jittery, the issue is likely tracking or timing

---

## Troubleshooting

### Ollama is not responding
- make sure Ollama is running locally
- ensure the model exists
- check the model name in the script

### Real Sphero does not connect
- confirm power and Bluetooth connectivity
- install the correct SDK
- verify the device is discoverable
- test the hardware separately before running the game

### The Sphero movement feels too random
- reduce the randomness factor
- use the level-based difficulty settings carefully
- confirm the AI prompt is returning valid JSON

### The Pi lags or freezes
- keep the AI request rate low
- avoid running heavy live tracking in the same loop as Pygame
- keep vision in a background thread if used

---

## Recommended development order

Use this exact order:

1. Install Python and Pygame
2. Run the game in simulation mode
3. Enable local Ollama and mock mode
4. Confirm the Sphero AI behaves correctly
5. Add the real Sphero Bolt only when stable
6. Keep the drone remote-controlled at first
7. Add camera detection only after the base system is working
8. Expand to full autonomy only if the computer power and hardware allow it

---

## Summary

This project is best thought of as a layered system:

- simulation first
- AI second
- real hardware third
- drone autonomy last

The simplest and most realistic combination for a Raspberry Pi 4 is:
- real Sphero Bolt
- local Ollama AI
- human-controlled drone or remote-flight setup
- a Pi acting as mission coordinator rather than a full autonomous drone brain

That path is much more stable, easier to debug, and far more likely to work reliably than trying to do everything fully autonomous on one Raspberry Pi 4.

---

## Quick command summary

```bash
pip install pygame
ollama pull llama3.2
python "sphero bolt game VERSION 3.py"

$env:AGENTIC_OLLAMA = "1"
python "sphero bolt game VERSION 3.py"

$env:MOCK_OLLAMA = "1"
$env:AGENTIC_OLLAMA = "1"
python "sphero bolt game VERSION 3.py"

$env:REAL_SPHERO_BOLT = "1"
$env:REAL_SPHERO_NAME = "Sphero Bolt"
$env:AGENTIC_OLLAMA = "1"
python "sphero bolt game VERSION 3.py"
```

This gives you the full path from a working simulation to a real-world Sphero demo and a human-driven drone setup.
