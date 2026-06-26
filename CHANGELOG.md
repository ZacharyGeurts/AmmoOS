# Changelog

All notable NEXUS-Shield changes. Historical `RELEASE-*.md` files remain in the repo archive.

## [10.0.1] — 2026-06-26

### Beta polish (Zachary reviewed)

- README trimmed: Well Wishes section, portable paths, panel quick-start
- GUI: personalized startup toast, Well Wishes banner, field.html warm landing
- Config: dedupe `NEXUS_I18N_DIR`, portable path comments (no operator-specific defaults)
- State hygiene: `.nexus-state/` gitignored; migration helper for repo-local state
- Integrity: manifest paths relative to install root; `nexus verify` on daemon boot
- CI: shellcheck + py_compile + editorial tests on push

## [10.0.0]

- Field plates rearchitecture, sense package meld, ZNEWOCR eye root, secure signal line