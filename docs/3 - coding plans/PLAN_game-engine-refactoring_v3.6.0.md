# PLAN — GameEngine Refactoring & Plugin System v3.6.0

---

## 📋 Executive Summary

| Campo               | Valore                                                    |
|---------------------|-----------------------------------------------------------|
| **Tipo**            | Refactoring + Feature                                     |
| **Priorità**        | Alta                                                      |
| **Stato**           | READY                                                     |
| **Branch**          | `feature/game-engine-refactoring-v3.6.0`                  |
| **Versione target** | v3.6.0                                                    |
| **Data**            | 2026-03-07                                                |
| **Autore**          | Copilot (generato da analisi iterativa — report v1/v2/v3) |
| **Effort stimato**  | 5 giorni / 12 commit atomici                              |
| **Fasi**            | 5 (Fase 0 — prerequisiti + Fasi 1–4)                      |

**Documento design correlato**: `docs/2 - projects/DESIGN_game-engine-refactoring.md` (da creare in Fase 0)

**Cruscotto operativo**: `docs/TODO.md` (da creare in Fase 0)

---

## 🎯 Problema / Obiettivo

### Problema

`src/application/game_engine.py` (attualmente ~2050 righe, ~46 metodi) concentra in un'unica facade:

- Logica di annuncio TTS — chiamate a `self.screen_reader.tts.speak(...)` tramite wrapper `_speak()` (~20 punti), senza un componente dedicato
- Configurazione partita e ricreazione deck — logica **inline** in `new_game()` (non come metodi separati estratti)
- Registrazione sessione — logica **inline** in `end_game()` che costruisce `SessionOutcome` tramite `SessionOutcome.create_new()` con ~15 parametri
- Gestione plugin deck/regole — codifica hard-coded con `if/elif` su tipo stringa

Conseguenze:

1. **Accoppiamento elevato** — ogni modifica richiede comprendere ~2050 righe di contesto
2. **Impossibilità di estendere** deck/regole senza modificare il core applicativo
3. **Accessibilità non configurabile** — `tts_rate` e `tts_volume` non persistono nel profilo utente
4. **Single Responsibility violata** — `GameEngine` fa troppe cose distinte

### Obiettivo

Decomporre `GameEngine` in componenti con responsabilità singola, aggiungere un sistema di plugin esplicito per deck e regole di gioco, e rendere i parametri TTS persistenti nel profilo utente. Tutto mantenendo **piena retrocompatibilità** con l'utente finale.

---

## 💡 Soluzione

### Architettura Target

```
Domain Layer:
  src/domain/interfaces/
    __init__.py                           ← CREATE (marca package)
    protocols.py                          ← CREATE (DeckProvider, RuleSet Protocol)
  src/domain/models/
    profile.py                            ← MODIFY (aggiunge tts_rate, tts_volume a UserProfile)

Application Layer:
  src/application/
    game_engine.py                        ← MODIFY (delega ai nuovi componenti)
    game_configurator.py                  ← CREATE (deck, settings, ricreazione tavolo)
    tts_announcer.py                      ← CREATE (delega TTS a ScreenReader)
    session_recorder.py                   ← CREATE (costruisce/persiste SessionOutcome)
    input_handler.py                      ← ESISTENTE, invariato

Infrastructure Layer:
  src/infrastructure/
    di_container.py                       ← MODIFY (registra nuovi componenti)
    storage/
      profile_storage.py                  ← MODIFY (serializza tts_rate, tts_volume)
    plugins/
      __init__.py                         ← CREATE
      plugin_registry.py                  ← CREATE (registry esplicito dict)
      french_deck_provider.py             ← CREATE
      neapolitan_deck_provider.py         ← CREATE
      klondike_ruleset.py                 ← CREATE

Presentation Layer:
  src/presentation/dialogs/
    options_dialog.py                     ← CREATE (nuovo dialog — il file NON esiste nel codebase)

Documentation:
  docs/2 - projects/DESIGN_game-engine-refactoring.md  ← CREATE (Fase 0)
  docs/UX_SHORTCUTS.md                    ← CREATE
  docs/API.md                             ← MODIFY
  docs/ARCHITECTURE.md                    ← MODIFY
  CHANGELOG.md                            ← MODIFY
  docs/TODO.md                            ← CREATE (cruscotto operativo)
```

---

## 📊 Impact Assessment

| File | Layer | Operazione | Rischio |
|------|-------|------------|---------|
| `src/application/game_engine.py` | Application | MODIFY | Alto |
| `src/application/tts_announcer.py` | Application | CREATE | Basso |
| `src/application/game_configurator.py` | Application | CREATE | Basso |
| `src/application/session_recorder.py` | Application | CREATE | Basso |
| `src/application/input_handler.py` | Application | INVARIATO | — |
| `src/domain/interfaces/__init__.py` | Domain | CREATE | Basso |
| `src/domain/interfaces/protocols.py` | Domain | CREATE | Basso |
| `src/domain/models/profile.py` | Domain | MODIFY | Medio |
| `src/domain/services/profile_service.py` | Domain | MODIFY (minor) | Basso |
| `src/infrastructure/di_container.py` | Infrastructure | MODIFY | Medio |
| `src/infrastructure/storage/profile_storage.py` | Infrastructure | MODIFY | Medio |
| `src/infrastructure/plugins/__init__.py` | Infrastructure | CREATE | Basso |
| `src/infrastructure/plugins/plugin_registry.py` | Infrastructure | CREATE | Basso |
| `src/infrastructure/plugins/french_deck_provider.py` | Infrastructure | CREATE | Basso |
| `src/infrastructure/plugins/neapolitan_deck_provider.py` | Infrastructure | CREATE | Basso |
| `src/infrastructure/plugins/klondike_ruleset.py` | Infrastructure | CREATE | Basso |
| `src/presentation/dialogs/options_dialog.py` | Presentation | CREATE | Alto |
| `docs/2 - projects/DESIGN_game-engine-refactoring.md` | Docs | CREATE | Nessuno |
| `docs/UX_SHORTCUTS.md` | Docs | CREATE | Nessuno |
| `docs/API.md` | Docs | MODIFY | Nessuno |
| `docs/ARCHITECTURE.md` | Docs | MODIFY | Nessuno |
| `CHANGELOG.md` | Docs | MODIFY | Nessuno |
| `docs/TODO.md` | Docs | CREATE | Nessuno |

---

## 📐 Requisiti Funzionali

### RF-1: Decomposizione GameEngine

- `GameEngine` NON chiama più `ScreenReader.speak(...)` direttamente — delega a `TTSAnnouncer`
- `GameEngine` NON gestisce più deck e settings direttamente — delega a `GameConfigurator`
- `GameEngine` NON costruisce più `SessionOutcome` direttamente — delega a `SessionRecorder`
- `GameEngine` mantiene ancora stato di gioco (wrapper su `GameService`, `ScoringService`, etc.)
- Zero regressioni: tutti i comandi da tastiera funzionano identicamente prima e dopo

### RF-2: TTS configurabile per profilo

- `UserProfile` espone `tts_rate: int = 0` (range 0–100, mappato a -10/+10 per `TtsProvider.set_rate()`) e `tts_volume: int = 80` (range 0–100, mappato a 0.0–1.0 per `TtsProvider.set_volume()`)
- `ProfileStorage` serializza/deserializza i nuovi campi con retrocompatibilità (default su profili legacy)
- `TTSAnnouncer` (Application layer) espone `apply_tts_settings(tts_rate, tts_volume)` che chiama `TtsProvider.set_rate()` e `TtsProvider.set_volume()` — **NON** `ProfileService`/Domain (violerebbe Clean Architecture)
- `OptionsDialog` mostra slider Rate e Volume TTS; salva modifica al profilo attivo
- I valori persistono dopo riavvio e vengono applicati all'avvio di ogni sessione

### RF-3: Plugin system deck e regole

- `protocols.py` definisce `DeckProvider` (Protocol) e `RuleSet` (Protocol) nel Domain layer
- `DeckProvider.create_deck() -> ProtoDeck` ritorna il tipo base `ProtoDeck`
- `plugin_registry.py` registra provider/ruleset in dict esplicito (nessuna discovery dinamica)
- `StandardFrenchDeckProvider` e `NeapolitanDeckProvider` implementati e registrati
- `KlondikeRuleSet` implementato, riceve `ProtoDeck` nel costruttore
- `GameConfigurator` usa il registry per creare deck e regole
- `OptionsDialog` mostra combo box per selezionare deck e set di regole

### RF-4: Documentazione accessibile

- `docs/UX_SHORTCUTS.md` elenca tutti i comandi da tastiera (estratti da `input_handler.py`)
- `docs/API.md` aggiornato con tutti i nuovi moduli e firme pubbliche
- `docs/ARCHITECTURE.md` aggiornato con nuova struttura a componenti e sezione plugin

---

## 🏗️ Architettura Layer

```
Presentation  →  Application  →  Domain  ←  Infrastructure
(dialogs)        (game_engine,    (models,    (di_container,
                  tts_announcer,   interfaces, plugins/,
                  game_configurator, services)  storage/)
                  session_recorder,
                  input_handler)
```

**Regole di dipendenza (invarianti — mai violare)**:

- `src/domain/` — zero import da `application`, `infrastructure`, `presentation`
- `src/application/` — import solo da `domain`; mai `wx` o `pygame`
- `src/infrastructure/` — implementa interfacce Domain; può importare `domain` e `application`
- `src/presentation/` — dipende da `application`; solo view logic (no business logic)

---

## 🔧 Implementazione

### Fase 0 — Prerequisiti e Setup

**Obiettivo**: Creare il DESIGN doc, strutture directory mancanti, cruscotto `docs/TODO.md`.

**Nessun prerequisito.**

**File coinvolti**:

- `docs/2 - projects/DESIGN_game-engine-refactoring.md` — CREATE
- `src/domain/interfaces/__init__.py` — CREATE (file vuoto, marca il package)
- `docs/TODO.md` — CREATE (cruscotto con link a questo PLAN e checklist fasi 0–4)

**Contenuto minimo `DESIGN_game-engine-refactoring.md`**:

```markdown
# DESIGN — GameEngine Refactoring & Plugin System

Stato: APPROVED | Versione target: v3.6.0

## Idea
GameEngine soffre di God Object anti-pattern (2050 righe, 46 metodi).
Decomporlo in componenti responsabili singoli e aggiungere interfacce
per plugin deck/regole estendibili senza modificare il core.

## Attori
- TTSAnnouncer: delega annunci TTS a ScreenReader
- GameConfigurator: gestisce deck e settings
- SessionRecorder: costruisce e persiste SessionOutcome
- DeckProvider / RuleSet: protocolli plugin nel Domain layer
- plugin_registry: registry esplicito in Infrastructure

## Invarianti
- ScreenReader (TTS/NVDA) e AudioManager (PCM/pygame) non si toccano mai
- Zero breaking changes per utenti esistenti
- Plugin discovery SEMPRE esplicita (no importlib glob)
```

**Commit**:
```
chore(docs): crea DESIGN doc e struttura src/domain/interfaces/ per v3.6.0
```

**Checklist**:
- [ ] `docs/2 - projects/DESIGN_game-engine-refactoring.md` creato con sezioni Idea, Attori, Invarianti
- [ ] `src/domain/interfaces/__init__.py` creato (anche se vuoto)
- [ ] `docs/TODO.md` creato con link a `docs/3 - coding plans/PLAN_game-engine-refactoring_v3.6.0.md`

---

### Fase 1 — Decomposizione GameEngine

**Prerequisito**: Fase 0 completata.
**Priorità**: Alta — prerequisito di Fase 3.

**File coinvolti**:

- `src/application/tts_announcer.py` — CREATE
- `src/application/game_configurator.py` — CREATE
- `src/application/session_recorder.py` — CREATE
- `src/application/game_engine.py` — MODIFY (delega ai nuovi componenti)
- `src/infrastructure/di_container.py` — MODIFY (metodi factory per i nuovi componenti)

#### Fase 1a: TTSAnnouncer

`TTSAnnouncer` incapsula **tutte** le chiamate `ScreenReader.speak(...)` per annunci TTS.

> **CRITICO — Non confondere i due sistemi audio**:
>
> - `TTSAnnouncer` usa **esclusivamente** `TtsProvider` (sintetizzatore vocale NVDA/SAPI5)
>   ricevuto tramite `screen_reader.tts` — `ScreenReader` **non ha** un metodo `speak()`
> - `AudioManager` gestisce **esclusivamente** PCM (file WAV via `pygame.mixer`)
>
> I due sistemi sono completamente indipendenti. `TTSAnnouncer` NON usa mai `AudioManager`.

```python
# src/application/tts_announcer.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from src.infrastructure.audio.tts_provider import TtsProvider

_ui_logger = logging.getLogger('ui')


class TTSAnnouncer:
    """Delegato per tutti gli annunci TTS verso TtsProvider (NVDA/SAPI5).

    Riceve direttamente TtsProvider (strategy), NON ScreenReader.
    ScreenReader.speak() non esiste — il metodo speak() è su TtsProvider.
    La catena corretta: screen_reader.tts.speak(...); da cui si estrae .tts.
    """

    def __init__(self, tts: Optional["TtsProvider"]) -> None:
        self._tts = tts

    def announce(self, message: str, interrupt: bool = True) -> None:
        """Annuncia un messaggio via sintetizzatore vocale."""
        if self._tts is None:
            return  # graceful degradation se TTS non disponibile
        try:
            self._tts.speak(message, interrupt=interrupt)
            _ui_logger.debug(f"TTS: {message!r}")
        except Exception:
            _ui_logger.warning(f"TTS speak failed for: {message!r}")

    def apply_tts_settings(self, tts_rate: int, tts_volume: int) -> None:
        """Applica rate e volume TTS al provider (Application layer).

        Converte i valori UI (range 0–100) ai range di TtsProvider:
          - tts_rate: 0–100 → -10/+10 (0=lento, 50=default sistema, 100=veloce)
          - tts_volume: 0–100 → 0.0–1.0

        Args:
            tts_rate: velocità voce da UserProfile (0–100)
            tts_volume: volume voce da UserProfile (0–100)
        """
        if self._tts is None:
            return
        mapped_rate = int((tts_rate / 100.0) * 20) - 10   # 0–100 → -10/+10
        mapped_volume = tts_volume / 100.0                 # 0–100 → 0.0–1.0
        self._tts.set_rate(mapped_rate)
        self._tts.set_volume(mapped_volume)

    def announce_game_start(self, profile_name: str) -> None:
        self.announce(f"Partita avviata per {profile_name}")

    def announce_move(self, card_label: str, from_pile: str, to_pile: str) -> None:
        self.announce(f"{card_label} spostato da {from_pile} a {to_pile}")

    def announce_victory(self) -> None:
        self.announce("Vittoria! Ottimo lavoro!")

    def announce_game_over(self) -> None:
        self.announce("Partita terminata")
```

**Rationale**: isola tutte le chiamate TTS sparse in `GameEngine` (pattern `self._speak(msg)` che catena a `self.screen_reader.tts.speak(msg)`) in un unico componente testabile. `GameEngine` chiamerà `self._tts.announce(msg)` invece di `self._speak(msg)`. I metodi con logica business complessa come `_announce_draw_threshold_warning` (dipendente da `ScoreWarningLevel` e `ScoreFormatter`) **restano in `GameEngine`** — solo il messaggio finale già formattato viene passato a `TTSAnnouncer.announce()`.

**Testing**:

```python
# tests/unit/application/test_tts_announcer.py
import pytest
from unittest.mock import MagicMock
from src.application.tts_announcer import TTSAnnouncer


@pytest.mark.unit
class TestTTSAnnouncer:
    def test_announce_calls_tts_provider_speak(self):
        tts = MagicMock()
        announcer = TTSAnnouncer(tts)
        announcer.announce("Ciao")
        tts.speak.assert_called_once_with("Ciao", interrupt=True)

    def test_announce_interrupt_false_passes_through(self):
        tts = MagicMock()
        announcer = TTSAnnouncer(tts)
        announcer.announce("Messaggio", interrupt=False)
        tts.speak.assert_called_once_with("Messaggio", interrupt=False)

    def test_announce_with_none_tts_does_not_crash(self):
        """Graceful degradation — TTS non disponibile non deve crashare."""
        announcer = TTSAnnouncer(None)
        announcer.announce("Test")  # deve completare senza eccezione

    def test_announce_move_contains_all_parts(self):
        tts = MagicMock()
        announcer = TTSAnnouncer(tts)
        announcer.announce_move("Asso di Cuori", "Stock", "Tableau 1")
        call_text = tts.speak.call_args[0][0]
        assert "Asso di Cuori" in call_text
        assert "Stock" in call_text
        assert "Tableau 1" in call_text

    def test_apply_tts_settings_converts_and_calls_provider(self):
        """apply_tts_settings converte range 0–100 a -10/+10 e 0.0–1.0."""
        tts = MagicMock()
        announcer = TTSAnnouncer(tts)
        announcer.apply_tts_settings(tts_rate=75, tts_volume=80)
        tts.set_rate.assert_called_once_with(5)    # (75/100)*20 - 10 = 5
        tts.set_volume.assert_called_once_with(0.8)  # 80/100 = 0.8

    def test_announce_does_not_use_audio_manager(self):
        """TTSAnnouncer non deve mai dipendere da AudioManager."""
        tts = MagicMock()
        announcer = TTSAnnouncer(tts)
        assert not hasattr(announcer, '_audio_manager')
```

**Commit Fase 1a**:
```
feat(application): aggiunge TTSAnnouncer — delega TTS da GameEngine a componente dedicato
```

---

#### Fase 1b: GameConfigurator

`GameConfigurator` gestisce inizializzazione del deck, applicazione settings, ricreazione tavolo.

```python
# src/application/game_configurator.py
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.domain.services.game_settings import GameSettings
    from src.domain.models.deck import ProtoDeck
    from src.domain.rules.solitaire_rules import SolitaireRules

_game_logger = logging.getLogger('game')


class GameConfigurator:
    """Gestisce configurazione partita: deck, regole, applicazione settings."""

    def __init__(self, settings: "GameSettings") -> None:
        self._settings = settings

    def build_deck(self, deck_type: str = "french") -> "ProtoDeck":
        """Crea deck appropriato in base alla preferenza profilo.

        Returns:
            ProtoDeck: istanza del mazzo (FrenchDeck o NeapolitanDeck).
        """
        from src.domain.models.deck import FrenchDeck, NeapolitanDeck
        if deck_type == "neapolitan":
            _game_logger.info("Building NeapolitanDeck")
            return NeapolitanDeck()
        _game_logger.info("Building FrenchDeck (default)")
        return FrenchDeck()

    def build_rules(self, deck: "ProtoDeck") -> "SolitaireRules":
        """Crea SolitaireRules per il deck dato."""
        from src.domain.rules.solitaire_rules import SolitaireRules
        return SolitaireRules(deck=deck)

    def apply_settings(self, settings: "GameSettings") -> None:
        """Aggiorna settings in-place."""
        self._settings = settings
        _game_logger.info(f"Settings applied: draw_count={settings.draw_count}")

    @property
    def current_settings(self) -> "GameSettings":
        return self._settings
```

**Commit Fase 1b**:
```
feat(application): aggiunge GameConfigurator — gestione deck, regole e settings
```

---

#### Fase 1c: SessionRecorder

`SessionRecorder` costruisce `SessionOutcome` e lo persiste tramite `ProfileService`.

> **CRITICO sui nomi**:
>
> - Il servizio è `ProfileService` — si trova in `src/domain/services/profile_service.py`
> - Lo storage è `ProfileStorage` — si trova in `src/infrastructure/storage/profile_storage.py`
> - Nel codebase NON esiste `ProfileRepository` — non usare quel nome
>
> `SessionRecorder` riceve `ProfileService` come dipendenza (orchestratore), NON `ProfileStorage` (storage diretto).

```python
# src/application/session_recorder.py
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.domain.services.profile_service import ProfileService
    from src.domain.models.profile import SessionOutcome
    from src.domain.models.game_end import EndReason  # enum — NON usare stringa

_game_logger = logging.getLogger('game')


class SessionRecorder:
    """Costruisce e persiste SessionOutcome al termine di ogni partita."""

    def __init__(self, profile_service: "ProfileService") -> None:
        self._profile_service = profile_service

    def record(self, outcome: "SessionOutcome") -> bool:
        """Registra il risultato sessione. Ritorna True se successo."""
        try:
            success = self._profile_service.record_session(outcome)
            if success:
                _game_logger.info(
                    f"Session recorded: profile={outcome.profile_id}, "
                    f"victory={outcome.is_victory}, score={outcome.final_score}"
                )
            else:
                _game_logger.warning(
                    f"record_session returned False for profile_id={outcome.profile_id}"
                )
            return success
        except Exception:
            _game_logger.exception("Failed to record session outcome — graceful degradation")
            return False

    def build_outcome(
        self,
        profile_id: str,
        end_reason: "EndReason",
        is_victory: bool,
        elapsed_time: float,
        timer_enabled: bool,
        timer_limit: int,
        timer_mode: str,
        timer_expired: bool,
        scoring_enabled: bool,
        final_score: int,
        difficulty_level: int,
        deck_type: str,
        move_count: int,
    ) -> "SessionOutcome":
        """Costruisce SessionOutcome tramite factory SessionOutcome.create_new().

        SessionOutcome ha ~20 campi obbligatori; usa il factory create_new()
        che aggiunge automaticamente session_id (uuid) e timestamp (utcnow).
        end_reason DEVE essere un valore dell'enum EndReason (NON una stringa).
        """
        from src.domain.models.profile import SessionOutcome
        return SessionOutcome.create_new(
            profile_id=profile_id,
            end_reason=end_reason,
            is_victory=is_victory,
            elapsed_time=elapsed_time,
            timer_enabled=timer_enabled,
            timer_limit=timer_limit,
            timer_mode=timer_mode,
            timer_expired=timer_expired,
            scoring_enabled=scoring_enabled,
            final_score=final_score,
            difficulty_level=difficulty_level,
            deck_type=deck_type,
            move_count=move_count,
        )
```

**Commit Fase 1c**:
```
feat(application): aggiunge SessionRecorder — costruisce e persiste SessionOutcome via ProfileService
```

---

#### Fase 1d: Aggiornamento GameEngine e DIContainer

`GameEngine.__init__` viene aggiornato per ricevere i tre nuovi componenti come **parametri opzionali** (retrocompatibile). I tre componenti vengono istanziati **all'interno di `GameEngine.create()`** (il factory classmethod usato da tutto il codebase e da `acs_wx.py`), NON passati dall'esterno.

```python
# src/application/game_engine.py — strategia di integrazione in due punti

# 1. Aggiungere i tre parametri OPZIONALI a __init__ (non breaking):
class GameEngine:
    def __init__(
        self,
        # ... tutte le dipendenze esistenti invariate ...
        tts_announcer: Optional["TTSAnnouncer"] = None,          # NUOVO
        game_configurator: Optional["GameConfigurator"] = None,  # NUOVO
        session_recorder: Optional["SessionRecorder"] = None,    # NUOVO
    ) -> None:
        # ... assegnazioni esistenti invariate ...
        self._tts = tts_announcer
        self._configurator = game_configurator
        self._recorder = session_recorder

# 2. Aggiornare create() per istanziare i tre componenti internamente:
@classmethod
def create(
    cls,
    # ... parametri esistenti invariati ...
) -> "GameEngine":
    # ... logica esistente invariata (deck, rules, service, screen_reader, ecc.) ...

    # NUOVO: istanzia i tre componenti di delega prima del return
    from src.application.tts_announcer import TTSAnnouncer
    from src.application.game_configurator import GameConfigurator
    from src.application.session_recorder import SessionRecorder

    tts = screen_reader.tts if (screen_reader and hasattr(screen_reader, 'tts')) else None
    tts_announcer = TTSAnnouncer(tts)
    game_configurator = GameConfigurator(settings or GameSettings())
    session_recorder = SessionRecorder(profile_service)

    return cls(
        table, service, rules, cursor, selection, screen_reader,
        settings, score_storage, dialog_provider,
        on_game_ended=None,
        profile_service=profile_service,
        tts_announcer=tts_announcer,          # NUOVO
        game_configurator=game_configurator,  # NUOVO
        session_recorder=session_recorder,    # NUOVO
    )
```

`DIContainer` (`src/infrastructure/di_container.py`) aggiunge i tre metodi factory:

```python
# src/infrastructure/di_container.py — aggiunta metodi factory
def get_tts_announcer(self) -> "TTSAnnouncer":
    from src.application.tts_announcer import TTSAnnouncer
    sr = self.get_screen_reader()
    # Estrae TtsProvider da ScreenReader — TTSAnnouncer dipende da TtsProvider, non da ScreenReader
    tts = sr.tts if (sr is not None and hasattr(sr, 'tts')) else None
    return TTSAnnouncer(tts)

def get_game_configurator(self) -> "GameConfigurator":
    from src.application.game_configurator import GameConfigurator
    return GameConfigurator(self.get_settings())

def get_session_recorder(self) -> "SessionRecorder":
    from src.application.session_recorder import SessionRecorder
    return SessionRecorder(self.get_profile_service())
```

> **NOTA DIContainer — path e uso corretto**:
>
> - `DIContainer` si trova in `src/infrastructure/di_container.py`
>   (NON in `src/application/` — errore comune)
> - Usare SEMPRE `self.container.get_tts_announcer()` sull'istanza `DependencyContainer`
>   già esistente in `acs_wx.py`
> - MAI chiamare `DIContainer()` direttamente dentro metodi UI — crea una nuova
>   istanza che bypassa il singleton e duplica risorse audio

**Commit Fase 1d**:
```
refactor(application,infrastructure): GameEngine delega TTS/config/session ai nuovi componenti; DIContainer registra TTSAnnouncer, GameConfigurator, SessionRecorder
```

**Testing Fase 1 (SessionRecorder)**:

```python
# tests/unit/application/test_session_recorder.py
import pytest
from unittest.mock import MagicMock
from src.application.session_recorder import SessionRecorder


@pytest.mark.unit
class TestSessionRecorder:
    def test_record_calls_profile_service(self):
        ps = MagicMock()
        ps.record_session.return_value = True
        recorder = SessionRecorder(ps)
        outcome = MagicMock()  # build_outcome usa SessionOutcome.create_new() reale; per questo test basta un Mock
        result = recorder.record(outcome)
        assert result is True
        ps.record_session.assert_called_once_with(outcome)

    def test_record_returns_false_on_exception(self):
        ps = MagicMock()
        ps.record_session.side_effect = RuntimeError("Storage error")
        recorder = SessionRecorder(ps)
        outcome = MagicMock()
        result = recorder.record(outcome)
        assert result is False

    def test_build_outcome_fields(self):
        """build_outcome usa SessionOutcome.create_new() con tutti i parametri richiesti."""
        ps = MagicMock()
        recorder = SessionRecorder(ps)
        from src.domain.models.game_end import EndReason  # import enum reale
        outcome = recorder.build_outcome(
            profile_id="p001",
            end_reason=EndReason.TIMEOUT_STRICT,
            is_victory=False,
            elapsed_time=120.0,
            timer_enabled=True,
            timer_limit=600,
            timer_mode="STRICT",
            timer_expired=True,
            scoring_enabled=True,
            final_score=800,
            difficulty_level=3,
            deck_type="french",
            move_count=45,
        )
        assert outcome.profile_id == "p001"
        assert outcome.is_victory is False
        assert outcome.final_score == 800
        assert outcome.end_reason == EndReason.TIMEOUT_STRICT
```

---

### Fase 2 — Accessibilità TTS Configurabile

**Prerequisito**: nessuno (indipendente da Fase 1, può procedere in parallelo).
**Priorità**: Alta.

**File coinvolti**:

- `src/domain/models/profile.py` — MODIFY
- `src/infrastructure/storage/profile_storage.py` — MODIFY
- `src/domain/services/profile_service.py` — MODIFY (metodo `apply_tts_settings`)
- `src/presentation/dialogs/options_dialog.py` — MODIFY
- `docs/UX_SHORTCUTS.md` — CREATE

#### Fase 2a: Aggiornamento UserProfile

> **CRITICI sui nomi**:
>
> - Il file è `src/domain/models/profile.py` — NON `user_profile.py`
> - La classe è `UserProfile` — NON `Profile`

```python
# src/domain/models/profile.py — modifica dataclass UserProfile
from dataclasses import dataclass, field

@dataclass
class UserProfile:
    profile_id: str
    profile_name: str
    preferred_deck: str = "french"
    tts_rate: int = 0       # NUOVO: velocità TTS (range 0–100, default 0=sistema)
                            # Mappato a TtsProvider.set_rate() range -10/+10 da TTSAnnouncer
    tts_volume: int = 80    # NUOVO: volume TTS (range 0–100, default 80=0.8)
                            # Mappato a TtsProvider.set_volume() range 0.0–1.0 da TTSAnnouncer
    # ... tutti gli altri campi esistenti invariati ...
```

#### Fase 2b: ProfileStorage — serializzazione con retrocompatibilità

> **CRITICO — ProfileStorage API reale**:
>
> - I metodi `_to_dict` e `_from_dict` **non esistono** in `ProfileStorage`
> - L'API reale è: `create_profile(profile: UserProfile)`, `load_profile(profile_id: str) -> Optional[Dict]`, `save_profile(profile_id: str, profile_data: Dict) -> bool`
> - Il costruttore accetta `data_dir: Optional[Path] = None` (NON `storage_path`)

```python
# src/infrastructure/storage/profile_storage.py
# Aggiungere tts_rate e tts_volume nella serializzazione dict dentro create_profile():
# Localizzare il blocco che costruisce profile_data e aggiungere:
#   profile_data["tts_rate"] = getattr(profile, "tts_rate", 0)    # NUOVO
#   profile_data["tts_volume"] = getattr(profile, "tts_volume", 80)  # NUOVO

# In save_profile(profile_id, profile_data) non servono modifiche —
# il dizionario viene scritto direttamente come JSON.

# La deserializzazione dict→UserProfile avviene in ProfileService:
# (load_profile ritorna Optional[Dict[str, Any]], non UserProfile)
# In ProfileService, aggiungere .get() con default nel punto
# dove viene costruito UserProfile dal dizionario:
#   tts_rate=data.get("tts_rate", 0),    # NUOVO — default 0 per profili legacy
#   tts_volume=data.get("tts_volume", 80)  # NUOVO — default 80 per profili legacy
```

Il `.get(..., default)` garantisce retrocompatibilità: i profili JSON pre-esistenti che non hanno `tts_rate` ottengono automaticamente il valore di default.

#### Fase 2c: TTSAnnouncer — apply_tts_settings (Application Layer)

> **Clean Architecture — apply_tts_settings appartiene all'Application Layer**:
>
> - NON aggiungere `apply_tts_settings` a `ProfileService` (Domain layer) — importare `ScreenReader`
>   o `TtsProvider` dal Domain violerebbe la separazione dei layer
> - `apply_tts_settings` è già incluso nel codice di `TTSAnnouncer` descritto in Fase 1a
> - `TtsProvider.set_rate(rate: int)` range -10/+10 (NON set_rate su ScreenReader)
> - `TtsProvider.set_volume(volume: float)` range 0.0–1.0 (NON set_volume su ScreenReader)

La chiamata avviene in `GameEngine.new_game()` o all'avvio sessione:

```python
# In GameEngine.new_game() — dopo load del profilo attivo:
if self._tts and self.profile_service and self.profile_service.active_profile:
    profile = self.profile_service.active_profile
    self._tts.apply_tts_settings(
        tts_rate=profile.tts_rate,
        tts_volume=profile.tts_volume,
    )
```

#### Fase 2d: OptionsDialog — slider TTS e audit scorciatoie

**CREARE** il file `src/presentation/dialogs/options_dialog.py` (non esiste nel codebase).
Il file deve implementare `OptionsDialog` con tab "Audio/TTS":

- `wx.Slider` per Rate TTS — label `"Velocità lettura &TTS:"`, range 0–100
- `wx.Slider` per Volume TTS — label `"&Volume lettura:"`, range 0–100
- Bottone "Applica" che chiama `tts_announcer.apply_tts_settings(profile.tts_rate, profile.tts_volume)`
- Binding tastiera: `wx.EVT_SLIDER` salva nel profilo corrente in tempo reale

**Requisiti accessibilità obbligatori**:
- Ogni slider ha `SetLabel()` con descrizione + valore corrente (NVDA legge `"Velocità: 50"`)
- TAB naviga slider → bottone Applica → bottone Chiudi in ordine logico
- ESC chiude il dialog (binding `wx.ID_CANCEL`)

**Audit scorciatoie** — leggere `src/application/input_handler.py` (NON in `src/infrastructure/ui/`):

```python
# src/application/input_handler.py — GameCommand enum con ~30 comandi
# Estrarre tutti i binding e documentarli in docs/UX_SHORTCUTS.md
```

> **ATTENZIONE path**: `input_handler.py` si trova in `src/application/` —
> NON in `src/infrastructure/ui/`. L'errore è comune e causa ImportError silenzioso.

**Struttura `docs/UX_SHORTCUTS.md`** (solo testo, nessuna tabella complessa):

```markdown
# Comandi da Tastiera — Solitario Classico Accessibile

## Navigazione pile
[lista comandi estratta da GameCommand in input_handler.py]

## Selezione e spostamento carte
[...]

## Controlli partita
[...]

## Comandi dialogs
- Esc: chiude qualsiasi dialog
- Tab / Shift+Tab: naviga i controlli
- Invio: attiva pulsante con focus
```

**Commit Fase 2**:
```
feat(domain,infrastructure,presentation): TTS persistente — tts_rate/tts_volume in UserProfile; slider in OptionsDialog; crea UX_SHORTCUTS.md
```

**Testing Fase 2**:

```python
# tests/unit/domain/test_profile_tts.py
import pytest
import json
from src.domain.models.profile import UserProfile
from src.infrastructure.storage.profile_storage import ProfileStorage


@pytest.mark.unit   # NON @pytest.mark.gui — nessuna dipendenza wx
class TestUserProfileTTS:
    def test_user_profile_defaults(self):
        p = UserProfile(profile_id="p001", profile_name="Test")
        assert p.tts_rate == 0    # default 0 (sistema), non 50
        assert p.tts_volume == 80

    def test_profile_storage_roundtrip_tts(self, tmp_path):
        """ProfileStorage serializza/deserializza tts_rate e tts_volume.
        
        Nota: ProfileStorage(data_dir=tmp_path), non storage_path.
        create_profile(profile) serializza; load_profile(id) -> Optional[Dict].
        """
        storage = ProfileStorage(data_dir=tmp_path)  # parametro è data_dir, NON storage_path
        p = UserProfile(profile_id="p001", profile_name="Test", tts_rate=75, tts_volume=60)
        storage.create_profile(p)  # metodo reale: create_profile(), non save()
        data = storage.load_profile("p001")  # ritorna Optional[Dict], non UserProfile
        assert data is not None
        assert data.get("tts_rate") == 75
        assert data.get("tts_volume") == 60

    def test_profile_storage_defaults_for_legacy_json(self, tmp_path):
        """Profili pre-esistenti senza tts_rate: i default vengono applicati in ProfileService."""
        (tmp_path / "p001.json").write_text(
            json.dumps({"profile_id": "p001", "profile_name": "Legacy"})
        )
        storage = ProfileStorage(data_dir=tmp_path)  # data_dir, non storage_path
        data = storage.load_profile("p001")  # ritorna dict; default gestiti da ProfileService
        assert data is not None
        # tts_rate/tts_volume non presenti nel JSON legacy — ProfileService usa .get(..., default)
        assert "tts_rate" not in data or data.get("tts_rate") == 0

    def test_apply_tts_settings_calls_tts_provider(self):
        """apply_tts_settings è su TTSAnnouncer (Application), non ProfileService (Domain)."""
        from unittest.mock import MagicMock
        from src.application.tts_announcer import TTSAnnouncer
        tts = MagicMock()
        announcer = TTSAnnouncer(tts)
        announcer.apply_tts_settings(tts_rate=70, tts_volume=55)
        tts.set_rate.assert_called_once()   # verifica chiamata con conversione range
        tts.set_volume.assert_called_once()
```

---

### Fase 3 — Plugin System Deck e Regole

**Prerequisito**: Fase 1 completata (`GameConfigurator` deve esistere).
**Priorità**: Media.

**File coinvolti**:

- `src/domain/interfaces/protocols.py` — CREATE
- `src/infrastructure/plugins/__init__.py` — CREATE
- `src/infrastructure/plugins/plugin_registry.py` — CREATE
- `src/infrastructure/plugins/french_deck_provider.py` — CREATE
- `src/infrastructure/plugins/neapolitan_deck_provider.py` — CREATE
- `src/infrastructure/plugins/klondike_ruleset.py` — CREATE
- `src/application/game_configurator.py` — MODIFY (usa registry)
- `src/presentation/dialogs/options_dialog.py` — MODIFY (combo box deck/regole)

#### Fase 3a: Protocolli Domain

> **CRITICI sul positioning**:
>
> - `protocols.py` va in `src/domain/interfaces/` — NON in `src/domain/plugins/`
>   Le interfacce/protocolli appartengono al Domain; le implementazioni all'Infrastructure
> - `create_deck()` ritorna `ProtoDeck` (tipo base) — NON `Deck` (non esiste)
>   e NON `FrenchDeck` (troppo specifico, rompe il polimorfismo)
> - La directory `src/domain/interfaces/` è stata creata in Fase 0

```python
# src/domain/interfaces/protocols.py
"""Protocolli (interfacce formali) per plugin deck e regole di gioco."""
from __future__ import annotations
from typing import Protocol, runtime_checkable
from src.domain.models.deck import ProtoDeck


@runtime_checkable
class DeckProvider(Protocol):
    """Interfaccia per provider di mazzi di carte."""

    @property
    def name(self) -> str:
        """Nome leggibile del deck (es. 'Mazzo Francese')."""
        ...

    @property
    def deck_id(self) -> str:
        """Identificatore univoco (es. 'french', 'neapolitan')."""
        ...

    def create_deck(self) -> ProtoDeck:
        """Crea e ritorna una nuova istanza del deck.

        Returns:
            ProtoDeck: tipo base — sottoclass concreta (FrenchDeck, NeapolitanDeck…)
        """
        ...


@runtime_checkable
class RuleSet(Protocol):
    """Interfaccia per set di regole di gioco."""

    @property
    def name(self) -> str:
        """Nome leggibile del ruleset (es. 'Klondike')."""
        ...

    @property
    def ruleset_id(self) -> str:
        """Identificatore univoco (es. 'klondike')."""
        ...

    def check_move(self, card: object, target_pile: object) -> bool:
        """Verifica se la mossa è valida secondo le regole del gioco."""
        ...
```

#### Fase 3b: Plugin Registry (esplicito)

```python
# src/infrastructure/plugins/plugin_registry.py
"""Registry esplicito dei plugin disponibili.

DELIBERATAMENTE non usa dynamic discovery (importlib, glob) per ragioni di sicurezza.
Per aggiungere un nuovo deck/ruleset: modificare questo file e aggiungere l'entry al dict.
"""
from __future__ import annotations
from typing import Dict

from src.domain.interfaces.protocols import DeckProvider, RuleSet
from src.infrastructure.plugins.french_deck_provider import StandardFrenchDeckProvider
from src.infrastructure.plugins.neapolitan_deck_provider import NeapolitanDeckProvider
from src.infrastructure.plugins.klondike_ruleset import KlondikeRuleSet

# Istanze provider (stateless — sicuro come singleton di modulo)
_french_provider = StandardFrenchDeckProvider()
_neapolitan_provider = NeapolitanDeckProvider()

DECK_REGISTRY: Dict[str, DeckProvider] = {
    "french": _french_provider,
    "neapolitan": _neapolitan_provider,
}

RULE_REGISTRY: Dict[str, RuleSet] = {
    "klondike": KlondikeRuleSet(deck=_french_provider.create_deck()),
}


def get_deck_provider(deck_id: str) -> DeckProvider:
    """Ritorna il DeckProvider per l'id dato.

    Raises:
        KeyError: se deck_id non è registrato.
    """
    if deck_id not in DECK_REGISTRY:
        raise KeyError(f"Deck provider non trovato: {deck_id!r}")
    return DECK_REGISTRY[deck_id]


def get_rule_set(ruleset_id: str) -> RuleSet:
    """Ritorna il RuleSet per l'id dato.

    Raises:
        KeyError: se ruleset_id non è registrato.
    """
    if ruleset_id not in RULE_REGISTRY:
        raise KeyError(f"RuleSet non trovato: {ruleset_id!r}")
    return RULE_REGISTRY[ruleset_id]


def list_deck_ids() -> list[str]:
    return list(DECK_REGISTRY.keys())


def list_ruleset_ids() -> list[str]:
    return list(RULE_REGISTRY.keys())
```

#### Fase 3c: Implementazioni Provider

```python
# src/infrastructure/plugins/french_deck_provider.py
from src.domain.interfaces.protocols import DeckProvider
from src.domain.models.deck import ProtoDeck, FrenchDeck


class StandardFrenchDeckProvider:
    """Provider per mazzo francese standard (52 carte, 4 semi)."""

    @property
    def name(self) -> str:
        return "Mazzo Francese"

    @property
    def deck_id(self) -> str:
        return "french"

    def create_deck(self) -> ProtoDeck:
        return FrenchDeck()
```

```python
# src/infrastructure/plugins/neapolitan_deck_provider.py
from src.domain.interfaces.protocols import DeckProvider
from src.domain.models.deck import ProtoDeck, NeapolitanDeck


class NeapolitanDeckProvider:
    """Provider per mazzo napoletano (40 carte, semi italiani)."""

    @property
    def name(self) -> str:
        return "Mazzo Napoletano"

    @property
    def deck_id(self) -> str:
        return "neapolitan"

    def create_deck(self) -> ProtoDeck:
        return NeapolitanDeck()
```

```python
# src/infrastructure/plugins/klondike_ruleset.py
from src.domain.interfaces.protocols import RuleSet
from src.domain.models.deck import ProtoDeck
from src.domain.rules.solitaire_rules import SolitaireRules


class KlondikeRuleSet:
    """RuleSet per Klondike — delega la verifica mosse a SolitaireRules.

    Args:
        deck: istanza ProtoDeck necessaria a SolitaireRules per regole
              specifiche del tipo di mazzo usato.
    """

    def __init__(self, deck: ProtoDeck) -> None:
        self._rules = SolitaireRules(deck=deck)

    @property
    def name(self) -> str:
        return "Klondike"

    @property
    def ruleset_id(self) -> str:
        return "klondike"

    def check_move(self, card: object, target_pile: object) -> bool:
        # SolitaireRules NON ha can_place() generico — usa metodi distinti per tipo pila:
        #   can_place_on_tableau(card, pile)  — movimento verso colonne tableau
        #   can_place_on_foundation(card, pile) — movimento verso fondazioni
        #   can_move_sequence(cards, pile) — spostamento sequenza
        # check_move usa can_place_on_tableau() come delega principale per mosse tableau.
        from src.domain.models.pile import Pile
        if isinstance(target_pile, Pile):
            return self._rules.can_place_on_tableau(card, target_pile)  # type: ignore[arg-type]
        return False
```

> **NOTA `KlondikeRuleSet`**: il costruttore richiede `deck: ProtoDeck` perché
> `SolitaireRules` usa il deck per determinare regole dipendenti dal tipo di mazzo.
> Usare `_french_provider.create_deck()` nel registry come mostrato sopra.

#### Fase 3d: GameConfigurator integra Registry

```python
# src/application/game_configurator.py — aggiorna build_deck e build_rules
def build_deck(self, deck_id: str = "french") -> "ProtoDeck":
    """Crea deck appropriato usando il plugin registry."""
    from src.infrastructure.plugins.plugin_registry import get_deck_provider
    provider = get_deck_provider(deck_id)
    _game_logger.info(f"Building deck via provider: {provider.name}")
    return provider.create_deck()

def build_rules(self, deck: "ProtoDeck", ruleset_id: str = "klondike") -> "SolitaireRules":
    """Crea SolitaireRules per il deck e ruleset dati."""
    from src.domain.rules.solitaire_rules import SolitaireRules
    # Compatibilità: SolitaireRules è ancora il tipo di ritorno concreto
    return SolitaireRules(deck=deck)
```

**Commit Fase 3**:
```
feat(domain,infrastructure): plugin system — DeckProvider/RuleSet protocols + registry esplicito con FrenchDeckProvider, NeapolitanDeckProvider, KlondikeRuleSet
```

**Testing Fase 3**:

```python
# tests/unit/infrastructure/plugins/test_plugin_registry.py
import pytest
from src.domain.models.deck import FrenchDeck, NeapolitanDeck, ProtoDeck
from src.domain.interfaces.protocols import DeckProvider, RuleSet


@pytest.mark.unit
class TestPluginRegistry:
    def test_get_deck_provider_french_returns_french_deck(self):
        from src.infrastructure.plugins.plugin_registry import get_deck_provider
        provider = get_deck_provider("french")
        deck = provider.create_deck()
        assert isinstance(deck, FrenchDeck)

    def test_get_deck_provider_neapolitan_returns_neapolitan_deck(self):
        from src.infrastructure.plugins.plugin_registry import get_deck_provider
        provider = get_deck_provider("neapolitan")
        deck = provider.create_deck()
        assert isinstance(deck, NeapolitanDeck)

    def test_create_deck_returns_proto_deck_base_type(self):
        """create_deck() deve ritornare ProtoDeck — contratto del protocollo."""
        from src.infrastructure.plugins.plugin_registry import get_deck_provider
        for deck_id in ("french", "neapolitan"):
            provider = get_deck_provider(deck_id)
            deck = provider.create_deck()
            assert isinstance(deck, ProtoDeck), (
                f"{deck_id}: create_deck() deve ritornare ProtoDeck, got {type(deck)}"
            )

    def test_get_unknown_deck_raises_key_error(self):
        from src.infrastructure.plugins.plugin_registry import get_deck_provider
        with pytest.raises(KeyError):
            get_deck_provider("unknown_deck")

    def test_deck_provider_satisfies_protocol(self):
        from src.infrastructure.plugins.plugin_registry import get_deck_provider
        provider = get_deck_provider("french")
        assert isinstance(provider, DeckProvider)

    def test_list_deck_ids_contains_expected(self):
        from src.infrastructure.plugins.plugin_registry import list_deck_ids
        ids = list_deck_ids()
        assert "french" in ids
        assert "neapolitan" in ids
```

```python
# tests/unit/domain/interfaces/test_protocols.py
import pytest
from src.domain.models.deck import ProtoDeck


@pytest.mark.unit
class TestProtocolConformance:
    def test_french_provider_implements_deck_provider_protocol(self):
        from src.infrastructure.plugins.french_deck_provider import StandardFrenchDeckProvider
        from src.domain.interfaces.protocols import DeckProvider
        provider = StandardFrenchDeckProvider()
        assert isinstance(provider, DeckProvider)
        assert provider.deck_id == "french"

    def test_neapolitan_provider_implements_deck_provider_protocol(self):
        from src.infrastructure.plugins.neapolitan_deck_provider import NeapolitanDeckProvider
        from src.domain.interfaces.protocols import DeckProvider
        provider = NeapolitanDeckProvider()
        assert isinstance(provider, DeckProvider)
        assert provider.deck_id == "neapolitan"

    def test_klondike_ruleset_implements_ruleset_protocol(self):
        from src.infrastructure.plugins.klondike_ruleset import KlondikeRuleSet
        from src.domain.interfaces.protocols import RuleSet
        from src.domain.models.deck import FrenchDeck
        ruleset = KlondikeRuleSet(deck=FrenchDeck())
        assert isinstance(ruleset, RuleSet)
        assert ruleset.ruleset_id == "klondike"
```

---

### Fase 4 — Test e Documentazione

**Prerequisito**: Fasi 1, 2, 3 completate.
**Priorità**: Media.

**File coinvolti**:

- `tests/unit/application/test_tts_announcer.py` — CREATE (snippet in Fase 1a)
- `tests/unit/application/test_game_configurator.py` — CREATE
- `tests/unit/application/test_session_recorder.py` — CREATE (snippet in Fase 1c)
- `tests/unit/domain/test_profile_tts.py` — CREATE (snippet in Fase 2)
- `tests/unit/infrastructure/plugins/test_plugin_registry.py` — CREATE (snippet in Fase 3)
- `tests/unit/domain/interfaces/test_protocols.py` — CREATE (snippet in Fase 3)
- `tests/integration/test_game_engine_decomposition.py` — CREATE
- `docs/UX_SHORTCUTS.md` — CREATE (da Fase 2d)
- `docs/API.md` — MODIFY
- `docs/ARCHITECTURE.md` — MODIFY
- `CHANGELOG.md` — MODIFY

#### Fase 4a: Test di integrazione

```python
# tests/integration/test_game_engine_decomposition.py
"""Verifica che GameEngine deleghi correttamente ai nuovi componenti."""
import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.unit  # solo mock, nessuna dipendenza wx o pygame
class TestGameEngineWithNewComponents:
    def test_game_engine_uses_tts_announcer_not_screen_reader_directly(self):
        """GameEngine chiama tts.announce_move(), non screen_reader.speak() direttamente."""
        # Setup: verifica che dopo una mossa, sia TTSAnnouncer il canale usato
        tts = MagicMock()
        # ... istanza GameEngine con tts iniettato ...
        # Esegui mossa e verifica tts.announce_move chiamato

    def test_session_recorder_called_on_game_end(self):
        """GameEngine chiama session_recorder.record() alla fine partita."""
        recorder = MagicMock()
        # ... setup GameEngine con recorder iniettato, simula fine partita ...
        # Verifica recorder.record chiamato con SessionOutcome corretto

    def test_tts_rate_applied_on_session_start(self):
        """Alla avvio sessione, TTSAnnouncer.apply_tts_settings viene chiamato con i valori del profilo."""
        # Simula profilo con tts_rate=75, tts_volume=60
        # Verifica che tts_provider.set_rate(5) sia chiamato (conversione: (75/100)*20-10=5)
        # e tts_provider.set_volume(0.6) sia chiamato (conversione: 60/100=0.6)
        pass
```

#### Fase 4b: Aggiornamento `docs/API.md`

Aggiungere sezioni:

```markdown
## TTSAnnouncer

**Package**: `src.application.tts_announcer`  
**Dipendenze**: `TtsProvider` (acceduto tramite `screen_reader.tts` — NON `ScreenReader` direttamente)

### Metodi pubblici
- `announce(message: str, interrupt: bool = True) -> None`
- `announce_game_start(profile_name: str) -> None`
- `announce_move(card_label: str, from_pile: str, to_pile: str) -> None`
- `announce_victory() -> None`
- `announce_game_over() -> None`
- `apply_tts_settings(tts_rate: int, tts_volume: int) -> None` — converte range 0–100 a TtsProvider ranges

[aggiungere analoghe sezioni per GameConfigurator, SessionRecorder,
 DeckProvider/RuleSetProtocolli, plugin_registry functions]
```

#### Fase 4c: Aggiornamento `docs/ARCHITECTURE.md`

Aggiornare:

- Diagramma componenti Application layer con `TTSAnnouncer`, `GameConfigurator`, `SessionRecorder`
- Sezione "Plugin System": flusso `OptionsDialog → GameConfigurator → plugin_registry → DeckProvider → ProtoDeck`
- Nota duello container DI: `DIContainer` vs `DependencyContainer` e quando usare quale
- Sezione "TTS vs Audio": diagramma distinto per `ScreenReader` (NVDA) e `AudioManager` (PCM)

**Commit Fase 4**:
```
test(all): copertura ≥90% per nuovi componenti v3.6.0
docs: aggiorna API.md, ARCHITECTURE.md; crea UX_SHORTCUTS.md
```

---

## 🧪 Testing Strategy

### Unit Testing

**Filosofia**: ogni nuova classe ha test indipendenti con mock per tutte le dipendenze esterne.

**Marker da usare**:

- `@pytest.mark.unit` — test senza dipendenze esterne (no wx, no filesystem reale, no pygame)
- `@pytest.mark.gui` — solo test che richiedono `wx.App` istanziata (modifiche `OptionsDialog`)

> **NOTA struttura test**:
> Non creare `tests/gui/`. I test GUI usano `@pytest.mark.gui` dentro le directory
> `tests/unit/` o `tests/integration/` già esistenti.

**Comandi**:

```bash
# CI-safe (headless) — obbligatorio pre-merge
pytest tests/ -m "not gui" -v --cov=src --cov-report=term-missing --cov-fail-under=90

# Test completi (richiede display Windows o Xvfb)
pytest tests/ -v
```

**Struttura nuovi file test**:

```
tests/
  unit/
    application/
      test_tts_announcer.py
      test_game_configurator.py
      test_session_recorder.py
    domain/
      test_profile_tts.py
      interfaces/
        test_protocols.py
    infrastructure/
      plugins/
        test_plugin_registry.py
  integration/
    test_game_engine_decomposition.py
```

### Integration Testing

**Scenario TTS persistence**:

```python
"""
Simula: profilo viene salvato con tts_rate=75, ricaricato, settings applicati.

Setup:
    ProfileStorage in tmp_path (costruttore: data_dir=tmp_path)
    ProfileService che usa quello storage
    TtsProvider mockato (acceduto tramite screen_reader.tts)

Azioni:
    1. Crea UserProfile(tts_rate=75, tts_volume=60)
    2. Salva via ProfileStorage.create_profile(profile)
    3. Ricarica profilo via ProfileStorage.load_profile("p001") -> Dict
    4. Chiama tts_announcer.apply_tts_settings(tts_rate=75, tts_volume=60)

Assertions:
    - Profilo ricaricato ha data["tts_rate"] == 75
    - mock_tts.set_rate chiamato con 5 (conversione: (75/100)*20 - 10 = 5)
    - mock_tts.set_volume chiamato con 0.6 (conversione: 60/100 = 0.6)
"""
```

### Manual Testing Checklist

- [ ] Mossa carta annunciata correttamente da NVDA
- [ ] Rate TTS modificabile in OptionsDialog e persistente dopo riavvio
- [ ] Volume TTS modificabile in OptionsDialog e persistente dopo riavvio
- [ ] Selezionare "Mazzo Napoletano" in OptionsDialog — partita usa mazzo napoletano
- [ ] Regole "Klondike" — comportamento identico a prima del refactoring
- [ ] ESC chiude ogni dialog, focus ritorna al pannello di gioco
- [ ] TAB naviga tutti i controlli in OptionsDialog nell'ordine atteso
- [ ] Sessione NVDA di 10 minuti: nessun crash, tutti i messaggi TTS udibili senza artefatti

---

## ⚠️ Common Pitfalls to Avoid

### ❌ DON'T: Confondere TTS e AudioManager

```python
# SBAGLIATO — TTSAnnouncer usa AudioManager (sistema sbagliato)
class TTSAnnouncer:
    def announce(self, msg: str) -> None:
        self._audio_manager.play(AudioEvent.SPEAK)  # ❌ sbagliato!
```

**Perché non funziona**: `AudioManager` gestisce PCM/WAV via `pygame.mixer`.
`ScreenReader` gestisce NVDA/SAPI5. Sono sistemi completamente separati.

### ✅ DO:

```python
# CORRETTO
class TTSAnnouncer:
    def announce(self, msg: str) -> None:
        self._tts.speak(msg)  # ✅ corretto — TtsProvider (non ScreenReader.speak() che non esiste)
```

---

### ❌ DON'T: Dynamic plugin discovery

```python
# SBAGLIATO — rischio esecuzione di codice arbitrario
import importlib, glob
for f in glob.glob("plugins/*.py"):
    module = importlib.import_module(f)  # ❌ security risk
```

### ✅ DO:

```python
# CORRETTO — registry esplicito
DECK_REGISTRY = {
    "french": StandardFrenchDeckProvider(),
    "neapolitan": NeapolitanDeckProvider(),
}
```

---

### ❌ DON'T: create_deck() ritorna tipo concreto

```python
# SBAGLIATO — tipo di ritorno rompe il polimorfismo
def create_deck(self) -> FrenchDeck:  # ❌ troppo specifico
    return FrenchDeck()
```

### ✅ DO:

```python
# CORRETTO — tipo base ProtoDeck
def create_deck(self) -> ProtoDeck:  # ✅
    return FrenchDeck()
```

---

### ❌ DON'T: pile.count()

```python
n = pile.count()  # ❌ AttributeError — metodo inesistente
```

### ✅ DO:

```python
n = pile.get_card_count()  # ✅ metodo corretto
```

---

### ❌ DON'T: DIContainer() istanza diretta in metodi UI

```python
def on_button_click(self) -> None:
    am = DIContainer().get_audio_manager()  # ❌ bypassa singleton!
```

### ✅ DO:

```python
def on_button_click(self) -> None:
    am = self.container.get_audio_manager()  # ✅ istanza DependencyContainer esistente
```

---

## 📦 Commit Strategy

### Atomic Commits (12 totali)

1. **[Fase 0]** Setup — DESIGN doc, directory, cruscotto
   - `chore(docs): crea DESIGN doc, src/domain/interfaces/__init__.py e docs/TODO.md per v3.6.0`
   - Files: `docs/2 - projects/DESIGN_game-engine-refactoring.md`, `src/domain/interfaces/__init__.py`, `docs/TODO.md`

2. **[Fase 1a]** TTSAnnouncer
   - `feat(application): aggiunge TTSAnnouncer — delega TTS da GameEngine a componente dedicato`
   - Files: `src/application/tts_announcer.py`
   - Tests: `tests/unit/application/test_tts_announcer.py`

3. **[Fase 1b]** GameConfigurator
   - `feat(application): aggiunge GameConfigurator — gestione deck, regole e settings`
   - Files: `src/application/game_configurator.py`
   - Tests: `tests/unit/application/test_game_configurator.py`

4. **[Fase 1c]** SessionRecorder
   - `feat(application): aggiunge SessionRecorder — costruisce e persiste SessionOutcome via ProfileService`
   - Files: `src/application/session_recorder.py`
   - Tests: `tests/unit/application/test_session_recorder.py`

5. **[Fase 1d]** GameEngine + DIContainer aggiornati
   - `refactor(application,infrastructure): GameEngine delega TTS/config/sessione ai nuovi componenti; DIContainer registra i tre factory`
   - Files: `src/application/game_engine.py`, `src/infrastructure/di_container.py`

6. **[Fase 2a+b]** UserProfile + ProfileStorage
   - `feat(domain,infrastructure): aggiunge tts_rate/tts_volume a UserProfile con retrocompatibilità ProfileStorage`
   - Files: `src/domain/models/profile.py`, `src/infrastructure/storage/profile_storage.py`
   - Tests: `tests/unit/domain/test_profile_tts.py`

7. **[Fase 2c]** apply_tts_settings già incluso in TTSAnnouncer (Fase 1a)
   - Nessun commit separato: `apply_tts_settings` è parte del commit Fase 1a (TTSAnnouncer)
   - Aggiornamento in `GameEngine.new_game()` per chiamare `self._tts.apply_tts_settings(...)`
   - `feat(application): GameEngine.new_game chiama tts_announcer.apply_tts_settings al caricamento profilo`
   - Files: `src/application/game_engine.py`

8. **[Fase 2d]** OptionsDialog + UX_SHORTCUTS
   - `feat(presentation,docs): CREA options_dialog.py con slider TTS; crea docs/UX_SHORTCUTS.md con audit scorciatoie`
   - Files: `src/presentation/dialogs/options_dialog.py` (CREATE), `docs/UX_SHORTCUTS.md`

9. **[Fase 3a]** Protocolli Domain
   - `feat(domain): aggiunge src/domain/interfaces/protocols.py — DeckProvider e RuleSet Protocol`
   - Files: `src/domain/interfaces/protocols.py`
   - Tests: `tests/unit/domain/interfaces/test_protocols.py`

10. **[Fase 3b+c]** Plugin registry e implementazioni
    - `feat(infrastructure): plugin registry esplicito — StandardFrenchDeckProvider, NeapolitanDeckProvider, KlondikeRuleSet`
    - Files: `src/infrastructure/plugins/__init__.py`, `plugin_registry.py`, `french_deck_provider.py`, `neapolitan_deck_provider.py`, `klondike_ruleset.py`
    - Tests: `tests/unit/infrastructure/plugins/test_plugin_registry.py`

11. **[Fase 3d]** GameConfigurator integra registry
    - `feat(application): GameConfigurator usa plugin_registry per build_deck e build_rules`
    - Files: `src/application/game_configurator.py`

12. **[Fase 4]** Test di integrazione + documentazione
    - `test(integration): copertura ≥90% per nuovi componenti v3.6.0; docs: API.md, ARCHITECTURE.md, CHANGELOG.md`
    - Files: file test integrazione, `docs/API.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:

- [ ] `grep -r "screen_reader\.tts\.speak\|self\._speak(" src/application/game_engine.py` → 0 risultati nei gestori di mosse (tutti delegati a `TTSAnnouncer.announce()`)
- [ ] `UserProfile.tts_rate` e `.tts_volume` serializzati/deserializzati correttamente
- [ ] Profili legacy (JSON senza `tts_rate`) caricati con default 0/80 senza errori
- [ ] `get_deck_provider("neapolitan")` ritorna `NeapolitanDeckProvider` registrato
- [ ] `docs/UX_SHORTCUTS.md` presente e completo con tutti i `GameCommand`

**Tecnici**:

- [ ] Zero breaking changes — tutti i test pre-esistenti restano verdi
- [ ] `pytest -m "not gui" --cov=src --cov-fail-under=90` passa
- [ ] `mypy src/ --strict` — 0 errori su tutti i file nuovi
- [ ] Nessun ciclo di import tra layer (pylint `--enable=cyclic-import`)
- [ ] `grep -r "print(" src/ --include="*.py"` → 0 risultati

**Code Quality**:

- [ ] PEP8 compliant (pycodestyle)
- [ ] Type hints completi su tutti i metodi pubblici
- [ ] Google-style docstrings su tutti i metodi pubblici
- [ ] `CHANGELOG.md` sezione `[Unreleased]` aggiornata

**Accessibilità**:

- [ ] NVDA legge ogni annuncio mossa (TTSAnnouncer funzionante)
- [ ] Slider Rate/Volume TTS in OptionsDialog leggibili con valore corrente
- [ ] TAB naviga correttamente tutti i controlli in OptionsDialog
- [ ] Keyboard shortcuts documentati in `docs/UX_SHORTCUTS.md`

---

*Fine PLAN — v3.6.0 — generato da analisi iterativa (report v1/v2/v3) con 15 correzioni applicate*

*Percorso archivio definitivo*: `docs/3 - coding plans/PLAN_game-engine-refactoring_v3.6.0.md`
