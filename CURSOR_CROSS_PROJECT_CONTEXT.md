# Cursor / AI Handoff — Cross-Project Context

**Purpose:** Attach this file (and the files listed below) when opening a **different** repository or a **new chat** so the assistant quickly matches Wilmer’s working agreements, stack, and standards.

**Student:** Wilmer Saenz — Data Engineering bootcamp — intermediate — **Windows 11 / PowerShell** — **`uv`** (not pip).

**Language:** Explanations to the student in **Spanish**; **code, comments, and repo files in English**.

---

## What to attach in the other project (priority order)

### Minimum (usually enough)

| File | Why |
|------|-----|
| `PROJECT4_CONTEXT.md` | Full profile, working style, Project 4 stack, coach Q&A, code standards summary |
| `CURSOR_CROSS_PROJECT_CONTEXT.md` | This checklist — forces the assistant to know what else to ask for |

### Architecture & brief

| File | Why |
|------|-----|
| `README.md` | Current architecture diagram, quick start, how the repo is meant to run |
| `Project4.md` | Official bootcamp brief, resources, stretch goals |
| `PLAN.md` | Milestones / plan if it exists |

### Runtime & config (no secrets)

| File | Why |
|------|-----|
| `docker-compose.yml` | Services, ports, health |
| `pyproject.toml` | Python version, dependencies |
| `.env.example` | Required env vars (**never** commit `.env`) |

### Progress log

| File | Why |
|------|-----|
| `study.md` | Spanish learning notes — what was built and why |

### dbt (when touching models/tests)

| Path pattern | Why |
|--------------|-----|
| `dbt_project/dbt_project.yml` | dbt project config |
| `dbt_project/profiles.yml` | **May contain secrets** — use placeholders in shared copies |
| `dbt_project/models/**/*.sql` | Models relevant to the task |
| `dbt_project/models/**/*.yml` | Sources, tests, docs |

### Duck Lake catalog (if lakehouse work)

| File | Why |
|------|-----|
| `ducklake/catalog.ducklake` | DuckLake catalog state (if present in repo) |

### Global Cursor rules (not inside this repo)

| File | Why |
|------|-----|
| `data-engineering-standards.mdc` | On this machine: `%USERPROFILE%\.cursor\rules\data-engineering-standards.mdc`. If the other project has no equivalent rule, **paste that file into the chat** or add it under the new repo’s `.cursor/rules/`. |

---

## Working style (short)

- Prefer **step-by-step** clarity; for **big design choices**, present options and trade-offs.
- **Commit after milestones**; avoid huge uncommitted batches.
- Academic project with **industry-style patterns**: frozen dataclasses for config, no hardcoded secrets, explicit SQL columns, retries/backoff where appropriate (see full rule file).

## Execution in terminal

**Project context file (`PROJECT4_CONTEXT.md`)** historically asked the assistant to only *show* commands. **If the user’s Cursor User Rules say the agent must run commands in the real environment, those rules take precedence.** When in doubt, follow what appears in **Cursor Rules** for that workspace/session.

---

## Files the assistant used to produce this handoff (example)

_so you can say: “attach the same files if missing”_

- `PROJECT4_CONTEXT.md`
- Repository scan: `**/*.{md,yml,yaml,toml}` at repo root and `dbt_project/`
- `Project4.md`, `README.md` (headers / architecture)
- `.env.example` (presence only)

If something above is not in the other project, **ask the user to add or `@`-reference** the corresponding path from this repository.
