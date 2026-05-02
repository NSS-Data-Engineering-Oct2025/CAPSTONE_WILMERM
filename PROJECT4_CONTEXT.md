# Project 4 — Context File for AI Assistant
## Read this before starting any work

---

## 1. Student Profile

**Name:** Wilmer Saenz  
**Username:** WILMERSAENZ81  
**Level:** Data Engineering bootcamp student — intermediate level  
**OS:** Windows 11, PowerShell  
**Package manager:** `uv` (NOT pip — always use `uv run` or `uv add`)  
**Editor:** Cursor IDE  
**Language preference:** Explanations in **Spanish**, all project files in **English**  

**Experience:**
- Completed Project 3 (COVID-19 pipeline): Python ingestion, Snowflake, dbt (staging/intermediate/marts), Streamlit dashboard, Airflow DAG skeleton
- Comfortable with: Git, pandas, loguru, snowflake-connector, dbt models and tests, dotenv
- NEW in Project 4: WebSockets, RabbitMQ, PostgreSQL, DuckDB, Metabase, real-time streaming

---

## 2. Working Style & Preferences

- **Step by step:** Wilmer prefers clear, visible steps — show what will run and why. If **Cursor User Rules** for the session say the agent must execute commands in the real environment, follow those rules; otherwise prefer confirming before destructive or unusual operations
- **Explanations in Spanish:** When explaining concepts or answering questions, use Spanish. Code, comments, and files stay in English
- **No surprises:** Always explain what a command does before asking to run it
- **Commit after each milestone:** Don't accumulate too many changes before committing
- **Ask before big decisions:** If there are multiple valid approaches, present the options with trade-offs instead of just picking one
- **Academic + industry balance:** This is an academic project that simulates industry standards. Don't over-engineer, but do apply real patterns (retry logic, dataclasses, no hardcoded secrets, etc.)

---

## 3. Project 4 Overview

**Project:** Real-Time Crypto Streaming & Lakehouse Analytics  
**Type:** Individual project (no teammate)  
**Duration:** ~4 days  
**Client scenario:** A boutique quant trading firm needs real-time crypto analytics without querying the production database directly

**Full data flow:**
```
Coinbase WebSocket
      ↓
Python Producer (websockets)
      ↓
RabbitMQ (message broker / buffer)
      ↓
Python Consumer (background worker)
      ↓
PostgreSQL — Bronze (raw JSON)
      ↓
dbt — Silver (cleaned) → Gold (aggregated: VWAP, moving avg)
      ↓
DuckDB Lakehouse (ducklake extension)
      ↓
Metabase Dashboard
```

---

## 4. Required Tech Stack (all new vs Project 3)

| Component | Technology | Notes |
|---|---|---|
| Data source | Coinbase WebSocket (market_trades channel) | Public, no auth required |
| Message broker | RabbitMQ | Runs in Docker |
| Landing DB | PostgreSQL | Runs in Docker, OLTP |
| Transformation | dbt (PostgreSQL adapter) | Medallion: Bronze/Silver/Gold |
| Lakehouse | DuckDB + ducklake extension | OLAP, isolated from Postgres |
| BI Dashboard | Metabase | Runs in Docker |
| Orchestration | Docker Compose (multi-container stack) | All services in one file |
| Language | Python 3.12+ | websockets, pika (RabbitMQ), psycopg2 |

---

## 5. Coach Guidance (from Q&A session)

These are clarifications and recommendations from the coach, extracted from a live Q&A session.

### 5.1 Recommended Order of Operations

The coach laid out a clear step-by-step approach:

1. **Step 1 — WebSocket to terminal:** Get the `websockets` library for Python connected to the Coinbase WebSocket. Just print data to the terminal. Once you see the stream flowing, you know it works.
2. **Step 2 — Filter + RabbitMQ:** Read the incoming data, filter for your chosen coin, and drop the filtered data into RabbitMQ. Getting data into a RabbitMQ queue is the first real "success" milestone.
3. **Step 3 — Consumer pulls from RabbitMQ:** With a queue populated, write the Python consumer/listener that pulls data out of RabbitMQ and inserts into PostgreSQL.
4. **Step 4 — DuckLake & the rest:** Everything after the consumer (dbt transforms, DuckDB lakehouse, Metabase) follows patterns similar to previous projects.

### 5.2 Pick ONE Coin

- **Do NOT subscribe to all coins.** The data volume is massive — without filtering, you can get ~480 messages in just 15 seconds.
- Pick a single coin to focus on (e.g., BTC-USD, ETH-USD, DOGE-USD, SOL-USD, XRP-USD — any one is fine).
- Data arrives sub-second per coin, so even one coin generates plenty of data to work with.

### 5.3 Two Filtering Strategies

The coach explained two valid approaches for filtering coins, each with trade-offs:

| Strategy | How it works | Best when |
|---|---|---|
| **Upstream (subscribe to specific coin)** | Pass the coin ticker directly in the WebSocket subscription message — only that coin's data arrives | You only ever need one coin; simplest approach |
| **Downstream (firehose + filter)** | Let all data come in from the WebSocket, then filter in your Python code before pushing to RabbitMQ | You want flexibility to add 4, 5, or 20 coins later without changing the WebSocket subscription |

**Key insight from coach:** "If you're only ever gonna do one coin, passing it upstream is fine. If you want to add 4 or 5 coins or 20 coins, filtering downstream is easier in the middle."

**Live subscription updates:** You can also update the WebSocket subscription mid-flight (e.g., start with BTC-USD, then add ETH-USD) without restarting the connection.

### 5.4 Filter In-Stream, Don't Batch-Then-Filter

> "Think about making sure you grab it in stream. Don't try to rest it and then filter yours out. You have the data coming in the WebSocket, look for a match there. And then drop the rest — don't even catch the rest, just grab it and stream and filter it out."

The idea: as each message arrives on the WebSocket, immediately check if it matches your coin. If yes, push to RabbitMQ. If no, discard it right away. Do NOT accumulate all messages and filter afterward.

### 5.5 WebSocket Ping-Pong Keep-Alive

- The Coinbase WebSocket has ping-pong endpoints that keep the session alive.
- The Python `websockets` library handles ping-pong automatically.
- Be aware they exist — they are different from the actual trade data messages.

---

## 6. Key Concepts to Know

**Why RabbitMQ?**  
The WebSocket produces data faster than PostgreSQL can write. RabbitMQ acts as a buffer — if Postgres goes down, messages queue safely in RabbitMQ instead of being lost.

**Why DuckDB separate from PostgreSQL?**  
Analysts running heavy aggregation queries (VWAP over hours of data) would lock tables in PostgreSQL and cause missed trades. DuckDB is a read-optimized OLAP database — same data, no lock conflicts.

**Medallion Architecture (dbt):**
- Bronze = raw JSON, untyped, as-is from Postgres
- Silver = parsed JSON, typed columns (timestamp, float for price/size), deduplicated by trade_id
- Gold = aggregated business metrics (1-minute windows, VWAP, trade count, high/low)

**VWAP = Volume Weighted Average Price:**
```
VWAP = SUM(price * size) / SUM(size)
```
The standard metric for a "fair price" in a time window.

---

## 7. Project 3 Lessons Applied to Project 4

| Lesson from P3 | How to apply in P4 |
|---|---|
| Use `@dataclass(frozen=True)` for config | Same pattern for DB, RabbitMQ, DuckDB config |
| Exponential backoff on API calls | Apply to WebSocket reconnect logic |
| Cursor context manager (`with conn.cursor()`) | Use everywhere in Postgres writes |
| DRY — extract shared logic | Single consumer base class, not copy-pasted handlers |
| `client_session_keep_alive` for long connections | WebSocket needs reconnect logic for same reason |
| Imports at top of file | Always |
| No `auto_create_table` — define schema explicitly | Create Bronze table DDL explicitly |

---

## 8. Resources

| Resource | URL |
|---|---|
| DuckLake Introduction (video) | https://youtu.be/Xkgox-DdumQ |
| Metabase/Superset to DuckLake (video) | https://youtu.be/WpzPfsjtibo |
| dbt + DuckLake + dlt demo repo | https://github.com/jeff-skoldberg-gmds/ducklake-demo |
| RabbitMQ Tutorials | https://www.rabbitmq.com/tutorials |
| Coinbase WebSocket Docs | https://docs.cdp.coinbase.com/exchange/websocket-feed/overview |
| Python websockets library | https://websockets.readthedocs.io/en/stable/intro/index.html |
| DuckLake extension for DuckDB | https://ducklake.select/docs/stable/duckdb/introduction |

---

## 9. Additional Notes from Project4.md

- **S3 for Parquet storage:** You can use S3 to store parquet files for DuckLake, and use a DuckDB file for the catalog. The DuckDB catalog file can be committed to the repo to share the lakehouse.
- **Stretch goal:** Add Airflow on top of dbt to automate the entire pipeline (if time permits).
- **Presentation (updated per coach Q&A):** NO slide deck required. The presentation is informal:
  1. **Live Metabase dashboard:** Spin up Metabase and walk through the dashboard — show the different questions/visuals and explain them.
  2. **Short pipeline video:** A pre-recorded, edited video (~1–2 minutes) showing the pipeline working end-to-end (WebSocket → RabbitMQ → Postgres → dbt → DuckDB → Metabase).
- **Fault tolerance demo:** During presentation, demonstrate that RabbitMQ queues messages safely when Postgres is temporarily down.

---

## 10. Environment Setup

- **OS:** Windows 11 / PowerShell
- **Docker:** Docker Desktop installed and working (v28.5.1)
- **uv:** Installed and working
- **Snowflake account:** nfsqmyv-ce67328 (NOT used in Project 4 — this uses PostgreSQL)
- **New `.env` needed** for: PostgreSQL credentials, RabbitMQ credentials, DuckDB path, Coinbase symbols

---

## 11. Code Standards (from global Cursor rule: data-engineering-standards.mdc)

These standards apply automatically via a global Cursor rule (`alwaysApply: true`). Summary for quick reference:

| Area | Standard |
|---|---|
| **Error Handling** | Raise exceptions immediately — never return `-1`, `False`, or `0` to signal errors. Use `try/except` only at the top-level orchestrator. |
| **SQL** | No `SELECT *` — always list columns explicitly in every query, CTE, and dbt model. |
| **DRY** | If the same logic appears in 2+ places, extract to a shared function, module, or dbt macro. |
| **Configuration** | Use `@dataclass(frozen=True)` for all config classes. Never read `os.environ` outside `config.py`. |
| **Security** | All secrets in `.env`, never hardcoded. Provide `.env.example` with placeholders only. `.gitignore` must cover `.env`, `target/`, `logs/`, `dbt_packages/`, `__pycache__/`. |
| **Resource Management** | Always use context managers (`with conn.cursor() as cur`) for DB cursors/connections. |
| **Retry Logic** | Exponential backoff for all external API calls and database operations. |
| **Linting** | Run `ruff check .` before every commit. Fix all warnings — never suppress with comments. |
| **Git Hygiene** | Never commit `target/`, `logs/`, `dbt_packages/`, `.venv/`, `__pycache__/`, binaries, or large data files. |
| **dbt Conventions** | Staging = light cleaning only. Intermediate = joins/aggregations. Marts = business metrics (materialized as tables). Custom tests return rows that FAIL. |
| **Python Structure** | Imports at top of file. One concern per module. Docstrings on public functions. Use `pathlib.Path` for file paths. |
| **Loops** | Avoid bare `while True:` when exit is only via `break` — use an explicit loop condition or a named flag so termination is obvious in review (see full rule in `data-engineering-standards.mdc`). Exception: intentional infinite workers (WebSocket, queues) — document shutdown and avoid scattered breaks. |
| **Dependencies** | Pin minimum versions in `pyproject.toml` (e.g., `>=2.32`). Use `[dependency-groups]` for dev deps. |

---

## 12. Assistant Instructions

- Always start by reading this file before doing any work
- When in doubt about the working style, refer to section 2
- **Terminal / commands:** Prefer showing what will run and why (section 2). If the user’s **Cursor User Rules** require executing commands in the real environment (typical in this setup), those rules **override** “only show commands.”
- For new technologies (RabbitMQ, DuckDB, Metabase), explain the concept in Spanish before writing code
- Keep a `study.md` updated in Spanish explaining what has been built and why
- After each major milestone, remind the student to commit
- Check for linter errors after every file edit

---

## 13. Context for another Cursor project (handoff)

To continue the same working agreements in **another repository** or a **new chat**, use the portable checklist:

- **`CURSOR_CROSS_PROJECT_CONTEXT.md`** — prioritized list of files to attach or copy, plus notes on global rules and execution precedence.

### Files to attach when the assistant cannot “see” this repo

Use this order (minimum first):

| Priority | File(s) |
|----------|---------|
| Essential | `PROJECT4_CONTEXT.md`, `CURSOR_CROSS_PROJECT_CONTEXT.md` |
| Brief + how to run | `README.md`, `Project4.md`, `PLAN.md` (if present) |
| Infra & deps | `docker-compose.yml`, `pyproject.toml`, `.env.example` |
| Learning log | `study.md` |
| dbt | `dbt_project/dbt_project.yml`, relevant `models/**/*.sql` / `**/*.yml`; treat `profiles.yml` as **possibly sensitive** |
| Lakehouse | `ducklake/catalog.ducklake` (if working on DuckLake) |
| Global standards | User rule file `data-engineering-standards.mdc` (Windows: `%USERPROFILE%\.cursor\rules\data-engineering-standards.mdc`) — paste into chat or copy to `.cursor/rules/` in the other project |

### Files used to build/update this handoff (for transparency)

The assistant can ask for these if something is missing:

- `PROJECT4_CONTEXT.md`
- `CURSOR_CROSS_PROJECT_CONTEXT.md`
- `README.md`, `Project4.md`, `PLAN.md`
- `docker-compose.yml`, `pyproject.toml`, `.env.example`, `study.md`
- `dbt_project/**` as needed for the task
- `%USERPROFILE%\.cursor\rules\data-engineering-standards.mdc` (or equivalent)
