"""Clean Architecture entry point - Audiogame version.

Launches the accessible solitaire game using Clean Architecture
with pure audiogame interface (no visual widgets, only TTS feedback).

Usage:
    python test.py

Controls:
    Menu: UP/DOWN arrows + ENTER
    Game: See H for help (60+ keyboard commands)

Architecture Layers (Complete):
    ✅ Domain Layer:
       - models/: Card, Pile, Deck, Table
       - rules/: SolitaireRules, MoveValidator
       - services/: GameService, GameSettings
    
    ✅ Application Layer:
       - GameEngine: Main game facade
       - GamePlayController: Gameplay orchestration
       - InputHandler: Keyboard → Command mapping [Commit #7]
       - GameSettings: Configuration management [Commit #8]
       - TimerManager: Timer functionality [Commit #8]
    
    ✅ Infrastructure Layer:
       - accessibility/: ScreenReader, TtsProvider [Commit #5]
       - ui/: VirtualMenu, VirtualDialogBox [Commits #6, #24]
    
    ✅ Presentation Layer:
       - GameFormatter: Output formatting [Commit #9]

All architectural components complete and ready for integration.

New in v1.4.2 [Commits #24-28] - COMPLETE:
- Virtual dialog boxes for confirmations
- ESC confirmation in all contexts
- Welcome message in game submenu
- Double-ESC quick exit during gameplay

New in v1.4.2.1 [Bug Fix] - IN PROGRESS:
- Dynamic deck type from GameSettings (#BUG-001)
- Fixed suit validation for foundations (#BUG-002)
"""

import sys
import time
import pygame
from pygame.locals import QUIT

# Application layer
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController
from src.application.dialog_manager import SolitarioDialogManager  # NEW v1.6.1

# Domain layer - Configuration
from src.domain.services.game_settings import GameSettings  # NEW IMPORT (v1.4.2.1)

# Infrastructure layer - UI components
from src.infrastructure.ui.menu import VirtualMenu
from src.infrastructure.ui.dialog import VirtualDialogBox  # New in v1.4.2

# Infrastructure layer - Accessibility
from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.accessibility.tts_provider import create_tts_provider


class SolitarioCleanArch:
    """Main application class - Audiogame for blind users.
    
    Manages application lifecycle and orchestrates menu ↔ gameplay ↔ options flow.
    Uses Clean Architecture with dependency injection.
    
    Architecture Notes:
    - All layers complete (Domain, Application, Infrastructure, Presentation)
    - Entry point depends only on Application + Infrastructure
    - Ready for full refactoring integration
    
    Attributes:
        screen: PyGame surface (blank white for audiogame)
        screen_reader: ScreenReader with TTS provider
        settings: GameSettings for configuration management (v1.4.2.1)
        engine: GameEngine facade for game logic
        gameplay_controller: Keyboard commands orchestrator
        menu: Virtual main menu for navigation
        game_submenu: Secondary menu with welcome message (v1.4.2)
        exit_dialog: Dialog for app exit confirmation (v1.4.2)
        return_to_main_dialog: Dialog for submenu exit confirmation (v1.4.2)
        abandon_game_dialog: Dialog for gameplay exit confirmation (v1.4.2)
        last_esc_time: Timestamp of last ESC press for double-ESC feature
        is_menu_open: Current UI state (menu vs gameplay/options)
        is_options_mode: Options window active (v1.4.1)
        is_running: Main loop control flag
    """
    
    # 🆕 NEW v1.5.2.2: Custom pygame event for timer checks
    TIME_CHECK_EVENT = pygame.USEREVENT + 1  # Fires every 1 second
    
    def __init__(self):
        """Initialize application with all components."""
        # PyGame initialization
        pygame.init()
        pygame.font.init()
        
        # Setup blank display (audiogame - no visuals needed)
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Solitario Accessibile - Clean Architecture")
        self.screen.fill((255, 255, 255))  # White background
        pygame.display.flip()
        
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
            # Fallback: silent mode
            self.screen_reader = None
        
        # Domain: Game settings (v1.4.2.1 - Bug Fix #1)
        print("Inizializzazione impostazioni di gioco...")
        self.settings = GameSettings()
        print("✓ Impostazioni pronte")
        
        # NEW v1.6.1: Dialog manager initialization
        print("Inizializzazione dialog manager...")
        self.dialog_manager = SolitarioDialogManager()
        if self.dialog_manager.is_available:
            print("✓ Dialog nativi wxPython attivi")
        else:
            print("⚠ wxPython non disponibile, uso fallback TTS")
        
        # Application: Game engine setup (now with settings AND dialogs!)
        print("Inizializzazione motore di gioco...")
        self.engine = GameEngine.create(
            audio_enabled=(self.screen_reader is not None),
            tts_engine="auto",
            verbose=1,
            settings=self.settings,  # v1.4.2.1
            use_native_dialogs=True  # v1.6.2 - ENABLE WX DIALOGS
        )
        print("✓ Game engine pronto")
        
        # Application: Gameplay controller (now with settings!)
        print("Inizializzazione controller gameplay...")
        self.gameplay_controller = GamePlayController(
            engine=self.engine,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
            settings=self.settings,  # NEW PARAMETER (v1.4.2.1)
            on_new_game_request=self.show_new_game_dialog  # NEW PARAMETER (v1.4.3)
        )
        print("✓ Controller pronto")
        
        # NEW v1.6.1: Pass dialog_manager to options_controller
        self.gameplay_controller.options_controller.dialog_manager = self.dialog_manager
        
        # Infrastructure: Virtual menu hierarchy
        print("Inizializzazione menu...")
        
        # Main menu
        self.menu = VirtualMenu(
            items=[
                "Gioca al solitario classico",
                "Esci dal gioco"
            ],
            callback=self.handle_menu_selection,
            screen=self.screen,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
        )
        
        # Game submenu with welcome message (v1.4.2 - Commit #28)
        self.game_submenu = VirtualMenu(
            items=[
                "Nuova partita",
                "Opzioni",
                "Chiudi"
            ],
            callback=self.handle_game_submenu_selection,
            screen=self.screen,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
            parent_menu=self.menu,
            welcome_message="Benvenuto nel menu di gioco del Solitario Classico!",
            show_controls_hint=True
        )
        
        print("✓ Menu pronto")
        
        # Double-ESC feature (Commit #27)
        self.last_esc_time = 0  # Timestamp of last ESC press
        self.DOUBLE_ESC_THRESHOLD = 2.0  # Seconds for double-ESC detection
        
        # Application state
        self.is_menu_open = True
        self.is_options_mode = False
        self.is_running = True
        
        # 🆕 NEW v1.5.2.2: Setup periodic timer check
        pygame.time.set_timer(self.TIME_CHECK_EVENT, 1000)  # 1000ms = 1 second
        self._timer_expired_announced = False  # Prevents repeated announcements
        
        print("="*60)
        print("✓ Applicazione avviata con successo!")
        print("✓ Architettura Clean completa")
        print("✓ GameSettings integrato (v1.4.2.1)")
        print("Usa i tasti freccia per navigare il menu.")
        print("="*60)
    
    def _dummy_sr(self):
        """Create dummy screen reader for silent mode."""
        class DummySR:
            class DummyTTS:
                def speak(self, text, interrupt=True):
                    print(f"[TTS] {text}")
            
            def __init__(self):
                self.tts = self.DummyTTS()
        
        return DummySR()
    
    def handle_menu_selection(self, selected_item: int) -> None:
        """Handle main menu item selection callback.
        
        Args:
            selected_item: Index of selected menu item
                0: Open game submenu
                1: Quit application (now shows confirmation)
        """
        if selected_item == 0:
            # Open game submenu
            self.menu.open_submenu(self.game_submenu)
        elif selected_item == 1:
            # Show exit confirmation dialog
            self.show_exit_dialog()
    
    def handle_game_submenu_selection(self, selected_item: int) -> None:
        """Handle game submenu item selection callback.
        
        Args:
            selected_item: Index of selected submenu item
                0: Start new game (with confirmation if game running - v1.4.3)
                1: Open virtual options window
                2: Close submenu - now shows confirmation dialog (v1.4.2)
        """
        if selected_item == 0:
            # Nuova partita - with safety check (v1.4.3)
            if self.engine.is_game_running():
                # Game in progress: show confirmation dialog
                self.show_new_game_dialog()
            else:
                # No game running: start immediately
                self._start_new_game()
        elif selected_item == 1:
            # Opzioni
            self.open_options()
        elif selected_item == 2:
            # Chiudi - show confirmation dialog (Commit #26)
            self.show_return_to_main_dialog()
    
    # === DIALOG HANDLERS (v1.4.2) ===
    
    def show_exit_dialog(self) -> None:
        """Show exit confirmation dialog - NATIVE WX (v1.6.1).
        
        Opens native wxPython dialog asking "Vuoi uscire dall'applicazione?"
        with Yes/No buttons.
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma uscita applicazione (wxPython)")
        print("="*60)
        
        result = self.dialog_manager.show_exit_app_prompt()
        
        if result:
            self.quit_app()
        # Else: stay in menu (no action needed)
    
    def close_exit_dialog(self) -> None:
        """Close exit dialog and return to main menu.
        
        Called when user presses Annulla or ESC in exit dialog.
        """
        print("Dialog chiuso - Ritorno al menu principale")
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu principale.",
                interrupt=True
            )
            pygame.time.wait(300)
        
        # Re-announce main menu
        if self.menu.active_submenu is None:
            self.menu._announce_menu_open()
    
    def show_return_to_main_dialog(self) -> None:
        """Show return to main menu confirmation - NATIVE WX (v1.6.1).
        
        Opens native wxPython dialog asking "Vuoi tornare al menu principale?"
        with Sì/No buttons.
        
        Triggered by:
        - ESC in game submenu
        - ENTER on "Chiudi" menu item
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma ritorno menu principale (wxPython)")
        print("="*60)
        
        result = self.dialog_manager.show_return_to_main_prompt()
        
        if result:
            self.confirm_return_to_main()
        else:
            self.close_return_dialog()
    
    def confirm_return_to_main(self) -> None:
        """Confirm return to main menu (Sì button).
        
        Closes game submenu and returns to main menu.
        Re-announces main menu after closing.
        """
        print("Confermato - Chiusura submenu e ritorno al menu principale")
        
        # Close game submenu
        self.menu.close_submenu()
        
        # Announce return
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu principale.",
                interrupt=True
            )
            pygame.time.wait(400)
            
            # Re-announce main menu
            self.menu._announce_menu_open()
    
    def close_return_dialog(self) -> None:
        """Close return dialog and stay in game submenu (No button or ESC).
        
        User chose to stay in game submenu, re-announce current position.
        """
        print("Dialog chiuso - Resta nel menu di gioco")
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Resta nel menu di gioco.",
                interrupt=True
            )
            pygame.time.wait(300)
        
        # Re-announce current submenu position
        self.game_submenu._announce_menu_open()
    
    def show_abandon_game_dialog(self) -> None:
        """Show abandon game confirmation - NATIVE WX (v1.6.1).
        
        Opens native wxPython dialog asking "Vuoi abbandonare la partita e tornare al menu di gioco?"
        with Sì/No buttons.
        
        Triggered by:
        - ESC during gameplay
        
        Note: Returns to GAME SUBMENU, not main menu!
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma abbandono partita (wxPython)")
        print("="*60)
        
        result = self.dialog_manager.show_abandon_game_prompt()
        
        if result:
            self.confirm_abandon_game()
        else:
            self.close_abandon_dialog()
    
    def confirm_abandon_game(self) -> None:
        """Confirm abandon game (Sì button).
        
        Abandons current game and returns to GAME SUBMENU (not main menu!).
        Re-announces game submenu after abandoning.
        """
        print("Confermato - Abbandono partita e ritorno al menu di gioco")
        
        # Reset ESC timer
        self.last_esc_time = 0
        
        # ✅ TASK #1: Reset game engine state (timer, moves, cursor, selection)
        # Questo resetta: service.start_time, service.move_count, service.is_game_running,
        # cursor position, selection state
        self.engine.reset_game()
        
        # ✅ TASK #2: Reset timer expiration announcement flag
        # Questo flag è in test.py, non in engine, quindi va resettato manualmente
        self._timer_expired_announced = False
        
        # Return to game submenu
        self.is_menu_open = True
        
        # Announce return
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Partita abbandonata. Ritorno al menu di gioco.",
                interrupt=True
            )
            pygame.time.wait(400)
            
            # Re-announce game submenu with welcome message
            self.game_submenu.announce_welcome()
    
    def close_abandon_dialog(self) -> None:
        """Close abandon dialog and resume gameplay (No button or first ESC).
        
        User chose to continue playing, announce resume.
        """
        print("Dialog chiuso - Ripresa gioco")
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ripresa gioco.",
                interrupt=True
            )
            pygame.time.wait(300)
        
        # Reset ESC timer
        self.last_esc_time = 0
    
    # === NEW GAME DIALOG HANDLERS (v1.4.3) ===
    
    def show_new_game_dialog(self) -> None:
        """Show new game confirmation - NATIVE WX (v1.6.1).
        
        Opens native wxPython dialog asking "Una partita è già in corso. 
        Vuoi abbandonarla e avviarne una nuova?" with Sì/No buttons.
        
        Triggered by:
        - "N" key during gameplay
        - "Nuova partita" menu selection when game is running
        
        Safety feature to prevent accidental game loss.
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma nuova partita (wxPython)")
        print("="*60)
        
        result = self.dialog_manager.show_new_game_prompt()
        
        if result:
            self._confirm_new_game()
        else:
            self._cancel_new_game()
    
    def _confirm_new_game(self) -> None:
        """Callback: User confirmed starting new game (abandoning current).
        
        Called when user presses:
        - "S" key (Sì shortcut)
        - Arrow keys + ENTER on "Sì" button
        
        Actions:
        1. Close dialog
        2. Abandon current game (no stats save)
        3. Start new game
        
        New in v1.4.3: Safety feature for preventing accidental game loss.
        """
        print("Confermato - Abbandono partita corrente e avvio nuova")
        
        # Announce action
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Partita precedente abbandonata.",
                interrupt=True
            )
            pygame.time.wait(300)
        
        # Start new game
        self._start_new_game()
    
    def _cancel_new_game(self) -> None:
        """Callback: User cancelled new game dialog.
        
        Called when user presses:
        - "N" key (No shortcut)
        - ESC key
        - Arrow keys + ENTER on "No" button
        
        Actions:
        1. Close dialog
        2. Resume current game
        3. Announce cancellation
        
        New in v1.4.3: Safety feature for preventing accidental game loss.
        """
        print("Dialog chiuso - Azione annullata, continuo partita corrente")
        
        # Announce cancellation
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Azione annullata. Torno alla partita.",
                interrupt=True
            )
            pygame.time.wait(300)
        
        # No further action needed, game continues
    
    def _check_timer_expiration(self) -> None:
        """Check timer expiration every second (v1.5.2.2).
        
        Triggered by TIME_CHECK_EVENT (pygame.USEREVENT+1) every 1000ms.
        
        Behavior based on settings.timer_strict_mode:
        
        STRICT Mode (True):
            - Game stops immediately when timer expires
            - Saves final statistics (elapsed time, moves, etc)
            - Shows complete game report via TTS
            - Returns to game menu
            - Legacy behavior from scr/game_engine.py
        
        PERMISSIVE Mode (False):
            - Game continues beyond time limit
            - Announces timeout + malus ONCE via TTS
            - Scoring penalty applied: -100 points per overtime minute
            - Allows player to complete game
            - New feature for casual/learning mode
        
        Skip Conditions:
            - Not in gameplay (menu or options open)
            - Timer disabled (max_time_game <= 0)
            - Game already over (victory or defeat)
        
        State Management:
            - self._timer_expired_announced: Prevents repeated TTS in PERMISSIVE mode
            - Reset to False when: timer OK, new game starts, return to menu
        """
        # Skip if not in gameplay mode
        if self.is_menu_open or self.is_options_mode:
            return
        
        # Skip if timer disabled or in stopwatch mode
        if self.settings.max_time_game <= 0:
            return
        
        # Skip if game already concluded
        state = self.engine.get_game_state()
        game_over = state.get('game_over', {}).get('is_over', False)
        if game_over:
            return
        
        # Get current elapsed time
        elapsed = self.engine.service.get_elapsed_time()
        max_time = self.settings.max_time_game
        
        # Timer still OK - reset announcement flag
        if elapsed < max_time:
            self._timer_expired_announced = False
            return
        
        # ⏰ TIMER EXPIRED - Decide action based on mode
        
        if self.settings.timer_strict_mode:
            # === STRICT MODE: Auto-stop game ===
            self._handle_game_over_by_timeout()
        
        else:
            # === PERMISSIVE MODE: Announce malus once, continue playing ===
            if not self._timer_expired_announced:
                overtime_seconds = int(elapsed - max_time)
                overtime_minutes = max(1, overtime_seconds // 60)  # At least 1 min
                
                # Calculate penalty
                penalty_points = 100 * overtime_minutes
                
                # Build announcement
                max_minutes = max_time // 60
                malus_msg = f"Attenzione! Tempo scaduto! "
                malus_msg += f"Hai superato il limite di {max_minutes} minuti. "
                malus_msg += f"Stai giocando in tempo extra. "
                malus_msg += f"Penalità applicata: meno {penalty_points} punti. "
                malus_msg += f"Tempo oltre il limite: {overtime_minutes} minuti."
                
                # Vocalize warning
                if self.screen_reader:
                    self.screen_reader.tts.speak(malus_msg, interrupt=True)
                    pygame.time.wait(800)  # Longer pause for important warning
                
                # Console log
                print(f"\n[TIMER PERMISSIVE] Overtime: +{overtime_minutes}min → Malus: -{penalty_points}pts")
                
                # Mark as announced (don't repeat)
                self._timer_expired_announced = True
    
    def _handle_game_over_by_timeout(self) -> None:
        """Handle game over by timeout in STRICT mode (v1.5.2.2).
        
        Called when timer expires and settings.timer_strict_mode = True.
        
        Actions:
        1. Stop timer event checks (set announcement flag)
        2. Retrieve final game statistics from engine
        3. Build comprehensive defeat message with:
           - Time limit exceeded message
           - Elapsed time vs max time comparison
           - Complete game report (moves, cards placed, etc)
        4. Vocalize defeat message via TTS (2 second pause)
        5. Return to game submenu (not main menu!)
        6. Reset timer flags for next game
        
        User Flow After Timeout:
            Game → [Timer expires] → This method → Game Submenu
            User can then:
            - Start new game (N key or menu option 1)
            - Change options (O key or menu option 2)
            - Return to main menu (ESC or menu option 3)
        
        Note:
            This replicates legacy behavior from scr/game_engine.py:
            - you_lost_by_time() method
            - ceck_lost_by_time() detection
            But with improved TTS feedback and Clean Architecture structure.
        """
        print("\n" + "="*60)
        print("⏰ GAME OVER - TEMPO SCADUTO (STRICT MODE)")
        print("="*60)
        
        # Stop timer announcements
        self._timer_expired_announced = True
        
        # Get final statistics
        elapsed = int(self.engine.service.get_elapsed_time())
        max_time = self.settings.max_time_game
        
        # Calculate time values for display
        minutes_elapsed = elapsed // 60
        seconds_elapsed = elapsed % 60
        max_minutes = max_time // 60
        max_seconds = max_time % 60
        
        # Build defeat message header
        defeat_msg = "⏰ TEMPO SCADUTO! PARTITA TERMINATA.\n\n"
        defeat_msg += f"Limite impostato: {max_minutes} minuti"
        if max_seconds > 0:
            defeat_msg += f" e {max_seconds} secondi"
        defeat_msg += ".\n"
        
        defeat_msg += f"Tempo trascorso: {minutes_elapsed} minuti"
        if seconds_elapsed > 0:
            defeat_msg += f" e {seconds_elapsed} secondi"
        defeat_msg += ".\n\n"
        
        # Add complete game report
        report, _ = self.engine.service.get_game_report()
        defeat_msg += "--- STATISTICHE FINALI ---\n"
        defeat_msg += report
        
        # Console output
        print(defeat_msg)
        print("="*60)
        
        # Vocalize with longer pause for readability
        if self.screen_reader:
            self.screen_reader.tts.speak(defeat_msg, interrupt=True)
            pygame.time.wait(2000)  # 2 second pause for long message
        
        # Return to game submenu (not main menu!)
        self.is_menu_open = True
        self._timer_expired_announced = False  # Reset for next game
        
        # Re-announce game submenu
        if self.screen_reader:
            pygame.time.wait(500)  # Small pause before menu
            self.game_submenu.announce_welcome()
    
    def _start_new_game(self) -> None:
        """Internal method: Start new game without confirmation.
        
        Called by:
        - handle_game_submenu_selection() when no game is running
        - _confirm_new_game() after user confirms dialog
        
        New in v1.4.3: Extracted to helper method for reuse.
        """
        self.is_menu_open = False
        self.start_game()
    
    # === MENU & GAMEPLAY HANDLERS ===
    
    def open_options(self) -> None:
        """Open virtual options window (v1.4.1)."""
        print("\n" + "="*60)
        print("APERTURA FINESTRA OPZIONI")
        print("="*60)
        
        # Switch to options mode
        self.is_menu_open = False
        self.is_options_mode = True
        
        # Open options through controller
        msg = self.gameplay_controller.options_controller.open_window()
        
        # Vocalize opening
        if self.screen_reader:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        print("Finestra opzioni aperta.")
        print("Usa frecce ↑↓ o tasti 1-5 per navigare.")
        print("Premi O o ESC per chiudere.")
        print("="*60)
    
    def close_options_and_return_to_menu(self) -> None:
        """Close options window and return to game submenu."""
        print("\n" + "="*60)
        print("CHIUSURA OPZIONI - RITORNO AL MENU")
        print("="*60)
        
        # Exit options mode
        self.is_options_mode = False
        self.is_menu_open = True
        
        # Re-announce game submenu
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu di gioco.",
                interrupt=True
            )
            pygame.time.wait(300)
            self.game_submenu._announce_menu_open()
    
    def start_game(self) -> None:
        """Start new game session."""
        print("\n" + "="*60)
        print("AVVIO PARTITA")
        print("="*60)
        
        # Reset e avvia nuova partita
        self.engine.reset_game()
        self.engine.new_game()
        
        # Reset ESC timer
        self.last_esc_time = 0
        
        # 🆕 Reset timer expiration flag (v1.5.2.2)
        self._timer_expired_announced = False
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Nuova partita avviata! Usa H per l'aiuto comandi.",
                interrupt=True
            )
        
        print("Partita in corso...")
        print("Premi H per l'aiuto comandi.")
        print("Premi ESC per tornare al menu (doppio ESC per uscita rapida).")
    
    def handle_events(self) -> None:
        """Main event loop - process all pygame events.
        
        Routes events based on current application state:
        - Menu open: Route to menu navigation (with ESC interception)
        - Options mode: Route to options controller
        - Gameplay: Route to gameplay controller (with double-ESC detection)
        
        NOTE v1.6.1: wxDialogs are modal (blocking), no longer need 
        priority routing in event loop. Dialog state management removed.
        """
        for event in pygame.event.get():
            # Window close event
            if event.type == QUIT:
                self.quit_app()
                return
            
            # 🆕 PRIORITY 0: Timer check event (v1.5.2.2)
            # Fires every 1 second during gameplay to check timeout
            if event.type == self.TIME_CHECK_EVENT:
                self._check_timer_expiration()
                continue  # Don't pass to other handlers
            
            # Route keyboard events based on state
            if self.is_menu_open:
                # Check for ESC key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # ESC in main menu → Exit dialog
                    if self.menu.active_submenu is None:
                        self.show_exit_dialog()
                        continue
                    
                    # ESC in game submenu → Return to main dialog (Commit #26)
                    elif self.menu.active_submenu == self.game_submenu:
                        self.show_return_to_main_dialog()
                        continue
                
                # Normal menu navigation (delegates to submenu if active)
                self.menu.handle_keyboard_events(event)
            
            elif self.is_options_mode:
                # Options window mode - route to gameplay controller
                self.gameplay_controller.handle_keyboard_events(event)
                
                # Check if options was closed
                if event.type == pygame.KEYDOWN:
                    if not self.gameplay_controller.options_controller.is_open:
                        # Options closed, return to menu
                        self.close_options_and_return_to_menu()
            
            else:
                # GAMEPLAY MODE - with double-ESC detection (Commit #27)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Only handle ESC if options not open
                    if not self.gameplay_controller.options_controller.is_open:
                        current_time = time.time()
                        
                        # Check if this is double-ESC (< 2 sec threshold)
                        if self.last_esc_time > 0 and current_time - self.last_esc_time <= self.DOUBLE_ESC_THRESHOLD:
                            # Double-ESC detected - instant abandon!
                            print("\n[DOUBLE-ESC] Uscita rapida!")
                            
                            if self.screen_reader:
                                self.screen_reader.tts.speak(
                                    "Uscita rapida!",
                                    interrupt=True
                                )
                                pygame.time.wait(300)
                            
                            # Auto-confirm abandon (skip dialog)
                            self.confirm_abandon_game()
                            self.last_esc_time = 0  # Reset timer
                        else:
                            # First ESC - show dialog
                            self.last_esc_time = current_time
                            self.show_abandon_game_dialog()
                        
                        continue  # Don't pass to gameplay controller
                
                # Normal gameplay commands
                self.gameplay_controller.handle_keyboard_events(event)
    
    def return_to_menu(self) -> None:
        """Return from gameplay to game submenu.
        
        Note: This method is now only called by gameplay_controller in legacy code paths.
        New behavior: ESC during gameplay shows abandon dialog (Commit #27).
        """
        print("\n" + "="*60)
        print("RITORNO AL MENU DI GIOCO (legacy path)")
        print("="*60)
        
        self.is_menu_open = True
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu di gioco.",
                interrupt=True
            )
            pygame.time.wait(300)
            # Re-announce game submenu
            self.game_submenu._announce_menu_open()
    
    def quit_app(self) -> None:
        """Graceful application shutdown."""
        print("\n" + "="*60)
        print("CHIUSURA APPLICAZIONE")
        print("="*60)
        
        if self.screen_reader:
            self.screen_reader.tts.speak("Chiusura in corso.", interrupt=True)
            pygame.time.wait(800)
        
        self.is_running = False
        pygame.quit()
        sys.exit(0)
    
    def run(self) -> None:
        """Main game loop.
        
        Runs at 60 FPS, processing events and updating display.
        Continues until is_running flag is set to False.
        """
        clock = pygame.time.Clock()
        
        print("\nLoop principale avviato (60 FPS)...")
        
        while self.is_running:
            # Process events
            pygame.event.pump()
            self.handle_events()
            
            # Update display (blank for audiogame)
            pygame.display.update()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        print("Loop principale terminato.")


def main():
    """Application entry point."""
    print("\n" + "="*60)
    print("🎴 SOLITARIO ACCESSIBILE - Clean Architecture")
    print("="*60)
    print("Versione: 2.0.0-beta (refactoring-engine branch)")
    print("Architettura: src/ (Clean Architecture - COMPLETA)")
    print("Modalità: Audiogame per non vedenti")
    print("Entry point: test.py")
    print("")
    print("✅✅✅ v1.4.2 COMPLETE! (Commits #24-28)")
    print("   - #24: Virtual Dialog Box ✓")
    print("   - #25: ESC in Main Menu ✓")
    print("   - #26: ESC in Game Submenu ✓")
    print("   - #27: ESC in Gameplay + Double-ESC ✓")
    print("   - #28: Welcome Message ✓")
    print("")
    print("🐛 v1.4.2.1 BUG FIX IN PROGRESS...")
    print("   - #29: Deck type from settings [1/3 COMPLETE]")
    print("   - #30: Ace suit validation [PENDING]")
    print("")
    print("Legacy version ancora disponibile: python acs.py")
    print("="*60)
    print("")
    
    try:
        app = SolitarioCleanArch()
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrotto dall'utente (Ctrl+C)")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"\n\n⚠ ERRORE FATALE: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
