"""Test per scripts/detect_agent.py"""

import pytest
import sys
import os

# Aggiungi scripts/ al path per import diretto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))

from detect_agent import detect_agent, format_agent_list


# --- Test Agent-Analyze ---

@pytest.mark.unit
class TestDetectAgentAnalyze:
    """Test rilevamento Agent-Analyze."""

    def test_keyword_analizza(self) -> None:
        agent, _ = detect_agent("analizza il sistema audio")
        assert agent == "Agent-Analyze"

    def test_keyword_come_funziona(self) -> None:
        agent, _ = detect_agent("come funziona il timer?")
        assert agent == "Agent-Analyze"

    def test_keyword_esplora(self) -> None:
        agent, _ = detect_agent("esplora la struttura del progetto")
        assert agent == "Agent-Analyze"

    def test_keyword_investigate(self) -> None:
        agent, _ = detect_agent("investigate the audio system")
        assert agent == "Agent-Analyze"


# --- Test Agent-Design ---

@pytest.mark.unit
class TestDetectAgentDesign:
    """Test rilevamento Agent-Design."""

    def test_keyword_progetta(self) -> None:
        agent, _ = detect_agent("progetta il nuovo sistema di profili")
        assert agent == "Agent-Design"

    def test_keyword_design(self) -> None:
        agent, _ = detect_agent("crea il design dell'architettura")
        assert agent == "Agent-Design"

    def test_keyword_riprogetta(self) -> None:
        agent, _ = detect_agent("riprogetta il modulo audio")
        assert agent == "Agent-Design"


# --- Test Agent-Plan ---

@pytest.mark.unit
class TestDetectAgentPlan:
    """Test rilevamento Agent-Plan."""

    def test_keyword_pianifica(self) -> None:
        agent, _ = detect_agent("pianifica il prossimo sprint del progetto")
        assert agent == "Agent-Plan"

    def test_keyword_step_by_step(self) -> None:
        agent, _ = detect_agent("dividi step by step questa feature")
        assert agent == "Agent-Plan"

    def test_keyword_roadmap(self) -> None:
        agent, _ = detect_agent("crea una roadmap del progetto")
        assert agent == "Agent-Plan"


# --- Test Agent-Code ---

@pytest.mark.unit
class TestDetectAgentCode:
    """Test rilevamento Agent-Code."""

    def test_keyword_implementa(self) -> None:
        agent, _ = detect_agent("implementa il salvataggio automatico")
        assert agent == "Agent-Code"

    def test_keyword_codifica(self) -> None:
        agent, _ = detect_agent("codifica la nuova classe ProfileStorage")
        assert agent == "Agent-Code"

    def test_keyword_fix(self) -> None:
        agent, _ = detect_agent("fix il bug nel timer")
        assert agent == "Agent-Code"


# --- Test Agent-Validate ---

@pytest.mark.unit
class TestDetectAgentValidate:
    """Test rilevamento Agent-Validate."""

    def test_keyword_testa(self) -> None:
        agent, _ = detect_agent("testa il modulo scoring")
        assert agent == "Agent-Validate"

    def test_keyword_coverage(self) -> None:
        agent, _ = detect_agent("quanta coverage abbiamo?")
        assert agent == "Agent-Validate"

    def test_keyword_run_tests(self) -> None:
        agent, _ = detect_agent("run tests for the game engine")
        assert agent == "Agent-Validate"


# --- Test Agent-Docs ---

@pytest.mark.unit
class TestDetectAgentDocs:
    """Test rilevamento Agent-Docs."""

    def test_keyword_aggiorna_docs(self) -> None:
        agent, _ = detect_agent("aggiorna docs dopo il refactor")
        assert agent == "Agent-Docs"

    def test_keyword_changelog(self) -> None:
        agent, _ = detect_agent("aggiorna il changelog per la release")
        assert agent == "Agent-Docs"

    def test_keyword_sync_docs(self) -> None:
        agent, _ = detect_agent("sync docs con i nuovi commit")
        assert agent == "Agent-Docs"


# --- Test Agent-Release ---

@pytest.mark.unit
class TestDetectAgentRelease:
    """Test rilevamento Agent-Release."""

    def test_keyword_rilascia(self) -> None:
        agent, _ = detect_agent("rilascia la versione 3.6.0")
        assert agent == "Agent-Release"

    def test_keyword_build_release(self) -> None:
        agent, _ = detect_agent("build release per la distribuzione")
        assert agent == "Agent-Release"

    def test_keyword_deploy(self) -> None:
        agent, _ = detect_agent("deploy the new version")
        assert agent == "Agent-Release"


# --- Test caso AMBIGUOUS ---

@pytest.mark.unit
class TestDetectAgentAmbiguous:
    """Test caso nessuna keyword corrisponde."""

    def test_no_keywords(self) -> None:
        agent, _ = detect_agent("buongiorno, come va?")
        assert agent == "AMBIGUOUS"

    def test_empty_string(self) -> None:
        agent, _ = detect_agent("")
        assert agent == "AMBIGUOUS"

    def test_unrelated_text(self) -> None:
        agent, _ = detect_agent("il meteo di domani sara soleggiato")
        assert agent == "AMBIGUOUS"


# --- Test format_agent_list ---

@pytest.mark.unit
class TestFormatAgentList:
    """Test della formattazione lista agenti."""

    def test_list_contains_all_agents(self) -> None:
        output = format_agent_list()
        assert "Agent-Analyze" in output
        assert "Agent-Design" in output
        assert "Agent-Plan" in output
        assert "Agent-Code" in output
        assert "Agent-Validate" in output
        assert "Agent-Docs" in output
        assert "Agent-Release" in output

    def test_list_not_empty(self) -> None:
        output = format_agent_list()
        assert len(output) > 0


# --- Test case-insensitive ---

@pytest.mark.unit
class TestCaseInsensitive:
    """Verifica che il matching sia case-insensitive."""

    def test_uppercase_input(self) -> None:
        agent, _ = detect_agent("ANALIZZA IL SISTEMA AUDIO")
        assert agent == "Agent-Analyze"

    def test_mixed_case(self) -> None:
        agent, _ = detect_agent("Implementa il Backup")
        assert agent == "Agent-Code"
