#!/usr/bin/env python3
"""Test entry point for Clean Architecture version.

Launches Solitario Classico Accessibile using src/ modules with
proper dependency injection and separation of concerns.

This is a testing/development entry point. The production entry
point (acs.py) will be migrated once this is fully tested.

Usage:
    python test.py

Controls:
    0-6: Select tableau pile
    7-10: Select foundation pile (auto-move)
    SPACE: Draw from stock
    R: Recycle waste pile
    A: Attempt auto-move to foundation
    N: New game
    I: Get game info/statistics
    Q: Quit
    
    Two-number selection:
    - Press first pile number (source)
    - Press second pile number (destination)
    - Card(s) will move if valid
"""

import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from typing import Optional

# Clean Architecture imports (src/)
from src.application.game_engine import GameEngine


class SolitarioCleanArch:
    """Main application class using Clean Architecture.
    
    Provides a simple game loop for testing the new architecture
    without the complexity of the full UI.
    """
    
    def __init__(self):
        """Initialize application with dependency injection."""
        print("🎴 Solitario Classico Accessibile - Clean Architecture")
        print("=" * 60)
        print("Initializing...")
        
        # Initialize PyGame
        pygame.init()
        pygame.font.init()
        
        # Setup minimal display (for event handling)
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Solitario Accessibile - Clean Arch Test")
        self.screen.fill((255, 255, 255))
        pygame.display.flip()
        
        # Create GameEngine with audio enabled
        try:
            self.engine = GameEngine.create(
                audio_enabled=True,
                tts_engine="auto",
                verbose=1
            )
            print("✅ GameEngine initialized with audio")
        except Exception as e:
            print(f"⚠️  GameEngine initialized without audio: {e}")
            self.engine = GameEngine.create(audio_enabled=False)
        
        # Game state
        self.is_running = True
        self.selected_pile: Optional[int] = None  # For two-step moves
        
        print("=" * 60)
        print("Ready! Starting new game...")
        print()
        self._print_controls()
        
        # Start first game
        self.new_game()
    
    def _print_controls(self):
        """Print keyboard controls."""
        print("\n📋 CONTROLS:")
        print("  0-6    : Select tableau pile (base piles)")
        print("  7-10   : Select foundation pile (try auto-move)")
        print("  SPACE  : Draw cards from stock")
        print("  R      : Recycle waste pile")
        print("  A      : Attempt auto-move to foundation")
        print("  N      : New game")
        print("  I      : Show game info/statistics")
        print("  Q/ESC  : Quit")
        print("\n💡 TIP: Press two pile numbers to move cards between piles")
        print("    Example: Press 0, then 7 to move from tableau 0 to foundation 0\n")
    
    def new_game(self):
        """Start a new game."""
        success, message = self.engine.new_game()
        print(f"🎮 {message}")
        self.selected_pile = None
        self.show_game_info()
    
    def show_game_info(self):
        """Display current game state."""
        state = self.engine.get_game_state()
        stats = state['statistics']
        
        print("\n" + "=" * 60)
        print(f"📊 GAME STATUS")
        print("=" * 60)
        print(f"Moves: {stats['moves_count']}")
        print(f"Time: {stats['elapsed_time']:.0f}s")
        
        # Foundation status
        print("\n🏆 Foundations:")
        foundations = state['piles']['foundations']
        for i, foundation in enumerate(foundations):
            count = foundation['card_count']
            top = foundation['top_card'] if foundation['top_card'] else "Empty"
            print(f"  [{i+7}] Foundation {i}: {count} cards (top: {top})")
        
        # Tableau status
        print("\n🃏 Tableau:")
        tableaus = state['piles']['tableaus']
        for i, tableau in enumerate(tableaus):
            count = tableau['card_count']
            top = tableau['top_card'] if tableau['top_card'] else "Empty"
            print(f"  [{i}] Pile {i}: {count} cards (top: {top})")
        
        # Stock and waste
        stock = state['piles']['stock']
        waste = state['piles']['waste']
        print("\n📚 Stock & Waste:")
        print(f"  [11] Stock: {stock['card_count']} cards")
        print(f"  [12] Waste: {waste['card_count']} cards (top: {waste['top_card'] or 'Empty'})")
        
        print("=" * 60 + "\n")
        
        if self.selected_pile is not None:
            print(f"🎯 Selected pile: {self.selected_pile}")
            print("   Press another number to complete the move\n")
    
    def handle_pile_selection(self, pile_idx: int):
        """Handle pile selection for moves.
        
        Args:
            pile_idx: Index of pile (0-12)
        """
        if self.selected_pile is None:
            # First selection - select source pile
            self.selected_pile = pile_idx
            pile_info = self.engine.get_pile_info(pile_idx)
            if pile_info:
                print(f"\n✅ Selected pile {pile_idx}: {pile_info}")
                print("   Press another pile number to move card(s)\n")
            else:
                print(f"\n❌ Invalid pile: {pile_idx}\n")
                self.selected_pile = None
        else:
            # Second selection - execute move
            source = self.selected_pile
            target = pile_idx
            print(f"\n🔄 Moving from pile {source} to pile {target}...")
            
            success, message = self.engine.move_card(source, target)
            print(f"{'✅' if success else '❌'} {message}\n")
            
            # Reset selection
            self.selected_pile = None
            
            # Show updated state
            if success:
                self.show_game_info()
                
                # Check victory
                if self.engine.is_victory():
                    print("\n" + "🎊" * 20)
                    print("🎉 CONGRATULATIONS! YOU WON! 🎉")
                    print("🎊" * 20 + "\n")
    
    def draw_from_stock(self):
        """Draw cards from stock."""
        print("\n🎴 Drawing from stock...")
        success, message = self.engine.draw_from_stock(count=3)
        print(f"{'✅' if success else '❌'} {message}\n")
        
        if success:
            # Show waste pile info
            waste_info = self.engine.get_pile_info(12)  # Waste pile
            if waste_info:
                print(f"   Waste pile: {waste_info}\n")
    
    def recycle_waste(self):
        """Recycle waste pile back to stock."""
        print("\n♻️  Recycling waste pile...")
        success, message = self.engine.recycle_waste(shuffle=False)
        print(f"{'✅' if success else '❌'} {message}\n")
    
    def auto_move(self):
        """Attempt automatic move to foundation."""
        print("\n🤖 Attempting auto-move to foundation...")
        success, message = self.engine.auto_move_to_foundation()
        print(f"{'✅' if success else '❌'} {message}\n")
        
        if success:
            self.show_game_info()
            
            # Check victory
            if self.engine.is_victory():
                print("\n" + "🎊" * 20)
                print("🎉 CONGRATULATIONS! YOU WON! 🎉")
                print("🎊" * 20 + "\n")
    
    def handle_keyboard_event(self, event):
        """Handle keyboard input.
        
        Args:
            event: PyGame keyboard event
        """
        if event.type != KEYDOWN:
            return
        
        key = event.key
        
        # Quit
        if key == K_ESCAPE or event.unicode.lower() == 'q':
            print("\n👋 Quitting...\n")
            self.quit_app()
            return
        
        # New game
        if event.unicode.lower() == 'n':
            print("\n🔄 Starting new game...\n")
            self.new_game()
            return
        
        # Show info
        if event.unicode.lower() == 'i':
            self.show_game_info()
            return
        
        # Draw from stock
        if key == pygame.K_SPACE:
            self.draw_from_stock()
            return
        
        # Recycle waste
        if event.unicode.lower() == 'r':
            self.recycle_waste()
            return
        
        # Auto-move
        if event.unicode.lower() == 'a':
            self.auto_move()
            return
        
        # Pile selection (0-9 on keyboard)
        if event.unicode.isdigit():
            pile_idx = int(event.unicode)
            if 0 <= pile_idx <= 9:
                self.handle_pile_selection(pile_idx)
            else:
                print(f"\n❌ Invalid pile index: {pile_idx} (must be 0-9)\n")
            return
        
        # Number pad (for pile 10)
        if key == pygame.K_KP1 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            # SHIFT+1 on numpad = pile 10 (last foundation)
            self.handle_pile_selection(10)
            return
    
    def handle_events(self):
        """Main event loop."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit_app()
                return
            
            self.handle_keyboard_event(event)
    
    def quit_app(self):
        """Clean shutdown."""
        print("Shutting down...")
        pygame.time.wait(500)
        self.is_running = False
        pygame.quit()
        sys.exit(0)
    
    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        
        print("\n🎮 Game loop started. Waiting for input...\n")
        
        while self.is_running:
            pygame.event.pump()
            self.handle_events()
            pygame.display.update()
            clock.tick(30)  # 30 FPS


def main():
    """Application entry point."""
    try:
        app = SolitarioCleanArch()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
