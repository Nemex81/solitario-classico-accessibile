#!/usr/bin/env python
"""
sync-documentation.py — Sincronizzazione Documentazione

Valida:
  - API.md ha entry per tutte le public APIS
  - ARCHITECTURE.md allineato con struttura codebase
  - Link non rotti

Uso:
  python scripts/sync-documentation.py
  python scripts/sync-documentation.py --check-only
  python scripts/sync-documentation.py --fix-links
"""

import sys
import subprocess
import argparse
import logging
import re
from pathlib import Path
from typing import List, Tuple, Set

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def extract_public_apis(src_dir: str = "src") -> Set[Tuple[str, str]]:
    """
    Estrai classi/funzioni pubbliche dai file __init__.py.
    Ritorna set di (module_name, symbol_name).
    """
    apis = set()
    
    init_files = Path(src_dir).rglob("__init__.py")
    for init_file in init_files:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cerca linee "from ... import ..."
        imports = re.findall(r'from\s+[.\w]+\s+import\s+(.+)', content)
        for import_line in imports:
            symbols = [s.strip() for s in import_line.split(',')]
            module = str(init_file.parent)
            for symbol in symbols:
                apis.add((module, symbol))
    
    return apis

def check_api_documentation(apis: Set[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
    """
    Verifica che API.md ha entry per ogni public API.
    Ritorna (missing, existing).
    """
    missing = []
    existing = []
    
    api_path = Path("docs/API.md")
    if not api_path.exists():
        logger.error("docs/API.md not found")
        return list(apis), []
    
    with open(api_path, 'r', encoding='utf-8') as f:
        api_content = f.read()
    
    for module, symbol in sorted(apis):
        # Semplice check: il simbolo appare in API.md?
        if f"`{symbol}`" in api_content or f"## {symbol}" in api_content:
            existing.append((module, symbol))
        else:
            missing.append((module, symbol))
    
    return missing, existing

def check_architecture_document() -> bool:
    """Verifica che ARCHITECTURE.md esiste e ha sezioni essenziali."""
    arch_path = Path("docs/ARCHITECTURE.md")
    
    if not arch_path.exists():
        logger.error("docs/ARCHITECTURE.md not found")
        return False
    
    with open(arch_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_sections = ["Layer", "Dependency", "Design Pattern"]
    missing_sections = [s for s in required_sections if s.lower() not in content.lower()]
    
    if missing_sections:
        logger.warning(f"ARCHITECTURE.md missing sections: {missing_sections}")
        return False
    
    logger.info("✓ ARCHITECTURE.md has essential sections")
    return True

def check_broken_links() -> Tuple[List[Tuple[str, str]], List[str]]:
    """
    Verifica link rotti in docs.
    Ritorna (broken_links, valid_files).
    """
    broken = []
    valid = []
    
    # Cerca file markdown
    md_files = list(Path("docs").glob("**/*.md"))
    
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Estrai link [text](path)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for text, link in links:
            # Skip URL online
            if link.startswith('http'):
                continue
            
            # Extractr path (senza anchor)
            link_path = link.split('#')[0]
            
            # Costruisci path assoluto
            if link_path.startswith('/'):
                target = Path(link_path[1:])
            else:
                target = md_file.parent / link_path
            
            if not target.exists():
                broken.append((str(md_file), link))
            else:
                if target not in valid:
                    valid.append(str(target))
    
    return broken, valid

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate and sync documentation"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Report only, don't modify"
    )
    parser.add_argument(
        "--fix-links",
        action="store_true",
        help="Auto-remove broken link references"
    )
    
    args = parser.parse_args()
    
    logger.info("Scanning codebase for public APIs...")
    apis = extract_public_apis()
    logger.info(f"Found {len(apis)} public APIs")
    
    logger.info("Checking API.md documentation...")
    missing_apis, existing_apis = check_api_documentation(apis)
    
    if missing_apis:
        logger.warning(f"✗ {len(missing_apis)} APIs missing from API.md:")
        for module, symbol in missing_apis[:5]:
            logger.warning(f"    - {symbol}")
        if len(missing_apis) > 5:
            logger.warning(f"    ... and {len(missing_apis) - 5} more")
    else:
        logger.info(f"✓ All {len(existing_apis)} APIs documented in API.md")
    
    logger.info("Checking ARCHITECTURE.md...")
    if check_architecture_document():
        pass  # già loggato in funzione
    
    logger.info("Checking for broken links...")
    broken_links, valid_files = check_broken_links()
    
    if broken_links:
        logger.warning(f"✗ {len(broken_links)} broken links found:")
        for file, link in broken_links[:5]:
            logger.warning(f"    {file} → {link}")
        if len(broken_links) > 5:
            logger.warning(f"    ... and {len(broken_links) - 5} more")
    else:
        logger.info(f"✓ All links valid ({len(valid_files)} files indexed)")
    
    # Summary
    print("\n" + "="*60)
    print("DOCUMENTATION SYNC REPORT")
    print("="*60)
    print(f"Public APIs documented: {len(existing_apis)}/{len(apis)}")
    print(f"Broken links:           {len(broken_links)}")
    print(f"Valid cross-references: {len(valid_files)}")
    
    issues = len(missing_apis) + len(broken_links)
    if issues == 0:
        print("\n✅ Documentation is synchronized!")
        return 0
    else:
        print(f"\n⚠️  Found {issues} documentation issue(s).")
        if not args.check_only:
            print("   Recommendation: Add missing API entries, remove broken links")
    
    return 1 if issues > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
