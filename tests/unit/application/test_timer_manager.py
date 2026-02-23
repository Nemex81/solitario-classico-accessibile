"""Unit tests for TimerManager callbacks and behavior."""

import time
from typing import List

import pytest

from src.application.timer_manager import TimerManager


def test_warning_callback_fires_once_per_interval():
    calls: List[int] = []

    def on_warning(minutes_left: int) -> None:
        calls.append(minutes_left)

    # 3-minute timer with warnings at 2 and 1
    tm = TimerManager(minutes=3, warning_callback=on_warning, warning_intervals=[2, 1])
    tm.start()

    # Simulate passage of time by monkeypatching get_remaining
    # We'll override duration_seconds so that checks see appropriate remaining minutes.
    tm.duration_seconds = 180  # 3 minutes in seconds

    # Helper to fake remaining
    def fake_remaining(seconds):
        return seconds

    # First check, 3 minutes remaining -> no warnings
    tm.get_remaining = lambda: 180
    tm.check_warnings()
    assert calls == []

    # 2 minutes remaining -> first warning
    tm.get_remaining = lambda: 120
    tm.check_warnings()
    assert calls == [2]

    # Still 2 minutes (should not repeat)
    tm.check_warnings()
    assert calls == [2]

    # 1 minute remaining -> second warning
    tm.get_remaining = lambda: 60
    tm.check_warnings()
    assert calls == [2, 1]


def test_expired_callback_and_reset():
    expired_called = False

    def on_expired():
        nonlocal expired_called
        expired_called = True

    tm = TimerManager(minutes=1, expired_callback=on_expired)
    tm.start()

    # simulate expiration by overriding is_expired (simpler than changing elapsed)
    tm.is_expired = lambda: True
    tm.check_warnings()
    assert expired_called is True

    # calling again shouldn't trigger again
    expired_called = False
    tm.check_warnings()
    assert expired_called is False

    # after reset, callback can fire again
    tm.reset(minutes=1)
    tm.start()
    tm.get_remaining = lambda: 0
    tm.check_warnings()
    assert expired_called is True


def test_invalid_minutes_raises():
    with pytest.raises(ValueError):
        TimerManager(minutes=0)
    with pytest.raises(ValueError):
        TimerManager(minutes=61)
