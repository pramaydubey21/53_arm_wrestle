import math
import random
import pygame


# ---------------------------------------------------------------------------
# Tuning constants (all timers are in frames; the game runs at 60 FPS)
# ---------------------------------------------------------------------------
FPS = 60

PUSH_FORCE = 2.5              # arm movement per valid (alternating) keypress
PUSH_STAMINA_COST = 3.0       # stamina spent per valid keypress
STAMINA_REGEN = 0.25          # stamina recovered per frame (15 / second)
EXHAUSTION_THRESHOLD = 10.0   # at or below this the player can no longer push
EXHAUSTION_RECOVERY = 35.0    # input stays locked until stamina climbs back here

# Task 2 - AI surge cycle
AI_PHASE_NORMAL = "NORMAL"
AI_PHASE_SURGE = "SURGE"
AI_PHASE_COOLDOWN = "COOLDOWN"
AI_NORMAL_FRAMES = (int(3.0 * FPS), int(5.0 * FPS))   # random range between surges
AI_FIRST_NORMAL_FRAMES = (int(2.5 * FPS), int(3.5 * FPS))
AI_SURGE_FRAMES = int(1.5 * FPS)
AI_COOLDOWN_FRAMES = int(2.0 * FPS)
AI_PHASE_MULTIPLIER = {
    AI_PHASE_NORMAL: 1.0,
    AI_PHASE_SURGE: 2.2,     # high-power surge
    AI_PHASE_COOLDOWN: 0.4,  # reduced resistance while the AI recovers
}

# Task 4 - counter-surge bonus
COUNTER_WINDOW_FRAMES = int(0.6 * FPS)    # how long after a surge ends the counter can be landed
COUNTER_BONUS_FRAMES = int(2.0 * FPS)     # how long the bonus lasts
COUNTER_PUSH_MULTIPLIER = 2.0             # double push strength
COUNTER_REGEN_MULTIPLIER = 3.0            # faster stamina recovery while boosted
COUNTER_INSTANT_STAMINA = 25.0            # immediate stamina refund on a successful counter


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None

        self.stamina = 100.0
        self.max_stamina = 100.0

        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.58   # rebalanced for the new stamina rules (was 0.35)

        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 22)

        self._reset_dynamic_state()

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def _reset_dynamic_state(self):
        """State introduced by Tasks 2-4. Shared by __init__ and reset()."""
        self.frame = 0

        # Task 2: AI surge cycle
        self.ai_phase = AI_PHASE_NORMAL
        self.ai_phase_length = random.randint(*AI_FIRST_NORMAL_FRAMES)
        self.ai_phase_timer = self.ai_phase_length

        # Task 3: player exhaustion (input locked until stamina recovers)
        self.exhausted = False

        # Task 4: counter-surge
        self.counter_window_timer = 0
        self.counter_bonus_timer = 0
        self.counter_flash_timer = 0

    def _set_ai_phase(self, phase):
        self.ai_phase = phase
        if phase == AI_PHASE_SURGE:
            self.ai_phase_length = AI_SURGE_FRAMES
        elif phase == AI_PHASE_COOLDOWN:
            self.ai_phase_length = AI_COOLDOWN_FRAMES
            # Surge just ended: open the counter-surge timing window.
            self.counter_window_timer = COUNTER_WINDOW_FRAMES
        else:
            self.ai_phase_length = random.randint(*AI_NORMAL_FRAMES)
        self.ai_phase_timer = self.ai_phase_length

    def _advance_ai_phase(self):
        self.ai_phase_timer -= 1
        if self.ai_phase_timer > 0:
            return
        if self.ai_phase == AI_PHASE_NORMAL:
            self._set_ai_phase(AI_PHASE_SURGE)
        elif self.ai_phase == AI_PHASE_SURGE:
            self._set_ai_phase(AI_PHASE_COOLDOWN)
        else:
            self._set_ai_phase(AI_PHASE_NORMAL)

    def _trigger_counter_surge(self):
        self.counter_window_timer = 0
        self.counter_bonus_timer = COUNTER_BONUS_FRAMES
        self.counter_flash_timer = int(0.5 * FPS)
        self.stamina = min(self.max_stamina, self.stamina + COUNTER_INSTANT_STAMINA)
        self.exhausted = False

    @property
    def counter_active(self):
        return self.counter_bonus_timer > 0

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type != pygame.KEYDOWN:
            return
        if event.key not in (pygame.K_LEFT, pygame.K_RIGHT):
            return

        # Task 4: a press inside the window right after a surge ends is a
        # counter-surge. It counts even while exhausted - that is the comeback.
        if self.counter_window_timer > 0 and not self.counter_active:
            self._trigger_counter_surge()

        if self.exhausted or self.stamina <= EXHAUSTION_THRESHOLD:
            self.exhausted = True
            return

        if event.key == self.last_key:
            return  # must alternate Left / Right

        push = PUSH_FORCE * (COUNTER_PUSH_MULTIPLIER if self.counter_active else 1.0)
        self.arm_position -= push   # Task 1 fix: player pulls toward -100 (player win)
        self.stamina = max(0.0, self.stamina - PUSH_STAMINA_COST)
        self.last_key = event.key

        if self.stamina <= EXHAUSTION_THRESHOLD:
            self.exhausted = True

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def update(self):
        if self.game_state != "PLAYING":
            return

        self.frame += 1

        # Task 2: AI force scaled by its current phase
        self._advance_ai_phase()
        ai_variance = random.uniform(0.3, 1.0)
        self.arm_position += self.ai_strength * ai_variance * AI_PHASE_MULTIPLIER[self.ai_phase]

        # Stamina recovery (boosted during a counter-surge)
        regen = STAMINA_REGEN * (COUNTER_REGEN_MULTIPLIER if self.counter_active else 1.0)
        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + regen)
        if self.exhausted and self.stamina >= EXHAUSTION_RECOVERY:
            self.exhausted = False

        # Task 4 timers
        if self.counter_window_timer > 0:
            self.counter_window_timer -= 1
        if self.counter_bonus_timer > 0:
            self.counter_bonus_timer -= 1
        if self.counter_flash_timer > 0:
            self.counter_flash_timer -= 1

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self._reset_dynamic_state()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _blink(self, period_frames=20):
        return (self.frame // (period_frames // 2)) % 2 == 0

    def _blit_centered(self, screen, surf, y):
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))

        surging = self.game_state == "PLAYING" and self.ai_phase == AI_PHASE_SURGE

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        border_color = (70, 30, 8)
        if surging and self._blink(16):
            border_color = (235, 45, 45)
        elif self.counter_active and self.game_state == "PLAYING":
            border_color = (240, 200, 60)
        pygame.draw.rect(screen, border_color, table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        # Computer arm flushes red while surging
        c_upper = (215, 95, 75) if surging else (170, 110, 85)
        c_fore = (230, 105, 85) if surging else (185, 125, 95)
        # Player arm turns pale/grey while exhausted, golden during a counter-surge
        if self.exhausted:
            p_upper, p_fore = (165, 150, 145), (180, 165, 160)
        elif self.counter_active:
            p_upper, p_fore = (225, 175, 90), (240, 190, 100)
        else:
            p_upper, p_fore = (200, 145, 110), (215, 160, 125)

        pygame.draw.line(screen, p_upper, p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, p_fore, p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, c_upper, c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, c_fore, c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        # Counter-surge burst ring around the hands
        if self.counter_flash_timer > 0:
            radius = 24 + (int(0.5 * FPS) - self.counter_flash_timer) * 2
            pygame.draw.circle(screen, (255, 220, 80), (hand_x, hand_y), radius, width=4)

        # --- Stamina bar ---------------------------------------------------
        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        if self.counter_active:
            bar_color = (240, 200, 60)
        elif self.exhausted:
            bar_color = (220, 60, 60) if self._blink(20) else (120, 40, 40)
        else:
            bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)
        # Marker showing where input unlocks again
        if self.exhausted:
            mark_x = 140 + int(240 * EXHAUSTION_RECOVERY / self.max_stamina)
            pygame.draw.line(screen, (240, 240, 240), (mark_x, 444), (mark_x, 473), 2)

        if self.exhausted and self.game_state == "PLAYING":
            ex_surf = self.font_med.render("EXHAUSTED!", True, (255, 90, 90))
            screen.blit(ex_surf, (395, 448))
        elif self.stamina <= 25 and self.game_state == "PLAYING":
            low_surf = self.font_small.render("Low stamina", True, (230, 150, 80))
            screen.blit(low_surf, (395, 451))

        # --- AI phase meter (Task 2/3) ------------------------------------
        ai_label = self.font_med.render("AI", True, (220, 220, 220))
        screen.blit(ai_label, (40, 485))
        ai_bg = pygame.Rect(140, 488, 240, 14)
        pygame.draw.rect(screen, (45, 50, 60), ai_bg, border_radius=5)
        progress = 1.0 - (self.ai_phase_timer / max(1, self.ai_phase_length))
        phase_colors = {
            AI_PHASE_NORMAL: (200, 160, 70),
            AI_PHASE_SURGE: (235, 50, 50),
            AI_PHASE_COOLDOWN: (90, 150, 230),
        }
        phase_names = {
            AI_PHASE_NORMAL: "Steady",
            AI_PHASE_SURGE: "SURGING",
            AI_PHASE_COOLDOWN: "Cooling down",
        }
        ai_fill = pygame.Rect(140, 488, int(240 * progress), 14)
        pygame.draw.rect(screen, phase_colors[self.ai_phase], ai_fill, border_radius=5)
        phase_surf = self.font_small.render(phase_names[self.ai_phase], True, phase_colors[self.ai_phase])
        screen.blit(phase_surf, (395, 486))

        # --- Alert banner ---------------------------------------------------
        if self.game_state == "PLAYING":
            banner = None
            if self.counter_active:
                secs = self.counter_bonus_timer / FPS
                banner = (f"COUNTER-SURGE!  x2 PUSH  {secs:0.1f}s", (255, 215, 70), (70, 55, 10))
            elif self.counter_window_timer > 0:
                banner = ("AI IS SPENT - PUSH NOW TO COUNTER!", (120, 255, 140), (15, 60, 25))
            elif surging:
                if self._blink(16):
                    banner = ("!! AI POWER SURGE !!", (255, 255, 255), (170, 25, 25))
                else:
                    banner = ("!! AI POWER SURGE !!", (255, 80, 80), (60, 15, 15))
            elif self.exhausted:
                banner = ("Too tired to push - catch your breath", (255, 150, 150), (55, 25, 25))

            if banner:
                text, fg, bg = banner
                surf = self.font_med.render(text, True, fg)
                box = pygame.Rect(0, 0, surf.get_width() + 36, 40)
                box.center = (self.width // 2, 555)
                pygame.draw.rect(screen, bg, box, border_radius=10)
                pygame.draw.rect(screen, fg, box, width=2, border_radius=10)
                screen.blit(surf, (box.x + 18, box.y + 20 - surf.get_height() // 2))

            hint = self.font_small.render(
                "Alternate LEFT / RIGHT to pull.  Push right after a surge to counter!",
                True, (140, 145, 155))
            self._blit_centered(screen, hint, 592)

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
