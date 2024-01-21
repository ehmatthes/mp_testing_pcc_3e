"""Test the Alien Invasion game."""

from pathlib import Path
import os
import importlib
import sys

import pytest

import utils


@pytest.fixture(scope='module', autouse=True)
def check_pygame_version(request, python_cmd):
    """Check if the correct version of Pygame is installed."""
    pygame_version = request.config.getoption("--pygame-version")

    if pygame_version:
        print(f"\n*** Installing pygame {pygame_version}\n")

        cmd = f"{python_cmd} -m pip install pygame=={pygame_version}"
        output = utils.run_command(cmd)
    else:
        print("\nUsing existing pygame version.")


def test_ai_game():
    """Test basic functionality of the game."""

    # Add source path to sys.path, so we can import AlienInvasion.
    ai_path = Path(__file__).parents[1] / 'chapter_14' / 'scoring'
    sys.path.insert(0, str(ai_path))
    from alien_invasion import AlienInvasion
    from ai_tester import AITester
    
    # Create a game instance, and an AITester instance, and run game.
    os.chdir(ai_path)
    ai_game = AlienInvasion()
    ai_tester = AITester(ai_game)
    ai_tester.run_game()

    # Make assertions to ensure first level was played through.
    assert ai_game.stats.score == 3375
    assert ai_game.stats.level == 2