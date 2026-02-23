"""wxPython-based entry point for Solitario Classico Accessibile.

This is the v2.0.0 entry point that replaces pygame event loop with wxPython MainLoop().
Maintains 100% functionality of pygame-based test.py while improving NVDA accessibility.

Clean Architecture: Application Entry Point
Dependency: wxPython 4.1.x+ (no pygame required)
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    python wx_main.py

Migration from pygame (v1.x):
    - Replaces pygame.event.get() with wx.EVT_KEY_DOWN
    - Replaces pygame.time.set_timer() with wx.Timer
    - Maintains all gameplay logic unchanged
    - Compatible with existing GameEngine, GamePlayController

New in v2.0.0: Complete pygame removal - wxPython-only audiogame
"""

import logging
import sys
import time
import wx

# Application layer
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController
from src.application.dialog_manager import SolitarioDialogManager

# Domain layer
from src.domain.services.game_settings import GameSettings

# Infrastructure layer - Dependency Injection (v2.2.0)
from src.infrastructure.di.dependency_container import DependencyContainer
from src.infrastructure.ui.window_controller import WindowController
from src.infrastructure.ui.factories import ViewFactory, WindowKey

# Infrastructure layer - UI components (wxPython)
from src.infrastructure.ui.wx_app import SolitarioWxApp
from src.infrastructure.ui.wx_frame import SolitarioFrame
# WxVirtualMenu removed in v1.7.4 - replaced by MenuPanel + OptionsDialog
from src.infrastructure.ui.view_manager import ViewManager
from src.infrastructure.ui.menu_panel import MenuPanel
from src.infrastructure.ui.gameplay_panel import GameplayPanel

# Infrastructure layer - Accessibility
from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.accessibility.tts_provider import create_tts_provider

# Infrastructure layer - Logging (v2.3.0)
from src.infrastructure.logging import setup_logging
from src.infrastructure.logging import game_logger as log


class SolitarioController:
    """Main application controller for wxPython-based audiogame.
    
    Manages application lifecycle and orchestrates menu ↔ gameplay ↔ options flow
    using wxPython event loop instead of pygame.
    
    Architecture:
    - Entry point depends on Application + Infrastructure layers
    - Uses Clean Architecture with dependency injection
    - Event routing: wx.KeyEvent → menu/gameplay handlers
    - Timer management: wx.Timer → timeout checks
    
    Attributes:
        app: SolitarioWxApp (wxPython application)
        frame: SolitarioFrame (visible minimized frame)
        view_manager: ViewManager for multi-window stack
        screen_reader: ScreenReader with TTS provider
        settings: GameSettings for configuration
        engine: GameEngine facade for game logic
        gameplay_controller: Keyboard command orchestrator
        dialog_manager: wxDialog provider for native dialogs
        
        # State flags
        is_menu_open: DEPRECATED - use view_manager instead
        is_options_mode: Options window active
        last_esc_time: DEPRECATED - moved to GameplayView
        _timer_expired_announced: Prevents repeated timeout messages
    
    Example:
        >>> controller = SolitarioController()
        >>> controller.run()  # Blocks until app closes
    """
    
    # Double-ESC feature threshold (seconds)
    DOUBLE_ESC_THRESHOLD = 2.0
    
    def __init__(self):
        """Initialize application with all components."""
        log.debug_state("app_startup", {"version": "v3.2.2", "status": "starting"})
        
        # v3.2.2: Initialize DependencyContainer (bridge mode)
        log.debug_state("dependency_container_init", {"status": "starting"})
        self.container = DependencyContainer()
        
        # Infrastructure: TTS setup
        log.debug_state("tts_init", {"status": "starting"})
        try:
            tts_provider = create_tts_provider(engine="auto")
            self.screen_reader = ScreenReader(
                tts=tts_provider,
                enabled=True,
                verbose=False
            )
            log.debug_state("tts_ready", {"status": "initialized"})
        except Exception as e:
            log.warning_issued("SolitarioController", f"TTS initialization failed: {e}")
            self.screen_reader = self._create_dummy_sr()
        
        # Domain: Game settings
        log.debug_state("game_settings_init", {"status": "starting"})
        self.settings = GameSettings()
        log.debug_state("game_settings_ready", {"status": "initialized"})
        
        # v3.1.0: Initialize ProfileService
        log.debug_state("profile_service_init", {"status": "starting"})
        from src.domain.services.profile_service import ProfileService
        self.profile_service = ProfileService()
        
        # Ensure guest profile exists (auto-create if missing)
        self.profile_service.ensure_guest_profile()
        
        # Look for default profile (is_default=True)
        all_profiles = self.profile_service.list_profiles()
        default_profile = None
        for p in all_profiles:
            if p.get('is_default', False):
                default_profile = p
                break
        
        # Load default profile if found, otherwise load guest
        if default_profile:
            profile_id = default_profile['profile_id']
            if self.profile_service.load_profile(profile_id):
                log.info_query_requested("default_profile_load", f"loaded_{default_profile['profile_name']}")
            else:
                # Fallback to guest if default profile is corrupted
                log.warning_issued("SolitarioController", "Default profile corrupted, fallback to guest")
                self.profile_service.load_profile("profile_000")
        else:
            # No default profile set, use guest
            self.profile_service.load_profile("profile_000")
            log.debug_state("profile_load", {"type": "guest", "reason": "no_default_set"})
        
        log.debug_state("profile_service_ready", {
            "active_profile": self.profile_service.active_profile.profile_name,
            "profile_id": self.profile_service.active_profile.profile_id
        })
        
        # Infrastructure: Dialog manager (v2.0.1 - initialized after frame in run())
        # Will be set in run() after frame is created (hs_deckmanager pattern)
        self.dialog_manager = None
        
        # Application: Game engine setup
        log.debug_state("game_engine_init", {"status": "starting"})
        self.engine = GameEngine.create(
            audio_enabled=(self.screen_reader is not None),
            tts_engine="auto",
            verbose=1,
            settings=self.settings,
            use_native_dialogs=True,
            parent_window=None,  # wx dialogs don't need parent
            profile_service=self.profile_service  # 🆕 NEW v3.1.0
        )
        
        # Inject end game callback for UI state management
        self.engine.on_game_ended = self.handle_game_ended
        log.debug_state("game_engine_ready", {"status": "initialized"})
        
        # Prepare audio subsystem
        log.debug_state("audio_manager_init", {"status": "starting"})
        self.audio_manager = self.container.get_audio_manager()
        if hasattr(self.audio_manager, 'initialize'):
            self.audio_manager.initialize()
        log.debug_state("audio_manager_ready", {"status": "initialized"})
        
        # Application: Gameplay controller
        log.debug_state("gameplay_controller_init", {"status": "starting"})
        self.gameplay_controller = GamePlayController(
            engine=self.engine,
            screen_reader=self.screen_reader,
            settings=self.settings,
            on_new_game_request=self.show_new_game_dialog,
            audio_manager=self.audio_manager  # pass audio manager for effects
        )
        log.debug_state("gameplay_controller_ready", {"status": "initialized"})
        
        # Dialog manager will be passed to options_controller in run()
        
        # State flags (v2.0.1 - hybrid legacy + ViewManager)
        self.is_menu_open = True  # App starts in menu
        self.is_options_mode = False
        self._timer_expired_announced = False
        
        # wxPython components (created in run())
        self.app: SolitarioWxApp = None
        self.frame: SolitarioFrame = None
        self.view_manager: ViewManager = None
        
        # v2.2.0: Register dependencies in container (bridge mode)
        self._register_dependencies()
        
        log.debug_state("app_ready", {
            "architecture": "clean",
            "ui_framework": "wxPython",
            "container_version": "v2.2.0",
            "status": "initialized"
        })
    
    def _register_dependencies(self) -> None:
        """Register application dependencies in DependencyContainer.
        
        v2.2.0: Bridge implementation - registers dependencies but existing
        initialization is maintained for compatibility. Future commits will
        migrate to full container-based resolution.
        
        Registration order:
            1. Infrastructure: TTS, ScreenReader
            2. Domain: GameSettings  
            3. Application: GameEngine, Controllers
            4. Infrastructure: WindowController
        
        Note:
            This is a preparatory step. Full migration to DI-based initialization
            will be completed in subsequent commits as async dialog API is integrated.
        
        Version:
            v2.2.0: Initial bridge implementation
        """
        log.debug_state("register_dependencies", {"phase": "start"})
        
        # 1. Infrastructure: TTS/ScreenReader
        self.container.register(
            "tts_provider",
            lambda: create_tts_provider(engine="auto")
        )
        self.container.register(
            "screen_reader",
            lambda: self.screen_reader  # Use existing instance
        )
        
        # 2. Domain: Settings
        self.container.register(
            "settings",
            lambda: self.settings  # Use existing instance
        )
        
        # 3. Application: Engine and Controllers
        self.container.register(
            "engine",
            lambda: self.engine  # Use existing instance
        )
        self.container.register(
            "gameplay_controller",
            lambda: self.gameplay_controller  # Use existing instance
        )
        # register audio manager so other components may request it
        self.container.register(
            "audio_manager",
            lambda: getattr(self, 'audio_manager', None)
        )
        
        # 4. Infrastructure: WindowController (for future async dialog integration)
        self.container.register(
            "window_controller",
            lambda: WindowController(container=self.container)
        )
        
        log.debug_state("register_dependencies", {"phase": "end", "status": "configured"})
    
    def _create_dummy_sr(self):
        """Create dummy screen reader for silent mode."""
        class DummySR:
            class DummyTTS:
                def speak(self, text, interrupt=True):
                    log.tts_spoken(f"[DUMMY_MODE] {text}", interrupt)
            tts = DummyTTS()
        return DummySR()
    
    # === MENU HANDLERS (v2.0.1 - Updated for ViewManager) ===
    
    def start_gameplay(self) -> None:
        """Start gameplay (called from MenuPanel or rematch).
        
        Shows GameplayPanel via ViewManager, initializing new game.
        Previous panel (menu or gameplay) is hidden but remains in memory.
        
        Handles two scenarios:
        1. Menu → Gameplay: Hide menu, show gameplay
        2. Gameplay → Gameplay (rematch): Hide gameplay, show gameplay
        
        Note:
            Uses show_panel() instead of push_view() (panel-swap pattern).
            
        Version:
            v2.0.1: Initial implementation for menu→gameplay
            v2.4.2: Added explicit panel hiding for rematch support (Bug #68)
        """
        if self.view_manager:
            # CRITICAL: Hide current panel before showing gameplay
            # This handles both menu→gameplay AND rematch (gameplay→gameplay)
            current_panel_name = self.view_manager.get_current_view()
            
            if current_panel_name:
                current_panel = self.view_manager.get_panel(current_panel_name)
                if current_panel:
                    current_panel.Hide()
            
            # Show gameplay panel (logs transition internally)
            self.view_manager.show_panel('gameplay')
            self.is_menu_open = False  # Sync flag: now in gameplay
            
            # Initialize game
            self.engine.reset_game()
            self.engine.new_game()
            self._timer_expired_announced = False
            
            if self.screen_reader:
                self.screen_reader.tts.speak(
                    "Nuova partita avviata! Usa H per l'aiuto comandi.",
                    interrupt=True
                )
    
    def return_to_menu(self) -> None:
        """Return from gameplay to menu (show MenuPanel only).
        
        IMPORTANT: This method should ONLY be called via wx.CallAfter() from
        deferred handlers, never directly from event handlers or callbacks.
        
        Defer Pattern (CRITICAL - Always use this):
            ✅ CORRECT: Call via wx.CallAfter() from deferred handlers
                Example from _safe_abandon_to_menu():
                    def _safe_abandon_to_menu(self):
                        gameplay_panel.Hide()
                        self.engine.reset_game()
                        self.return_to_menu()  # ← Safe: Called from deferred context
            
            ❌ WRONG: Call directly from event handlers
                Example from show_abandon_game_dialog() (DON'T DO THIS):
                    def show_abandon_game_dialog(self):
                        result = self.dialog_manager.show_abandon_game_prompt()
                        if result:
                            self.return_to_menu()  # ← CRASH: Nested event loop
        
        Caller Responsibility:
            Before calling this method, the caller MUST:
            1. Hide gameplay panel explicitly (panel.Hide())
            2. Reset game engine (engine.reset_game())
            3. Then call return_to_menu() to show menu
        
        This method only handles:
            - Showing menu panel via ViewManager
            - Setting application state flag
            - TTS announcement
        
        Version:
            v2.0.2: Added diagnostics + clarified caller responsibility
            v2.0.4: Simplified after wx.CallAfter() pattern implementation
        """
        if not self.view_manager:
            log.warning_issued("SolitarioController", "ViewManager not initialized")
            return
        
        # Show menu panel (logs transition internally)
        self.view_manager.show_panel('menu')
        
        # Update state
        self.is_menu_open = True
        
        # Announce via TTS
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu principale.",
                interrupt=True
            )
    
    def show_options(self) -> None:
        """Show options window using OptionsDialog with native wx widgets.
        
        Opens modal OptionsDialog with:
        - Native wx.RadioBox, wx.CheckBox, wx.ComboBox for all 8 options
        - Salva/Annulla buttons
        - Smart ESC (confirmation if modifications present)
        
        Flow:
        1. Set is_options_mode flag
        2. Call controller.open_window() (sets state=OPEN_CLEAN, saves snapshot)
        3. Vocalize opening message (optional)
        4. Create OptionsDialog with controller + screen_reader
        5. Show modal (blocks until closed)
        6. Clean up and reset flag
        
        State Management:
        - controller.open_window() saves settings snapshot for change tracking
        - Any widget change sets state to OPEN_DIRTY
        - ESC with OPEN_DIRTY triggers save confirmation dialog
        - Buttons or ESC with OPEN_CLEAN close directly
        
        Navigation:
        - TAB: Move between widgets (standard wx)
        - UP/DOWN: Change value in RadioBox/ComboBox
        - SPACE: Toggle CheckBox
        - ENTER: Activate focused button
        - ESC: Smart close (confirmation if dirty)
        """
        from src.infrastructure.ui.options_dialog import OptionsDialog
        
        self.is_options_mode = True
        
        # Initialize controller state (OPEN_CLEAN, save snapshot)
        open_msg = self.gameplay_controller.options_controller.open_window()
        if self.screen_reader:
            self.screen_reader.tts.speak(open_msg, interrupt=True)
            wx.MilliSleep(500)  # Brief pause before showing dialog
        
        # Log dialog opening
        log.dialog_shown("options", "Impostazioni di Gioco")
        
        # Create and show modal options dialog
        dlg = OptionsDialog(
            parent=self.frame,
            controller=self.gameplay_controller.options_controller,
            screen_reader=self.screen_reader
        )
        result = dlg.ShowModal()
        
        # Log dialog closing with result
        result_str = "saved" if result == wx.ID_OK else "cancelled"
        log.dialog_closed("options", result_str)
        
        dlg.Destroy()
        
        self.is_options_mode = False
    
    def show_exit_dialog(self) -> None:
        """Show exit confirmation dialog (called from MenuPanel).
        
        Delegates to quit_app() which shows dialog and handles exit.
        
        Version:
            v1.7.5: Simplified to delegate to quit_app()
        """
        # Fallback if dialog_manager not initialized
        if not self.dialog_manager or not hasattr(self.dialog_manager, 'is_available'):
            log.warning_issued("DialogManager", "Not available, exiting directly")
            sys.exit(0)
            return
        
        # Delegate to quit_app() which now shows dialog
        self.quit_app()
    
    def show_last_game_summary(self) -> None:
        """Show last game summary dialog (called from MenuPanel).
        
        Displays LastGameDialog with summary of most recent game.
        
        Version:
            v3.1.0 Phase 9.1
        """
        if self.engine and hasattr(self.engine, 'show_last_game_summary'):
            self.engine.show_last_game_summary()
    
    def show_leaderboard(self) -> None:
        """Show global leaderboard dialog (called from MenuPanel).
        
        Displays LeaderboardDialog with rankings across all profiles.
        
        Version:
            v3.1.0 Phase 9.2
        """
        import wx
        from src.presentation.dialogs.leaderboard_dialog import LeaderboardDialog
        
        log.info_query_requested("leaderboard", "main_menu")
        
        # Check if ProfileService is available
        if not self.engine or not hasattr(self.engine, 'profile_service'):
            log.warning_issued("SolitarioController", "ProfileService not available for leaderboard")
            wx.MessageBox(
                "Servizio profili non disponibile.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        profile_service = self.engine.profile_service
        if profile_service is None:
            log.warning_issued("SolitarioController", "ProfileService not initialized")
            wx.MessageBox(
                "Servizio profili non inizializzato.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        # Load all profiles with full stats (using ProfileService helper)
        # This respects Clean Architecture: Controller -> Service -> Storage
        profiles_with_stats = profile_service.get_all_profiles_with_stats()
        
        # Get current profile ID
        current_profile_id = profile_service.active_profile.profile_id if profile_service.active_profile else "guest"
        
        # Show leaderboard dialog
        dialog = LeaderboardDialog(None, profiles_with_stats, current_profile_id, metric="victories")
        dialog.ShowModal()
        dialog.Destroy()
    
    def show_profile_menu(self) -> None:
        """Show profile management menu (called from MenuPanel).
        
        Displays ProfileMenuPanel modal dialog with 6 profile management options.
        
        Version:
            v3.1.0 Phase 10.4
        """
        import wx
        from src.infrastructure.ui.profile_menu_panel import ProfileMenuPanel
        
        log.info_query_requested("profile_menu", "main_menu")
        
        # Check if ProfileService and engine available
        if not self.engine or not hasattr(self.engine, 'profile_service'):
            log.warning_issued("SolitarioController", "ProfileService not available for profile menu")
            wx.MessageBox(
                "Servizio profili non disponibile.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        profile_service = self.engine.profile_service
        if profile_service is None:
            log.warning_issued("SolitarioController", "ProfileService not initialized")
            wx.MessageBox(
                "Servizio profili non inizializzato.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        # Show profile menu panel
        panel = ProfileMenuPanel(None, profile_service, self.screen_reader)
        panel.ShowModal()
        panel.Destroy()
        
        log.dialog_closed("profile_menu", "closed")
    
    # ============================================================================
    # DEFERRED UI TRANSITIONS PATTERN (v2.4.3)
    # ============================================================================
    # CRITICAL: All UI panel transitions MUST use wx.CallAfter()
    #
    # Rationale:
    #   - wxPython 4.1.1: CallAfter is a module-level function, not instance method
    #   - wx.CallAfter() schedules callback execution after current event completes
    #   - Prevents nested event loops and modal dialog crashes
    #   - Ensures safe UI state transitions after dialog dismissal
    #
    # Pattern Flow:
    #   1. Event handler executes (ESC, timer, game end callback)
    #   2. Shows dialog if needed (modal, blocking)
    #   3. Calls wx.CallAfter(deferred_method) to schedule UI transition
    #   4. Returns immediately (event handler completes)
    #   5. [wxPython idle loop processes deferred call]
    #   6. Deferred method executes (safe context, no nested loops)
    #   7. Panel swap, state reset, UI updates happen safely
    #
    # Correct Usage:
    #   ✅ wx.CallAfter(self._safe_abandon_to_menu)
    #   ✅ wx.CallAfter(self.start_gameplay)
    #   ✅ wx.CallAfter(self._safe_return_to_main_menu)
    #
    # Anti-Patterns to AVOID:
    #   ❌ self.app.CallAfter() - Not an instance method in wxPython 4.1.1
    #   ❌ wx.SafeYield() - Creates nested event loop, causes crashes
    #   ❌ Direct panel swaps from handlers - Synchronous, nested loops
    #
    # Version History:
    #   v2.0.3: Added wx.SafeYield() (mistaken belief, caused crashes)
    #   v2.0.4: Introduced wx.CallAfter() defer pattern
    #   v2.0.6-v2.0.9: Experimented with self.app.CallAfter() (incorrect API)
    #   v2.4.3: DEFINITIVE FIX - wx.CallAfter() global function (correct API)
    # ============================================================================
    
    def show_abandon_game_dialog(self) -> None:
        """Show abandon game confirmation dialog (non-blocking).
        
        Uses async dialog API to prevent nested event loops.
        Callback invoked after user responds.
        
        Called from:
            GameplayPanel._handle_esc() when ESC pressed during gameplay
        
        Dialog behavior:
            - Title: "Abbandono Partita"
            - Message: "Vuoi abbandonare la partita e tornare al menu di gioco?"
            - Non-blocking Show() (not ShowModal)
            - Callback pattern for result handling
        
        Async Pattern Benefits:
            ✅ No nested event loops (Show vs ShowModal)
            ✅ No wx.CallAfter needed (callback already deferred by dialog)
            ✅ Better focus management
            ✅ Screen reader friendly
        
        Returns:
            None (dialog shows immediately, callback handles result)
        
        Version:
            v1.7.5: Fixed to use semantic API without parameters
            v2.0.2-v2.0.9: Used blocking ShowModal + CallAfter deferred
            v2.2: Migrated to async dialog API (no CallAfter needed)
        """
        def on_abandon_result(confirmed: bool):
            if confirmed:
                # No CallAfter needed, callback already deferred by Show()
                self._safe_abandon_to_menu()
        
        self.dialog_manager.show_abandon_game_prompt_async(
            callback=on_abandon_result
        )
    
    def _safe_abandon_to_menu(self) -> None:
        """Deferred handler for abandon game → menu transition.
        
        FIXED v3.1.3.2: Simplified flow - removed callback suppression.
        
        Previous behavior (REMOVED):
            - Suppressed on_game_ended callback
            - Called end_game() with callback disabled
            - Manually called return_to_menu()
        
        New behavior (v3.1.3.2):
            - Hides gameplay panel (CRITICAL for Bug #68)
            - Calls end_game() with callback ACTIVE
            - end_game() shows AbandonDialog
            - User chooses: "Nuova Partita" / "Menu Principale" / "Statistiche"
            - end_game() calls on_game_ended(wants_rematch) callback
            - handle_game_ended() handles UI transition automatically
        
        Flow:
            1. Hide gameplay panel (prevent empty window)
            2. Call end_game(ABANDON_EXIT) → shows AbandonDialog
            3. Dialog closed → end_game() calls on_game_ended(bool)
            4. handle_game_ended() → start_gameplay() OR _safe_return_to_main_menu()
        
        Version:
            v3.1.3.2: Removed callback suppression (OPZIONE A fix)
        """
        log.debug_state("_safe_abandon_to_menu", {"phase": "start"})
        
        # 1. Hide gameplay panel (CRITICAL for Bug #68)
        if self.view_manager:
            gameplay_panel = self.view_manager.get_panel('gameplay')
            if gameplay_panel:
                gameplay_panel.Hide()
                log.debug_state("_safe_abandon_to_menu", {"gameplay_panel": "hidden"})
            else:
                log.warning_issued("SolitarioController", "_safe_abandon_to_menu: gameplay_panel è None")
        else:
            log.warning_issued("SolitarioController", "_safe_abandon_to_menu: view_manager è None")
        
        # 2. Call end_game() with callback ACTIVE (no suppression)
        log.debug_state("_safe_abandon_to_menu", {"phase": "calling_end_game"})
        from src.domain.models.game_end import EndReason
        self.engine.end_game(EndReason.ABANDON_EXIT)
        
        # 3. end_game() will:
        #    - Show AbandonDialog
        #    - User chooses: "Nuova Partita" / "Menu Principale" / "Statistiche"
        #    - Call on_game_ended(wants_rematch) callback
        #    - handle_game_ended() will handle UI transition
        
        log.debug_state("_safe_abandon_to_menu", {"phase": "end"})
    
    def show_new_game_dialog(self) -> None:
        """Show new game confirmation dialog (non-blocking).
        
        FIXED v3.1.3: Records abandoned session before starting new game.
        Uses callback suppression to avoid double dialog (abandon + rematch).
        
        Uses async dialog API to prevent nested event loops.
        
        Dialog behavior:
            - Title: "Nuova Partita"
            - Message: "Una partita è già in corso..."
            - Non-blocking Show() (not ShowModal)
            - Callback pattern for result handling
        
        Called from:
            - GamePlayController via N key during gameplay
            - Menu "Nuova partita" when game already active
        
        Returns:
            None (dialog shows immediately, callback handles result)
        
        Version:
            v1.7.5: Fixed to use semantic API without parameters
            v2.2: Migrated to async dialog API
            v3.1.3: FIXED - Record abandoned session via end_game() before new_game()
        """
        def on_new_game_result(confirmed: bool):
            if confirmed:
                # 🔥 FIXED v3.1.3: Record abandoned session via end_game()
                # Use callback suppression to prevent double dialog
                
                # Step 1: Temporarily suppress on_game_ended callback
                # This prevents AbandonDialog from showing (we already showed confirmation)
                original_callback = self.engine.on_game_ended
                self.engine.on_game_ended = None
                
                # Step 2: End current game properly (records session)
                from src.domain.models.game_end import EndReason
                self.engine.end_game(EndReason.ABANDON_EXIT)
                
                # What end_game() does (without callback):
                # 1. Creates SessionOutcome with ABANDON_EXIT reason
                # 2. Calls profile_service.record_session() ✅
                # 3. Shows AbandonDialog (SUPPRESSED by None callback) ❌
                # 4. Resets game internally
                
                # Step 3: Restore callback for future games
                self.engine.on_game_ended = original_callback
                
                # Step 4: Start new game immediately
                self.engine.new_game()
                
                # Result: Single dialog, session recorded, clean UX ✅
                
                self._timer_expired_announced = False
                
                if self.screen_reader:
                    self.screen_reader.tts.speak(
                        "Nuova partita avviata! Usa H per l'aiuto comandi.",
                        interrupt=True
                    )
        
        self.dialog_manager.show_new_game_prompt_async(
            callback=on_new_game_result
        )
    
    def confirm_abandon_game(self, skip_dialog: bool = False) -> None:
        """Abandon game immediately without dialog (double-ESC from GameplayView).
        
        Args:
            skip_dialog: If True, skips confirmation (for double-ESC)
        """
        if self.screen_reader and skip_dialog:
            self.screen_reader.tts.speak(
                "Partita abbandonata.",
                interrupt=True
            )
            wx.MilliSleep(300)
        
        # Reset game engine (clear cards, score, timer)
        log.debug_state("confirm_abandon_game", {"trigger": "double_esc"})
        self.engine.reset_game()
        
        self._timer_expired_announced = False
        self.return_to_menu()
    
    # === GAME LIFECYCLE (v2.0.1 - Updated for ViewManager) ===
    
    def handle_game_ended(self, wants_rematch: bool) -> None:
        """Handle game end callback from GameEngine.
        
        Called by GameEngine.end_game() after dialog closes.
        Handles UI transition based on user choice.
        
        Args:
            wants_rematch: True if user chose "Nuova Partita"/"Rivincita",
                          False if user chose "Menu Principale"
        
        Flow:
            - wants_rematch=True → start_gameplay() (new game)
            - wants_rematch=False → _safe_return_to_main_menu() (menu)
        
        Version:
            v2.5.0: Created for async dialog callback chain
            v3.1.3.2: Added debug logging for abandon flow troubleshooting
        """
        log.debug_state("handle_game_ended", {"phase": "start", "wants_rematch": wants_rematch})
        
        # Reset timer expiry flag
        self._timer_expired_announced = False
        
        if wants_rematch:
            log.debug_state("handle_game_ended", {"route": "rematch"})
            self.start_gameplay()
        else:
            log.debug_state("handle_game_ended", {"route": "decline"})
            self._safe_return_to_main_menu()
        
        log.debug_state("handle_game_ended", {"phase": "end"})
    
    def _safe_decline_to_menu(self) -> None:
        """Deferred handler for decline rematch → menu transition (called via wx.CallAfter).
        
        This method runs AFTER the game end callback completes, preventing nested
        event loops and crashes. Performs safe 3-step transition:
            1. Hide gameplay panel
            2. Reset game engine
            3. Return to menu
        
        IMPORTANT: This method should ONLY be called via wx.CallAfter() from
        handle_game_ended(). Do NOT call directly from callbacks.
        
        Pattern:
            ✅ CORRECT: Call via wx.CallAfter() from game end handlers
                wx.CallAfter(self._safe_decline_to_menu)
            
            ❌ WRONG: Direct call from callback
                self._safe_decline_to_menu()  # Causes nested event loop
        
        Version History:
            v2.0.3: Initial implementation with panel swap logic
            v2.0.4: Created as deferred handler for decline rematch flow
            v2.0.9: Added CallAfter deferred execution
            v2.4.3: Corrected to wx.CallAfter (global function)
        """
        log.debug_state("_safe_decline_to_menu", {"phase": "start"})
        
        # Hide gameplay panel
        if self.view_manager:
            gameplay_panel = self.view_manager.get_panel('gameplay')
            if gameplay_panel:
                gameplay_panel.Hide()
        
        # Reset game engine
        self.engine.reset_game()
        
        # Return to menu
        self.return_to_menu()
        
        log.debug_state("_safe_decline_to_menu", {"phase": "end"})
    
    def _safe_return_to_main_menu(self) -> None:
        """Return to main menu after declining rematch.
        
        Called by handle_game_ended(wants_rematch=False).
        
        Flow:
            1. Hide gameplay panel (if not already hidden)
            2. Reset game state (clear statistics, timer)
            3. Show menu panel
            4. Announce return to menu via TTS
        
        Version:
            v2.5.0: Created for Bug #68.2 fix
            v3.1.3.2: Added debug logging for abandon flow troubleshooting
        """
        log.debug_state("_safe_return_to_main_menu", {"phase": "start"})
        
        # 1. Hide gameplay panel (CRITICAL FIX for Bug #68)
        if self.view_manager:
            gameplay_panel = self.view_manager.get_panel('gameplay')
            if gameplay_panel:
                gameplay_panel.Hide()
                log.debug_state("_safe_return_to_main_menu", {"gameplay_panel": "hidden"})
            else:
                log.warning_issued("SolitarioController", "_safe_return_to_main_menu: gameplay_panel è None")
        else:
            log.warning_issued("SolitarioController", "_safe_return_to_main_menu: view_manager è None")
        
        # 2. Reset game state
        self.engine.service.reset_game()
        
        # 3. Switch to main menu panel
        self.view_manager.show_panel("menu")
        
        # 4. Announce return to menu via TTS
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Sei tornato al menu principale. Usa le frecce per navigare.",
                interrupt=True
            )
        
        log.debug_state("_safe_return_to_main_menu", {"phase": "end"})
    
    # === OPTIONS HANDLING ===
    
    # === OPTIONS HANDLING ===
    # (Empty section - open_options() removed)
    # Use show_options() at line ~208 ✅
    
    # DEPRECATED v2.0.1: Legacy method, use return_to_menu() instead
    # def close_options_and_return_to_menu(self) -> None:
    #     """Close options window and return to game submenu."""
    #     print("\n" + "="*60)
    #     print("CHIUSURA OPZIONI - RITORNO AL MENU")
    #     print("="*60)
    #     
    #     self.is_options_mode = False
    #     self.is_menu_open = True
    #     
    #     if self.screen_reader:
    #         self.screen_reader.tts.speak(
    #             "Ritorno al menu di gioco.",
    #             interrupt=True
    #         )
    #         wx.MilliSleep(300)
    #         self.game_submenu._announce_menu_open()
    
    # === TIMER MANAGEMENT ===
    
    def _check_timer_expiration(self) -> None:
        """Check timer expiration (called every second by wx.Timer).
        
        FIXED v3.1.3.1: Delegates to engine.on_timer_tick() instead of local handler.
        This ensures proper session recording and dialog flow via end_game().
        """
        # Skip if not in gameplay mode
        # PRIORITY 1: Use ViewManager if available (modern approach)
        if self.view_manager:
            current_view = self.view_manager.get_current_view()
            if current_view != 'gameplay' or self.is_options_mode:
                return
        else:
            # PRIORITY 2: Fallback to legacy flags during initialization
            if self.is_menu_open or self.is_options_mode:
                return
        
        # Skip if timer disabled
        if self.settings.max_time_game <= 0:
            return
        
        # Skip if game already over
        state = self.engine.get_game_state()
        game_over = state.get('game_over', {}).get('is_over', False)
        if game_over:
            return
        
        # 🔥 FIXED v3.1.3.1: Delegate to engine.on_timer_tick()
        # This replaces local timer handling which bypassed end_game()
        self.engine.on_timer_tick()
        
        # What engine.on_timer_tick() does:
        # 1. Checks if timer expired
        # 2. STRICT mode: calls _handle_strict_timeout()
        #    → Announces timeout
        #    → Calls end_game(TIMEOUT_STRICT)
        #    → Shows AbandonDialog with statistics
        #    → Calls on_game_ended(wants_rematch) callback
        #    → handle_game_ended() manages UI transition
        # 3. PERMISSIVE mode: starts overtime tracking + announces
    
    # ❌ DEPRECATED v3.1.3.1: _handle_game_over_by_timeout() removed
    # ❌ DEPRECATED v3.1.3.1: _safe_timeout_to_menu() removed
    # These methods bypassed end_game() and didn't record sessions properly.
    # Timer timeout now handled via engine.on_timer_tick() → end_game() → on_game_ended() callback
    
    # === EVENT HANDLERS (v2.0.1 - Simplified with ViewManager) ===
    
    def _on_timer_tick(self) -> None:
        """Timer tick handler (called every 1 second)."""
        self._check_timer_expiration()
    
    def _on_frame_close(self) -> None:
        """Frame close handler."""
        self.quit_app()
    
    def quit_app(self) -> bool:
        """Graceful application shutdown with confirmation dialog (non-blocking).
        
        Shows exit confirmation dialog. If user confirms, exits application.
        If user cancels, returns control to caller (veto support for ALT+F4).
        
        Uses async dialog API. Note: Currently returns False immediately
        because async dialog doesn't block. For veto support with async
        dialogs, frame close handling needs refactoring.
        
        Called from:
        - show_exit_dialog() (menu "Esci" button, ESC in menu)
        - _on_frame_close() (ALT+F4, X button)
        
        Returns:
            bool: False (dialog shown, callback will handle exit)
        
        Version:
            v1.7.5: Changed return type from None to bool for veto support
            v2.2: Migrated to async dialog API (veto not yet supported)
        """
        def on_quit_result(confirmed: bool):
            if confirmed:
                log.debug_state("quit_app", {"status": "confirmed"})
                
                if self.screen_reader:
                    self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
                    wx.MilliSleep(800)
                
                sys.exit(0)
            else:
                log.debug_state("quit_app", {"status": "cancelled"})
                if self.screen_reader:
                    self.screen_reader.tts.speak("Uscita annullata.", interrupt=True)
        
        self.dialog_manager.show_exit_app_prompt_async(
            callback=on_quit_result
        )
        return False  # Async dialog doesn't block, callback handles exit
    
    # === MAIN ENTRY POINT ===
    
    def run(self) -> None:
        """Start wxPython application and enter main loop.
        
        Creates wxPython app, visible frame, and starts timer.
        Blocks until application closes.
        """
        log.debug_state("run", {"phase": "start"})
        
        # Create wxPython app
        def on_init(app):
            """Callback after wx.App initialization."""
            # Create visible frame (single-frame pattern)
            # Note: Frame no longer routes keys - panels handle their own
            self.frame = SolitarioFrame(
                on_timer_tick=self._on_timer_tick,
                on_close=self._on_frame_close
            )
            
            # Initialize dialog manager with parent frame (v1.7.3 - single-frame pattern)
            log.debug_state("run", {"phase": "dialog_manager_init"})
            from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
            dialog_provider = WxDialogProvider(parent_frame=self.frame)
            self.dialog_manager = SolitarioDialogManager(dialog_provider=dialog_provider)
            if not self.dialog_manager.is_available:
                log.warning_issued("SolitarioController", "wxPython non disponibile, uso fallback TTS")
            
            # Pass dialog_manager to options_controller
            self.gameplay_controller.options_controller.dialog_manager = self.dialog_manager
            
            # Initialize ViewManager (v1.7.3 - single-frame panel-swap pattern)
            log.debug_state("run", {"phase": "view_manager_init"})
            self.view_manager = ViewManager(self.frame)
            
            # Create panels as children of frame.panel_container
            menu_panel = MenuPanel(
                parent=self.frame.panel_container,
                controller=self
            )
            gameplay_panel = GameplayPanel(
                parent=self.frame.panel_container,
                controller=self
            )
            
            # Register panels with ViewManager
            self.view_manager.register_panel('menu', menu_panel)
            self.view_manager.register_panel('gameplay', gameplay_panel)
            
            # Show initial menu panel
            self.view_manager.show_panel('menu')
            
            # Start timer (1 second interval)
            self.frame.start_timer(1000)
        
        self.app = SolitarioWxApp(on_init_complete=on_init)
        
        # Start wx main loop (blocks)
        self.app.MainLoop()
        
        log.debug_state("run", {"phase": "end"})


def main():
    """Application entry point."""
    # Setup logging FIRST (before any other init)
    setup_logging(
        level=logging.INFO,      # INFO level for production
        console_output=False     # Log only to file
    )
    
    log.app_started()
    
    try:
        controller = SolitarioController()
        controller.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        log.error_occurred("Application", "Unhandled exception in main loop", e)
        sys.exit(1)
    finally:
        log.app_shutdown()


if __name__ == "__main__":
    main()
