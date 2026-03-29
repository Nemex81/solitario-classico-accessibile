"""SCF-MCP-Server: expose the SPARK Code Framework as MCP Resources and Tools.

Transport: stdio only.
Logging: stderr or file — never stdout (would corrupt the JSON-RPC stream).
Python: 3.10+ required (MCP SDK baseline).

Domain boundary:
- Slash commands (/scf-*): handled by VS Code natively from .github/prompts/
- Tools and Resources: handled by this server — dynamic, on-demand, Agent mode only
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Logging — configure before any other import so import errors are visible.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
_log: logging.Logger = logging.getLogger("scf-mcp")

# ---------------------------------------------------------------------------
# FastMCP import guard
# ---------------------------------------------------------------------------
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as _import_exc:
    _log.critical(
        "mcp library not installed. Run: pip install mcp  (Python 3.10+ required)"
    )
    raise SystemExit(1) from _import_exc

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkspaceContext:
    """Resolve and expose the active workspace and all SCF-relevant roots."""

    workspace_root: Path
    github_root: Path
    scripts_root: Path
    scf_mcp_root: Path


@dataclass(frozen=True)
class FrameworkFile:
    """Describe a discovered SCF file and the metadata extracted from it."""

    name: str
    path: Path
    category: str
    summary: str
    metadata: dict[str, Any]  # frontmatter values can be str, int or bool


# ---------------------------------------------------------------------------
# WorkspaceLocator
# ---------------------------------------------------------------------------


class WorkspaceLocator:
    """Resolve WORKSPACE_FOLDER env var with fallback to cwd.

    Validates that the resolved root is an existing directory and logs
    a warning when optional subdirectories (.github/, scripts/) are absent.
    """

    def resolve(self) -> WorkspaceContext:
        """Return a WorkspaceContext pointing to the active workspace root."""
        workspace_root_str: str | None = os.environ.get("WORKSPACE_FOLDER")
        if workspace_root_str:
            workspace_root = Path(workspace_root_str)
        else:
            workspace_root = Path.cwd()
            _log.warning(
                "WORKSPACE_FOLDER env var not set; falling back to cwd: %s",
                workspace_root,
            )

        if not workspace_root.is_dir():
            raise RuntimeError(
                f"Workspace root does not exist or is not a directory: {workspace_root}"
            )

        github_root = workspace_root / ".github"
        scripts_root = workspace_root / "scripts"
        scf_mcp_root = workspace_root / "scf-mcp"

        if not github_root.is_dir():
            _log.warning(".github/ not found in workspace: %s", github_root)
        if not scripts_root.is_dir():
            _log.warning("scripts/ not found in workspace: %s", scripts_root)

        return WorkspaceContext(
            workspace_root=workspace_root,
            github_root=github_root,
            scripts_root=scripts_root,
            scf_mcp_root=scf_mcp_root,
        )


# ---------------------------------------------------------------------------
# Standalone parsers
# ---------------------------------------------------------------------------


def parse_markdown_frontmatter(content: str) -> dict[str, Any]:
    """Parse optional YAML-style key:value frontmatter from markdown content.

    Returns a normalised dict on success, or an empty dict when no frontmatter
    block is found. Handles str, int and bool scalar types. Depends only on
    stdlib — pyyaml is not required.
    """
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    result: dict[str, Any] = {}
    for raw_line in parts[1].strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        value_str = raw_value.strip().strip('"').strip("'")
        if value_str.lower() in ("true", "yes"):
            result[key.strip()] = True
        elif value_str.lower() in ("false", "no"):
            result[key.strip()] = False
        elif value_str.isdigit():
            result[key.strip()] = int(value_str)
        else:
            result[key.strip()] = value_str
    return result


def extract_framework_version(changelog_path: Path) -> str:
    """Extract the latest framework version label from FRAMEWORK_CHANGELOG.md.

    Scans for the first markdown heading matching a version pattern such as
    '## [v1.10.3]' or '## [v1.10.3-bootstrap]'.
    Returns 'unknown' when the file is absent or no version heading is found.
    """
    if not changelog_path.is_file():
        _log.warning("FRAMEWORK_CHANGELOG.md not found: %s", changelog_path)
        return "unknown"
    try:
        text = changelog_path.read_text(encoding="utf-8")
    except OSError as exc:
        _log.error("Cannot read FRAMEWORK_CHANGELOG.md: %s", exc)
        return "unknown"
    pattern = re.compile(
        r"^\s*#{1,3}\s+\[?(v?[\d]+\.[\d]+\.[\d]+[^\]\s]*)\]?",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1) if match else "unknown"


# ---------------------------------------------------------------------------
# FrameworkInventory
# ---------------------------------------------------------------------------


class FrameworkInventory:
    """Discover framework files under .github/ and scripts/ dynamically.

    All discovery is performed on first call; no results are cached so that
    the server reflects filesystem changes across invocations.
    """

    def __init__(self, context: WorkspaceContext) -> None:
        self._ctx = context

    def _build_framework_file(self, path: Path, category: str) -> FrameworkFile:
        """Read a file from disk and return a populated FrameworkFile."""
        name = path.stem
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            _log.warning("Cannot read %s: %s", path, exc)
            content = ""
        metadata = parse_markdown_frontmatter(content)
        summary = ""
        for raw in content.splitlines():
            stripped = raw.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                summary = stripped[:160]
                break
        return FrameworkFile(
            name=name,
            path=path,
            category=category,
            summary=summary,
            metadata=metadata,
        )

    def _list_by_pattern(
        self,
        directory: Path,
        glob_pattern: str,
        category: str,
    ) -> list[FrameworkFile]:
        """Return sorted list of FrameworkFile for all files matching glob."""
        if not directory.is_dir():
            _log.debug(
                "Directory not found for pattern '%s': %s", glob_pattern, directory
            )
            return []
        return sorted(
            [self._build_framework_file(p, category) for p in directory.glob(glob_pattern)],
            key=lambda ff: ff.name,
        )

    def list_agents(self) -> list[FrameworkFile]:
        """Return all agent files from .github/agents/."""
        return self._list_by_pattern(
            self._ctx.github_root / "agents", "*.md", "agent"
        )

    def list_skills(self) -> list[FrameworkFile]:
        """Return all skill files from .github/skills/."""
        return self._list_by_pattern(
            self._ctx.github_root / "skills", "*.skill.md", "skill"
        )

    def list_instructions(self) -> list[FrameworkFile]:
        """Return all instruction files from .github/instructions/."""
        return self._list_by_pattern(
            self._ctx.github_root / "instructions",
            "*.instructions.md",
            "instruction",
        )

    def list_prompts(self) -> list[FrameworkFile]:
        """Return all prompt files from .github/prompts/ (read-only, not registered as MCP Prompts).

        Prompt files are served as Resources (prompts://list, prompts://{name})
        and via scf_list_prompts / scf_get_prompt tools so that Agent mode can
        read their content on demand. They are NOT registered as MCP Prompts to
        avoid duplicating the slash commands that VS Code already creates natively
        from .github/prompts/*.prompt.md.
        """
        return self._list_by_pattern(
            self._ctx.github_root / "prompts", "*.prompt.md", "prompt"
        )

    def list_scripts(self) -> list[FrameworkFile]:
        """Return all Python scripts from scripts/."""
        return self._list_by_pattern(self._ctx.scripts_root, "*.py", "script")

    def get_project_profile(self) -> FrameworkFile | None:
        """Return project-profile.md as FrameworkFile, or None if absent."""
        path = self._ctx.github_root / "project-profile.md"
        if not path.is_file():
            return None
        return self._build_framework_file(path, "config")

    def get_global_instructions(self) -> FrameworkFile | None:
        """Return copilot-instructions.md as FrameworkFile, or None if absent."""
        path = self._ctx.github_root / "copilot-instructions.md"
        if not path.is_file():
            return None
        return self._build_framework_file(path, "config")

    def get_model_policy(self) -> FrameworkFile | None:
        """Return model-policy.instructions.md as FrameworkFile, or None if absent."""
        path = self._ctx.github_root / "instructions" / "model-policy.instructions.md"
        if not path.is_file():
            return None
        return self._build_framework_file(path, "instruction")

    def get_agents_index(self) -> FrameworkFile | None:
        """Return AGENTS.md as FrameworkFile, or None if absent."""
        path = self._ctx.github_root / "AGENTS.md"
        if not path.is_file():
            return None
        return self._build_framework_file(path, "index")

    def get_framework_version(self) -> str:
        """Return the latest framework version string from FRAMEWORK_CHANGELOG.md."""
        return extract_framework_version(
            self._ctx.github_root / "FRAMEWORK_CHANGELOG.md"
        )


# ---------------------------------------------------------------------------
# workspace-info builder
# ---------------------------------------------------------------------------


def build_workspace_info(
    context: WorkspaceContext,
    inventory: FrameworkInventory,
) -> dict[str, Any]:
    """Assemble a structured summary of workspace paths, init state and SCF assets."""
    profile = inventory.get_project_profile()
    initialized: bool = False
    if profile:
        initialized = bool(profile.metadata.get("initialized", False))
    return {
        "workspace_root": str(context.workspace_root),
        "github_root": str(context.github_root),
        "scripts_root": str(context.scripts_root),
        "initialized": initialized,
        "framework_version": inventory.get_framework_version(),
        "agent_count": len(inventory.list_agents()),
        "skill_count": len(inventory.list_skills()),
        "instruction_count": len(inventory.list_instructions()),
        "prompt_count": len(inventory.list_prompts()),
        "script_count": len(inventory.list_scripts()),
    }


# ---------------------------------------------------------------------------
# ScriptExecutor
# ---------------------------------------------------------------------------

_SCRIPT_TIMEOUT_SECONDS: int = 30


class ScriptExecutor:
    """Run selected scripts from scripts/ with allowlist, timeout and NVDA-safe output.

    git_runner.py, update_changelog.py and audio_debug.py are excluded from v1.0.0:
    - git_runner.py: would bypass the framework git policy.
    - update_changelog.py / audio_debug.py: no stable CLI in v1.0.0.
    All output is captured as plain text and never written to stdout.
    """

    _ALLOWLIST: frozenset[str] = frozenset(
        {
            "detect_agent.py",
            "validate_gates.py",
            "ci-local-validate.py",
            "generate-changelog.py",
            "sync-documentation.py",
            "create-project-files.py",
        }
    )

    def __init__(self, context: WorkspaceContext) -> None:
        self._ctx = context

    def run(self, script_name: str, args: list[str]) -> dict[str, Any]:
        """Execute an allowlisted script from scripts/ and return a structured result."""
        if script_name not in self._ALLOWLIST:
            return {
                "success": False,
                "error": (
                    f"{script_name!r} is not in the allowed set. "
                    f"Allowed: {sorted(self._ALLOWLIST)}"
                ),
                "stdout": "",
                "stderr": "",
                "returncode": -1,
            }

        script_path = self._ctx.scripts_root / script_name
        if not script_path.is_file():
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
                "stdout": "",
                "stderr": "",
                "returncode": -1,
            }

        cmd = [sys.executable, str(script_path)] + args
        _log.info("Running script: %s %s", script_name, args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=_SCRIPT_TIMEOUT_SECONDS,
                cwd=str(self._ctx.workspace_root),
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": (
                    f"Script timed out after {_SCRIPT_TIMEOUT_SECONDS}s: {script_name}"
                ),
                "stdout": "",
                "stderr": "",
                "returncode": -1,
            }
        except OSError as exc:
            return {
                "success": False,
                "error": f"OS error running {script_name}: {exc}",
                "stdout": "",
                "stderr": "",
                "returncode": -1,
            }

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }


# ---------------------------------------------------------------------------
# ScfMcpApplication — Resources (16) and Tools (13)
# ---------------------------------------------------------------------------


class ScfMcpApplication:
    """Register MCP resources and tools over FastMCP via workspace discovery.

    MCP Prompts are intentionally NOT registered here.
    VS Code already exposes .github/prompts/*.prompt.md as native slash commands
    (/scf-*). Registering them again via MCP would create duplicate entries in
    the / command picker. The prompt files remain accessible as Resources
    (prompts://list, prompts://{name}) and via scf_list_prompts / scf_get_prompt
    tools for Agent mode consumption.
    """

    def __init__(
        self,
        mcp: FastMCP,
        context: WorkspaceContext,
        inventory: FrameworkInventory,
        executor: ScriptExecutor,
    ) -> None:
        self._mcp = mcp
        self._ctx = context
        self._inventory = inventory
        self._executor = executor

    def register_resources(self) -> None:
        """Register all 16 MCP resources.

        List resources: agents://list, skills://list, instructions://list,
            prompts://list, scripts://list.
        Template resources: agents://{name}, skills://{name},
            instructions://{name}, prompts://{name}, scripts://{name}.
        Singleton scf:// resources: global-instructions, project-profile,
            model-policy, agents-index, framework-version, workspace-info.
        All resources return plain text UTF-8.
        """
        inventory = self._inventory
        ctx = self._ctx

        def _fmt_list(items: list[FrameworkFile], title: str) -> str:
            if not items:
                return f"# {title}\n\nNone found."
            lines = [f"# {title} ({len(items)} total)\n"]
            for ff in items:
                desc = str(ff.summary)[:120] if ff.summary else "(no description)"
                lines.append(f"- {ff.name}: {desc}")
            return "\n".join(lines)

        def _fmt_workspace_info(info: dict[str, Any]) -> str:
            lines = ["# SCF Workspace Info\n"]
            for key, val in info.items():
                lines.append(f"{key}: {val}")
            return "\n".join(lines)

        # ---- agents ----

        @self._mcp.resource("agents://list")
        async def resource_agents_list() -> str:  # type: ignore[misc]
            return _fmt_list(inventory.list_agents(), "SCF Agents")

        @self._mcp.resource("agents://{name}")
        async def resource_agent_by_name(name: str) -> str:  # type: ignore[misc]
            name_lower = name.lower()
            for ff in inventory.list_agents():
                if ff.name.lower() == name_lower:
                    return ff.path.read_text(encoding="utf-8", errors="replace")
            return (
                f"Agent '{name}' not found. "
                "Use resource agents://list to see available agent names."
            )

        # ---- skills ----

        @self._mcp.resource("skills://list")
        async def resource_skills_list() -> str:  # type: ignore[misc]
            return _fmt_list(inventory.list_skills(), "SCF Skills")

        @self._mcp.resource("skills://{name}")
        async def resource_skill_by_name(name: str) -> str:  # type: ignore[misc]
            query = name.lower().removesuffix(".skill")
            for ff in inventory.list_skills():
                if ff.name.lower().removesuffix(".skill") == query:
                    return ff.path.read_text(encoding="utf-8", errors="replace")
            return (
                f"Skill '{name}' not found. "
                "Use resource skills://list to see available skill names."
            )

        # ---- instructions ----

        @self._mcp.resource("instructions://list")
        async def resource_instructions_list() -> str:  # type: ignore[misc]
            return _fmt_list(inventory.list_instructions(), "SCF Instructions")

        @self._mcp.resource("instructions://{name}")
        async def resource_instruction_by_name(name: str) -> str:  # type: ignore[misc]
            query = name.lower().removesuffix(".instructions")
            for ff in inventory.list_instructions():
                if ff.name.lower().removesuffix(".instructions") == query:
                    return ff.path.read_text(encoding="utf-8", errors="replace")
            return (
                f"Instruction '{name}' not found. "
                "Use resource instructions://list to see available instruction names."
            )

        # ---- prompts (read-only resources, NOT MCP Prompts) ----

        @self._mcp.resource("prompts://list")
        async def resource_prompts_list() -> str:  # type: ignore[misc]
            return _fmt_list(inventory.list_prompts(), "SCF Prompts")

        @self._mcp.resource("prompts://{name}")
        async def resource_prompt_by_name(name: str) -> str:  # type: ignore[misc]
            query = name.lower().removesuffix(".prompt")
            for ff in inventory.list_prompts():
                if ff.name.lower().removesuffix(".prompt") == query:
                    return ff.path.read_text(encoding="utf-8", errors="replace")
            return (
                f"Prompt '{name}' not found. "
                "Use resource prompts://list to see available prompt names."
            )

        # ---- scripts ----

        @self._mcp.resource("scripts://list")
        async def resource_scripts_list() -> str:  # type: ignore[misc]
            return _fmt_list(inventory.list_scripts(), "SCF Scripts")

        @self._mcp.resource("scripts://{name}")
        async def resource_script_by_name(name: str) -> str:  # type: ignore[misc]
            query = name.lower().removesuffix(".py")
            for ff in inventory.list_scripts():
                if ff.name.lower() == query:
                    return ff.path.read_text(encoding="utf-8", errors="replace")
            return (
                f"Script '{name}' not found. "
                "Use resource scripts://list to see available script names."
            )

        # ---- scf:// singletons ----

        @self._mcp.resource("scf://global-instructions")
        async def resource_global_instructions() -> str:  # type: ignore[misc]
            ff = inventory.get_global_instructions()
            if ff is None:
                return "copilot-instructions.md not found in .github/."
            return ff.path.read_text(encoding="utf-8", errors="replace")

        @self._mcp.resource("scf://project-profile")
        async def resource_project_profile() -> str:  # type: ignore[misc]
            ff = inventory.get_project_profile()
            if ff is None:
                return "project-profile.md not found in .github/."
            content = ff.path.read_text(encoding="utf-8", errors="replace")
            if not ff.metadata.get("initialized", False):
                return (
                    "# WARNING: project not initialized (initialized: false)\n"
                    "Run #project-setup to configure this workspace.\n\n"
                    + content
                )
            return content

        @self._mcp.resource("scf://model-policy")
        async def resource_model_policy() -> str:  # type: ignore[misc]
            ff = inventory.get_model_policy()
            if ff is None:
                return "model-policy.instructions.md not found in .github/instructions/."
            return ff.path.read_text(encoding="utf-8", errors="replace")

        @self._mcp.resource("scf://agents-index")
        async def resource_agents_index() -> str:  # type: ignore[misc]
            ff = inventory.get_agents_index()
            if ff is None:
                return "AGENTS.md not found in .github/."
            return ff.path.read_text(encoding="utf-8", errors="replace")

        @self._mcp.resource("scf://framework-version")
        async def resource_framework_version() -> str:  # type: ignore[misc]
            version = inventory.get_framework_version()
            return f"SCF Framework version: {version}"

        @self._mcp.resource("scf://workspace-info")
        async def resource_workspace_info_res() -> str:  # type: ignore[misc]
            info = build_workspace_info(ctx, inventory)
            return _fmt_workspace_info(info)

        _log.info(
            "Resources registered: 5 list + 5 template + 6 scf:// singletons (16 total)"
        )

    def register_tools(self) -> None:  # noqa: C901
        """Register all 13 MCP tools.

        Informational: scf_list_agents, scf_get_agent, scf_list_skills,
            scf_get_skill, scf_list_instructions, scf_get_instruction,
            scf_list_prompts, scf_get_prompt, scf_list_scripts,
            scf_get_framework_version, scf_get_workspace_info.
        Singleton docs: scf_get_project_profile, scf_get_global_instructions,
            scf_get_model_policy.
        Execution: scf_run_script (allowlisted, 30s timeout).

        Note: scf_list_prompts and scf_get_prompt are kept as tools so that
        Agent mode can read prompt file content on demand. They do NOT register
        MCP Prompts and do not cause slash command duplication.
        """
        inventory = self._inventory
        executor = self._executor

        def _ff_to_dict(ff: FrameworkFile) -> dict[str, Any]:
            return {
                "name": ff.name,
                "path": str(ff.path),
                "category": ff.category,
                "summary": ff.summary,
                "metadata": ff.metadata,
            }

        # ----------------------------------------------------------------
        # Agent tools
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_list_agents() -> dict[str, Any]:  # type: ignore[misc]
            """Return all discovered SCF agents with name, path and summary."""
            items = inventory.list_agents()
            return {"count": len(items), "agents": [_ff_to_dict(ff) for ff in items]}

        @self._mcp.tool()
        async def scf_get_agent(name: str) -> dict[str, Any]:  # type: ignore[misc]
            """Return full content and metadata for a single SCF agent by name."""
            name_lower = name.lower()
            for ff in inventory.list_agents():
                if ff.name.lower() == name_lower:
                    result = _ff_to_dict(ff)
                    result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
                    return result
            return {
                "error": f"Agent '{name}' not found.",
                "available": [ff.name for ff in inventory.list_agents()],
            }

        # ----------------------------------------------------------------
        # Skill tools
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_list_skills() -> dict[str, Any]:  # type: ignore[misc]
            """Return all discovered SCF skills with name, path and summary."""
            items = inventory.list_skills()
            return {"count": len(items), "skills": [_ff_to_dict(ff) for ff in items]}

        @self._mcp.tool()
        async def scf_get_skill(name: str) -> dict[str, Any]:  # type: ignore[misc]
            """Return full content and metadata for a single SCF skill by name."""
            query = name.lower().removesuffix(".skill")
            for ff in inventory.list_skills():
                if ff.name.lower().removesuffix(".skill") == query:
                    result = _ff_to_dict(ff)
                    result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
                    return result
            return {
                "error": f"Skill '{name}' not found.",
                "available": [ff.name for ff in inventory.list_skills()],
            }

        # ----------------------------------------------------------------
        # Instruction tools
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_list_instructions() -> dict[str, Any]:  # type: ignore[misc]
            """Return all discovered SCF instruction files with name, path and summary."""
            items = inventory.list_instructions()
            return {"count": len(items), "instructions": [_ff_to_dict(ff) for ff in items]}

        @self._mcp.tool()
        async def scf_get_instruction(name: str) -> dict[str, Any]:  # type: ignore[misc]
            """Return full content and metadata for a single SCF instruction by name."""
            query = name.lower().removesuffix(".instructions")
            for ff in inventory.list_instructions():
                if ff.name.lower().removesuffix(".instructions") == query:
                    result = _ff_to_dict(ff)
                    result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
                    return result
            return {
                "error": f"Instruction '{name}' not found.",
                "available": [ff.name for ff in inventory.list_instructions()],
            }

        # ----------------------------------------------------------------
        # Prompt tools (read-only, no MCP Prompt registration)
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_list_prompts() -> dict[str, Any]:  # type: ignore[misc]
            """Return all SCF prompt files with name, path and summary.

            These are read-only tool results. The actual slash commands (/scf-*)
            are provided natively by VS Code from .github/prompts/ — no duplication.
            """
            items = inventory.list_prompts()
            return {"count": len(items), "prompts": [_ff_to_dict(ff) for ff in items]}

        @self._mcp.tool()
        async def scf_get_prompt(name: str) -> dict[str, Any]:  # type: ignore[misc]
            """Return full content of a SCF prompt file by stem name (without extension)."""
            query = name.lower().removesuffix(".prompt")
            for ff in inventory.list_prompts():
                if ff.name.lower().removesuffix(".prompt") == query:
                    result = _ff_to_dict(ff)
                    result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
                    return result
            return {
                "error": f"Prompt '{name}' not found.",
                "available": [ff.name for ff in inventory.list_prompts()],
            }

        # ----------------------------------------------------------------
        # Script tools
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_list_scripts() -> dict[str, Any]:  # type: ignore[misc]
            """Return all scripts in scripts/ with name, path and allowlist status."""
            items = inventory.list_scripts()
            return {
                "count": len(items),
                "scripts": [
                    {**_ff_to_dict(ff), "allowed": ff.path.name in ScriptExecutor._ALLOWLIST}
                    for ff in items
                ],
            }

        @self._mcp.tool()
        async def scf_run_script(  # type: ignore[misc]
            script_name: str,
            args: list[str] | None = None,
        ) -> dict[str, Any]:
            """Execute an allowlisted script from scripts/ and return captured output.

            Allowed: detect_agent.py, validate_gates.py, ci-local-validate.py,
            generate-changelog.py, sync-documentation.py, create-project-files.py.
            Excluded: git_runner.py, update_changelog.py, audio_debug.py.
            Timeout: 30 seconds. Output is plain text, NVDA-safe.
            """
            return executor.run(script_name, args or [])

        # ----------------------------------------------------------------
        # Singleton document tools
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_get_project_profile() -> dict[str, Any]:  # type: ignore[misc]
            """Return project-profile.md content, metadata and initialized state."""
            ff = inventory.get_project_profile()
            if ff is None:
                return {"error": "project-profile.md not found in .github/."}
            result = _ff_to_dict(ff)
            result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
            result["initialized"] = bool(ff.metadata.get("initialized", False))
            if not result["initialized"]:
                result["warning"] = (
                    "Project not initialized (initialized: false). "
                    "Run #project-setup to configure this workspace."
                )
            return result

        @self._mcp.tool()
        async def scf_get_global_instructions() -> dict[str, Any]:  # type: ignore[misc]
            """Return copilot-instructions.md content and metadata."""
            ff = inventory.get_global_instructions()
            if ff is None:
                return {"error": "copilot-instructions.md not found in .github/."}
            result = _ff_to_dict(ff)
            result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
            return result

        @self._mcp.tool()
        async def scf_get_model_policy() -> dict[str, Any]:  # type: ignore[misc]
            """Return model-policy.instructions.md content and metadata."""
            ff = inventory.get_model_policy()
            if ff is None:
                return {
                    "error": "model-policy.instructions.md not found in "
                    ".github/instructions/."
                }
            result = _ff_to_dict(ff)
            result["content"] = ff.path.read_text(encoding="utf-8", errors="replace")
            return result

        # ----------------------------------------------------------------
        # Framework version & workspace info
        # ----------------------------------------------------------------

        @self._mcp.tool()
        async def scf_get_framework_version() -> dict[str, Any]:  # type: ignore[misc]
            """Return the latest SCF framework version from FRAMEWORK_CHANGELOG.md."""
            return {"framework_version": inventory.get_framework_version()}

        @self._mcp.tool()
        async def scf_get_workspace_info() -> dict[str, Any]:  # type: ignore[misc]
            """Return workspace paths, initialization state and SCF asset counts."""
            return build_workspace_info(self._ctx, inventory)

        _log.info("Tools registered: 13 total")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _build_app() -> FastMCP:
    """Initialise workspace, inventory and FastMCP application."""
    mcp: FastMCP = FastMCP("scfMcp")

    locator = WorkspaceLocator()
    context = locator.resolve()
    _log.info("Workspace resolved: %s", context.workspace_root)

    inventory = FrameworkInventory(context)
    _log.info(
        "Framework inventory: %d agents, %d skills, %d instructions, "
        "%d prompts, %d scripts",
        len(inventory.list_agents()),
        len(inventory.list_skills()),
        len(inventory.list_instructions()),
        len(inventory.list_prompts()),
        len(inventory.list_scripts()),
    )

    executor = ScriptExecutor(context)

    app = ScfMcpApplication(mcp, context, inventory, executor)
    app.register_resources()
    app.register_tools()

    return mcp


if __name__ == "__main__":
    _build_app().run(transport="stdio")
