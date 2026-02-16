# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

- Planned: Leaderboard online, achievement system, daily challenges

---

## [2.6.1] - 2026-02-16

### Added
- Score warning level control in options menu (Option #9 with arrow navigation). (#66)

### Changed
- Options menu extended from 8 to 9 items with "Avvisi Soglie Punteggio" control.
- Options display updated to show "X di 9" instead of "X di 8".

---

## [2.6.0] - 2026-02-16

### Added
- **Score warning system** with 4 verbosity levels (Disabled, Minimal, Balanced, Complete) for TTS penalty announcements.
- Real-time TTS warnings for draw/recycle thresholds based on selected level.
- Persistent score warning level preference with auto-save/load.

### Fixed
- **CRITICAL**: Fixed STOCK_DRAW events never recorded, causing progressive penalties (21/41 draws) to fail.
- Fixed circular import crash blocking test infrastructure.
- Fixed settings persistence crash by adding score_warning_level serialization.

---

## [2.5.1] - 2026-02-15

### Changed
- Improved focus management logging: removed duplicates, moved auto-selection log after success check.

### Added
- Score clamping logging (WARNING level when final score < 0).
- Recycle penalty logging (WARNING level after 3rd recycle).

---

## [2.4.0] - 2026-02-14

### Added
- **5 difficulty presets** (Beginner, Easy, Normal, Expert, Master) with progressive option locking.
- TimerComboBox widget with 13 presets (0-60 minutes) for improved UX.
- Anti-cheat JSON validation on settings load.

### Changed
- **BREAKING**: `difficulty` field changed from `int` to `DifficultyLevel` enum.
- Timer UI simplified from CheckBox+ComboBox to single TimerComboBox widget.
- Expert/Master presets now lock timer and draw count options.

---

## [2.3.0] - 2026-02-14

### Added
- Centralized logging system with file rotation (5MB max, 5 backups).
- 15+ semantic helper functions for game/UI/error events.
- Application lifecycle logging (startup/shutdown).

---

## [2.2.1] - 2026-02-14

### Fixed
- **CRITICAL**: Fixed async dialogs not closing when clicking YES/NO buttons.
- Fixed ESC/ALT+F4 handlers with semi-modal pattern (ShowModal + wx.CallAfter).

### Changed
- Migrated all async dialogs to semi-modal pattern for stable event handling.
- Always-veto-first pattern for EVT_CLOSE to prevent premature exits.

---

## [2.2.0] - 2026-02-14

### Added
- **DependencyContainer** for IoC with thread-safe resolution and circular dependency detection.
- **ViewFactory** for centralized window creation with DI.
- **WidgetFactory** for accessible widget creation (buttons, sizers).
- **WindowController** for hierarchical window lifecycle management.
- Async dialog API: `show_yes_no_async()`, `show_info_async()`, `show_error_async()`.

### Changed
- Migrated all dialogs from blocking ShowModal() to async callback pattern.
- Simplified event loop: removed ~50 LOC of dialog state management.

### Deprecated
- `WxDialogProvider.show_yes_no()` - Use `show_yes_no_async()` (removal in v3.0).
- `WxDialogProvider.show_alert()` - Use `show_info_async()` (removal in v3.0).

---

## [2.1.0] - 2026-02-14

### Changed
- Enhanced documentation for deferred UI pattern (`self.app.CallAfter()`).
- Complete codebase audit for CallAfter pattern compliance (100% validated).
- Architectural documentation added to ARCHITECTURE.md.

---

## [2.0.9] - 2026-02-14

### Fixed
- **CRITICAL**: Fixed `AssertionError: No wx.App created yet` by replacing `wx.CallAfter()` with `self.app.CallAfter()`.

---

## [2.0.8] - 2026-02-14

### Fixed
- **CRITICAL**: Fixed `RuntimeError: wxYield called recursively` by removing `wx.SafeYield()` from `ViewManager.show_panel()`.

---

## [2.0.7] - 2026-02-14

### Fixed
- **CRITICAL**: Fixed `AttributeError: 'SolitarioFrame' object has no attribute 'CallAfter'` by using `wx.CallAfter()` (wxPython 4.1.1 compatible).

---

## [2.0.6] - 2026-02-14

### Fixed
- **CRITICAL**: Fixed hang on deferred transitions by replacing `wx.CallLater()` with `self.frame.CallAfter()` (0ms delay, 100% reliable).

---

## [2.0.5] - 2026-02-14

### Fixed
- **CRITICAL**: Fixed app hang after panel transitions by replacing `wx.CallAfter()` with `wx.CallLater(10, ...)` for timer-based execution.

---

## [2.0.4] - 2026-02-13

### Fixed
- **CRITICAL**: Fixed panel swap crash during event handling using `wx.CallAfter()` deferred UI pattern.
- ESC abandon, decline rematch, and timeout defeat now use deferred transitions.

---

## [2.0.3] - 2026-02-13

### Fixed
- **CRITICAL**: Fixed race condition in `show_panel()` by adding `wx.SafeYield()` before hide loop.
- Prevented redundant hide operations on target panel.

---

## [2.0.2] - 2026-02-13

### Fixed
- **CRITICAL**: Fixed crash on return to menu by inverting operation order (Hide → Reset → Show).

---

## [2.0.0] - 2026-02-12

### Changed
- **BREAKING**: Migrated from Pygame to wxPython-only event loop.

### Added
- `wx_app.py`, `wx_frame.py`, `wx_menu.py`, `wx_key_adapter.py` for wxPython infrastructure.
- New `test.py` entry point (wxPython-based).

### Removed
- **BREAKING**: `pygame==2.1.2` and `pygame-menu==4.3.7` dependencies.

---

## [1.8.0] - 2026-02-13

### Added
- Native wx widgets for all 8 options (RadioBox, CheckBox, ComboBox).
- Save/Cancel buttons with mnemonics (ALT+S/ALT+A).
- ESC with change tracking and confirmation dialog.

### Changed
- Options navigation migrated from virtual (arrows/numbers) to native wxPython (TAB standard).

### Fixed
- Reset gameplay on ESC abandon, timeout, decline rematch, and double-ESC.

### Removed
- Virtual options navigation (arrows/numbers replaced by TAB).

---

## [1.7.5] - 2026-02-13

### Fixed
- **CRITICAL**: Fixed ALT+F4 infinite loop by removing recursive `frame.Close()` call.
- Fixed exit dialog validation with null check for `dialog_manager`.
- Fixed options navigation TTS by passing `screen_reader` to `OptionsDialog`.

### Added
- ESC handling in MenuPanel with exit confirmation.
- Complete keyboard support for options 6-8 (hints, scoring, timer mode).

---

## [1.7.3] - 2026-02-13

### Changed
- **BREAKING**: Migrated to single-frame panel-swap architecture (wxPython standard).
- `BasicView(wx.Frame)` → `BasicPanel(wx.Panel)`.
- `ViewManager`: Frame stack → Panel dictionary (show/hide).

---

## [1.7.1] - 2026-02-12

### Fixed
- **CRITICAL**: Fixed `TypeError: unexpected keyword argument 'parent'` in `WxDialogProvider` by changing to `parent_frame=`.

---

## [1.6.1] - 2026-02-11

### Changed
- Replaced all `VirtualDialogBox` (TTS-only) with native wxPython dialogs.
- Centralized dialog management with `SolitarioDialogManager`.

### Added
- Native dialogs for ESC gameplay, N key, submenu ESC, main menu ESC, options save.

### Removed
- 4 VirtualDialogBox attributes and ~50 LOC dialog state management.

---

## [1.6.0] - 2026-02-11

### Added
- **Victory flow system** with statistics snapshot, score calculation, native dialogs, and rematch prompt.
- Native dialogs: `show_alert()`, `show_yes_no()`, `show_input()`.
- Suit statistics tracking and final report formatter.
- Debug victory command (CTRL+ALT+W).

---

## [1.5.2.5] - 2026-02-11

### Changed
- Rebalanced deck bonuses: Neapolitan +50 (was 0), French +75 (was 150).
- Timer mandatory for difficulty levels 4-5 with enforced ranges.
- Auto-preset draw count for levels 1-3 (1/2/3 cards).
- Scoring mandatory from level 3 (was level 4).

---

## [1.5.2.4] - 2026-02-11

### Fixed
- Fixed draw count bug: `engine.draw_count` now uses `settings.draw_count` directly.

### Changed
- Extended constraints for difficulty 4-5: hints disabled, scoring enabled, timer strict (level 5).

---

## [1.5.2.3] - 2026-02-11

### Fixed
- Fixed game state reset on abandon: now calls `engine.reset_game()`.
- Added timer announcement flag reset to prevent issues.

---

## [1.5.2.2] - 2026-02-11

### Added
- **Timer mode** option #8: STRICT (auto-end on timeout) vs PERMISSIVE (-100 points/min overtime).
- Periodic timer check event (1000ms) for mode-aware expiration.

---

## [1.5.2.1] - 2026-02-11

### Fixed
- **CRITICAL**: Fixed draw count not applied for levels 4-5 (always drew 1 card instead of 3).
- **CRITICAL**: Fixed timer constraints validation incomplete for levels 4-5.

---

## [1.5.2] - 2026-02-11

### Added
- **Complete scoring system v2** with 7 event types, 5 difficulty levels, and persistent statistics.
- Score bonuses: deck type, draw count, time, victory (+500).
- Difficulty multipliers: 1.0x (Easy) to 2.5x (Master).
- JSON storage for score history and statistics (up to 100 scores).
- Score commands: P (current score), SHIFT+P (last 5 events).

### Changed
- Options menu extended with #3 (Draw Count 1/2/3) and #7 (Scoring ON/OFF).

---

## [1.5.1] - 2026-02-10

### Changed
- Timer cycling improved: ENTER cycles with 5-min increments and wrap-around (OFF → 5 → ... → 60 → 5).
- Timer display enhanced: contextual info (elapsed vs remaining) with T command during gameplay.

---

## [1.5.0] - 2026-02-10

### Added
- **Command hints** option #5 with 17 contextual hints (Active/Disabled).
- Hint generation in Domain layer, conditional vocalization in Application layer.

---

## [1.4.3] - 2026-02-11

### Fixed
- **CRITICAL**: Fixed deck type not applied from settings (F1 French ↔ Neapolitan).
- **CRITICAL**: Fixed suit validation for aces (any ace → correct suit only).
- **CRITICAL**: Fixed settings ignored in `new_game()` (deck, difficulty, timer, shuffle).
- **CRITICAL**: Fixed double distribution crash on deck change (IndexError).
- **CRITICAL**: Fixed auto-recycle requiring double draw press (now auto-recycle + draw in one).
- Fixed confusing TTS sequence during auto-recycle (problem → solution → result).

### Added
- Double-tap auto-selection for piles 1-7 and SHIFT+1-4.
- Numeric menu shortcuts (1-5) for main and in-game menus.
- New game confirmation dialog when game already in progress.

---

## [1.4.2] - 2026-02-09

### Added
- `VirtualDialogBox` component with keyboard navigation and TTS.
- ESC confirmation dialogs in main menu, game submenu, and gameplay.
- Double-ESC quick exit feature (<2s threshold).
- Welcome message system for submenus with control hints.

---

## [1.4.1] - 2026-02-08

### Added
- **Virtual options window** with HYBRID navigation (arrows + numbers 1-5).
- 5 options: Deck Type, Difficulty (1-3), Timer (OFF/5-60min), Shuffle Mode, Future.
- State machine (CLOSED/OPEN_CLEAN/OPEN_DIRTY) with snapshot save/discard.
- Commands: O (open), ↑↓/1-5 (navigate), ENTER/+/-/T (modify), I (recap), H (help), ESC (close).

### Deprecated
- F1-F5 direct settings shortcuts (replaced by options window).

---

## [1.4.0] - 2026-02-08

### Added
- **Clean Architecture migration** complete with 4 layers (Domain, Application, Infrastructure, Presentation).
- DI Container for dependency management with factory methods.
- Integration test suite (14 tests) validating architecture.
- New entry point: `test.py` (Clean Arch) coexists with `acs.py` (legacy).

---

## [1.3.3] - 2026-02-06

### Fixed
- **CRITICAL**: Fixed crash on deck change (F1) by dynamic reserve calculation (24 vs 12 cards).
- **CRITICAL**: Fixed Neapolitan King (value 10) blocked on empty piles (now uses `is_king()` method).

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

---

**For detailed technical changes, see commit history or [docs/DETAILED_CHANGELOG.md](docs/DETAILED_CHANGELOG.md)**

[Unreleased]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.6.1...HEAD
[2.6.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.6.0...v2.6.1
[2.6.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.5.1...v2.6.0
[2.5.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.4.0...v2.5.1
[2.4.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.2.1...v2.3.0
[2.2.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.9...v2.1.0
[2.0.9]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.8...v2.0.9
[2.0.8]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.7...v2.0.8
[2.0.7]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.6...v2.0.7
[2.0.6]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.5...v2.0.6
[2.0.5]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.4...v2.0.5
[2.0.4]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v2.0.0...v2.0.2
[2.0.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.8.0...v2.0.0
[1.8.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.7.5...v1.8.0
[1.7.5]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.7.3...v1.7.5
[1.7.3]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.7.1...v1.7.3
[1.7.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.6.1...v1.7.1
[1.6.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.2.5...v1.6.0
[1.5.2.5]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.2.4...v1.5.2.5
[1.5.2.4]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.2.3...v1.5.2.4
[1.5.2.3]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.2.2...v1.5.2.3
[1.5.2.2]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.2.1...v1.5.2.2
[1.5.2.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.2...v1.5.2.1
[1.5.2]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.4.3...v1.5.0
[1.4.3]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.4.2...v1.4.3
[1.4.2]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Nemex81/solitario-classico-accessibile/compare/v1.3.3...v1.4.0
[1.3.3]: https://github.com/Nemex81/solitario-classico-accessibile/releases/tag/v1.3.3