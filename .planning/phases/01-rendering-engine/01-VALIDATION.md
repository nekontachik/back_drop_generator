---
phase: 1
slug: rendering-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-02
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| **Config file** | None — Wave 0 creates pyproject.toml [tool.pytest.ini_options] |
| **Quick run command** | `cd backend && uv run pytest tests/ -x --timeout=30` |
| **Full suite command** | `cd backend && uv run pytest tests/ -v --timeout=120` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && uv run pytest tests/ -x --timeout=30`
- **After every plan wave:** Run `cd backend && uv run pytest tests/ -v --timeout=120`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 1 | INP-01 | integration | `pytest tests/test_api.py::test_generate_returns_job_id -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | INP-02 | unit | `pytest tests/test_api.py::test_bpm_validation -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | VFX-01 | unit | `pytest tests/test_effects.py::test_tunnel_renders -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | VFX-02 | unit | `pytest tests/test_effects.py::test_fractal_renders -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | VFX-03 | unit | `pytest tests/test_effects.py::test_particles_renders -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | VFX-04 | unit | `pytest tests/test_effects.py::test_plasma_renders -x` | ❌ W0 | ⬜ pending |
| TBD | 02 | 2 | RND-01 | unit | `pytest tests/test_seamless.py -x` | ❌ W0 | ⬜ pending |
| TBD | 02 | 2 | RND-02 | integration | `pytest tests/test_encoder.py::test_output_codec -x` | ❌ W0 | ⬜ pending |
| TBD | 03 | 3 | RND-03 | integration | `pytest tests/test_api.py::test_sse_progress -x` | ❌ W0 | ⬜ pending |
| TBD | 03 | 3 | RND-04 | integration | `pytest tests/test_api.py::test_health_during_render -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/pyproject.toml` — project config with [tool.pytest.ini_options]
- [ ] `backend/tests/conftest.py` — shared fixtures (FastAPI test client, temp render dir)
- [ ] `backend/tests/test_api.py` — endpoint tests for INP-01, INP-02, RND-03, RND-04
- [ ] `backend/tests/test_effects.py` — renders each effect at 480p, asserts shape + dtype
- [ ] `backend/tests/test_seamless.py` — pixel diff test per effect
- [ ] `backend/tests/test_encoder.py` — ffprobe validates H.264 output
- [ ] `backend/tests/test_loop_math.py` — frame count and phase calculations
- [ ] `backend/tests/test_prompt_mapper.py` — keyword matching correctness
- [ ] Framework install: `uv add --dev pytest pytest-asyncio httpx`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual quality of effects | VFX-01-04 | Subjective visual quality cannot be automated | Render each effect at 480p, visually inspect for obvious artifacts |
| Beat sync perception | VFX-01-04 | Human perception of "on-beat" feel | Render at 120 BPM, play video, verify pulses feel aligned to beat |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
