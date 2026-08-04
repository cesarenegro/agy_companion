# Technical Spike Report

Status: in progress

This document will record verified behavior for the selected official Antigravity SDK and CLI versions.

## Current findings

Date checked: 2026-08-04
Platform checked: Windows 11 workspace environment

### Environment readiness

- Python runtime in PATH: Verified unavailable at initial check
- Python launcher `py`: Verified unavailable at initial check
- Antigravity CLI binary `antigravity`: Verified unavailable at initial check
- Antigravity CLI binary `ag`: Verified unavailable at initial check
- Antigravity CLI installation after manual user setup: Verified working

### Notes

- `python --version` failed because `python` is not installed or not available in PATH.
- `py --version` returned `No installed Python found!`.
- `where.exe antigravity` returned no result.
- `where.exe ag` returned no result.
- The user then manually installed the Antigravity CLI and successfully launched it on Windows.

## Verified CLI behavior on Windows

### Installation and launch

Classification: Verified working

Observed behavior:

- Antigravity CLI launched successfully on Windows.
- The CLI reported version `1.1.10`.
- The visible model at launch was `Gemini 3.6 Flash (High)`.

### Prompt submission

Classification: Verified working

Observed behavior:

- The CLI accepted direct natural-language prompts from the terminal prompt and executed them.

### File modification behavior

Classification: Verified working

Observed behavior:

- Prompt used: create a file named `agy_test.txt` containing exactly `hello from antigravity`.
- The CLI created `C:/Users/user/agy_test.txt`.
- The CLI rendered a structured activity block showing the file creation action.

### Terminal command behavior

Classification: Verified working

Observed behavior:

- Prompt used: run the command `dir`.
- The CLI executed the command successfully.
- The CLI rendered a structured activity block labeled `Bash(dir)`.
- Output was summarized back to the user.

### Tool or activity event availability

Classification: Partially working

Observed behavior:

- The CLI visibly exposes structured activity blocks such as `Create(...)`, `Bash(dir)`, and `Read(...)`.
- This confirms observable tool/activity rendering in the interactive CLI.
- Local CLI files also expose evidence of machine-usable metadata:
  - `history.jsonl` records prompt display text, workspace path, timestamps, and `conversationId`;
  - `cli.log` records conversation creation, conversation switching, streaming start, user input handling, and some tool confirmation events.
- Example observed log behaviors on 2026-08-04 included:
  - `Created conversation ...`
  - `Streaming conversation ...`
  - `Surfacing tool confirmation: "Bash" ...`
  - permission check failures and user-denied command confirmations
- It is still not verified whether Google documents these logs as a stable integration surface. For now they are implementation evidence, not a contractual API.

### Task cancellation

Classification: Verified working

Observed behavior:

- The user issued `stop`.
- The CLI responded with a stop acknowledgement stating that it was stopping tasks.
- User follow-up indicated the cancellation test behaved as expected.

### Approval and permission behavior

Classification: Partially working

Observed behavior:

- The CLI surfaced an approval request before attempting at least one sensitive command.
- `cli.log` recorded:
  - tool confirmation surfacing for `Bash`;
  - explicit user approval rejection state;
  - permission-manager denial for the rejected command.
- This is evidence that the CLI has a real permission and confirmation layer.
- It is not yet verified how, or whether, these approvals can be intercepted and resolved programmatically from a custom bridge.

### Local agent API behavior

Classification: Partially working

Observed behavior:

- The installed launcher `C:\Users\user\AppData\Local\agy\bin\agy.exe` exposes an `agentapi` subcommand.
- Verified subcommands:
  - `get-conversation-metadata <conversation_id>`
  - `new-conversation [--model=...] [--title=...] <prompt>`
  - `send-message [--title=...] <recipient_id> <content>`
- `agentapi` requires:
  - `ANTIGRAVITY_LS_ADDRESS`
  - `ANTIGRAVITY_CSRF_TOKEN`
- The correct token variable was verified as `ANTIGRAVITY_CSRF_TOKEN`.
- A working API call was verified on Windows on 2026-08-04:
  - `agy.exe agentapi send-message 3b3f5781-2aa9-4cfb-83a5-f38b2616ae30 "Reply with only: api message ok"`
  - when invoked with:
    - `ANTIGRAVITY_LS_ADDRESS=127.0.0.1:59102`
    - `ANTIGRAVITY_CSRF_TOKEN=<token from active language server process>`
- `get-conversation-metadata` against tested conversation IDs returned `trajectory not found` on the selected server instance.
- `new-conversation` reached the server but failed with:
  - `project_id is required when providing project_env_config`

Interpretation:

- A programmable local API surface exists and is callable from the CLI launcher.
- `send-message` is the first verified operation suitable for bridge automation.
- Conversation lookup and new conversation creation still require correct server/project routing.

### Session continuity and restore

Classification: Verified working

Observed behavior:

- After closing and reopening the CLI normally, a fresh session did not automatically recover prior conversational context.
- The CLI surfaced an explicit resume command:
  - `agy --conversation=ac752527-ed0e-48d1-91b2-0cca3b189dc9`
- After reopening with that conversation identifier, the CLI correctly recalled prior actions in the same conversation, including:
  - prior file verification of `agy_test.txt`;
  - creation and cancellation flow around `long_task_test.txt`;
  - transcript-aware summary of earlier actions such as listing files, creating `agy_test.txt`, running `dir`, and stopping.
- This is evidence of explicit conversation restore via conversation ID rather than implicit conversational memory on plain restart.

### Filesystem persistence across restarts

Classification: Verified working

Observed behavior:

- A file created before closing the CLI remained present and readable after the CLI was reopened.

## Current interpretation

The Windows CLI surface appears promising for the Desktop Bridge spike because it can already:

- accept prompts;
- write files;
- run shell commands;
- expose user-visible action blocks;
- persist prompt/workspace/conversation metadata in local files;
- emit detailed local logs about conversation lifecycle and some permission events;
- stop tasks;
- inspect persisted workspace state after restart.

However, the most important unanswered production questions remain:

- whether the CLI offers a documented headless or machine-readable event stream;
- whether approvals are interceptable in a controlled way;
- how to map Desktop Bridge sessions to the correct local server instance and conversation identifiers programmatically;
- whether attachments are supported in a way the Bridge can safely automate.

## Required classification

Each capability must be marked as one of:

- Verified working
- Verified unavailable
- Partially working
- Not documented
- Not tested

## Capabilities to verify

- installation process
- authentication process
- session creation
- prompt submission
- streamed output
- conversation persistence
- session identifiers
- tool-call or activity event availability
- file modification behavior
- terminal command behavior
- permission and approval interception
- task cancellation
- task resumption
- attachment support
- Windows support
- macOS support
- packaging feasibility
- license and redistribution constraints
- rate limits or account limitations
- desktop offline behavior
- runtime crash behavior
