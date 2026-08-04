# Task Status - 2026-08-04

## Summary

This snapshot separates:

- completed work
- partial work that is code-complete but not live-verified
- blocked work that depends on Google Cloud billing recovery

## Epic 1 - Technical Spike

### Story 1.1 - Establish official runtime test environment

- Done: official Antigravity CLI installed and verified locally.
- Done: official Python SDK installed and import verified.
- Done: auth prerequisites documented for local CLI and Vertex SDK.
- Done: versions and platform notes recorded.

### Story 1.2 - Verify session lifecycle

- Done: test workspace and repo fixture established.
- Done: CLI session creation verified.
- Done: CLI prompt submission verified.
- Done: CLI streamed bridge events verified.
- Done: CLI runtime session identifiers verified.
- Partial: SDK session lifecycle wired in code but live verification blocked by billing backend.

### Story 1.3 - Verify agent execution behavior

- Done: CLI file read/write behavior verified through local runs.
- Done: terminal command execution observed through CLI behavior and approval policy.
- Done: event observation implemented through bridge event tailing.
- Done: task cancellation verified for CLI path.
- Partial: task resumption remains minimal.
- Partial: attachments now wired in bridge + SDK adapter, not live-verified.

### Story 1.4 - Produce spike deliverables

- Done: `docs/technical_spike_report.md`
- Done: `docs/sdk_cli_capability_matrix.md`
- Done: `prototype/desktop_bridge_poc/`

## Epic 2 - Desktop Bridge Proof of Concept

### Story 2.1 - Scaffold bridge service

- Done: Python project scaffolded under `desktop_bridge/`
- Done: FastAPI and WebSocket entrypoints added
- Done: config loading added through env-driven runtime selection
- Done: basic structured logging added

### Story 2.2 - Define runtime abstraction

- Done: `AgentRuntimeAdapter` protocol created
- Done: bridge-owned session and event models created
- Done: CLI adapter implemented and verified
- Partial: official SDK adapter scaffolded for Vertex mode, blocked on live billing-enabled execution

### Story 2.3 - Implement authorized workspace handling

- Done: workspace registration model added
- Done: authorized path restriction added
- Partial: symlink/junction escape is guarded through resolved paths, but no dedicated regression tests yet
- Done: one authorized workspace configured for POC

### Story 2.4 - Implement session and message flow

- Done: create-session endpoint
- Done: send-message endpoint
- Done: stop-task endpoint
- Partial: resume-session remains minimal
- Done: polling and WebSocket streaming for normalized events
- Done: SDK-oriented token chunk plumbing added to bridge event model

### Story 2.5 - Implement first approval workflow

- Done: sensitive action policy for bridge-managed approval
- Done: approve/reject endpoints
- Done: local approval persistence
- Partial: native SDK hook interception scaffolded
- Blocked: live external-approval resume behavior for official SDK not verified yet

### Story 2.6 - Implement diff and audit outputs

- Done: changed-files endpoint
- Done: real Git diff endpoint
- Done: JSONL audit log
- Done: SQLite-backed audit log mirror

## Epics 3-8

- Not started intentionally, except for light groundwork related to attachments and policy enforcement inside Epic 2.
- Mobile, packaging, pairing, notifications, and production auth remain future work.

## Current Blocking Item

Live official SDK execution on project `agy-companion` is blocked by Google billing backend state:

```text
403: Lightning dunning decision is deny for project: projects/793680989680
```

## Next Unblock Sequence

1. Restore healthy billing for project `agy-companion`.
2. Re-run official SDK smoke test.
3. Verify attachments with a real file.
4. Verify SDK tool approval interception with a real command prompt.
5. Verify real token streaming from `ChatResponse.__aiter__()`.
6. Decide whether SDK runtime can fully replace CLI path or should remain optional.
