# Implementation Plan

## Objective

Build a Flutter mobile companion for controlling an Antigravity agent running on an authorized desktop, without exposing repositories or credentials to the phone.

## Delivery Strategy

The brief is explicit: do not start with polished mobile UI. The first delivery is a desktop proof of concept that validates the real Antigravity integration surface.

## Phase 0 - Technical Spike

### Goal

Verify that the official Antigravity SDK and/or CLI can support the required remote-control workflow.

### Required outputs

- `docs/technical_spike_report.md`
- `docs/sdk_cli_capability_matrix.md`
- `prototype/desktop_bridge_poc/`

### Exit criteria

The spike is only complete when the team can prove or explicitly rule out:

- session creation;
- prompt submission;
- streaming output;
- observable tool or activity events;
- test-repo file modification;
- approved command execution;
- real diff generation;
- task stop or documented stop limitation;
- session restore or resume;
- Windows and macOS support status.

## Phase 1 - Desktop Bridge Core

### Goal

Create the first functional local bridge service that owns session lifecycle and event normalization.

### Scope

- FastAPI service;
- SQLite-backed metadata;
- workspace authorization model;
- runtime adapter interface;
- one runtime adapter implementation;
- session manager;
- WebSocket event streaming;
- structured logging;
- audit log foundation.

### Deliverable

A local bridge that can create a session, send a message, stream events, surface one approval flow, and expose Git diff data for one authorized workspace.

## Phase 2 - Security and Pairing

### Goal

Establish secure device-to-desktop trust before broader feature expansion.

### Scope

- QR pairing flow;
- one-time token exchange;
- device identity confirmation;
- secure token storage;
- device revocation;
- explicit workspace allowlist;
- path traversal and symlink-escape protection.

## Phase 3 - Flutter Core

### Goal

Ship a usable mobile control surface for the validated bridge features.

### Scope

- app shell and routing;
- secure storage;
- pairing;
- desktop list;
- workspace list;
- session list;
- chat and response streaming;
- reconnect and offline state handling.

## Phase 4 - Approvals and Changes

### Goal

Support safe intervention and trustworthy review of agent activity.

### Scope

- approval queue and policy display;
- biometric confirmation;
- changed-file list;
- real Git diff viewer;
- stop-task UI;
- session status transitions.

## Phase 5 - Attachments and Notifications

### Goal

Support realistic remote use while keeping the bridge controlled.

### Scope

- attachment upload and validation;
- temporary storage and cleanup;
- runtime forwarding for supported file types;
- push notifications for actionable events;
- resume and disconnect recovery.

## Phase 6 - Hardening and Packaging

### Goal

Prepare supported desktop and mobile test distributions.

### Scope

- token rotation;
- rate limiting;
- dependency audit;
- penetration-test checklist;
- tray/menu integration;
- autostart;
- Windows installer;
- macOS installer;
- TestFlight build;
- Google Play internal build.

## Architecture Decisions To Resolve Early

These are gating decisions and should be made from evidence gathered during the spike:

- SDK vs CLI as the primary runtime;
- event capture model for approvals and tool activity;
- packaging approach for the Python bridge;
- local-network-only first release vs relay-backed remote access;
- exact session persistence model exposed by the official runtime.

## Working Rules

- Do not invent Antigravity APIs, flags, or event names.
- Keep all runtime-specific code behind an adapter boundary.
- Keep the mobile app independent from any undocumented IDE GUI behavior.
- Treat Git diff, workspace access, and approvals as bridge-owned responsibilities.
