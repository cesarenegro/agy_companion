# Official SDK Setup

## Purpose

Use the official Antigravity SDK adapter when the bridge should talk to the Vertex-backed runtime instead of the local CLI transport.

## Required Environment

Set:

```powershell
$env:ANTIGRAVITY_RUNTIME='official_sdk'
$env:GOOGLE_CLOUD_PROJECT='agy-companion'
$env:GOOGLE_CLOUD_LOCATION='global'
```

Optional:

```powershell
$env:ANTIGRAVITY_MODEL='gemini-2.5-pro'
$env:ANTIGRAVITY_CONVERSATION_ID='<existing-conversation-id>'
$env:ANTIGRAVITY_SAVE_DIR='E:\Projects\ANTIGRAV FLUTTER COMPANION\desktop_bridge\data'
$env:ANTIGRAVITY_APP_DATA_DIR='E:\Projects\ANTIGRAV FLUTTER COMPANION\desktop_bridge\data'
```

## Install

```powershell
pip install -e .[sdk]
```

## Verified Local Facts

- `google-antigravity==0.1.9` imports successfully.
- `LocalAgentConfig` supports:
  - `workspaces`
  - `conversation_id`
  - `policies`
  - `hooks`
  - `vertex`
  - `project`
  - `location`
- `from_file(path)` exists for attachments.
- `ChatResponse.__aiter__()` streams raw text deltas.

## Current Blocker

As of `August 4, 2026`, live SDK execution on project `agy-companion` is still blocked by Google billing backend state:

```text
403: Lightning dunning decision is deny for project: projects/793680989680
```

This is not a bridge code error. Resume live verification after billing is healthy.
