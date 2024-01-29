import pygame

from alien_invasion import AlienInvasion

class AITester:

    def __init__(self, ai_game):
        """Automatic player for Alien Invasion."""
        # Make a reference to the game object.
        self.ai_game = ai_game

    def run_game(self):
        """Replaces the original run_game(),
        so we can control the game.
        """
        # Start out in an active state.
        self.ai_game.game_active = True

        # Speed up the game for testing.
        self.ai_game.settings.speedup_scale = 50
        self.ai_game.settings.increase_speed()

        # Start the main loop for the game.
        while True:
            # Still call ai_game._check_events(),
            # so we can use keyboard to quit.
            self.ai_game._check_events()

            # Sweep the ship right and left continuously.
            ship = self.ai_game.ship
            screen_rect = self.ai_game.screen.get_rect()

            if not ship.moving_right and not ship.moving_left:
                # Ship hasn't started moving yet; move to the right.
                ship.moving_right = True
            elif (ship.moving_right
                        and ship.rect.right > screen_rect.right - 10):
                # Ship about to hit right edge; move left.
                ship.moving_right = False
                ship.moving_left = True
            elif ship.moving_left and ship.rect.left < 10:
                ship.moving_left = False
                ship.moving_right = True

            self.ai_game.ship.update()
            self.ai_game._update_bullets()
            self.ai_game._update_aliens()

            # Fire as often as possible.
            self.ai_game._fire_bullet()

            self.ai_game._update_screen()
            self.ai_game.clock.tick(60)

            if self.ai_game.stats.level > 1:
                break

if __name__ == '__main__':
    ai_game = AlienInvasion()

    ai_tester = AITester(ai_game)
    ai_tester.run_game()