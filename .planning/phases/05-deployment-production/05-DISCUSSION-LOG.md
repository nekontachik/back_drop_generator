# Phase 5: Deployment & Production - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 05-deployment-production
**Areas discussed:** Backend deployment (Railway), Frontend deployment (Vercel), Pre-generated gallery content

---

## Backend Deployment (Railway)

| Option | Description | Selected |
|--------|-------------|----------|
| Local filesystem with TTL cleanup | Simple, free, files lost on redeploy | ✓ |
| Cloud storage (R2/S3) | Persists across deploys, more complex | |
| You decide | Claude picks | |

**User's choice:** Local filesystem with TTL cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Full Dockerfile with ffmpeg + Python deps | Multi-stage build, self-contained, ~1-2GB | ✓ |
| Railway Nixpack auto-detect | Less control, less config | |
| You decide | Claude picks | |

**User's choice:** Full Dockerfile with ffmpeg + Python deps

| Option | Description | Selected |
|--------|-------------|----------|
| Re-seed on every startup (Recommended) | Genre docs re-seed from YAML on startup, ~1-2s | ✓ |
| Railway volume for persistence | Persistent volume, avoids re-seeding | |
| You decide | Claude picks | |

**User's choice:** Re-seed on every startup

---

## Frontend Deployment (Vercel)

| Option | Description | Selected |
|--------|-------------|----------|
| Environment variable (NEXT_PUBLIC_API_URL) | Set in Vercel dashboard, standard pattern | ✓ |
| Hardcoded with env override | Default in code, env var overrides | |
| You decide | Claude picks | |

**User's choice:** Environment variable (NEXT_PUBLIC_API_URL)

| Option | Description | Selected |
|--------|-------------|----------|
| Default URLs are fine | .vercel.app / .up.railway.app, free | ✓ |
| Custom domain for frontend only | beatvisuals.dev or similar | |
| You decide | Claude picks | |

**User's choice:** Default URLs are fine

---

## Pre-Generated Gallery Content

| Option | Description | Selected |
|--------|-------------|----------|
| 4-6 examples | One per effect + 1-2 blends | ✓ |
| 8-10 examples | Two per effect, more variety | |
| You decide | Claude picks | |

**User's choice:** 4-6 examples

| Option | Description | Selected |
|--------|-------------|----------|
| Git LFS in the repo | Always available, no external dep | ✓ |
| Public cloud storage (R2/S3) | CDN, faster loads, smaller repo | |
| Generated on first deploy | Self-contained but slow first deploy | |
| You decide | Claude picks | |

**User's choice:** Git LFS in the repo

---

## Claude's Discretion

- Dockerfile structure and base image
- Railway service config
- CORS origin format
- Health check config
- Git LFS setup
- Gallery example combinations
- Vercel build settings
- Production logging

## Deferred Ideas

None — discussion stayed within phase scope
