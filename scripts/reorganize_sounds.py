#!/usr/bin/env python3
"""Script di riorganizzazione file audio per sistema audio v3.4.0.

Rinomina e riorganizza file .ogg dalla struttura flat sounds/ alla nuova
struttura categorizzata sounds/default/{gameplay,ui,voice,ambient,music}/.

Usage:
    python scripts/reorganize_sounds.py
    
    Script esegue automaticamente da root del progetto.
    Crea backup in sounds_backup/ prima di modificare.

Version: 1.0
Author: Nemex81 + AI Assistant
Date: 2026-02-23
"""

import shutil
from pathlib import Path
from typing import Dict, Tuple

# Mapping COMPLETO: vecchio_nome -> (categoria, nuovo_nome)
SOUND_MAPPING: Dict[str, Tuple[str, str]] = {
    # === GAMEPLAY SOUNDS (8 file) ===
    "shuffle-cards-1.ogg": ("gameplay", "card_shuffle.ogg"),
    "shuffle-cards-2.ogg": ("gameplay", "card_shuffle_alt.ogg"),
    "sound1.ogg": ("gameplay", "card_flip.ogg"),
    "sound2.ogg": ("gameplay", "card_move.ogg"),
    "sound3.ogg": ("gameplay", "card_place.ogg"),
    "sound101.ogg": ("gameplay", "stock_draw.ogg"),
    "sound102.ogg": ("gameplay", "foundation_drop.ogg"),
    "sound103.ogg": ("gameplay", "tableau_drop.ogg"),
    
    # === UI SOUNDS (13 file) ===
    "sound11.ogg": ("ui", "navigate.ogg"),
    "sound12.ogg": ("ui", "navigate_alt.ogg"),
    "sound29.ogg": ("ui", "confirm.ogg"),
    "sound33.ogg": ("ui", "cancel.ogg"),
    "sound36.ogg": ("ui", "boundary_hit.ogg"),
    "sound53.ogg": ("ui", "invalid_move.ogg"),
    "sound55.ogg": ("ui", "error.ogg"),
    "sound58.ogg": ("ui", "menu_open.ogg"),
    "sound59.ogg": ("ui", "menu_close.ogg"),
    "sound61.ogg": ("ui", "button_click.ogg"),
    "sound62.ogg": ("ui", "button_hover.ogg"),
    "sound7.ogg": ("ui", "select.ogg"),
    "sound84.ogg": ("ui", "notification.ogg"),
    "sound111.ogg": ("ui", "focus_change.ogg"),
    
    # === VOICE SOUNDS (6 file) ===
    "1.ogg": ("voice", "victory_fanfare.ogg"),
    "welcome-eng.ogg": ("voice", "welcome_english.ogg"),
    "welcome-it.ogg": ("voice", "welcome_italian.ogg"),
    "solve.ogg": ("voice", "auto_solve.ogg"),
    "level.ogg": ("voice", "level_complete.ogg"),
    "speed.ogg": ("voice", "speed_mode.ogg"),
    
    # === AMBIENT SOUNDS (3 file) ===
    "stirring.ogg": ("ambient", "thinking_loop.ogg"),
    "arteries.ogg": ("ambient", "heartbeat_loop.ogg"),
    "2.ogg": ("ambient", "game_start_ambient.ogg"),
    
    # === MUSIC SOUNDS (5 file - tracce lunghe) ===
    "3.ogg": ("music", "ambient_music_01.ogg"),
    "4.ogg": ("music", "ambient_music_02.ogg"),
    "5.ogg": ("music", "ambient_music_03_calm.ogg"),
    "6.ogg": ("music", "ambient_music_04_upbeat.ogg"),
    "7.ogg": ("music", "ambient_music_05_extended.ogg"),
}


def reorganize_sounds(
    old_sounds_dir: Path = Path("sounds"),
    new_base_dir: Path = Path("sounds/default")
) -> None:
    """Riorganizza file audio dalla struttura flat alla nuova struttura categorizzata.
    
    Args:
        old_sounds_dir: Path alla cartella sounds/ flat attuale
        new_base_dir: Path base per la nuova struttura (sounds/default/)
    """
    print("="*70)
    print("🎵 RIORGANIZZAZIONE FILE AUDIO - Sistema Audio v3.4.0")
    print("="*70)
    
    # Verifica che old_sounds_dir esista
    if not old_sounds_dir.exists():
        print(f"❌ ERRORE: Directory {old_sounds_dir} non trovata!")
        print("   Assicurati di eseguire lo script dalla root del progetto.")
        return
    
    # === FASE 1: BACKUP ===
    backup_dir = Path("sounds_backup")
    if not backup_dir.exists():
        print(f"\n📦 Fase 1: Creazione backup in {backup_dir}/")
        shutil.copytree(old_sounds_dir, backup_dir)
        print(f"   ✅ Backup completato")
    else:
        print(f"\n📦 Fase 1: Backup già esistente in {backup_dir}/")
    
    # === FASE 2: CREAZIONE DIRECTORY STRUCTURE ===
    print(f"\n📁 Fase 2: Creazione struttura directory in {new_base_dir}/")
    categories = ["gameplay", "ui", "voice", "ambient", "music"]
    for category in categories:
        category_dir = new_base_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {category_dir}")
    
    # === FASE 3: MIGRAZIONE FILE ===
    print(f"\n🔄 Fase 3: Migrazione e rinomina file audio")
    print("-"*70)
    
    migrated = 0
    skipped = 0
    
    for old_name, (category, new_name) in SOUND_MAPPING.items():
        old_path = old_sounds_dir / old_name
        new_path = new_base_dir / category / new_name
        
        if old_path.exists():
            # Copia (non sposta) per sicurezza
            shutil.copy2(old_path, new_path)
            size_kb = old_path.stat().st_size // 1024
            print(f"✅ {old_name:25s} → {category:8s}/{new_name:30s} ({size_kb:4d} KB)")
            migrated += 1
        else:
            print(f"⚠️  {old_name:25s} → NON TROVATO (saltato)")
            skipped += 1
    
    # === FASE 4: CREAZIONE .gitkeep PER DIRECTORY VUOTE ===
    print(f"\n📌 Fase 4: Creazione .gitkeep per directory vuote")
    for category in categories:
        category_dir = new_base_dir / category
        files_in_dir = list(category_dir.glob("*.ogg"))
        if not files_in_dir:
            gitkeep = category_dir / ".gitkeep"
            gitkeep.touch()
            print(f"   ✅ {category}/.gitkeep (directory vuota)")
    
    # === REPORT FINALE ===
    print("\n" + "="*70)
    print("✅ RIORGANIZZAZIONE COMPLETATA!")
    print("="*70)
    print(f"📊 Statistiche:")
    print(f"   • File migrati:     {migrated}/{len(SOUND_MAPPING)}")
    print(f"   • File mancanti:    {skipped}/{len(SOUND_MAPPING)}")
    print(f"   • Backup salvato:   {backup_dir.absolute()}")
    print(f"   • Nuova struttura:  {new_base_dir.absolute()}")
    print()
    print(f"📁 Struttura finale:")
    print(f"   sounds/")
    print(f"     ├── default/")
    for category in categories:
        count = len(list((new_base_dir / category).glob("*.ogg")))
        print(f"     │   ├── {category}/ ({count} file)")
    print(f"     └── [file vecchi ancora presenti nella root sounds/]")
    print()
    print("🚨 IMPORTANTE:")
    print("   1. Verifica che tutti i file siano stati copiati correttamente")
    print("   2. Testa il gioco per confermare che i suoni funzionino")
    print("   3. Solo DOPO i test, elimina i file vecchi dalla root sounds/")
    print("   4. Commit con messaggio: 'refactor(assets): riorganizza file audio in struttura categorizzata'")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Esegui riorganizzazione
    reorganize_sounds()
