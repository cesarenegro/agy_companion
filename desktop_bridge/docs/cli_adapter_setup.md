# CLI Adapter Setup

The current Desktop Bridge adapter can use the verified local `agy.exe agentapi` surface.

## Required environment variables

```text
ANTIGRAVITY_CLI_PATH
ANTIGRAVITY_LS_ADDRESS
ANTIGRAVITY_CSRF_TOKEN
ANTIGRAVITY_CONVERSATION_ID
```

Only `ANTIGRAVITY_LS_ADDRESS` and `ANTIGRAVITY_CSRF_TOKEN` are strictly required for the adapter to activate.

## Fast discovery on Windows

Use this script to inspect active Antigravity language server processes and extract candidate values:

```powershell
powershell -ExecutionPolicy Bypass -File .\desktop_bridge\scripts\find_antigravity_servers.ps1
```

The script returns JSON including:

- `recommendedLsAddress`
- `csrfToken`
- `workspaceId`
- `extensionServerPort`
- full `commandLine`

Example setup from one discovered process:

```powershell
$env:ANTIGRAVITY_LS_ADDRESS = '127.0.0.1:59102'
$env:ANTIGRAVITY_CSRF_TOKEN = '<token>'
$env:ANTIGRAVITY_CONVERSATION_ID = '<conversation-id>'
```

Defaults:

- `ANTIGRAVITY_CLI_PATH` defaults to:
  - `C:\Users\user\AppData\Local\agy\bin\agy.exe`

Optional:

- `ANTIGRAVITY_CONVERSATION_ID`
  - provides a default conversation id for bridge sessions when the request does not pass one explicitly.

## Current behavior

- `create_session`
  - reuses an existing conversation id passed in `options.conversation_id` or `ANTIGRAVITY_CONVERSATION_ID`
- `send_message`
  - calls `agy.exe --print --output-format=json --conversation=<id> "<message>"`
  - returns captured response text to the bridge caller
- `stop_task`
  - sends the literal message `stop` to the same conversation

## Known limitations

- no automatic new-conversation flow yet
- no programmable approval resolution yet
- no attachment forwarding yet
- no response stream wiring yet
- LS address selection is still heuristic when multiple Antigravity server processes are active
