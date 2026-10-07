# Arm Wrestle Showdown Lab

This project is a tug-of-war button mashing game using **Pygame**. It introduces students to vector interpolation, resource/stamina management, alternating key-stroke detection, and simple AI pressure modeling inside an object-oriented codebase.

---

## What's Provided

A working Arm Wrestling game with:

- An arm wrestling table arena rendering procedural arms, elbows, shoulders, and clasping hands
- An alternating input mechanism requiring rhythmic pressing of Left and Right arrow keys
- A stamina bar that depletes during rapid pressing and recovers naturally over time
- Continuous computer AI force pushing toward the player's side
- Win/loss boundary detection and a post-game rematch screen

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

**Controls:** Rapidly alternate Left Arrow and Right Arrow to push, R to restart after a match.   


## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the inverted arm push bug

Alternating Left and Right arrow keys pushes the arm toward the computer's side instead of pulling it toward the player's side, causing the player to pin themselves. Ensure that player keystrokes push the hands toward the player's winning threshold.

### Task 2: Implement dynamic AI surge

The computer currently applies force at a predictable constant rate. Introduce an AI stamina cycle where the computer periodically enters a brief high-power surge with increased pushing force, followed by a cooldown period with reduced resistance

### Task 3: Implement an exhaustion warning indicator

Building upon Task 2's surge cycle, give the player visual cues for fatigue states. Display an active warning indicator when the AI enters its power surge, and show an exhaustion state whenever the player's stamina drops too low to push

### Task 4: Implement counter-surge bonus resistance

Building upon the warnings in Task 3, reward strategic timing during fatigue states. If the player pushes right as the AI's surge ends and enters its cooldown phase, grant a temporary stamina recovery boost and double push strength to mount a comeback.

---

## Expected Behavior

- Rapidly alternating between Left Arrow and Right Arrow pulls the hands toward the player's side.
- Rapid pushing drains stamina; falling below 10 stamina temporarily halts input until it recovers.
- Reaching -100.0 awards victory to the player, while reaching +100.0 triggers a computer win.
- Pressing R on the Game Over screen resets stamina, arm position, and game states for a rematch.
---

## Folder Structure

```
arm_wrestle/
├── game/
│   └── game_engine.py
├── main.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history

---

## Submission

| Item | Link |
|------|------|
| Gameplay **before** changes (bug: presses push toward the computer) | [videos/before.mov](videos/before.mov) |
| Gameplay **after** changes (fix + AI surge, warnings, counter-surge) | [videos/after.mov](videos/after.mov) |
| LLM chat history | _add your chat share link here_ |

### Changes made

- **Task 1:** Left/Right presses now pull the hands toward -100, so the player can win.
- **Task 2:** The AI cycles Steady → Power Surge (2.2× force, 1.5 s) → Cooldown (0.4× force, 2 s).
- **Task 3:** Flashing surge banner, red table border, AI phase meter, and an EXHAUSTED state that locks input until stamina recovers to 35.
- **Task 4:** Pushing within 0.6 s of a surge ending triggers a counter-surge: 2 s of double push, 3× stamina regen, +25 stamina.
- Push force, stamina cost/regen and AI strength were rebalanced so stamina and surges actually matter.
