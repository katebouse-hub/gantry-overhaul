
# Important Changes

Summary
- Prevent pydantic validation errors by not emitting empty `TextMessageContentEvent.delta` values.

Files to change
- `pydantic-model/.venv/lib/python3.12/site-packages/pydantic_ai/ag_ui.py`

Problem
- The AG-UI adapter emits `TextMessageContentEvent` with an empty string `delta` (``""``).
- Pydantic validation for `TextMessageContentEvent.delta` requires a non-empty string (length >= 1), causing a `ValidationError` and aborting the SSE stream.

Change to make
- In `_handle_model_request_event`, within the `PartDeltaEvent` handling, only yield `TextMessageContentEvent` when `delta.content_delta` is truthy (non-empty).

Original snippet (approx):
```py
if isinstance(delta, TextPartDelta):
    yield TextMessageContentEvent(
        message_id=stream_ctx.message_id,
        delta=delta.content_delta,
    )
```

Replacement snippet:
```py
if isinstance(delta, TextPartDelta):
    # Guard against empty string deltas which fail Pydantic validation
    if delta.content_delta:
        yield TextMessageContentEvent(
            message_id=stream_ctx.message_id,
            delta=delta.content_delta,
        )
```

Rationale
- Empty string message chunks carry no information and should not be sent as `TextMessageContentEvent`, because pydantic requires non-empty `delta` values.
- This keeps behavior consistent with the `PartStartEvent` handling, which already checks `if part.content:` before sending a start content event.

Testing
- Restart the Python server (run `uvicorn` or your usual start command).
- Reproduce the interaction that previously caused the pydantic validation error. The error `String should have at least 1 character` should no longer appear.

Notes
- This is a minimal defensive fix. Consider opening an upstream issue or PR against `pydantic-ai` so the library handles empty deltas gracefully or documents the invariant.


