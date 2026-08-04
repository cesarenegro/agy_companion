# SDK / CLI Capability Matrix

Status: pending execution

| Capability | SDK | CLI | Notes |
|---|---|---|---|
| Install and authenticate | Partially working | Verified working | SDK blocked by missing Python at initial check; CLI manually installed and launched successfully on Windows on 2026-08-04 |
| Create session | Not tested | Partially working | `agentapi new-conversation` exists, but tested call on 2026-08-04 failed with `project_id is required when providing project_env_config` |
| Submit prompt | Not tested | Verified working | Interactive terminal prompt accepted and executed user prompts |
| Stream output | Not tested | Partially working | Interactive streaming observed; `cli.log` shows `Streaming conversation ...`, but no documented structured bridge stream verified yet |
| Persist and restore session | Not tested | Verified working | Explicit resume via `agy --conversation=<id>` verified on Windows on 2026-08-04 |
| Expose runtime session identifier | Not tested | Partially working | Conversation IDs observed in history/logs and resume flag; API/server mapping still incomplete |
| Expose tool or activity events | Not tested | Partially working | User-visible blocks observed; local `cli.log` and `history.jsonl` also expose conversation and activity metadata |
| Modify files in workspace | Not tested | Verified working | Created `C:/Users/user/agy_test.txt` with expected content |
| Run terminal commands | Not tested | Verified working | Executed `dir` successfully |
| Support approval interception | Not tested | Partially working | CLI surfaced a tool confirmation and logged approval rejection/permission denial, but no programmable interception model verified |
| Stop running task | Not tested | Verified working | `stop` was accepted and user indicated expected behavior |
| Resume task or session | Not tested | Verified working | Conversation resume via `--conversation=<id>` verified; task resume semantics beyond conversation restore still not separately verified |
| Local programmable API | Not tested | Partially working | `agentapi` verified; `send-message` works with `ANTIGRAVITY_LS_ADDRESS` + `ANTIGRAVITY_CSRF_TOKEN` |
| Accept attachments | Not tested | Not tested | |
| Run on Windows | Not tested | Verified working | CLI launched and executed prompts on Windows |
| Run on macOS | Not tested | Not tested | SDK column for native support, CLI column for runtime support |
| Package inside bridge distribution | Not tested | Not tested | |
| Redistribution allowed | Not tested | Not tested | |
