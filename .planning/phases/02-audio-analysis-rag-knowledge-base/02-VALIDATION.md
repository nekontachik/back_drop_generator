---
phase: 2
slug: audio-analysis-rag-knowledge-base
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-02
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `backend/pyproject.toml` |
| **Quick run command** | `cd backend && python -m pytest tests/ -x -q --timeout=30` |
| **Full suite command** | `cd backend && python -m pytest tests/ -v --timeout=60` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && python -m pytest tests/ -x -q --timeout=30`
- **After every plan wave:** Run `cd backend && python -m pytest tests/ -v --timeout=60`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | AUD-01 | unit | `pytest tests/test_audio_analysis.py -k bpm_detection` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | AUD-02 | unit | `pytest tests/test_audio_analysis.py -k mood_analysis` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | AUD-04 | unit | `pytest tests/test_audio_analysis.py -k octave_correction` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | INP-03 | integration | `pytest tests/test_audio_upload.py -k upload` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | RAG-01 | unit | `pytest tests/test_rag_knowledge.py -k genre_docs` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | RAG-02 | integration | `pytest tests/test_rag_knowledge.py -k retrieval` | ❌ W0 | ⬜ pending |
| 02-XX-XX | XX | 2 | AUD-03 | integration | `pytest tests/test_bpm_visualization.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_audio_analysis.py` — stubs for AUD-01, AUD-02, AUD-04
- [ ] `backend/tests/test_audio_upload.py` — stubs for INP-03
- [ ] `backend/tests/test_rag_knowledge.py` — stubs for RAG-01, RAG-02
- [ ] `backend/tests/test_bpm_visualization.py` — stubs for AUD-03
- [ ] `backend/tests/conftest.py` — shared fixtures (test audio file, ChromaDB test collection)
- [ ] `backend/tests/fixtures/` — sample audio file for testing (~5s sine wave with beat)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| BPM visualization chart renders correctly | AUD-03 | Visual output verification | Upload audio, check response contains beat_times and energy arrays suitable for charting |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
