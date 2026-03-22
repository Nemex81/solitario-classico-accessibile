#!/usr/bin/env python
"""
generate-changelog.py — Semantic Versioning & Changelog Generator

Analizza commit messages da ultimo tag e propone:
  - Versione next (SemVer: MAJOR/MINOR/PATCH)
  - Draft sezione CHANGELOG.md

Uso:
  python scripts/generate-changelog.py
  python scripts/generate-changelog.py --dry-run
  python scripts/generate-changelog.py --force-version 3.6.0
  python scripts/generate-changelog.py --list-commits
"""

import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_latest_tag() -> str:
    """Ottieni ultimo tag di versione (es: v3.5.0)."""
    result = subprocess.run(
        ["git", "tag", "--list", "--sort=-version:refname"],
        capture_output=True,
        text=True,
        cwd="."
    )
    
    tags = result.stdout.strip().split('\n')
    for tag in tags:
        if tag.startswith('v'):
            return tag
    return None

def get_commits_since_tag(tag: str) -> List[str]:
    """Ottieni commit messages da tag al HEAD."""
    if tag:
        commit_range = f"{tag}..HEAD"
    else:
        commit_range = "HEAD"
    
    result = subprocess.run(
        ["git", "log", commit_range, "--pretty=format:%B"],
        capture_output=True,
        text=True,
        cwd="."
    )
    
    commits = result.stdout.strip().split('\n\n')
    return [c.strip() for c in commits if c.strip()]

def parse_conventional_commits(commits: List[str]) -> Tuple[List[dict], str]:
    """
    Analizza conventional commits e restituisce:
      - Lista dict con tipo/scope/subject
      - Suggerimento versione (MAJOR/MINOR/PATCH)
    """
    parsed = []
    has_breaking = False
    has_feature = False
    has_fix = False
    
    # Pattern: type(scope): subject
    pattern = r'^(feat|fix|docs|style|refactor|test|chore|perf)(?:\(([^)]+)\))?:\s*(.+)'
    
    for commit in commits:
        lines = commit.split('\n')
        message = lines[0]
        
        match = re.match(pattern, message)
        if match:
            commit_type = match.group(1)
            scope = match.group(2) or "general"
            subject = match.group(3)
            
            # Detecta breaking changes (sezione BREAKING CHANGE: in body)
            if any("BREAKING CHANGE:" in line for line in lines[1:]):
                has_breaking = True
            
            if commit_type == "feat":
                has_feature = True
            elif commit_type == "fix":
                has_fix = True
            
            parsed.append({
                "type": commit_type,
                "scope": scope,
                "subject": subject,
                "full": message
            })
    
    # Suggerisci versione (SemVer)
    if has_breaking:
        version_type = "MAJOR"
    elif has_feature:
        version_type = "MINOR"
    elif has_fix:
        version_type = "PATCH"
    else:
        version_type = "PATCH"  # Default
    
    return parsed, version_type

def calculate_next_version(current_tag: str, version_type: str) -> str:
    """Calcola versione next da versione attuale e tipo bump."""
    if not current_tag:
        return "1.0.0"
    
    # Estrai versione da tag (v3.5.0 → 3.5.0)
    version_str = current_tag.lstrip('v')
    parts = version_str.split('.')
    
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, IndexError):
        logger.warning(f"Cannot parse version from tag: {current_tag}")
        return "0.0.1"
    
    if version_type == "MAJOR":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "MINOR":
        minor += 1
        patch = 0
    elif version_type == "PATCH":
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def generate_changelog_section(commits_parsed: List[dict], version: str) -> str:
    """Genera sezione CHANGELOG.md per versione."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    sections = {
        "feat": [],
        "fix": [],
        "docs": [],
        "refactor": [],
        "perf": [],
        "test": [],
        "chore": [],
    }
    
    for commit in commits_parsed:
        commit_type = commit["type"]
        if commit_type in sections:
            sections[commit_type].append(commit["subject"])
    
    # Build sezione
    section = f"## [{version}] — {date_str}\n"
    
    if sections["feat"]:
        section += f"\n### Added\n"
        for subject in sections["feat"]:
            section += f"- {subject}\n"
    
    if sections["fix"]:
        section += f"\n### Fixed\n"
        for subject in sections["fix"]:
            section += f"- {subject}\n"
    
    if sections["refactor"] or sections["perf"]:
        section += f"\n### Changed\n"
        for subject in sections["refactor"] + sections["perf"]:
            section += f"- {subject}\n"
    
    if sections["docs"]:
        section += f"\n### Documentation\n"
        for subject in sections["docs"]:
            section += f"- {subject}\n"
    
    return section

def update_changelog(new_section: str, version: str) -> bool:
    """Aggiorna CHANGELOG.md con nuova sezione."""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        logger.warning("CHANGELOG.md not found")
        return False
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Inserisci dopo heading ## [Unreleased]
    lines = content.split('\n')
    insert_idx = None
    
    for i, line in enumerate(lines):
        if line.startswith('## [Unreleased]'):
            insert_idx = i + 1
            break
    
    if insert_idx is None:
        # Inserisci dopo primo ## heading
        for i, line in enumerate(lines):
            if line.startswith('## '):
                insert_idx = i
                break
    
    if insert_idx is None:
        logger.error("Cannot find insertion point in CHANGELOG.md")
        return False
    
    # Inserisci nuova sezione
    new_lines = (
        lines[:insert_idx] +
        [new_section] +
        lines[insert_idx:]
    )
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    logger.info(f"✓ CHANGELOG.md updated with version {version}")
    return True

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelog and suggest next version"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't modify CHANGELOG.md, just show proposal"
    )
    parser.add_argument(
        "--force-version",
        type=str,
        help="Force specific version (skip SemVer detection)"
    )
    parser.add_argument(
        "--list-commits",
        action="store_true",
        help="List analyzed commits and exit"
    )
    
    args = parser.parse_args()
    
    # Get latest tag
    latest_tag = get_latest_tag()
    if latest_tag:
        logger.info(f"Latest tag: {latest_tag}")
    else:
        logger.info("No tags found (initial release)")
    
    # Get commits
    commits = get_commits_since_tag(latest_tag)
    
    if not commits or commits == ['']:
        logger.info("No commits since last tag")
        return 0
    
    logger.info(f"Found {len(commits)} commits")
    
    # Parse conventional commits
    parsed_commits, version_type = parse_conventional_commits(commits)
    
    if args.list_commits:
        for commit in parsed_commits:
            print(f"  {commit['type']:8} ({commit['scope']:10}) {commit['subject']}")
        return 0
    
    if not parsed_commits:
        logger.warning("No conventional commits found (feat:/fix:/etc)")
        return 1
    
    # Calcola next version
    if args.force_version:
        next_version = args.force_version
        logger.info(f"Forced version: {next_version}")
    else:
        next_version = calculate_next_version(latest_tag, version_type)
        logger.info(f"Suggested version: {next_version} ({version_type} bump)")
    
    # Genera sezione CHANGELOG
    changelog_section = generate_changelog_section(parsed_commits, next_version)
    
    print("\n" + "="*60)
    print("CHANGELOG DRAFT:")
    print("="*60)
    print(changelog_section)
    print("="*60 + "\n")
    
    if args.dry_run:
        logger.info("Dry-run: not updating CHANGELOG.md")
        return 0
    
    # Ask confirmation
    response = input("Update CHANGELOG.md? (yes/no): ").strip().lower()
    
    if response in ('yes', 'y'):
        if update_changelog(changelog_section, next_version):
            logger.info(f"✅ CHANGELOG updated to version {next_version}")
            return 0
        else:
            return 1
    else:
        logger.info("Cancelled")
        return 0

if __name__ == "__main__":
    sys.exit(main())
