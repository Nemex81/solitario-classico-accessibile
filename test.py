"""Clean Architecture entry point - Audiogame version.

Launches the accessible solitaire game using Clean Architecture
with pure audiogame interface (no visual widgets, only TTS feedback).

Usage:
    python test.py

Controls:
    Menu: UP/DOWN arrows + ENTER
    Game: See H for help (60+ keyboard commands)

Architecture:
    - Domain: Game logic (deck, table, rules)
    - Application: Orchestration (engine, controller)
    - Infrastructure: External adapters (TTS, UI)
    - Presentation: Output formatting
"""

import sys
import pygame
from pygame.locals import QUIT

# Application layer
from src.application.game_engine import GameEngine
from src.application.gameplay_controller import GamePlayController

# Infrastructure layer
from src.infrastructure.ui.menu import VirtualMenu
from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import create_tts_provider


class SolitarioCleanArch:
    """Main application class - Audiogame for blind users.
    
    Manages application lifecycle and orchestrates menu ↔ gameplay flow.
    Uses Clean Architecture with dependency injection.
    
    Attributes:
        screen: PyGame surface (blank white for audiogame)
        screen_reader: ScreenReader with TTS provider
        engine: GameEngine facade for game logic
        gameplay_controller: Keyboard commands orchestrator
        menu: Virtual menu for navigation
        is_menu_open: Current UI state (menu vs gameplay)
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
        
        # Infrastructure: Virtual menu
        print("Inizializzazione menu...")
        self.menu = VirtualMenu(
            items=[
                "Gioca al solitario classico",
                "Esci dal gioco"
            ],
            callback=self.handle_menu_selection,
            screen=self.screen,
            screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr()
        )
        print("✓ Menu pronto")
        
        # Application state
        self.is_menu_open = True
        self.is_running = True
        
        print("="*60)
        print("✓ Applicazione avviata con successo!")
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
        """Handle menu item selection callback.
        
        Args:
            selected_item: Index of selected menu item
                0: Start game
                1: Quit application
        """
        if selected_item == 0:
            # Avvia partita
            self.is_menu_open = False
            self.start_game()
        elif selected_item == 1:
            # Esci
            self.quit_app()
    
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
        
        Routes events to menu or gameplay controller based on
        current application state.
        """
        for event in pygame.event.get():
            # Window close event
            if event.type == QUIT:
                self.quit_app()
                return
            
            # Route keyboard events based on state
            if self.is_menu_open:
                # Menu navigation
                self.menu.handle_keyboard_events(event)
            else:
                # Gameplay commands
                self.gameplay_controller.handle_keyboard_events(event)
                
                # Check ESC to return to menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
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
    print("Architettura: src/ (Clean Architecture)")
    print("Modalità: Audiogame per non vedenti")
    print("Entry point: test.py")
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
