# BACKLOG_V1_0

Build: `0.7.5-planning`

This backlog contains only remaining work required by MASTER DESIGN V1.0 or already recorded audits. It intentionally excludes new ideas and V1.1/V2.0 enhancements.

## Must Complete Before V1.0

### 1. Full-text handoff from Document Library to Knowledge Engine

- Evidence: `docs/audit_build_0_5_lts/TECHNICAL_DEBT.md` TD-001 and `AI_AUDIT_08_MASTER_COMPLIANCE.md`.
- Current gap: Knowledge sync can fall back to title, document number, summary and keywords instead of full document text.
- Required outcome: Knowledge Engine indexes source document text with correct chunk/citation lineage.

### 2. User-facing AI Search workflow

- Evidence: MASTER DESIGN lists `Tim kiem AI`; `docs/BUILD_0_5_AI.md` says no AI Search UI; `modules/knowledge_engine/` has only a module marker.
- Current gap: Backend search/index layers exist, but the user workflow for AI Search is not complete.
- Required outcome: V1.0 AI Search workflow using existing service/repository boundaries, without chat or AI Assistant scope.

### 3. AI Draft final evidence-quality validation

- Evidence: AI Draft exists and uses Knowledge evidence; audit notes Knowledge quality depends on full-text handoff.
- Current gap: AI Draft can run, but source quality depends on the Knowledge ingestion fix.
- Required outcome: AI Draft evidence, outline, review and export remain human-gated and validated against full-text Knowledge data.

### 4. Advisory report completion

- Evidence: MASTER DESIGN lists `Bao cao tham muu`; task export and AI Draft exist, but dedicated V1.0 advisory report completion is not fully documented.
- Current gap: Reporting is partial across tasks/KPI/export and AI Draft.
- Required outcome: Complete only the advisory report outputs already implied by MASTER DESIGN V1.0.

### 5. Document Library UI polish for V1.0

- Evidence: audits flag direct `st.json` rendering in Document Library.
- Current gap: Some user-facing screens expose technical JSON.
- Required outcome: Replace technical debug display with user-readable review/detail presentation.

### 6. Path ownership safety in Document Library

- Evidence: `TECHNICAL_DEBT.md` TD-002.
- Current gap: Missing-file detection uses string prefix checks.
- Required outcome: Use safe path ownership checks before marking files deleted.

### 7. Final schema validation / migration recovery checklist

- Evidence: migration audit and architecture audit.
- Current gap: Migration runner is safe, but manual partial failure recovery is not formalized.
- Required outcome: Add final V1.0 schema validation or operational checklist without changing business workflow.

### 8. Final packaging and release workflow

- Evidence: MASTER DESIGN lists PyInstaller for final packaging.
- Current gap: No final packaging workflow is complete.
- Required outcome: Build and document the V1.0 offline distribution process.

### 9. V1.0 operator/user documentation

- Evidence: README and build docs exist, but final operating guide is not complete.
- Current gap: No final V1.0 guide covering init, backup, restore, indexing, review and export.
- Required outcome: One V1.0 operator guide aligned to existing workflows.

### 10. Final full-suite verification

- Evidence: tests currently pass, but final V1.0 must re-run after backlog fixes.
- Current gap: Release candidate verification not frozen.
- Required outcome: `python -m database.init_db` and `python -m pytest -q` pass on the V1.0 release branch.

## Explicitly Not In V1.0 Backlog

- Chatbot.
- AI Assistant.
- Hybrid Search beyond the V1.0 AI Search workflow.
- New business workflows not listed in MASTER DESIGN V1.0.
- Cloud API integration.
- New vector database dependency.
