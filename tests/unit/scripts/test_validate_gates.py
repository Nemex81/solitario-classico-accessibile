"""Test per scripts/validate_gates.py"""

import os
import sys
import pytest
from typing import Any, Dict, Optional

# Aggiungi scripts/ al path per import diretto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))

from validate_gates import (
    detect_doc_type,
    parse_frontmatter,
    validate_document,
    check_all,
    REQUIRED_FIELDS,
    VALID_STATUS,
)


# --- Helper: crea file temporanei ---


def _write_temp_md(tmp_path: Any, filename: str, content: str) -> str:
    """Scrive un file .md temporaneo e restituisce il path."""
    filepath = os.path.join(str(tmp_path), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


# --- Test parse_frontmatter ---


@pytest.mark.unit
class TestParseFrontmatter:
    """Test parsing del frontmatter YAML."""

    def test_valid_frontmatter(self) -> None:
        content = "---\ntype: design\nfeature: audio\nstatus: DRAFT\nagent: Agent-Design\n---\n# Title\n"
        result = parse_frontmatter(content)
        assert result is not None
        assert result["type"] == "design"
        assert result["feature"] == "audio"

    def test_no_frontmatter(self) -> None:
        content = "# Title\nSome content\n"
        result = parse_frontmatter(content)
        assert result is None

    def test_empty_frontmatter(self) -> None:
        content = "---\n---\n# Title\n"
        result = parse_frontmatter(content)
        assert result is None

    def test_missing_closing_delimiter(self) -> None:
        content = "---\ntype: design\n# Title\n"
        result = parse_frontmatter(content)
        assert result is None

    def test_non_dict_yaml(self) -> None:
        content = "---\n- item1\n- item2\n---\n"
        result = parse_frontmatter(content)
        assert result is None

    def test_blank_lines_before_frontmatter(self) -> None:
        content = "\n\n---\ntype: plan\nfeature: test\nstatus: READY\nagent: Agent-Plan\n---\n"
        result = parse_frontmatter(content)
        assert result is not None
        assert result["type"] == "plan"

    def test_content_before_frontmatter(self) -> None:
        content = "Some text\n---\ntype: design\n---\n"
        result = parse_frontmatter(content)
        assert result is None


# --- Test detect_doc_type ---


@pytest.mark.unit
class TestDetectDocType:
    """Test rilevamento tipo documento dal nome file."""

    def test_design_file(self) -> None:
        assert detect_doc_type("DESIGN_audio.md") == "design"

    def test_plan_file(self) -> None:
        assert detect_doc_type("PLAN_audio.md") == "plan"

    def test_todo_file(self) -> None:
        assert detect_doc_type("TODO.md") == "todo"

    def test_todo_with_prefix(self) -> None:
        assert detect_doc_type("project_TODO.md") == "todo"

    def test_unknown_file(self) -> None:
        assert detect_doc_type("README.md") is None

    def test_design_lowercase(self) -> None:
        assert detect_doc_type("design_feature.md") == "design"

    def test_nested_path(self) -> None:
        assert detect_doc_type("docs/2 - projects/DESIGN_audio.md") == "design"


# --- Test validate_document ---


@pytest.mark.unit
class TestValidateDocument:
    """Test validazione documenti."""

    def test_valid_design(self, tmp_path: Any) -> None:
        content = (
            "---\n"
            "type: design\n"
            "feature: audio-system\n"
            "status: DRAFT\n"
            "agent: Agent-Design\n"
            "---\n"
            "# Design Document\n"
        )
        filepath = _write_temp_md(tmp_path, "DESIGN_audio.md", content)
        code, msgs = validate_document(filepath, "design")
        assert code == 0
        assert any("OK" in m for m in msgs)

    def test_valid_plan(self, tmp_path: Any) -> None:
        content = (
            "---\n"
            "type: plan\n"
            "feature: backup-profiles\n"
            "status: READY\n"
            "agent: Agent-Plan\n"
            "---\n"
            "# Plan\n"
        )
        filepath = _write_temp_md(tmp_path, "PLAN_backup.md", content)
        code, msgs = validate_document(filepath, "plan")
        assert code == 0

    def test_valid_todo(self, tmp_path: Any) -> None:
        content = (
            "---\n"
            "type: todo\n"
            "feature: scoring\n"
            "status: IN PROGRESS\n"
            "---\n"
            "# TODO\n"
        )
        filepath = _write_temp_md(tmp_path, "TODO.md", content)
        code, msgs = validate_document(filepath, "todo")
        assert code == 0

    def test_missing_frontmatter_warns(self, tmp_path: Any) -> None:
        content = "# Design Document\nNo frontmatter here.\n"
        filepath = _write_temp_md(tmp_path, "DESIGN_old.md", content)
        code, msgs = validate_document(filepath, "design")
        assert code == 2
        assert any("WARN" in m for m in msgs)

    def test_wrong_type_field(self, tmp_path: Any) -> None:
        content = (
            "---\n"
            "type: plan\n"
            "feature: audio\n"
            "status: DRAFT\n"
            "agent: Agent-Design\n"
            "---\n"
        )
        filepath = _write_temp_md(tmp_path, "DESIGN_audio.md", content)
        code, msgs = validate_document(filepath, "design")
        assert code == 1
        assert any("ERRORE" in m for m in msgs)

    def test_missing_required_fields(self, tmp_path: Any) -> None:
        content = (
            "---\n"
            "type: design\n"
            "---\n"
        )
        filepath = _write_temp_md(tmp_path, "DESIGN_minimal.md", content)
        code, msgs = validate_document(filepath, "design")
        assert code == 1
        assert any("campi mancanti" in m for m in msgs)

    def test_nonexistent_file(self) -> None:
        code, msgs = validate_document("/nonexistent/path.md", "design")
        assert code == 1
        assert any("non trovato" in m for m in msgs)

    def test_invalid_status_warns(self, tmp_path: Any) -> None:
        content = (
            "---\n"
            "type: design\n"
            "feature: audio\n"
            "status: BANANA\n"
            "agent: Agent-Design\n"
            "---\n"
        )
        filepath = _write_temp_md(tmp_path, "DESIGN_audio.md", content)
        code, msgs = validate_document(filepath, "design")
        assert code == 2
        assert any("non standard" in m for m in msgs)


# --- Test check_all ---


@pytest.mark.unit
class TestCheckAll:
    """Test validazione di una directory intera."""

    def test_empty_directory(self, tmp_path: Any) -> None:
        code, msgs = check_all(str(tmp_path))
        assert any("nessun documento" in m for m in msgs)

    def test_directory_with_valid_docs(self, tmp_path: Any) -> None:
        design_content = (
            "---\n"
            "type: design\n"
            "feature: audio\n"
            "status: DRAFT\n"
            "agent: Agent-Design\n"
            "---\n"
            "# Design\n"
        )
        plan_content = (
            "---\n"
            "type: plan\n"
            "feature: audio\n"
            "status: READY\n"
            "agent: Agent-Plan\n"
            "---\n"
            "# Plan\n"
        )
        _write_temp_md(tmp_path, "DESIGN_audio.md", design_content)
        _write_temp_md(tmp_path, "PLAN_audio.md", plan_content)
        code, msgs = check_all(str(tmp_path))
        assert code == 0
        assert len([m for m in msgs if "OK" in m]) == 2

    def test_directory_missing_frontmatter(self, tmp_path: Any) -> None:
        content = "# Old Design\nNo YAML here.\n"
        _write_temp_md(tmp_path, "DESIGN_old.md", content)
        code, msgs = check_all(str(tmp_path))
        assert code == 2

    def test_nonexistent_directory(self) -> None:
        code, msgs = check_all("/nonexistent/dir")
        assert code == 1
        assert any("non trovata" in m for m in msgs)

    def test_ignores_non_md_files(self, tmp_path: Any) -> None:
        # Crea un file .txt che non deve essere processato
        txt_path = os.path.join(str(tmp_path), "DESIGN_audio.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("not a markdown file")
        code, msgs = check_all(str(tmp_path))
        assert any("nessun documento" in m for m in msgs)

    def test_ignores_unrecognized_md(self, tmp_path: Any) -> None:
        _write_temp_md(tmp_path, "README.md", "# Readme\n")
        code, msgs = check_all(str(tmp_path))
        assert any("nessun documento" in m for m in msgs)


# --- Test costanti ---


@pytest.mark.unit
class TestConstants:
    """Verifica correttezza delle costanti."""

    def test_required_fields_design(self) -> None:
        assert "type" in REQUIRED_FIELDS["design"]
        assert "status" in REQUIRED_FIELDS["design"]
        assert "feature" in REQUIRED_FIELDS["design"]
        assert "agent" in REQUIRED_FIELDS["design"]

    def test_required_fields_plan(self) -> None:
        assert "type" in REQUIRED_FIELDS["plan"]
        assert "agent" in REQUIRED_FIELDS["plan"]

    def test_required_fields_todo(self) -> None:
        assert "type" in REQUIRED_FIELDS["todo"]
        assert "status" in REQUIRED_FIELDS["todo"]

    def test_valid_status_contains_draft(self) -> None:
        assert "DRAFT" in VALID_STATUS

    def test_valid_status_contains_ready(self) -> None:
        assert "READY" in VALID_STATUS
