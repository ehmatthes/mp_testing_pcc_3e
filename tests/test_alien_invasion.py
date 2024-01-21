"""Test the Alien Invasion game.

Test the game by doing the following:
- Add alien_invasion.py to PATH, so we can import it.
- Create a new game object.
- Pass it to AITester.
- Call AITester's run_game().
- Make a few simple assertions about game state.
- Main point is not to test scoring system, but that
  a game can be run successfully.

Only need to focus on the final version of the game, unless any major
  changes made to the game's code.
"""

from pathlib import Path
import os
import importlib
import sys


def test_ai_game():
    """Test basic functionality of the game.

    Running the game does not modify any files.
    So, it can be run using existing venv,
      from the source path.
    We just add the alien_invasion.py path to sys.path,
      so we can import AlienInvasion.
    """

    ai_path = Path(__file__).parents[1] / 'chapter_14' / 'scoring'
    sys.path.insert(0, str(ai_path))
    from alien_invasion import AlienInvasion
    from ai_tester import AITester
    
    os.chdir(ai_path)
    ai_game = AlienInvasion()
    ai_tester = AITester(ai_game)
    ai_tester.run_game()

    assert ai_game.stats.score == 3375
    assert ai_game.stats.level == 2