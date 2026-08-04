# Desktop Bridge POC

Local proof of concept for the Antigravity Mobile Companion desktop bridge.

Current scope:

- FastAPI service scaffold;
- runtime adapter boundary;
- session and event models;
- workspace authorization foundation;
- REST and WebSocket endpoints for the technical spike;
- CLI-backed session bootstrap, messaging, git-status, diff, audit, and bridge-managed approval flow;
- official SDK adapter scaffold for Vertex-backed attachments, policy hooks, and token streaming.

## Runtime Selection

The bridge selects a runtime in this order:

1. `ANTIGRAVITY_RUNTIME=antigravity_cli`
2. `ANTIGRAVITY_RUNTIME=official_sdk`
3. auto-detect CLI if `ANTIGRAVITY_LS_ADDRESS` and `ANTIGRAVITY_CSRF_TOKEN` exist
4. auto-detect official SDK if `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` exist
5. fallback to stub

## Current Status

- `antigravity_cli`: verified locally on Windows
- `official_sdk`: code path scaffolded and importable, but live execution remains blocked until Google Cloud billing clears on project `agy-companion`
