# ROADMAP_LOCK

Build: `0.7.5-planning`

This document freezes the V1.0 roadmap. It prevents scope creep between the current repository state and V1.0 completion.

## Locked Product Scope For V1.0

The V1.0 product scope is limited to the MASTER DESIGN V1.0 daily-use areas:

- Dashboard.
- Profile, roles, staff, work codes and KPI rules.
- Task management.
- Workspace Lite.
- Document drafting.
- Document Library.
- AI Search.
- AI Draft / advisory drafting with human approval.
- Advisory reports.
- Offline SQLite runtime.
- Final packaging and operating documentation.

## Locked Architecture

- Python.
- Streamlit.
- SQLite.
- MVC/module structure.
- Repository Pattern.
- Service Layer.
- Local/offline operation.
- AI remains advisory; user remains final decision maker.

## Locked Build Order To V1.0

1. Sprint A0: gap analysis and backlog freeze.
2. Full-text Knowledge handoff.
3. AI Search V1.0 user workflow.
4. AI Draft final validation after full-text handoff.
5. Advisory report completion.
6. UI polish and technical debt cleanup required for V1.0.
7. Packaging, operator guide and release verification.
8. V1.0 release.

## Frozen Out Of V1.0

The following are not allowed into V1.0 unless MASTER DESIGN V1.0 is formally amended:

- Chatbot.
- General AI Assistant.
- Agent workflows.
- New business modules.
- Cloud API dependency.
- Vector database dependency.
- Major architecture replacement.
- V1.1/V2.0 feature ideas.

## V1.1 Holding Area

Items already identified as useful but not required for V1.0 move to V1.1:

- Mature plugin lifecycle.
- Static type checker in CI.
- Schema validator automation beyond V1.0 release checklist.
- Vector search scalability beyond SQLite/Python scan.
- Broader UI indexing operations.
- Advanced content store/citation lineage refinements beyond V1.0 needs.

## Change Control

Any new request before V1.0 must be classified as one of:

- Required by MASTER DESIGN V1.0.
- Required to fix V1.0 correctness/release risk.
- Deferred to V1.1.

If it is not one of the first two, it does not enter the V1.0 backlog.
