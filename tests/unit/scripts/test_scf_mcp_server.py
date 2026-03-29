"""Unit tests for scf-mcp/scf-mcp-server.py

Covers: parse_markdown_frontmatter, normalize_prompt_name,
        extract_framework_version, WorkspaceLocator, FrameworkInventory,
        ScriptExecutor, build_workspace_info.

mcp is mocked at sys.modules level before importing the server module so
tests run in any environment where mcp is not installed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock mcp before importing the server module (mcp may not be installed)
# ---------------------------------------------------------------------------
_mock_mcp = MagicMock()
_mock_fastmcp = MagicMock()
_mock_mcp.server = MagicMock()
_mock_mcp.server.fastmcp = MagicMock()
_mock_mcp.server.fastmcp.FastMCP = _mock_fastmcp

sys.modules.setdefault("mcp", _mock_mcp)
sys.modules.setdefault("mcp.server", _mock_mcp.server)
sys.modules.setdefault("mcp.server.fastmcp", _mock_mcp.server.fastmcp)

# Now safe to import server symbols
_SERVER_PATH = str(
    Path(__file__).parents[3] / "scf-mcp" / "scf-mcp-server.py"
)
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("scf_mcp_server", _SERVER_PATH)
assert _spec is not None and _spec.loader is not None
_module = _ilu.module_from_spec(_spec)
# Must register in sys.modules BEFORE exec_module so that @dataclass
# can resolve cls.__module__ via sys.modules.get(...)
sys.modules["scf_mcp_server"] = _module
_spec.loader.exec_module(_module)  # type: ignore[union-attr]

parse_markdown_frontmatter = _module.parse_markdown_frontmatter
normalize_prompt_name = _module.normalize_prompt_name
extract_framework_version = _module.extract_framework_version
build_workspace_info = _module.build_workspace_info
WorkspaceLocator = _module.WorkspaceLocator
WorkspaceContext = _module.WorkspaceContext
FrameworkFile = _module.FrameworkFile
FrameworkInventory = _module.FrameworkInventory
ScriptExecutor = _module.ScriptExecutor


# ===========================================================================
# parse_markdown_frontmatter
# ===========================================================================


@pytest.mark.unit
class TestParseMarkdownFrontmatter:
    """Tests for parse_markdown_frontmatter()."""

    def test_parse_frontmatter_returns_dict(self) -> None:
        content = "---\ntype: plan\nstatus: READY\n---\nBody text."
        result = parse_markdown_frontmatter(content)
        assert result["type"] == "plan"
        assert result["status"] == "READY"

    def test_parse_bool_true(self) -> None:
        content = "---\ninitialized: true\n---\n"
        result = parse_markdown_frontmatter(content)
        assert result["initialized"] is True

    def test_parse_bool_false(self) -> None:
        content = "---\ninitialized: false\n---\n"
        result = parse_markdown_frontmatter(content)
        assert result["initialized"] is False

    def test_parse_integer(self) -> None:
        content = "---\ncount: 42\n---\n"
        result = parse_markdown_frontmatter(content)
        assert result["count"] == 42

    def test_no_frontmatter_returns_empty(self) -> None:
        content = "# Heading\n\nSome text without frontmatter."
        result = parse_markdown_frontmatter(content)
        assert result == {}

    def test_incomplete_frontmatter_returns_empty(self) -> None:
        content = "---\nno closing marker"
        result = parse_markdown_frontmatter(content)
        assert result == {}

    def test_quoted_string_values_stripped(self) -> None:
        content = '---\nname: "My Agent"\n---\n'
        result = parse_markdown_frontmatter(content)
        assert result["name"] == "My Agent"

    def test_empty_content_returns_empty(self) -> None:
        assert parse_markdown_frontmatter("") == {}


# ===========================================================================
# normalize_prompt_name
# ===========================================================================


@pytest.mark.unit
class TestNormalizePromptName:
    """Tests for normalize_prompt_name()."""

    def test_simple_name(self) -> None:
        assert normalize_prompt_name("help.prompt.md") == "help"

    def test_hyphenated_name(self) -> None:
        assert normalize_prompt_name("framework-unlock.prompt.md") == "frameworkUnlock"

    def test_two_word_name(self) -> None:
        assert normalize_prompt_name("git-commit.prompt.md") == "gitCommit"

    def test_three_word_name(self) -> None:
        assert normalize_prompt_name("project-setup.prompt.md") == "projectSetup"

    def test_sync_docs(self) -> None:
        assert normalize_prompt_name("sync-docs.prompt.md") == "syncDocs"

    def test_framework_changelog(self) -> None:
        assert normalize_prompt_name("framework-changelog.prompt.md") == "frameworkChangelog"

    def test_already_camel_like(self) -> None:
        assert normalize_prompt_name("init.prompt.md") == "init"

    def test_framework_release(self) -> None:
        assert normalize_prompt_name("framework-release.prompt.md") == "frameworkRelease"


# ===========================================================================
# extract_framework_version
# ===========================================================================


@pytest.mark.unit
class TestExtractFrameworkVersion:
    """Tests for extract_framework_version()."""

    def test_extracts_version_with_brackets(self, tmp_path: Path) -> None:
        changelog = tmp_path / "FRAMEWORK_CHANGELOG.md"
        changelog.write_text("## [v1.10.3] - 2026-03-28\n\nSome content.", encoding="utf-8")
        assert extract_framework_version(changelog) == "v1.10.3"

    def test_extracts_version_with_suffix(self, tmp_path: Path) -> None:
        changelog = tmp_path / "FRAMEWORK_CHANGELOG.md"
        changelog.write_text("## [v1.10.3-bootstrap] - 2026-03-28\n", encoding="utf-8")
        assert extract_framework_version(changelog) == "v1.10.3-bootstrap"

    def test_extracts_first_version_when_multiple(self, tmp_path: Path) -> None:
        changelog = tmp_path / "FRAMEWORK_CHANGELOG.md"
        changelog.write_text(
            "## [Unreleased]\n\n## [v1.10.3] - 2026-03-28\n\n## [v1.9.0] - 2026-01-01\n",
            encoding="utf-8",
        )
        assert extract_framework_version(changelog) == "v1.10.3"

    def test_missing_file_returns_unknown(self, tmp_path: Path) -> None:
        missing = tmp_path / "NONEXISTENT.md"
        assert extract_framework_version(missing) == "unknown"

    def test_no_version_heading_returns_unknown(self, tmp_path: Path) -> None:
        changelog = tmp_path / "FRAMEWORK_CHANGELOG.md"
        changelog.write_text("## [Unreleased]\n\nNothing released yet.", encoding="utf-8")
        assert extract_framework_version(changelog) == "unknown"


# ===========================================================================
# WorkspaceLocator
# ===========================================================================


@pytest.mark.unit
class TestWorkspaceLocator:
    """Tests for WorkspaceLocator.resolve()."""

    def test_resolves_from_env_var(self, tmp_path: Path) -> None:
        (tmp_path / ".github").mkdir()
        (tmp_path / "scripts").mkdir()
        with patch.dict("os.environ", {"WORKSPACE_FOLDER": str(tmp_path)}):
            ctx = WorkspaceLocator().resolve()
        assert ctx.workspace_root == tmp_path
        assert ctx.github_root == tmp_path / ".github"
        assert ctx.scripts_root == tmp_path / "scripts"

    def test_falls_back_to_cwd_when_env_absent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        env_without_var = {k: v for k, v in __import__("os").environ.items() if k != "WORKSPACE_FOLDER"}
        with patch.dict("os.environ", env_without_var, clear=True):
            ctx = WorkspaceLocator().resolve()
        assert ctx.workspace_root == tmp_path

    def test_raises_when_root_does_not_exist(self) -> None:
        with patch.dict("os.environ", {"WORKSPACE_FOLDER": "/nonexistent/path/xyz"}):
            with pytest.raises(RuntimeError, match="does not exist or is not a directory"):
                WorkspaceLocator().resolve()

    def test_context_scf_mcp_root_correct(self, tmp_path: Path) -> None:
        with patch.dict("os.environ", {"WORKSPACE_FOLDER": str(tmp_path)}):
            ctx = WorkspaceLocator().resolve()
        assert ctx.scf_mcp_root == tmp_path / "scf-mcp"


# ===========================================================================
# FrameworkInventory
# ===========================================================================


def _make_context(root: Path) -> WorkspaceContext:
    """Create a minimal WorkspaceContext pointing to a tmp directory."""
    return WorkspaceContext(
        workspace_root=root,
        github_root=root / ".github",
        scripts_root=root / "scripts",
        scf_mcp_root=root / "scf-mcp",
    )


def _write_md(directory: Path, filename: str, content: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    p = directory / filename
    p.write_text(content, encoding="utf-8")
    return p


@pytest.mark.unit
class TestFrameworkInventory:
    """Tests for FrameworkInventory discovery methods."""

    def test_list_agents_returns_all_md_files(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / ".github" / "agents"
        _write_md(agents_dir, "Agent-Code.md", "---\nname: Agent-Code\n---\nCode agent.")
        _write_md(agents_dir, "Agent-Git.md", "---\nname: Agent-Git\n---\nGit agent.")
        inv = FrameworkInventory(_make_context(tmp_path))
        agents = inv.list_agents()
        assert len(agents) == 2
        names = {ff.name for ff in agents}
        assert "Agent-Code" in names
        assert "Agent-Git" in names

    def test_list_skills_returns_skill_md_files_only(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / ".github" / "skills"
        _write_md(skills_dir, "validate-accessibility.skill.md", "# Skill")
        _write_md(skills_dir, "README.md", "# README")  # must be excluded
        inv = FrameworkInventory(_make_context(tmp_path))
        skills = inv.list_skills()
        assert len(skills) == 1
        assert skills[0].name == "validate-accessibility.skill"

    def test_list_instructions_returns_instructions_files(self, tmp_path: Path) -> None:
        instr_dir = tmp_path / ".github" / "instructions"
        _write_md(instr_dir, "python.instructions.md", "---\napplyTo: '**/*.py'\n---\n# Python")
        inv = FrameworkInventory(_make_context(tmp_path))
        items = inv.list_instructions()
        assert len(items) == 1
        assert items[0].metadata.get("applyTo") == "**/*.py"

    def test_list_prompts_returns_prompt_files(self, tmp_path: Path) -> None:
        prompts_dir = tmp_path / ".github" / "prompts"
        _write_md(prompts_dir, "init.prompt.md", "---\nname: Init Task\n---\nBody")
        _write_md(prompts_dir, "help.prompt.md", "Help content")
        inv = FrameworkInventory(_make_context(tmp_path))
        prompts = inv.list_prompts()
        assert len(prompts) == 2

    def test_list_scripts_returns_py_files(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "detect_agent.py").write_text("# script", encoding="utf-8")
        (scripts_dir / "not_python.txt").write_text("ignored", encoding="utf-8")
        inv = FrameworkInventory(_make_context(tmp_path))
        scripts = inv.list_scripts()
        assert len(scripts) == 1
        assert scripts[0].name == "detect_agent"

    def test_missing_github_dir_returns_empty_lists(self, tmp_path: Path) -> None:
        inv = FrameworkInventory(_make_context(tmp_path))
        assert inv.list_agents() == []
        assert inv.list_skills() == []
        assert inv.list_instructions() == []
        assert inv.list_prompts() == []

    def test_get_project_profile_returns_none_when_missing(self, tmp_path: Path) -> None:
        inv = FrameworkInventory(_make_context(tmp_path))
        assert inv.get_project_profile() is None

    def test_get_project_profile_parses_initialized_flag(self, tmp_path: Path) -> None:
        github_dir = tmp_path / ".github"
        _write_md(github_dir, "project-profile.md", "---\ninitialized: false\n---\n")
        inv = FrameworkInventory(_make_context(tmp_path))
        ff = inv.get_project_profile()
        assert ff is not None
        assert ff.metadata.get("initialized") is False

    def test_inventory_sorted_alphabetically(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / ".github" / "agents"
        _write_md(agents_dir, "Agent-Z.md", "Z")
        _write_md(agents_dir, "Agent-A.md", "A")
        _write_md(agents_dir, "Agent-M.md", "M")
        inv = FrameworkInventory(_make_context(tmp_path))
        names = [ff.name for ff in inv.list_agents()]
        assert names == sorted(names)

    def test_get_framework_version_uses_real_changelog(self, tmp_path: Path) -> None:
        github_dir = tmp_path / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        (github_dir / "FRAMEWORK_CHANGELOG.md").write_text(
            "## [v2.0.0] - 2026-01-01\n", encoding="utf-8"
        )
        inv = FrameworkInventory(_make_context(tmp_path))
        assert inv.get_framework_version() == "v2.0.0"


# ===========================================================================
# build_workspace_info
# ===========================================================================


@pytest.mark.unit
class TestBuildWorkspaceInfo:
    """Tests for build_workspace_info()."""

    def test_initialized_false_when_profile_absent(self, tmp_path: Path) -> None:
        ctx = _make_context(tmp_path)
        inv = FrameworkInventory(ctx)
        info = build_workspace_info(ctx, inv)
        assert info["initialized"] is False

    def test_initialized_false_surfaced_explicitly(self, tmp_path: Path) -> None:
        github_dir = tmp_path / ".github"
        _write_md(github_dir, "project-profile.md", "---\ninitialized: false\n---\n")
        ctx = _make_context(tmp_path)
        inv = FrameworkInventory(ctx)
        info = build_workspace_info(ctx, inv)
        assert info["initialized"] is False

    def test_contains_path_fields(self, tmp_path: Path) -> None:
        ctx = _make_context(tmp_path)
        inv = FrameworkInventory(ctx)
        info = build_workspace_info(ctx, inv)
        assert "workspace_root" in info
        assert "github_root" in info
        assert "scripts_root" in info

    def test_counts_match_discovered_files(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / ".github" / "agents"
        _write_md(agents_dir, "Agent-A.md", "A")
        _write_md(agents_dir, "Agent-B.md", "B")
        ctx = _make_context(tmp_path)
        inv = FrameworkInventory(ctx)
        info = build_workspace_info(ctx, inv)
        assert info["agent_count"] == 2
        assert info["skill_count"] == 0


# ===========================================================================
# ScriptExecutor
# ===========================================================================


@pytest.mark.unit
class TestScriptExecutor:
    """Tests for ScriptExecutor.run()."""

    def _executor(self, tmp_path: Path) -> Any:
        ctx = _make_context(tmp_path)
        return ScriptExecutor(ctx)

    def test_rejects_non_allowlisted_script(self, tmp_path: Path) -> None:
        result = self._executor(tmp_path).run("git_runner.py", [])
        assert result["success"] is False
        assert "not in the allowed set" in result["error"]

    def test_rejects_update_changelog(self, tmp_path: Path) -> None:
        result = self._executor(tmp_path).run("update_changelog.py", [])
        assert result["success"] is False

    def test_rejects_audio_debug(self, tmp_path: Path) -> None:
        result = self._executor(tmp_path).run("audio_debug.py", [])
        assert result["success"] is False

    def test_returns_error_when_script_file_missing(self, tmp_path: Path) -> None:
        result = self._executor(tmp_path).run("validate_gates.py", [])
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_runs_allowlisted_script(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        script = scripts_dir / "validate_gates.py"
        script.write_text("print('hello')", encoding="utf-8")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "hello\n"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            result = self._executor(tmp_path).run("validate_gates.py", ["--check-structure"])
        assert result["success"] is True
        assert result["stdout"] == "hello\n"
        assert result["returncode"] == 0

    def test_handles_timeout(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "validate_gates.py").write_text("", encoding="utf-8")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=30)):
            result = self._executor(tmp_path).run("validate_gates.py", [])
        assert result["success"] is False
        assert "timed out" in result["error"]

    def test_handles_os_error(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "validate_gates.py").write_text("", encoding="utf-8")
        with patch("subprocess.run", side_effect=OSError("permission denied")):
            result = self._executor(tmp_path).run("validate_gates.py", [])
        assert result["success"] is False
        assert "OS error" in result["error"]

    def test_failed_script_returncode_nonzero(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "validate_gates.py").write_text("", encoding="utf-8")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error output"
        with patch("subprocess.run", return_value=mock_result):
            result = self._executor(tmp_path).run("validate_gates.py", [])
        assert result["success"] is False
        assert result["returncode"] == 1
