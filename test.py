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

import sys
import time
import wx

# Application layer
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController
from src.application.dialog_manager import SolitarioDialogManager

# Domain layer
from src.domain.services.game_settings import GameSettings

# Infrastructure layer - UI components (wxPython)
from src.infrastructure.ui.wx_app import SolitarioWxApp
from src.infrastructure.ui.wx_frame import SolitarioFrame
from src.infrastructure.ui.wx_menu import WxVirtualMenu

# Infrastructure layer - Accessibility
from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.accessibility.tts_provider import create_tts_provider


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
        frame: SolitarioFrame (invisible 1x1 event sink)
        screen_reader: ScreenReader with TTS provider
        settings: GameSettings for configuration
        engine: GameEngine facade for game logic
        gameplay_controller: Keyboard command orchestrator
        dialog_manager: wxDialog provider for native dialogs
        menu: WxVirtualMenu (main menu)
        game_submenu: WxVirtualMenu (secondary menu)
        
        # State flags
        is_menu_open: Current UI state (True = menu, False = gameplay/options)
        is_options_mode: Options window active
        last_esc_time: Timestamp for double-ESC detection
        _timer_expired_announced: Prevents repeated timeout messages
    
    Example:
        >>> controller = SolitarioController()
        >>> controller.run()  # Blocks until app closes
    """
    
    # Double-ESC feature threshold (seconds)
    DOUBLE_ESC_THRESHOLD = 2.0
    
    def __init__(self):
        """Initialize application with all components."""
        print("\n" + "="*60)
        print("🎴 SOLITARIO ACCESSIBILE - wxPython v2.0.0")
        print("="*60)
        print("Inizializzazione componenti...")
        
        # Infrastructure: TTS setup
        print("Inizializzazione TTS...")
        try:
            tts_provider = create_tts_provider(engine="auto")
            self.screen_reader = ScreenReader(
                tts=tts_provider,
                enabled=True,
                verbose=False
            )
            print("✓ TTS inizializzato")
        except Exception as e:
            print(f"⚠ Errore TTS: {e}")
            print("Continuando senza audio...")
            self.screen_reader = self._create_dummy_sr()
        
        # Domain: Game settings
        print("Inizializzazione impostazioni di gioco...")
        self.settings = GameSettings()
        print("✓ Impostazioni pronte")
        
        # Infrastructure: Dialog manager
        print("Inizializzazione dialog manager...")
        self.dialog_manager = SolitarioDialogManager()
        if self.dialog_manager.is_available:
            print("✓ Dialog nativi wxPython attivi")
        else:
            print("⚠ wxPython non disponibile, uso fallback TTS")
        
        # Application: Game engine setup
        print("Inizializzazione motore di gioco...")
        self.engine = GameEngine.create(
            audio_enabled=(self.screen_reader is not None),
            tts_engine="auto",
            verbose=1,
            settings=self.settings,
            use_native_dialogs=True,
            parent_window=None  # wx dialogs don't need parent
        )
        
        # Inject end game callback for UI state management
        self.engine.on_game_ended = self.handle_game_ended
        print("✓ Game engine pronto")
        
        # Application: Gameplay controller
        print("Inizializzazione controller gameplay...")
        self.gameplay_controller = GamePlayController(
            engine=self.engine,
            screen_reader=self.screen_reader,
            settings=self.settings,
            on_new_game_request=self.show_new_game_dialog
        )
        print("✓ Controller pronto")
        
        # Pass dialog_manager to options_controller
        self.gameplay_controller.options_controller.dialog_manager = self.dialog_manager
        
        # Infrastructure: Virtual menu hierarchy (wxPython version)
        print("Inizializzazione menu...")
        
        # Main menu
        self.menu = WxVirtualMenu(
            items=[
                "Gioca al solitario classico",
                "Esci dal gioco"
            ],
            callback=self.handle_menu_selection,
            screen_reader=self.screen_reader
        )
        
        # Game submenu with welcome message
        self.game_submenu = WxVirtualMenu(
            items=[
                "Nuova partita",
                "Opzioni",
                "Chiudi"
            ],
            callback=self.handle_game_submenu_selection,
            screen_reader=self.screen_reader,
            parent_menu=self.menu,
            welcome_message="Benvenuto nel menu di gioco del Solitario Classico!",
            show_controls_hint=True
        )
        
        print("✓ Menu pronto")
        
        # State flags
        self.is_menu_open = True
        self.is_options_mode = False
        self.last_esc_time = 0
        self._timer_expired_announced = False
        
        # wxPython components (created in run())
        self.app: SolitarioWxApp = None
        self.frame: SolitarioFrame = None
        
        print("="*60)
        print("✓ Applicazione avviata con successo!")
        print("✓ Architettura Clean completa")
        print("✓ wxPython-only (no pygame)")
        print("Usa i tasti freccia per navigare il menu.")
        print("="*60)
    
    def _create_dummy_sr(self):
        """Create dummy screen reader for silent mode."""
        class DummySR:
            class DummyTTS:
                def speak(self, text, interrupt=True):
                    print(f"[TTS] {text}")
            tts = DummyTTS()
        return DummySR()
    
    # === MENU HANDLERS ===
    
    def handle_menu_selection(self, index: int) -> None:
        """Handle main menu selection."""
        if index == 0:  # "Gioca"
            self.menu.open_submenu(self.game_submenu)
            self.game_submenu.announce_welcome()
        elif index == 1:  # "Esci"
            self.show_exit_dialog()
    
    def handle_game_submenu_selection(self, index: int) -> None:
        """Handle game submenu selection."""
        if index == 0:  # "Nuova partita"
            # Check if game is running
            if self.engine.service.get_elapsed_time() > 0 and not self.engine.is_game_over():
                self.show_new_game_dialog()
            else:
                self._start_new_game()
        elif index == 1:  # "Opzioni"
            self.open_options()
        elif index == 2:  # "Chiudi"
            self.show_return_to_main_dialog()
    
    # === DIALOG HANDLERS ===
    
    def show_exit_dialog(self) -> None:
        """Show exit confirmation dialog."""
        result = self.dialog_manager.show_yes_no(
            "Vuoi davvero uscire dal gioco?",
            "Conferma uscita"
        )
        if result:
            self.quit_app()
    
    def show_return_to_main_dialog(self) -> None:
        """Show return to main menu confirmation."""
        result = self.dialog_manager.show_yes_no(
            "Vuoi tornare al menu principale?",
            "Conferma"
        )
        if result:
            self.game_submenu.close()
    
    def show_abandon_game_dialog(self) -> None:
        """Show abandon game confirmation."""
        result = self.dialog_manager.show_yes_no(
            "Vuoi abbandonare la partita corrente?",
            "Abbandona partita"
        )
        if result:
            self.confirm_abandon_game()
    
    def show_new_game_dialog(self) -> None:
        """Show new game confirmation when game is active."""
        result = self.dialog_manager.show_yes_no(
            "C'è già una partita in corso. Vuoi abbandonarla e iniziare una nuova partita?",
            "Nuova partita"
        )
        if result:
            self._confirm_new_game()
        else:
            self._cancel_new_game()
    
    def _confirm_new_game(self) -> None:
        """Callback: User confirmed new game."""
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Partita precedente abbandonata.",
                interrupt=True
            )
            wx.MilliSleep(300)
        self._start_new_game()
    
    def _cancel_new_game(self) -> None:
        """Callback: User cancelled new game."""
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Azione annullata. Torno alla partita.",
                interrupt=True
            )
            wx.MilliSleep(300)
    
    def confirm_abandon_game(self) -> None:
        """Abandon current game and return to menu."""
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Partita abbandonata.",
                interrupt=True
            )
            wx.MilliSleep(300)
        
        self.is_menu_open = True
        self.last_esc_time = 0
        self._timer_expired_announced = False
        
        if self.screen_reader:
            self.game_submenu.announce_welcome()
    
    # === GAME LIFECYCLE ===
    
    def _start_new_game(self) -> None:
        """Start new game without confirmation."""
        self.is_menu_open = False
        self.start_game()
    
    def start_game(self) -> None:
        """Start new game session."""
        print("\n" + "="*60)
        print("AVVIO PARTITA")
        print("="*60)
        
        self.engine.reset_game()
        self.engine.new_game()
        self.last_esc_time = 0
        self._timer_expired_announced = False
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Nuova partita avviata! Usa H per l'aiuto comandi.",
                interrupt=True
            )
        
        print("Partita in corso...")
        print("Premi H per l'aiuto comandi.")
        print("Premi ESC per tornare al menu (doppio ESC per uscita rapida).")
    
    def handle_game_ended(self, wants_rematch: bool) -> None:
        """Handle game end callback from GameEngine."""
        print("\n" + "="*60)
        print(f"CALLBACK: Game ended - Rematch requested: {wants_rematch}")
        print("="*60)
        
        self._timer_expired_announced = False
        
        if wants_rematch:
            print("→ User chose rematch - Starting new game")
            self.start_game()
        else:
            print("→ User declined rematch - Returning to game submenu")
            self.is_menu_open = True
            
            if self.screen_reader:
                self.screen_reader.tts.speak(
                    "Ritorno al menu di gioco.",
                    interrupt=True
                )
                wx.MilliSleep(400)
                self.game_submenu.announce_welcome()
        
        print("="*60)
    
    # === OPTIONS HANDLING ===
    
    def open_options(self) -> None:
        """Open virtual options window."""
        print("\n" + "="*60)
        print("APERTURA FINESTRA OPZIONI")
        print("="*60)
        
        self.is_menu_open = False
        self.is_options_mode = True
        
        msg = self.gameplay_controller.options_controller.open_window()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        print("Finestra opzioni aperta.")
        print("="*60)
    
    def close_options_and_return_to_menu(self) -> None:
        """Close options window and return to game submenu."""
        print("\n" + "="*60)
        print("CHIUSURA OPZIONI - RITORNO AL MENU")
        print("="*60)
        
        self.is_options_mode = False
        self.is_menu_open = True
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu di gioco.",
                interrupt=True
            )
            wx.MilliSleep(300)
            self.game_submenu._announce_menu_open()
    
    # === TIMER MANAGEMENT ===
    
    def _check_timer_expiration(self) -> None:
        """Check timer expiration (called every second by wx.Timer)."""
        # Skip if not in gameplay mode
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
        
        # Get current elapsed time
        elapsed = self.engine.service.get_elapsed_time()
        max_time = self.settings.max_time_game
        
        # Timer still OK
        if elapsed < max_time:
            self._timer_expired_announced = False
            return
        
        # Timer expired
        if self.settings.timer_strict_mode:
            self._handle_game_over_by_timeout()
        else:
            # Permissive mode - announce once
            if not self._timer_expired_announced:
                overtime_seconds = int(elapsed - max_time)
                overtime_minutes = max(1, overtime_seconds // 60)
                penalty_points = 100 * overtime_minutes
                max_minutes = max_time // 60
                
                malus_msg = f"Attenzione! Tempo scaduto! "
                malus_msg += f"Hai superato il limite di {max_minutes} minuti. "
                malus_msg += f"Penalità applicata: meno {penalty_points} punti."
                
                if self.screen_reader:
                    self.screen_reader.tts.speak(malus_msg, interrupt=True)
                    wx.MilliSleep(800)
                
                self._timer_expired_announced = True
    
    def _handle_game_over_by_timeout(self) -> None:
        """Handle game over by timeout in STRICT mode."""
        max_time = self.settings.max_time_game
        elapsed = self.engine.service.get_elapsed_time()
        
        minutes_max = max_time // 60
        seconds_max = max_time % 60
        minutes_elapsed = int(elapsed) // 60
        seconds_elapsed = int(elapsed) % 60
        
        defeat_msg = "⏰ TEMPO SCADUTO!\n\n"
        defeat_msg += f"Tempo limite: {minutes_max} minuti"
        if seconds_max > 0:
            defeat_msg += f" e {seconds_max} secondi"
        defeat_msg += ".\n"
        defeat_msg += f"Tempo trascorso: {minutes_elapsed} minuti"
        if seconds_elapsed > 0:
            defeat_msg += f" e {seconds_elapsed} secondi"
        defeat_msg += ".\n\n"
        
        report, _ = self.engine.service.get_game_report()
        defeat_msg += "--- STATISTICHE FINALI ---\n"
        defeat_msg += report
        
        print(defeat_msg)
        
        if self.screen_reader:
            self.screen_reader.tts.speak(defeat_msg, interrupt=True)
            wx.MilliSleep(2000)
        
        self.is_menu_open = True
        self._timer_expired_announced = False
        
        if self.screen_reader:
            wx.MilliSleep(500)
            self.game_submenu.announce_welcome()
    
    # === EVENT ROUTING ===
    
    def _on_key_event(self, event: wx.KeyEvent) -> None:
        """Main keyboard event handler (wxPython).
        
        Routes events based on current application state:
        - Menu open: Route to menu navigation (with ESC interception)
        - Options mode: Route to options controller
        - Gameplay: Route to gameplay controller (with double-ESC detection)
        
        Args:
            event: wx.KeyEvent from frame
        
        Note:
            event.Skip() is called by frame, not here
        """
        key_code = event.GetKeyCode()
        
        if self.is_menu_open:
            # ESC in main menu → Exit dialog
            if key_code == wx.WXK_ESCAPE:
                if self.menu._active_submenu is None:
                    self.show_exit_dialog()
                    return
                elif self.menu._active_submenu == self.game_submenu:
                    self.show_return_to_main_dialog()
                    return
            
            # Normal menu navigation (delegates to submenu if active)
            self.menu.handle_key_event(event)
        
        elif self.is_options_mode:
            # Options window mode - route to gameplay controller
            self.gameplay_controller.handle_wx_key_event(event)
            
            # Check if options was closed
            if not self.gameplay_controller.options_controller.is_open:
                self.close_options_and_return_to_menu()
        
        else:
            # GAMEPLAY MODE - with double-ESC detection
            if key_code == wx.WXK_ESCAPE:
                if not self.gameplay_controller.options_controller.is_open:
                    current_time = time.time()
                    
                    # Check for double-ESC
                    if self.last_esc_time > 0 and current_time - self.last_esc_time <= self.DOUBLE_ESC_THRESHOLD:
                        # Double-ESC detected - instant abandon
                        print("\n[DOUBLE-ESC] Uscita rapida!")
                        
                        if self.screen_reader:
                            self.screen_reader.tts.speak(
                                "Uscita rapida!",
                                interrupt=True
                            )
                            wx.MilliSleep(300)
                        
                        self.confirm_abandon_game()
                        self.last_esc_time = 0
                    else:
                        # First ESC - show dialog
                        self.last_esc_time = current_time
                        self.show_abandon_game_dialog()
                    
                    return
            
            # Normal gameplay commands
            self.gameplay_controller.handle_wx_key_event(event)
    
    def _on_timer_tick(self) -> None:
        """Timer tick handler (called every 1 second)."""
        self._check_timer_expiration()
    
    def _on_frame_close(self) -> None:
        """Frame close handler."""
        self.quit_app()
    
    def quit_app(self) -> None:
        """Graceful application shutdown."""
        print("\n" + "="*60)
        print("CHIUSURA APPLICAZIONE")
        print("="*60)
        
        if self.screen_reader:
            self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
            wx.MilliSleep(800)
        
        # Close frame and exit app
        if self.frame:
            self.frame.Close()
        sys.exit(0)
    
    # === MAIN ENTRY POINT ===
    
    def run(self) -> None:
        """Start wxPython application and enter main loop.
        
        Creates wxPython app, invisible frame, and starts timer.
        Blocks until application closes.
        """
        print("\nAvvio wxPython MainLoop()...")
        
        # Create wxPython app
        def on_init(app):
            """Callback after wx.App initialization."""
            # Create invisible frame for event capture
            self.frame = SolitarioFrame(
                on_key_event=self._on_key_event,
                on_timer_tick=self._on_timer_tick,
                on_close=self._on_frame_close
            )
            
            # Start timer (1 second interval)
            self.frame.start_timer(1000)
            
            # Show frame (stays invisible due to 1x1 size)
            self.frame.Show()
        
        self.app = SolitarioWxApp(on_init_complete=on_init)
        
        # Start wx main loop (blocks)
        self.app.MainLoop()
        
        print("wxPython MainLoop terminato.")


def main():
    """Application entry point."""
    print("\n" + "="*60)
    print("🎴 SOLITARIO ACCESSIBILE - wxPython v2.0.0")
    print("="*60)
    print("Versione: 2.0.0 (wxPython-only)")
    print("Architettura: Clean Architecture (COMPLETA)")
    print("Modalità: Audiogame per non vedenti")
    print("Entry point: wx_main.py")
    print("")
    print("🎉 v2.0.0: Pygame removed, wxPython-only!")
    print("   ✓ Native wx.MainLoop() event loop")
    print("   ✓ wx.Timer for timeout checks")
    print("   ✓ 80+ key mappings preserved")
    print("   ✓ 100% feature parity")
    print("   ✓ Improved NVDA accessibility")
    print("")
    print("Legacy pygame version: python test_pygame_legacy.py")
    print("="*60)
    print("")
    
    try:
        controller = SolitarioController()
        controller.run()
    except KeyboardInterrupt:
        print("\n\nInterrotto dall'utente (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n⚠ ERRORE FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
