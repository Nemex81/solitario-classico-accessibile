"""Dialog implementations based on wxPython.

This module provides concrete dialog implementations for the application.
All dialogs depend on wxPython and belong to Infrastructure layer.
"""

from .abandon_dialog import AbandonDialog
from .detailed_stats_dialog import DetailedStatsDialog
from .game_info_dialog import GameInfoDialog
from .last_game_dialog import LastGameDialog
from .leaderboard_dialog import LeaderboardDialog
from .victory_dialog import VictoryDialog

__all__ = [
    'AbandonDialog',
    'DetailedStatsDialog',
    'GameInfoDialog',
    'LastGameDialog',
    'LeaderboardDialog',
    'VictoryDialog',
]
