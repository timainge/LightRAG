# Roadmap: LightRAG (fork)

- **Date**: 2026-03-07
- **Target**: Open source contribution — maintain a clean upstream-contribution fork
- **Effort**: ~2–3 hours of housekeeping, then ongoing low-effort sync cadence

## Why This Target

This fork is a staging area for patches to the well-regarded HKUDS/LightRAG project
(25k+ stars). Tim has already landed multiple PRs upstream. The goal is to keep the
fork tidy and maximize contribution velocity, not to diverge or ship independently.

## Steps to Ship

### Phase 1: Fork Hygiene
- [ ] Add `.venv/` to `.gitignore` (committed venv inflates repo size)
- [ ] Move root-level `test.py`, `test_neo4j.py`, `test_chromadb.py` into `tests/`
- [ ] Add a minimal `tests/README.md` explaining how to run each test script
- [ ] Verify `.dev/` is in `.gitignore` (internal planning files shouldn't go upstream)

### Phase 2: Sync & Contribution Workflow
- [ ] Run `git fetch upstream && git merge upstream/main` to catch up with upstream
- [ ] Resolve any conflicts from the one-ahead `Update __init__.py` commit
- [ ] Tag a clean post-sync state: `git tag sync-YYYYMMDD`
- [ ] Document the sync + PR workflow in a short `CONTRIBUTING_FORK.md` (local only)

### Phase 3: Next Contribution
- [ ] Identify the next patch opportunity (review open upstream issues / Discord)
- [ ] Develop and test the fix on a feature branch in this fork
- [ ] Open a PR to `HKUDS/LightRAG` from the feature branch

## Claude Code Tooling

### Skills
- **claude-api**: Not directly applicable here, but useful if building a demo or
  integration script on top of LightRAG to validate a patch end-to-end.

### Plugins / MCP Servers
- **GitHub MCP server**: Speeds up tracking upstream issues, reviewing open PRs in
  HKUDS/LightRAG, and drafting PR descriptions without leaving the editor.

### Reference Material
- **arXiv:2410.05779**: The LightRAG paper — informs which components are
  architecturally core vs. implementation detail when evaluating patch scope.
- **upstream CHANGELOG / releases**: Tells you what landed recently so you don't
  duplicate effort or submit a patch for something already fixed.

## Success Criteria

- Fork is in sync with `upstream/main` with no stray committed artifacts (`.venv/`)
- Test scripts live under `tests/` and are runnable with a one-liner
- At least one additional PR opened (or merged) into `HKUDS/LightRAG`
