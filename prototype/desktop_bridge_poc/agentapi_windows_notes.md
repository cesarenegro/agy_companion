# AgentAPI Windows Notes

Date: 2026-08-04

## Verified launcher

The working launcher is:

`C:\Users\user\AppData\Local\agy\bin\agy.exe`

The batch wrapper in:

`C:\Users\user\.gemini\antigravity-cli\bin\agentapi.bat`

delegates to that executable.

## Verified subcommands

```text
agentapi get-conversation-metadata <conversation_id>
agentapi new-conversation [--model=<flash_lite|flash|pro>] [--title=<title>] [--profile=<profile>] <prompt>
agentapi send-message [--title=<title>] <recipient_id> <content>
```

## Required environment

The tested local API call required:

```text
ANTIGRAVITY_LS_ADDRESS
ANTIGRAVITY_CSRF_TOKEN
```

## Verified working call

PowerShell example:

```powershell
$env:ANTIGRAVITY_LS_ADDRESS = '127.0.0.1:59102'
$env:ANTIGRAVITY_CSRF_TOKEN = '...'
& 'C:\Users\user\AppData\Local\agy\bin\agy.exe' agentapi send-message 3b3f5781-2aa9-4cfb-83a5-f38b2616ae30 "Reply with only: api message ok"
```

Observed result:

```json
{
  "response": {
    "sendMessage": {
      "recipientId": "3b3f5781-2aa9-4cfb-83a5-f38b2616ae30",
      "content": "Reply with only: api message ok"
    }
  }
}
```

## Known blockers

- `get-conversation-metadata` returned `trajectory not found` for tested IDs on the selected server instance.
- `new-conversation` reached the server but failed with `project_id is required when providing project_env_config`.
- Server selection appears tied to the specific active language server instance and workspace/project routing.
