# CLAUDE.md — EchoGlove project conventions

Project-specific guidance for Claude Code sessions on this repo. Inherits and adds to `~/Projects/CLAUDE.md`. The authoritative project plan is `docs/superpowers/specs/2026-05-12-echoglove-orchestration-design.md` — read it first.

## Builder context

- Total beginner with embedded hardware, strong Python, some C/C++.
- 5–8 hrs/week sustainable pace, bi-weekly milestones.
- Mac (Apple Silicon) only for development.
- Goal: learn embedded + perception. v1 = live hand pose in a Python viewer.

## Commit messages

No conventional-commit prefixes (no `feat:` / `chore:` / etc.). Title is imperative mood, under 50 chars.

**Match the message to what's being committed:**

- **Actual work** (code, firmware, fix, design decision, real progress) → short title + blank line + body explaining the *why*. Body wraps at ~72 chars.
- **Setup / admin / docs / notes / convention files** → one-line title is enough. Don't manufacture filler bodies.
- **Bootstrap or trivial commits** when the user asks (e.g. `init`) → whatever short form the user requests.

Example of a real-work commit:

```
Add Phase 0 firmware skeleton

First PlatformIO project: blink onboard LED, read button, print
counter over USB serial. Placeholder for the I2C sensor read that
gets filled in once Freenove kit contents are confirmed.
```

Example of an admin commit:

```
Add project CLAUDE.md
```

## Git operations

- Local commits are fine without confirmation when scoped to the current phase's work.
- **Never push to the remote without asking.** The repo is private at the user's preference; the user pushes.
- Never `--force` anything, never `git reset --hard` on uncommitted work, never amend committed history.
- Do not create new branches without asking — flat `main` history is fine for a solo project at this stage.

## Phased work discipline

- The project is decomposed into Phases 0–6 (see the orchestration design doc). Work in scope of the **current phase only**.
- Out-of-scope ideas go to `docs/phases/parking-lot.md`, not into the current phase's deliverables.
- Each phase has its own brainstorm → spec → plan → execute cycle. Do not start implementing a future phase ahead of its plan.
- Each phase ships only when its verification criteria in §6 of the orchestration doc are met. No subjective "looks fine."
- Two-week rule: if blocked > 2 weeks on a phase, re-scope or escalate. No infinite tunneling.

## Hardware safety

- The user is a beginner. Before any first power-on of new wiring, request a photo of the breadboard and sanity-check it against the wiring diagram.
- LiPo batteries are involved from Phase 3 onward. Treat any LiPo guidance as safety-critical: never recommend leaving a charging battery unattended, never recommend reverse-polarity-tolerant assumptions.

## Toolchain

- Firmware: PlatformIO (VS Code extension). Arduino framework for Phases 1–4; ESP-IDF for Phases 5–6.
- Pin exact library versions in `platformio.ini`. Treat it as a lockfile.
- Each phase gets its own subdir under `firmware/phaseN-<name>/` as a self-contained PlatformIO project.
- Host: Python 3.12 via [`uv`](https://github.com/astral-sh/uv). Single `host/pyproject.toml`.
- Host code lives under `host/echoglove/`. Tests under `host/tests/`. Notebooks under `notebooks/`.

## Documentation conventions

- Per-phase kickoff notes: `docs/phases/phaseN-kickoff.md`.
- Per-phase retros: `docs/phases/phaseN-retro.md`.
- BOMs with Amazon links and receipts: `hardware/bom-phaseN.md`.
- Wiring diagrams: `hardware/wiring/phaseN-<name>.{md,fzz,png}`.
- `STATE.md` at repo root: 3-line "where I left off" updated at the end of every working session.

## Sourcing

- Amazon-first for all parts.
- Two specialty parts (CH-101 ultrasonic, eventually DW3000 UWB) are allowed from SparkFun.
- Do not introduce new vendors without asking the user.

## What Claude should not do

- Buy parts on the user's behalf (cannot anyway, but also do not generate clickable purchase links presented as "I'll order this for you").
- Push to GitHub remote.
- Skip ahead on phase verification.
- Refactor or modify files outside the current phase's scope.
- Fully complete fill-in-the-blank firmware sections the user is meant to fill in for learning — leave them blank and explain what goes there.
