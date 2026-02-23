import pytest
from src.infrastructure.di.dependency_container import DependencyContainer

def test_get_audio_manager_singleton():
    """Verifica che get_audio_manager ritorni sempre la stessa istanza (singleton)."""
    container = DependencyContainer()
    am1 = container.get_audio_manager()
    am2 = container.get_audio_manager()
    assert am1 is am2
    # Deve esporre almeno il metodo initialize
    assert hasattr(am1, "initialize")
    # Deve esporre almeno il metodo shutdown
    assert hasattr(am1, "shutdown")

@pytest.mark.unit
def test_get_audio_manager_stub_on_failure(monkeypatch):
    """Verifica che venga restituito uno stub se AudioManager fallisce."""
    container = DependencyContainer()
    # Monkeypatch AudioManager per sollevare eccezione
    import src.infrastructure.di.dependency_container as di_mod
    def fail_init():
        raise RuntimeError("fail")
    monkeypatch.setattr(
        "src.infrastructure.config.audio_config_loader.AudioConfigLoader.load",
        lambda: (_ for _ in ()).throw(RuntimeError("fail"))
    )
    am = container.get_audio_manager()
    # Lo stub espone is_available = False
    assert hasattr(am, "is_available")
    assert am.is_available is False
