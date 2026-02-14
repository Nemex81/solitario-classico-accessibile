"""Unit tests for ViewManager (hs_deckmanager pattern).

Tests the LIFO stack-based window management system.
"""

import pytest
import wx


class MockView(wx.Frame):
    """Mock view for testing."""
    
    def __init__(self, parent, title="Mock View"):
        super().__init__(parent, title=title)
        self.destroyed = False
        
    def Destroy(self):
        """Override to track destruction."""
        self.destroyed = True
        return super().Destroy()


@pytest.fixture
def wx_app():
    """Create wx.App instance for tests."""
    app = wx.App()
    yield app
    app.Destroy()


@pytest.fixture
def parent_frame(wx_app):
    """Create parent frame for ViewManager."""
    frame = wx.Frame(None, title="Parent Frame")
    yield frame
    frame.Destroy()


@pytest.fixture
def view_manager(parent_frame):
    """Create ViewManager instance."""
    from src.infrastructure.ui.view_manager import ViewManager
    vm = ViewManager(parent_frame)
    yield vm
    vm.clear_stack()


def test_register_view(view_manager):
    """Test view registration."""
    # Register a view constructor
    view_manager.register_view('test', lambda p: MockView(p, "Test View"))
    
    # Check it was registered
    assert 'test' in view_manager.view_constructors
    assert len(view_manager) == 0  # Stack still empty


def test_push_view(view_manager, parent_frame):
    """Test pushing a view onto stack."""
    # Register view
    view_manager.register_view('test', lambda p: MockView(p, "Test View"))
    
    # Push view
    view = view_manager.push_view('test')
    
    # Check view was created and pushed
    assert view is not None
    assert isinstance(view, MockView)
    assert len(view_manager) == 1
    assert view_manager.get_current_view() == view
    assert view.IsShown()


def test_push_multiple_views(view_manager, parent_frame):
    """Test pushing multiple views."""
    # Register views
    view_manager.register_view('view1', lambda p: MockView(p, "View 1"))
    view_manager.register_view('view2', lambda p: MockView(p, "View 2"))
    
    # Push first view
    view1 = view_manager.push_view('view1')
    assert len(view_manager) == 1
    assert view1.IsShown()
    
    # Push second view
    view2 = view_manager.push_view('view2')
    assert len(view_manager) == 2
    assert not view1.IsShown()  # Previous view hidden
    assert view2.IsShown()
    assert view_manager.get_current_view() == view2


def test_pop_view(view_manager, parent_frame):
    """Test popping view from stack."""
    # Setup: Push two views
    view_manager.register_view('view1', lambda p: MockView(p, "View 1"))
    view_manager.register_view('view2', lambda p: MockView(p, "View 2"))
    
    view1 = view_manager.push_view('view1')
    view2 = view_manager.push_view('view2')
    
    # Pop view2
    result = view_manager.pop_view()
    
    assert result is True
    assert len(view_manager) == 1
    assert view2.destroyed  # View2 was destroyed
    assert view1.IsShown()  # View1 restored
    assert view_manager.get_current_view() == view1


def test_pop_empty_stack(view_manager):
    """Test popping from empty stack."""
    result = view_manager.pop_view()
    assert result is False
    assert len(view_manager) == 0


def test_stack_depth(view_manager):
    """Test stack depth tracking."""
    assert len(view_manager) == 0
    
    # Register and push views
    view_manager.register_view('v1', lambda p: MockView(p, "V1"))
    view_manager.register_view('v2', lambda p: MockView(p, "V2"))
    view_manager.register_view('v3', lambda p: MockView(p, "V3"))
    
    view_manager.push_view('v1')
    assert len(view_manager) == 1
    
    view_manager.push_view('v2')
    assert len(view_manager) == 2
    
    view_manager.push_view('v3')
    assert len(view_manager) == 3
    
    view_manager.pop_view()
    assert len(view_manager) == 2
    
    view_manager.pop_view()
    assert len(view_manager) == 1


def test_clear_stack(view_manager):
    """Test clearing entire stack."""
    # Register and push multiple views
    for i in range(3):
        view_manager.register_view(f'v{i}', lambda p, i=i: MockView(p, f"View {i}"))
        view_manager.push_view(f'v{i}')
    
    assert len(view_manager) == 3
    
    # Clear stack
    view_manager.clear_stack()
    
    assert len(view_manager) == 0
    assert view_manager.get_current_view() is None


def test_get_current_view_empty(view_manager):
    """Test getting current view from empty stack."""
    assert view_manager.get_current_view() is None


def test_push_unregistered_view(view_manager):
    """Test pushing view that wasn't registered."""
    view = view_manager.push_view('nonexistent')
    
    assert view is None
    assert len(view_manager) == 0


def test_view_manager_repr(view_manager):
    """Test string representation."""
    # Empty stack
    repr_str = repr(view_manager)
    assert 'ViewManager' in repr_str
    assert 'stack_depth=0' in repr_str
    
    # With views
    view_manager.register_view('test', lambda p: MockView(p, "Test View"))
    view_manager.push_view('test')
    
    repr_str = repr(view_manager)
    assert 'stack_depth=1' in repr_str
    assert 'Test View' in repr_str


def test_lifo_order(view_manager):
    """Test LIFO (Last-In-First-Out) ordering."""
    # Register views
    for i in range(5):
        view_manager.register_view(f'v{i}', lambda p, i=i: MockView(p, f"View {i}"))
    
    # Push in order: 0, 1, 2, 3, 4
    views = []
    for i in range(5):
        views.append(view_manager.push_view(f'v{i}'))
    
    # Pop should return in reverse order: 4, 3, 2, 1, 0
    for i in range(4, -1, -1):
        current = view_manager.get_current_view()
        assert current.GetTitle() == f"View {i}"
        view_manager.pop_view()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
