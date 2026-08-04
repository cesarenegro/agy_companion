# Task List

## Epic 1 - Technical Spike

### Story 1.1 - Establish official runtime test environment

- Install the official Antigravity SDK.
- Install the official Antigravity CLI.
- document authentication prerequisites.
- Record exact versions, installation steps, and platform notes.

### Story 1.2 - Verify session lifecycle

- Create a test workspace and authorized repository fixture.
- Verify session creation.
- Verify prompt submission.
- Verify streamed output.
- Verify session identifiers returned by the runtime.
- Verify session persistence and restore behavior.

### Story 1.3 - Verify agent execution behavior

- Test file read behavior.
- Test file write behavior in a disposable repo.
- Test terminal command execution.
- Test whether tool or process events are observable.
- Test task cancellation.
- Test task resumption.
- Test attachment support.

### Story 1.4 - Produce spike deliverables

- Write `docs/technical_spike_report.md`.
- Write `docs/sdk_cli_capability_matrix.md`.
- Create `prototype/desktop_bridge_poc/`.
- Classify each tested capability as:
  - Verified working
  - Verified unavailable
  - Partially working
  - Not documented
  - Not tested

## Epic 2 - Desktop Bridge Proof of Concept

### Story 2.1 - Scaffold bridge service

- Create Python project structure under `desktop_bridge/`.
- Add FastAPI and WebSocket entrypoints.
- Add configuration loading.
- Add structured logging.

### Story 2.2 - Define runtime abstraction

- Create `AgentRuntimeAdapter` protocol in `desktop_bridge/app/runtime/base.py`.
- Define bridge-owned session, task, and event models.
- Implement SDK or CLI adapter selected from spike results.

### Story 2.3 - Implement authorized workspace handling

- Add workspace registration model.
- Restrict access to explicitly approved paths.
- Block path traversal and symlink escape.
- Add one authorized test workspace for POC use.

### Story 2.4 - Implement session and message flow

- Add create-session endpoint.
- Add send-message endpoint.
- Add stop-task endpoint.
- Add resume-session experiment.
- Add WebSocket streaming for normalized events.

### Story 2.5 - Implement first approval workflow

- Define sensitive action policy for POC.
- Capture or simulate one real approval gate using the validated runtime behavior.
- Add approve and reject endpoints.
- Persist approval records locally.

### Story 2.6 - Implement diff and audit outputs

- Add changed-files endpoint.
- Add real Git diff endpoint.
- Add audit-log persistence.

## Epic 3 - Desktop Bridge Productionization

### Story 3.1 - Add database and migrations

- Add SQLite schema.
- Add migrations for sessions, tasks, messages, approvals, uploads, and audit logs.

### Story 3.2 - Add pairing and auth

- Implement one-time pairing token flow.
- Implement QR payload generation.
- Implement device confirmation flow.
- Add token refresh and revocation.

### Story 3.3 - Add tray/menu integration

- Show online/offline status.
- Show active sessions.
- Show paired devices.
- Add pause remote access.
- Add open logs and settings.

## Epic 4 - Flutter Mobile Core

### Story 4.1 - Scaffold mobile app

- Create Flutter app under `mobile/`.
- Add routing, state management, networking, secure storage, and serialization foundations.

### Story 4.2 - Implement onboarding and pairing

- Welcome screen.
- QR pairing screen.
- Manual code fallback.
- Desktop fingerprint confirmation.

### Story 4.3 - Implement primary navigation flows

- Desktop list.
- Workspace list.
- Session list.
- Chat screen with streaming state.

### Story 4.4 - Implement reliability basics

- Reconnect handling.
- offline banners.
- persisted session metadata.

## Epic 5 - Review and Intervention Features

### Story 5.1 - Approval UX

- Approval list or badge state.
- Approval detail screen.
- Biometric confirmation.
- Approve once and reject actions.

### Story 5.2 - Change review UX

- Changed-file list.
- Unified diff viewer.
- refresh state.
- staged vs unstaged presentation if supported.

### Story 5.3 - Activity UX

- Timeline of commands, tests, file writes, and failures.
- concise event rendering for normalized bridge events.

## Epic 6 - Attachments, Notifications, Recovery

### Story 6.1 - Attachments

- File picker integration.
- MIME and size validation.
- temporary upload flow.
- retention cleanup.

### Story 6.2 - Notifications

- FCM integration.
- actionable notification routing.
- app-open handling from notifications.

### Story 6.3 - Recovery

- desktop disconnect handling.
- bridge restart recovery.
- mobile background and foreground recovery.

## Epic 7 - Security Hardening

### Story 7.1 - Policy enforcement

- command classification.
- approval expiration.
- blocked operation rules.
- secret access restrictions.

### Story 7.2 - Security validation

- traversal tests.
- replay-token tests.
- revoked-device tests.
- malformed-event tests.
- oversized-upload tests.
- unauthorized-workspace tests.

## Epic 8 - Release Readiness

### Story 8.1 - Desktop packaging

- validate Python packaging approach.
- produce Windows installer.
- produce macOS installer.
- verify autostart behavior.

### Story 8.2 - Mobile test distribution

- create TestFlight build.
- create Google Play internal test build.

## Suggested Order Of Execution

1. Complete Epic 1 before production bridge work.
2. Build only the POC subset of Epic 2 needed to satisfy the brief's first delivery.
3. Delay Epic 4 mobile work until the runtime integration is verified.
4. Expand to Epics 5 through 8 only after the bridge proves stable.
