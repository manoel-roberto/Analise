---
type: project
created: 2026-07-18
updated: 2026-08-25
---

# Technical Decisions

- Component metadata uses SemVer while the toolkit release keeps CalVer.
- `manifest.json` and `manifest.lock.json` must remain synchronized with component frontmatter.
- **Installed Toolkits**:
  - `vudovn/ag-kit` (Antigravity Kit): Managed in `.agents/` directory.
  - `github/spec-kit` (Spec Kit): Managed via `specify-cli` with `agy` integration.
  - `data-exploration-profiling`: Managed in `.agents/skills/data-exploration-profiling/SKILL.md` (v1.1.0) with statistical, visual EDA, and DuckDB profiling capabilities.
