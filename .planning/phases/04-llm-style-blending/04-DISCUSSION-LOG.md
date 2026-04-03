# Phase 4: LLM Style Blending - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 04-llm-style-blending
**Areas discussed:** LLM model & integration, Prompt engineering & chain design, Fallback & validation

---

## LLM Model & Integration

| Option | Description | Selected |
|--------|-------------|----------|
| GPT-4o-mini via OpenAI (Recommended) | ~$0.15/1M tokens, fast, CLAUDE.md recommends | |
| Claude 3.5 Haiku via Anthropic | Similar price tier, strong structured output | ✓ |
| Multiple providers with fallback | Primary GPT-4o-mini, fallback Claude Haiku | |
| You decide | Claude picks | |

**User's choice:** Claude 3.5 Haiku via Anthropic

| Option | Description | Selected |
|--------|-------------|----------|
| LangChain LCEL chain | Prompt template + output parser, CLAUDE.md recommends | |
| Raw Anthropic Python SDK | Direct API calls, less abstraction, simpler | ✓ |
| You decide | Claude picks | |

**User's choice:** Raw Anthropic Python SDK

| Option | Description | Selected |
|--------|-------------|----------|
| Cache by prompt + genre + mood hash | Identical inputs skip LLM, saves cost | |
| No caching | Every request hits LLM, unique output | ✓ |
| You decide | Claude picks | |

**User's choice:** No caching

---

## Prompt Engineering & Chain Design

| Option | Description | Selected |
|--------|-------------|----------|
| Highly creative | Push parameters beyond RAG doc values | |
| Grounded creative | Interpolate within RAG values | ✓ |
| Conservative | Weighted selection from RAG docs | |
| You decide | Claude picks | |

**User's choice:** Grounded creative — interpolate within RAG values

**Prompt context (multiSelect):**
- [x] RAG-retrieved genre docs (required)
- [x] Audio mood vector + semantic labels
- [x] User's blend ratio
- [x] Available effect list + parameter ranges

**User's choice:** All four context types included

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — 1-2 sentence description | LLM returns params + creative blurb | ✓ |
| No — parameters only | Pure structured JSON | |
| You decide | Claude picks | |

**User's choice:** Yes — include creative description

---

## Fallback & Validation

| Option | Description | Selected |
|--------|-------------|----------|
| Retry once, then genre defaults | One retry, then fallback | ✓ |
| Fall back immediately | No retry, straight to defaults | |
| Return error to user | Show error, let user retry | |
| You decide | Claude picks | |

**User's choice:** Retry once, then fall back to genre defaults

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — deterministic fallback | Skip LLM if no API key, use prompt_mapper | ✓ |
| No — require API key | LLM mandatory | |
| You decide | Claude picks | |

**User's choice:** Yes — deterministic fallback mode

---

## Claude's Discretion

- Prompt template wording and structure
- Temperature setting
- Mood vector mapping approach
- Pipeline wiring details
- Blend ratio format
- LLM timeout duration
- Logging verbosity

## Deferred Ideas

None — discussion stayed within phase scope
