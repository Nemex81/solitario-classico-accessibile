# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 📝 CHANGELOG Writing Guidelines

### 🎯 Purpose

CHANGELOG.md is a **user-facing document** that answers:
- "What changed in this version?"
- "Is there a breaking change?"
- "What bugs were fixed?"

**Target Audience**: Users, contributors, maintainers scanning for updates.

**Philosophy**: *"Concise, scannable, user-focused. Technical details belong in commit messages."*

---

### 📊 Format Structure

#### Version Header
```markdown
## [X.Y.Z] - YYYY-MM-DD
```

**Rules**:
- Use **Semantic Versioning** (Major.Minor.Patch)
- Include release date in ISO format (YYYY-MM-DD)
- Link version to tag/release: `[X.Y.Z]` (anchor at bottom)

---

#### Change Categories

Group changes under these standard categories (use only relevant ones):

**➕ Added**: New features, capabilities, APIs
**🔄 Changed**: Changes in existing functionality (including breaking changes)
**🚫 Deprecated**: Features marked for future removal (with timeline)
**❌ Removed**: Features removed (breaking changes)
**🐛 Fixed**: Bug fixes
**🔒 Security**: Vulnerability fixes, security improvements

**Order**: Always use this category order for consistency.

---

### ✏️ Writing Rules

| DO ✅ | DON'T ❌ |
|-------|----------|
| **One line per change** (max 2 for breaking) | **No paragraphs/essays** (move to docs) |
| **User perspective** (what changed for user) | **No implementation details** ("refactored to use X pattern") |
| **Action verbs** (Added, Fixed, Improved, Changed, Removed) | **No vague descriptions** ("various improvements", "bug fixes") |
| **Include impact/benefit** ("reduced startup by 40%") | **No technical jargon** ("fixed race condition in async dispatcher") |
| **Mark breaking**: `**BREAKING**: renamed X → Y` | **No commit duplication** (verbose git format with WIP/closes) |
| **Link references**: (#234), (commit abc), (see docs/X.md) | **No tiny changes** (typo in comment, copyright year, code format) |

**Examples**:
```markdown
✅ Added score warning system with 4 verbosity levels.
✅ Fixed crash when rapidly switching panels. (#234)
✅ Improved TTS clarity for better screen reader compatibility.

❌ Refactored GameEngine to use state machine pattern. (internal detail)
❌ Fixed null pointer exception in GameEngine.java:234. (what did user see?)
❌ Various improvements. (too vague)
```

---

### 📏 Entry Length Guidelines

**Target per version**:
- **Patch (X.Y.Z)**: 3-8 lines total
- **Minor (X.Y.0)**: 8-15 lines total  
- **Major (X.0.0)**: 15-25 lines total (more breaking changes)

**Per change**:
- **Simple**: 1 line
- **Complex**: 2 lines (breaking change + migration hint)
- **Never**: 3+ lines (move to docs or commit message)

---

### 🎯 Examples

#### ✅ Good Example (Concise)

```markdown
## [2.6.0] - 2025-02-05

### Added
- Score warning system with 4 verbosity levels (Disabled, Minimal, Balanced, Complete).
- TTS announcements for score milestones at 100pt intervals.
- Settings control for warning level (arrows to cycle).

### Changed
- Improved TTS message clarity for score events.

### Fixed
- Fixed score calculation edge case when rapidly moving multiple cards.
```

**Why good**: Scannable in 10 seconds, user-facing only, clear categories, benefit implicit.

---

#### ❌ Bad Example (Too Verbose)

```markdown
## [2.6.0] - 2025-02-05

### Added

#### Score Warning System
We have implemented a comprehensive score warning system that allows
users to configure the verbosity of TTS announcements...
[continues for 3 more paragraphs with implementation details]
```

**Why bad**: Essay format, too long, implementation details, hard to scan. Belongs in docs/feature-guide.

---

### 🔗 Linking to Details

If a change needs explanation, link to external documentation:

```markdown
### Added
- Score warning system. (See docs/SCORE_WARNINGS.md for configuration guide)

### Changed
- **BREAKING**: Difficulty now uses enum instead of int. (See MIGRATION.md)
```

**External detail locations**:
- `docs/DETAILED_CHANGELOG.md` - Technical implementation notes
- `docs/MIGRATION.md` - Breaking change migration guides
- `docs/PLAN_*.md` - Feature planning documents
- Commit messages - Detailed technical changes
- PR descriptions - Discussion, screenshots, videos

---

### 🗓️ Unreleased Section

Keep an `[Unreleased]` section at the top for ongoing work:

```markdown
## [Unreleased]

### Added
- Hint system for suggesting next move (in development).

### Changed
- Improved card animation smoothness (experimental).
```

**Rules**:
- Update as features merge to main/development branch
- Move to versioned section on release
- Helps contributors know what's coming

---

### 🎯 Breaking Changes

**Always mark clearly with "BREAKING:" prefix**:

```markdown
### Changed
- **BREAKING**: Renamed `GameEngine.move()` → `GameEngine.move_card()`.
- **BREAKING**: Minimum Python version now 3.10 (was 3.8).

### Removed
- **BREAKING**: Removed deprecated `old_scoring_method()` (use `calculate_score()`).
```

**Optional**: Include quick migration hint
```markdown
- **BREAKING**: Settings file format changed to JSON (was INI). 
  Old settings auto-migrate on first launch.
```

---

### 🔢 Semantic Versioning Guide

**When to bump version**:

**MAJOR (X.0.0)**: Breaking changes
- API signature changes
- Removed features
- Behavior changes that break existing usage

**MINOR (0.X.0)**: New features (backwards compatible)
- New functionality
- Deprecations (not yet removed)
- Performance improvements

**PATCH (0.0.X)**: Bug fixes only
- Bug fixes
- Security patches
- Documentation fixes

---

### ✨ Special Cases

#### Security Fixes

```markdown
### Security
- Fixed path traversal vulnerability in save file loading. (CVE-2024-12345)
- Updated dependencies to patch known vulnerabilities.
```

**Rules**:
- Always use "Security" category
- Include CVE if applicable
- Be specific about impact (but don't include exploit details)

---

#### Deprecations

```markdown
### Deprecated
- `old_method()` is deprecated and will be removed in v3.0.0. Use `new_method()` instead.
- Python 3.8 support will be dropped in v2.8.0 (June 2025).
```

**Rules**:
- Include removal timeline
- Suggest replacement
- Keep in CHANGELOG until actually removed

---

#### Performance Improvements

```markdown
### Changed
- Improved game startup time by 40% through lazy loading.
- Reduced memory usage by 25% in large game states.
```

**Rules**:
- Include measurable improvement if significant (>10%)
- User-perceivable benefit
- Skip micro-optimizations (<5% gain)

---

## 📋 Template Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- [New features in development]

### Changed
- [Changes in progress]

---

## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description in one line.
- Another feature with clear user benefit.

### Changed
- Change description with reason if not obvious.
- **BREAKING**: Breaking change with migration hint.

### Deprecated
- Deprecated feature with removal timeline and replacement.

### Removed
- **BREAKING**: Removed feature (what and why).

### Fixed
- Bug description and user impact.
- Another fix with reference. (#issue)

### Security
- Security fix description. (CVE-YYYY-XXXXX)

---

## [Previous versions continue...]

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality  
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

---

**For detailed technical changes, see commit history or docs/DETAILED_CHANGELOG.md**

[Unreleased]: https://github.com/username/repo/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/username/repo/compare/vA.B.C...vX.Y.Z
[Previous]: https://github.com/username/repo/releases/tag/vA.B.C
```

---

## 🛠️ Workflow for Updating CHANGELOG

### During Development

1. **Add to [Unreleased]** as features merge:
   ```markdown
   ## [Unreleased]
   
   ### Added
   - Score warning system with 4 levels.
   ```

2. **Keep it updated** with each PR/commit that affects users

### On Release

1. **Move Unreleased to new version**:
   ```markdown
   ## [2.6.0] - 2025-02-05
   
   ### Added
   - Score warning system with 4 levels.
   ```

2. **Clear Unreleased section** (or keep for next features)

3. **Add comparison links** at bottom:
   ```markdown
   [2.6.0]: https://github.com/user/repo/compare/v2.5.0...v2.6.0
   ```

4. **Commit**: `docs(changelog): Release v2.6.0`

---

## ⚖️ Detailed vs Concise: Two-File Strategy

**Recommended**: Maintain two separate changelogs:

**1. `CHANGELOG.md` (Root)**: Concise, user-facing (1 line/change, user perspective, scannable in 2-3 min, public-facing)

**2. `docs/DETAILED_CHANGELOG.md` (Optional)**: Verbose, technical (implementation details, rationale, metrics, internal reference)

**Link**: `## [2.6.0] - 2025-02-05` **[See detailed notes](docs/DETAILED_CHANGELOG.md#260)**

**Benefits**: Professional public changelog + detailed archive for maintainers, no information loss.

---

## 📊 Metrics: Good CHANGELOG

Your CHANGELOG is good when:

- ✅ User can scan full version history in <5 minutes
- ✅ Each version entry readable in 10-30 seconds
- ✅ Breaking changes immediately obvious (BREAKING prefix)
- ✅ User understands "what changed for me"
- ✅ No need to read commit history for basic understanding
- ✅ Links to details available but not required

**Target lengths**:
- Patch release: 3-8 lines
- Minor release: 8-15 lines  
- Major release: 15-25 lines
- Full CHANGELOG: 500-1000 lines for mature project (2-3 years)

---

## 📝 Quick Reference Card

### The Golden Rules

1. **One line per change** (exceptions: complex breaking changes)
2. **User perspective** (not implementation details)
3. **Action verbs** (Added, Fixed, Improved, Changed, Removed)
4. **Mark breaking** (BREAKING: prefix in Changed/Removed)
5. **Link for details** (optional: #PR, see docs/X.md)
6. **Scannable** (user reads in seconds, not minutes)

### When in Doubt

Ask yourself:
- **Would a user care about this?** (Yes → include, No → skip)
- **Can I describe it in 1 line?** (Yes → good, No → too detailed, link to docs)
- **Is it user-facing?** (Yes → CHANGELOG, No → commit only)

---

## 🎯 Real-World Examples

### Django CHANGELOG Style

```markdown
## 4.2.1 - 2023-05-03

### Bugfixes
- Fixed a regression that caused crashes when using QuerySet.select_related().
- Prevented AdminSite.each_context() from failing if get_queryset() is overridden.
```

**Characteristics**: Concise, technical terms OK (Django audience), issue-focused.

---

### React CHANGELOG Style

```markdown
## 18.2.0 (June 14, 2022)

### React DOM
- Add useId hook for generating unique IDs. (@acdlite)
- Fix Safari not always triggering onFocus when switching tabs. (@gaearon)
```

**Characteristics**: Component-scoped, attribution, user impact clear.

---

### Keep a Changelog Example

```markdown
## [1.0.0] - 2017-06-20

### Added
- New visual identity by [@tylerfortune8].
- Version navigation.

### Changed
- Start using "changelog" over "change log" since it's the common usage.

### Removed
- Section about "changelog" vs "CHANGELOG".
```

**Characteristics**: Ultra-concise, category-first, credits optional.

---

## 🔗 Resources

- **Keep a Changelog**: https://keepachangelog.com/
- **Semantic Versioning**: https://semver.org/
- **Conventional Commits**: https://www.conventionalcommits.org/ (optional, for automation)
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github

---

## 📌 Template Metadata

**Template Version**: v1.1 (ottimizzato -19.5%)  
**Created**: 2026-02-16  
**Last Updated**: 2026-02-22  
**Standard**: Keep a Changelog v1.0.0  
**Maintainer**: AI Assistant + Nemex81  
**Philosophy**: "Concise, scannable, user-focused. Details in commits."

---

## 🎯 Uso Template

1. **Copia struttura** da § Template Structure
2. **Aggiungi versioni** (più recente in alto)
3. **Regola 1-line-per-change**, BREAKING prefix per breaking changes
4. **Aggiungi comparison links** in fondo
5. **Review**: User può scannare in <5 min? Se no, taglia.

**Workflow**: Aggiorna [Unreleased] ad ogni merge user-facing → On release: muovi a versioned section + aggiungi comparison links → Commit `docs(changelog): Release vX.Y.Z`

**Quality check**: Entries 1-2 righe ✓ User perspective ✓ Breaking marked ✓ Categorie ordinate (Added/Changed/Deprecated/Removed/Fixed/Security) ✓ SemVer ✓ Date ISO ✓ Links ✓

---

**End of Template**

**Keep it concise. Keep it scannable. Keep it user-focused. 📝**
