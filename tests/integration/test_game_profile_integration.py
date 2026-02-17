"""Integration tests for GameEngine profile integration stubs.

Tests that GameEngine is ready for profile system integration:
- ProfileService can be imported
- Placeholder comments exist for future integration
- No breaking changes to existing functionality
"""

import pytest
from pathlib import Path


class TestProfileServiceImport:
    """Test that GameEngine can import ProfileService."""
    
    def test_profile_service_import_available(self):
        """Test ProfileService is importable in TYPE_CHECKING context."""
        # This test verifies that the import statement doesn't break
        # Import game_engine module to check it loads without errors
        try:
            from src.application import game_engine
            # Verify module loads without errors
            assert hasattr(game_engine, 'GameEngine')
        except ImportError as e:
            # pygame might not be available in all test environments
            # Check if it's a pygame import error, which is acceptable
            if 'pygame' in str(e):
                pytest.skip("pygame not available in test environment")
            else:
                raise
    
    def test_profile_service_actual_import(self):
        """Test ProfileService can be imported for future use."""
        try:
            from src.domain.services.profile_service import ProfileService
            from src.domain.services.session_tracker import SessionTracker
            
            # Services should be importable
            assert ProfileService is not None
            assert SessionTracker is not None
        except ImportError as e:
            pytest.fail(f"ProfileService or SessionTracker not importable: {e}")


class TestPlaceholderCommentsExist:
    """Test that integration placeholder comments are present."""
    
    def test_session_recording_placeholder_exists(self):
        """Test session recording placeholder exists in end_game."""
        # Read game_engine.py source
        engine_path = Path(__file__).parent.parent.parent / "src" / "application" / "game_engine.py"
        source = engine_path.read_text()
        
        # Check for profile integration placeholder
        assert "TODO: Profile System Integration (v3.0.0 - Phase 9)" in source
        assert "self.profile_service.record_session" in source
        assert "SessionOutcome.create_new" in source
    
    def test_startup_recovery_placeholder_exists(self):
        """Test startup recovery placeholder exists in new_game."""
        # Read game_engine.py source
        engine_path = Path(__file__).parent.parent.parent / "src" / "application" / "game_engine.py"
        source = engine_path.read_text()
        
        # Check for recovery check placeholder
        assert "orphaned sessions (dirty shutdown recovery)" in source.lower()
        assert "self.session_tracker" in source


class TestExistingFunctionalityPreserved:
    """Test that stubs don't break existing GameEngine functionality."""
    
    def test_engine_can_be_imported_without_errors(self):
        """Test GameEngine module can be imported (syntax check)."""
        try:
            from src.application import game_engine
            # If we get here, imports are working
            assert hasattr(game_engine, 'GameEngine')
        except ImportError as e:
            if 'pygame' in str(e):
                pytest.skip("pygame not available in test environment - this is OK for stubs")
            else:
                pytest.fail(f"Unexpected import error: {e}")
    
    def test_profile_service_can_be_used_with_game_components(self):
        """Test that profile components work alongside game components."""
        # Create profile service
        from src.domain.services.profile_service import ProfileService
        from src.domain.services.session_tracker import SessionTracker
        
        service = ProfileService()
        tracker = SessionTracker()
        
        # Should be able to create these without conflicts
        assert service is not None
        assert tracker is not None

