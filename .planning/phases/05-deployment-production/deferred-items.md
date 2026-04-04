# Deferred Items — Phase 05

## Pre-existing Test Failures (out of scope for 05-01)

### test_sse_progress and test_download_after_render

- **File:** backend/tests/test_api.py
- **Error:** `invalid literal for int() with base 16: ''` in `app/worker.py:100`
- **Root cause:** Hex color string with empty value being passed to `int(..., 16)` in the worker rendering pipeline
- **Status:** Pre-existing before Phase 05 — not introduced by 05-01 changes
- **Impact:** 2 of 102 tests fail; 100 pass
- **Action needed:** Fix hex color validation in worker.py before shipping
