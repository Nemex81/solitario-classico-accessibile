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
        
        # Application: Game engine setup (now with settings!)
        print("Inizializzazione motore di gioco...")
        self.engine = GameEngine.create(
            audio_enabled=(self.screen_reader is not None),
            tts_engine="auto",
            verbose=1,
            settings=self.settings  # NEW PARAMETER (v1.4.2.1)
        )
        print("✓ Game engine pronto")
        
        # Application: Gameplay controller (now with settings!)
        print("Inizializzazione controller gameplay...")
        self.gameplay_controller = GamePlayController(
            engine=self.engine,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
            settings=self.settings  # NEW PARAMETER (v1.4.2.1)
        )
        print("✓ Controller pronto")
        
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
        
        # Infrastructure: Dialog boxes (v1.4.2 + v1.4.3)
        self.exit_dialog = None  # Exit confirmation dialog (Commit #25)
        self.return_to_main_dialog = None  # Submenu exit dialog (Commit #26)
        self.abandon_game_dialog = None  # Gameplay exit dialog (Commit #27)
        self.new_game_dialog = None  # New game confirmation dialog (v1.4.3)
        
        # Double-ESC feature (Commit #27)
        self.last_esc_time = 0  # Timestamp of last ESC press
        self.DOUBLE_ESC_THRESHOLD = 2.0  # Seconds for double-ESC detection
        
        # Application state
        self.is_menu_open = True
        self.is_options_mode = False
        self.is_running = True
        
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
        """Show exit confirmation dialog (Commit #25).
        
        Opens dialog asking "Vuoi uscire dall'applicazione?" with
        OK/Annulla buttons. OK has default focus.
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma uscita applicazione")
        print("="*60)
        
        self.exit_dialog = VirtualDialogBox(
            message="Vuoi uscire dall'applicazione?",
            buttons=["OK", "Annulla"],
            default_button=0,  # Focus on OK
            on_confirm=self.quit_app,
            on_cancel=self.close_exit_dialog,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
        )
        
        self.exit_dialog.open()
    
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
        
        self.exit_dialog = None
        
        # Re-announce main menu
        if self.menu.active_submenu is None:
            self.menu._announce_menu_open()
    
    def show_return_to_main_dialog(self) -> None:
        """Show return to main menu confirmation dialog (Commit #26).
        
        Opens dialog asking "Vuoi tornare al menu principale?" with
        Sì/No buttons. Sì has default focus.
        
        Triggered by:
        - ESC in game submenu
        - ENTER on "Chiudi" menu item
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma ritorno al menu principale")
        print("="*60)
        
        self.return_to_main_dialog = VirtualDialogBox(
            message="Vuoi tornare al menu principale?",
            buttons=["Sì", "No"],
            default_button=0,  # Focus on Sì
            on_confirm=self.confirm_return_to_main,
            on_cancel=self.close_return_dialog,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
        )
        
        self.return_to_main_dialog.open()
    
    def confirm_return_to_main(self) -> None:
        """Confirm return to main menu (Sì button).
        
        Closes game submenu and returns to main menu.
        Re-announces main menu after closing.
        """
        print("Confermato - Chiusura submenu e ritorno al menu principale")
        
        # Close dialog
        self.return_to_main_dialog = None
        
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
        
        self.return_to_main_dialog = None
        
        # Re-announce current submenu position
        self.game_submenu._announce_menu_open()
    
    def show_abandon_game_dialog(self) -> None:
        """Show abandon game confirmation dialog (Commit #27).
        
        Opens dialog asking "Vuoi abbandonare la partita e tornare al menu di gioco?" with
        Sì/No buttons. Sì has default focus.
        
        Triggered by:
        - ESC during gameplay
        
        Note: Returns to GAME SUBMENU, not main menu!
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma abbandono partita")
        print("="*60)
        
        self.abandon_game_dialog = VirtualDialogBox(
            message="Vuoi abbandonare la partita e tornare al menu di gioco?",
            buttons=["Sì", "No"],
            default_button=0,  # Focus on Sì
            on_confirm=self.confirm_abandon_game,
            on_cancel=self.close_abandon_dialog,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
        )
        
        self.abandon_game_dialog.open()
    
    def confirm_abandon_game(self) -> None:
        """Confirm abandon game (Sì button).
        
        Abandons current game and returns to GAME SUBMENU (not main menu!).
        Re-announces game submenu after abandoning.
        """
        print("Confermato - Abbandono partita e ritorno al menu di gioco")
        
        # Close dialog
        self.abandon_game_dialog = None
        
        # Reset ESC timer
        self.last_esc_time = 0
        
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
        
        self.abandon_game_dialog = None
        
        # Reset ESC timer
        self.last_esc_time = 0
    
    # === NEW GAME DIALOG HANDLERS (v1.4.3) ===
    
    def show_new_game_dialog(self) -> None:
        """Show new game confirmation dialog (v1.4.3).
        
        Opens dialog asking "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?" with
        Sì/No buttons. Sì has default focus.
        
        Triggered by:
        - "N" key during gameplay
        - "Nuova partita" menu selection when game is running
        
        Safety feature to prevent accidental game loss.
        """
        print("\n" + "="*60)
        print("DIALOG: Conferma nuova partita")
        print("="*60)
        
        self.new_game_dialog = VirtualDialogBox(
            message="Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
            buttons=["Sì", "No"],
            default_button=0,  # Focus on Sì
            on_confirm=self._confirm_new_game,
            on_cancel=self._cancel_new_game,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
        )
        
        self.new_game_dialog.open()
    
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
        
        # Close dialog
        self.new_game_dialog = None
        
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
        
        # Close dialog
        self.new_game_dialog = None
        
        # Announce cancellation
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Azione annullata. Torno alla partita.",
                interrupt=True
            )
            pygame.time.wait(300)
        
        # No further action needed, game continues
    
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
        - Exit dialog open: Route to exit dialog
        - Return dialog open: Route to return dialog (Commit #26)
        - Abandon dialog open: Route to abandon dialog (Commit #27)
        - Menu open: Route to menu navigation (with ESC interception)
        - Options mode: Route to options controller
        - Gameplay: Route to gameplay controller (with double-ESC detection)
        """
        for event in pygame.event.get():
            # Window close event
            if event.type == QUIT:
                self.quit_app()
                return
            
            # PRIORITY 1: Exit dialog open
            if self.exit_dialog and self.exit_dialog.is_open:
                self.exit_dialog.handle_keyboard_events(event)
                continue  # Block all other input
            
            # PRIORITY 2: Return to main dialog open (Commit #26)
            if self.return_to_main_dialog and self.return_to_main_dialog.is_open:
                self.return_to_main_dialog.handle_keyboard_events(event)
                continue  # Block all other input
            
            # PRIORITY 3: Abandon game dialog open (Commit #27)
            if self.abandon_game_dialog and self.abandon_game_dialog.is_open:
                # Check for double-ESC (instant confirm)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_time = time.time()
                    if current_time - self.last_esc_time <= self.DOUBLE_ESC_THRESHOLD:
                        # Double-ESC detected!
                        print("\n[DOUBLE-ESC] Uscita rapida!")
                        
                        if self.screen_reader:
                            self.screen_reader.tts.speak(
                                "Uscita rapida!",
                                interrupt=True
                            )
                            pygame.time.wait(300)
                        
                        # Auto-confirm abandon
                        self.confirm_abandon_game()
                        continue
                
                # Normal dialog handling
                self.abandon_game_dialog.handle_keyboard_events(event)
                continue  # Block all other input
            
            # PRIORITY 4: New game confirmation dialog open (v1.4.3)
            if self.new_game_dialog and self.new_game_dialog.is_open:
                self.new_game_dialog.handle_keyboard_events(event)
                continue  # Block all other input
            
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
                        
                        # Check if this is first ESC or dialog was just closed
                        if self.last_esc_time == 0 or current_time - self.last_esc_time > self.DOUBLE_ESC_THRESHOLD:
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
