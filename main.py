import machine
from neopixel import NeoPixel
import time
import random

LED_RING_PIN = 6
SCORE_LEDS_PIN = 7
PLAYER_PINS = {
    'green': {'button': 4, 'led': 8},
    'red': {'button': 3, 'led': 9},
    'yellow': {'button': 2, 'led': 10},
    'blue': {'button': 1, 'led': 20}
}

RING_LEDS = 60
SCORE_LEDS = 20
LEDS_PER_PLAYER = 5
LEDS_PER_QUADRANT = 15

COLORS = {
    'off': (0, 0, 0),
    'green': (0, 255, 0),
    'red': (255, 0, 0),
    'yellow': (255, 255, 0),
    'blue': (0, 0, 255)
}


class Player:
    def __init__(self, color, button_pin, led_pin, score_start_idx):
        self.color = color
        self.button = machine.Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.button_led = machine.Pin(led_pin, machine.Pin.OUT)
        self.score = 0
        self.score_start_idx = score_start_idx
        self.joined = False
        self.qualified_for_round = True
        self.last_press_time = 0
        self.button_led.value(0)

    def reset_round(self):
        self.qualified_for_round = True
        self.button_led.value(1)

    def check_button(self):
        if not self.button.value():
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.last_press_time) > 200:
                self.last_press_time = current_time
                return True
        return False


class Game:
    def __init__(self):
        self.ring = NeoPixel(machine.Pin(LED_RING_PIN), RING_LEDS)
        self.score_leds = NeoPixel(machine.Pin(SCORE_LEDS_PIN), SCORE_LEDS)
        self.score_led_states = [(0, 0, 0)] * SCORE_LEDS

        self.players = {
            'green': Player('green', PLAYER_PINS['green']['button'],
                            PLAYER_PINS['green']['led'], 0),
            'red': Player('red', PLAYER_PINS['red']['button'],
                          PLAYER_PINS['red']['led'], 5),
            'yellow': Player('yellow', PLAYER_PINS['yellow']['button'],
                             PLAYER_PINS['yellow']['led'], 10),
            'blue': Player('blue', PLAYER_PINS['blue']['button'],
                           PLAYER_PINS['blue']['led'], 15)
        }
        self.round_active = False
        self.fading = False
        self.should_stop = False
        self.clear_all_leds()

    def update_score_led_states(self):
        self.score_led_states = [(0, 0, 0)] * SCORE_LEDS

        for player in self.players.values():
            r, g, b = COLORS[player.color]
            for i in range(LEDS_PER_PLAYER):
                score_idx = player.score_start_idx + i
                if i < player.score:
                    self.score_led_states[score_idx] = (r, g, b)

    def get_quadrant_colors(self):
        return ['yellow', 'red', 'green', 'blue']

    def write_score_leds(self):
        for i, color in enumerate(self.score_led_states):
            self.score_leds[i] = color
        self.score_leds.write()

    def sequential_fade(self, duration_per_quadrant=0.25):
        self.fading = True
        quadrant_colors = self.get_quadrant_colors()

        for quad_idx, color in enumerate(quadrant_colors):
            if self.should_stop:
                self.fading = False
                return None

            start_idx = quad_idx * LEDS_PER_QUADRANT
            steps = 20

            for step in range(steps + 1):
                brightness = 1.0 - (step / steps)

                for i in range(LEDS_PER_QUADRANT):
                    led_idx = start_idx + i
                    r, g, b = COLORS[color]
                    self.ring[led_idx] = (
                        int(r * brightness),
                        int(g * brightness),
                        int(b * brightness)
                    )
                self.ring.write()
                time.sleep(duration_per_quadrant / steps)

                if not self.round_active:
                    for player in self.players.values():
                        if player.check_button() and player.qualified_for_round:
                            self.fading = False
                            return player

        self.clear_ring()
        self.fading = False
        return None

    def clear_ring(self):
        for i in range(RING_LEDS):
            self.ring[i] = COLORS['off']
        self.ring.write()

    def clear_all_leds(self):
        self.clear_ring()
        self.score_led_states = [(0, 0, 0)] * SCORE_LEDS
        for i in range(SCORE_LEDS):
            self.score_leds[i] = (0, 0, 0)
        self.score_leds.write()

    def setup_quadrants(self):
        quadrant_colors = self.get_quadrant_colors()
        for idx, color in enumerate(quadrant_colors):
            start_idx = idx * LEDS_PER_QUADRANT
            for i in range(LEDS_PER_QUADRANT):
                self.ring[start_idx + i] = COLORS[color]
        self.ring.write()

    def update_score_leds(self):
        self.update_score_led_states()
        self.write_score_leds()

    def boot_up_phase(self):
        self.setup_quadrants()
        self.update_score_leds()

        while not all(player.joined for player in self.players.values()):
            for player in self.players.values():
                if not player.joined and player.check_button():
                    player.joined = True
                    player.button_led.value(1)

            time.sleep(0.1)

        self.sequential_fade()
        time.sleep(1)
        return True

    def handle_round(self):
        for player in self.players.values():
            player.reset_round()

        self.setup_quadrants()
        self.update_score_leds()
        self.round_active = True

        start_time = time.time()
        wait_time = random.uniform(3, 8)

        while time.time() - start_time < wait_time:
            for player in self.players.values():
                if player.check_button():
                    player.qualified_for_round = False
                    player.button_led.value(0)

            time.sleep(0.01)

        self.round_active = False
        winner = self.sequential_fade()

        if not winner:
            while any(p.qualified_for_round for p in self.players.values()):
                for player in self.players.values():
                    if player.check_button() and player.qualified_for_round:
                        winner = player
                        break
                time.sleep(0.01)

        if winner:
            winner.score += 1
            self.update_score_leds()

            for i in range(RING_LEDS):
                self.ring[i] = COLORS[winner.color]
            self.ring.write()
            time.sleep(2)

        return winner

    def run_game(self):
        while True:
            self.should_stop = False
            self.score_led_states = [(0, 0, 0)] * SCORE_LEDS
            self.boot_up_phase()

            while True:
                winner = self.handle_round()

                if winner and winner.score >= 5:
                    victory_color = COLORS[winner.color]
                    for i in range(RING_LEDS):
                        self.ring[i] = victory_color
                    self.ring.write()

                    self.score_led_states = [victory_color] * SCORE_LEDS
                    self.write_score_leds()

                    any_button = False
                    while not any_button:
                        for player in self.players.values():
                            if player.check_button():
                                any_button = True
                                break
                        time.sleep(0.01)
                    break

                self.clear_ring()
                self.update_score_leds()
                time.sleep(1)

            for player in self.players.values():
                player.score = 0
                player.joined = False
                player.button_led.value(0)
            self.clear_all_leds()

if __name__ == "__main__":
    game = Game()
    game.run_game()