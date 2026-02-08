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
       - services/: GameService
    
    ✅ Application Layer:
       - GameEngine: Main game facade
       - GamePlayController: Gameplay orchestration
       - InputHandler: Keyboard → Command mapping [Commit #7]
       - GameSettings: Configuration management [Commit #8]
       - TimerManager: Timer functionality [Commit #8]
    
    ✅ Infrastructure Layer:
       - accessibility/: ScreenReader, TtsProvider [Commit #5]
       - ui/: VirtualMenu [Commit #6]
    
    ✅ Presentation Layer:
       - GameFormatter: Output formatting [Commit #9]

All architectural components complete and ready for integration.

New in v1.4.1 [Commit #15]:
- Hierarchical menu system (Main → Game Submenu)
- Virtual options window (O key settings management)
"""

import sys
import pygame
from pygame.locals import QUIT

# Application layer
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController

# New components available (Commits #7-9):
# from src.application import InputHandler, GameCommand  # Keyboard mapping
# from src.application import GameSettings               # Configuration
# from src.application import TimerManager, TimerState   # Timer
# from src.presentation import GameFormatter             # Output formatting

# Infrastructure layer - Accessibility (Commit #5)
from src.infrastructure.ui.menu import VirtualMenu
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
        engine: GameEngine facade for game logic
        gameplay_controller: Keyboard commands orchestrator
        menu: Virtual main menu for navigation
        game_submenu: Secondary menu for game options (New in v1.4.1)
        is_menu_open: Current UI state (menu vs gameplay/options)
        is_options_mode: Options window active (v1.4.1)
        is_running: Main loop control flag
    """
    
    def __init__(self):
        """Initialize application with all components.
        
        Future Integration:
        - InputHandler will replace direct pygame key handling
        - GameSettings will manage configuration
        - TimerManager will handle timed games
        - GameFormatter will replace ad-hoc message formatting
        """
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
        
        # Application: Game engine setup
        print("Inizializzazione motore di gioco...")
        self.engine = GameEngine.create(
            audio_enabled=(self.screen_reader is not None),
            tts_engine="auto",
            verbose=1
        )
        print("✓ Game engine pronto")
        
        # Application: Gameplay controller
        print("Inizializzazione controller gameplay...")
        self.gameplay_controller = GamePlayController(
            engine=self.engine,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
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
        
        # Game submenu (new in v1.4.1)
        self.game_submenu = VirtualMenu(
            items=[
                "Nuova partita",
                "Opzioni",
                "Chiudi"
            ],
            callback=self.handle_game_submenu_selection,
            screen=self.screen,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
            parent_menu=self.menu  # Link to parent for ESC handling
        )
        
        print("✓ Menu pronto")
        
        # Application state
        self.is_menu_open = True
        self.is_options_mode = False  # New: Options window state
        self.is_running = True
        
        print("="*60)
        print("✓ Applicazione avviata con successo!")
        print("✓ Architettura Clean completa (15/15 commits)")
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
                0: Open game submenu (new in v1.4.1)
                1: Quit application
        """
        if selected_item == 0:
            # Open game submenu instead of starting game directly
            self.menu.open_submenu(self.game_submenu)
        elif selected_item == 1:
            # Esci
            self.quit_app()
    
    def handle_game_submenu_selection(self, selected_item: int) -> None:
        """Handle game submenu item selection callback (new in v1.4.1).
        
        Args:
            selected_item: Index of selected submenu item
                0: Start new game
                1: Open virtual options window
                2: Close submenu and return to main menu
        """
        if selected_item == 0:
            # Nuova partita
            self.is_menu_open = False
            self.start_game()
        elif selected_item == 1:
            # Opzioni
            self.open_options()
        elif selected_item == 2:
            # Chiudi - return to main menu
            self.menu.close_submenu()
    
    def open_options(self) -> None:
        """Open virtual options window (new in v1.4.1).
        
        Opens interactive settings window managed by GamePlayController.
        User can modify settings using keyboard commands documented in
        OptionsWindowController.
        
        Flow:
        1. Close menu and enter options mode
        2. Open options via gameplay_controller
        3. Route all input to options controller until closed
        4. Return to menu when options closed
        """
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
        """Close options window and return to game submenu.
        
        Called when user closes options from within the window.
        """
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
        """Start new game session.
        
        Initializes game state and announces start.
        """
        print("\n" + "="*60)
        print("AVVIO PARTITA")
        print("="*60)
        
        # Reset e avvia nuova partita
        self.engine.reset_game()
        self.engine.new_game()
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Nuova partita avviata! Usa H per l'aiuto comandi.",
                interrupt=True
            )
        
        print("Partita in corso...")
        print("Premi H per l'aiuto comandi.")
        print("Premi ESC per tornare al menu.")
    
    def handle_events(self) -> None:
        """Main event loop - process all pygame events.
        
        Routes events based on current application state:
        - Menu open: Route to menu navigation
        - Options mode: Route to options controller
        - Gameplay: Route to gameplay controller
        """
        for event in pygame.event.get():
            # Window close event
            if event.type == QUIT:
                self.quit_app()
                return
            
            # Route keyboard events based on state
            if self.is_menu_open:
                # Menu navigation (delegates to submenu if active)
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
                # Normal gameplay commands
                self.gameplay_controller.handle_keyboard_events(event)
                
                # Check ESC to return to menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Only return to menu if options not open
                        if not self.gameplay_controller.options_controller.is_open:
                            self.return_to_menu()
    
    def return_to_menu(self) -> None:
        """Return from gameplay to main menu."""
        print("\n" + "="*60)
        print("RITORNO AL MENU")
        print("="*60)
        
        self.is_menu_open = True
        
        if self.screen_reader:
            self.screen_reader.tts.speak(
                "Ritorno al menu principale.",
                interrupt=True
            )
            pygame.time.wait(500)
            # Re-announce menu
            self.menu._announce_menu_open()
    
    def quit_app(self) -> None:
        """Graceful application shutdown.
        
        Announces closure, waits for TTS completion, and exits.
        """
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
    """Application entry point.
    
    Prints banner, creates application instance, and starts main loop.
    """
    print("\n" + "="*60)
    print("🎴 SOLITARIO ACCESSIBILE - Clean Architecture")
    print("="*60)
    print("Versione: 2.0.0-beta (refactoring-engine branch)")
    print("Architettura: src/ (Clean Architecture - COMPLETA)")
    print("Modalità: Audiogame per non vedenti")
    print("Entry point: test.py")
    print("")
    print("✅ Commits 1-15: Tutti completati!")
    print("   - Domain Layer: Models, Rules, Services")
    print("   - Application Layer: Engine, Controllers, Settings, Input")
    print("   - Infrastructure Layer: Accessibility, UI")
    print("   - Presentation Layer: Formatters")
    print("   - v1.4.1: Menu secondario + Finestra opzioni (COMPLETA!)")
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
