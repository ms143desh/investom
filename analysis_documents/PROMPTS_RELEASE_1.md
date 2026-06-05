# Investom — Release 1: Complete AI Build Prompts

> **How to use this document:**
> Each section is a self-contained prompt to give your AI coding assistant (Claude in Cursor IDE, or Claude.ai Projects).
> Work through prompts in order — each one builds on the previous. Do not skip prompts or reorder them.
> Prompts marked **[BLOCKING]** must be fully completed and verified before any subsequent prompt begins.
> No code is included here — these are instructions for your AI assistant to generate and explain.

---

## Release 1 Scope Summary

**Goal:** Get users to sign up, discover stocks, ask AI questions, and set basic price alerts.
**Timeline:** Weeks 1–5
**Modules:** Infrastructure + Auth, Module 1 (Discover — core), Module 5 (Ask AI — core), Module 8 (Smart Alerts — basic)

**What gets built in Release 1:**

- User authentication and onboarding with risk profile
- Stocks master database with 5,000+ NSE/BSE tickers
- Daily market data ingestion pipeline (OHLCV + corporate actions)
- Fundamentals data ingestion pipeline
- Stock search (name and ticker)
- Stock overview card
- Sector heatmap
- AI Stock Screener (natural language)
- Watchlist (add, remove, view price changes)
- Trending stocks widget
- Ask AI — global floating chat interface
- Ask AI — stock Q&A
- Ask AI — concept explainer
- Ask AI — stock comparison
- Smart Alerts — price above/below threshold
- Smart Alerts — in-app notification badge and panel

---

## Prompt 0 — Prerequisites, Decisions, and Environment Setup

**[BLOCKING] — Complete every item in this section before writing a single line of application code.**

---

### 0.1 Accounts and Services to Create

Before development begins, create accounts and verify access to all of the following services. Record all credentials in a secure vault (Doppler — see Section 0.6). Do not store any credentials in code, `.env` files committed to git, or any local notes file.

**Hosting and Infrastructure:**

- Vercel account — this is where the Next.js frontend will be deployed. Create a new project named `investom-frontend`. Connect it to your GitHub repository immediately so preview deployments work from day one.
- Railway account — this is where the Node.js API server will be deployed. Create a new project named `investom-api`. Note the Railway project ID.
- Modal.com account — this is where the Python AI microservices will run. Confirm you can deploy a basic Python function before proceeding.
- Supabase account — create a new project named `investom`. Note the project URL, **publishable key** (formerly anon key — safe to use in browser/client code), and **secret key** (formerly service role key — never expose to browser). Enable pgvector extension immediately after project creation (SQL: `create extension if not exists vector`). Enable Row Level Security on the database globally.
- Upstash account — create a Redis database named `investom-cache`. Select a region closest to your Railway deployment region for lowest latency.
- Cloudflare account — add your domain and configure the DNS to point at Vercel.
- Doppler account — create a project named `investom` with environments: `development`, `staging`, `production`.

**AI / LLM Services:**

> **Cost Strategy for Development:** During local development and early testing, use the free-tier options listed below. Switch to paid tiers only when deploying to staging/production or when free limits are exhausted. All services below are drop-in compatible with the same OpenAI-compatible API format unless noted.

**Primary LLM — Claude (Anthropic):**

- Anthropic account — create an API key. Note it as `ANTHROPIC_API_KEY`. Enable prompt caching on your account (required for cost optimisation). Set a usage alert at $50/month and a hard cap at $200/month.
- **Free alternative for development:** Google AI Studio (studio.google.com) provides Gemini 1.5 Flash free with generous limits (1,500 requests/day, 1M context). Use the OpenAI-compatible endpoint so you can swap back to Claude without code changes. Note the key as `GEMINI_API_KEY`. This is suitable for all Haiku-equivalent tasks during development.

**Embeddings and LLM Fallback — OpenAI:**

- OpenAI account — create an API key. Note it as `OPENAI_API_KEY`. This is used only for embeddings (`text-embedding-3-small`) and as an LLM fallback. Set a usage alert at $20/month.
- **Free alternative for embeddings:** Hugging Face Inference API (huggingface.co) provides the `sentence-transformers/all-MiniLM-L6-v2` embedding model free (no credit card required). Produces 384-dimension embeddings vs OpenAI's 1536 — acceptable for local development but switch to `text-embedding-3-small` before production for accuracy.
- **Free alternative for LLM fallback:** xAI Grok (x.ai/api) provides a free tier with `grok-3-mini` and `grok-2-mini` models. xAI uses the OpenAI SDK format with `base_url="https://api.x.ai/v1"` — swap `base_url` and `api_key` only, no other code changes. Note the key as `XAI_API_KEY`. Get it at console.x.ai with your X (Twitter) account. Use this as fallback instead of GPT-4o-mini during development to avoid OpenAI spend.
- **Free alternative for vector search (development only):** pgvector in Supabase free tier is already included — no separate service needed for R1 since we are using Supabase for vectors.

**Free Tier Summary Table:**

| Service | Free Tier Limit | Production Ready? |
|---------|----------------|-------------------|
| Google AI Studio (Gemini 1.5 Flash) | 1,500 req/day, 1M tokens/min | No — switch to Claude Haiku for production |
| xAI Grok (grok-3-mini) | Free tier available | No — switch to Claude Haiku for production |
| Hugging Face Inference API | Rate-limited, shared compute | No — switch to OpenAI embeddings for production |
| Supabase (pgvector) | Included in free tier | Yes — Supabase free tier is usable for early staging |
| Anthropic Claude 3.5 Haiku | No free tier — $0.80/1M input tokens | Yes — very cheap, use from staging onwards |
| OpenAI text-embedding-3-small | No free tier — $0.02/1M tokens | Yes — use from staging onwards |

**Market Data Services:**

> **Cost Strategy for Development:** All three free options below are sufficient to build and test every R1 feature. EODHD ($19/month) is only needed when you move to staging/production and need reliable bulk historical data for all 5,000+ stocks. Do not pay for EODHD until the data pipeline (Prompt 4) is ready to ingest it.

**Live Quotes, OHLCV, and Instruments List:**
- **yfinance (Python library) — primary market data source, no account or API key required.** Fetches NSE stock data by appending `.NS` suffix (e.g., `RELIANCE.NS`). Provides live/delayed quotes, full OHLCV history, and basic fundamentals for all NSE-listed stocks. Install via `pip install yfinance`. Used in all environments including production for R1 — it is sufficient for end-of-day data which is all R1 needs.
- **Note on yfinance reliability:** yfinance is unofficial (scrapes Yahoo Finance). It is stable for end-of-day data and has been reliable for years, but has no formal SLA. For R1 this is an acceptable tradeoff — upgrade to EODHD only if yfinance breaks or you need intraday data in a future release.
- **NSE India public JSON endpoints** (e.g., `https://www.nseindia.com/api/quote-equity?symbol=RELIANCE`) — use only as a fallback for live quote checks during development. No account needed but rate-limited by IP.

**Historical OHLCV and Fundamentals (Bulk Data):**

- EODHD account — subscribe to the All World plan ($19/month). Note the `EODHD_API_KEY`. Confirm you can fetch the NSE exchange instruments list before proceeding. **Required for production — covers full 5,000+ stock history and fundamentals.**
- **Free alternative for development (limited stocks):** Alpha Vantage free tier (alphavantage.co) provides daily OHLCV for individual stocks at 25 requests/day with no credit card. Sufficient to test the ingestion pipeline with 10–20 stocks before switching to EODHD. Note the key as `ALPHA_VANTAGE_API_KEY`. Does not cover Indian fundamentals — use only for OHLCV pipeline testing.
- **Free alternative for fundamentals (limited):** Ticker (ticker.finology.in) provides basic fundamentals for NSE stocks via their website. No official API, but structured data is accessible for manual fixture creation during development. Use this to build `__tests__/fixtures/` data only — not for production ingestion.
- **yfinance — primary source for all environments in R1.** Add `yfinance` to `pyproject.toml` as a regular (not dev-only) dependency. Use it in the backfill script, daily OHLCV worker, and fundamentals worker across all environments. Wrap in a provider abstraction so it can be swapped for EODHD in a future release without changing worker code.

**Corporate Actions and Exchange Reference Data:**

- BSE India Developer Portal — register at bseindia.com. No API key required for public endpoints but bookmark the base URLs for: corporate actions, quarterly results, annual reports, and bulk deals. **Free — always.**
- **Also free:** NSE's public CSV/JSON endpoints for index constituent lists (Nifty 50, Nifty 100, etc.) — available at nseindia.com/market-data/live-equity-market. Use these during the seed script (Prompt 4.1) to assign `market_cap_category` and `index_memberships` without any API key.

**Market Data Free Tier Summary:**

| Service | Free Tier | Coverage | Production Ready? |
|---------|-----------|----------|-------------------|
| yfinance (Python) | Free, no account | OHLCV + quotes + basic fundamentals for all NSE stocks | **Yes — primary source for R1** |
| NSE unofficial JSON | No account needed | Live quotes only | Dev fallback only — no SLA |
| Alpha Vantage | 25 req/day (free key) | OHLCV for individual stocks | No — too slow for 5,000 stocks |
| BSE Developer Portal | Free always | Corporate actions, filings | Yes |
| NSE index CSVs | Free always | Index constituents | Yes |
| **EODHD ($19/month)** | 14-day trial | Full historical + fundamentals for all NSE/BSE stocks | Optional — upgrade in R2 if yfinance is insufficient |

**Notifications:**

- Resend account — create an API key. Note it as `RESEND_API_KEY`. Create a sending domain and verify it with DNS. Create an email template for alert notifications.
- Firebase project — create a project named `investom`. Enable Cloud Messaging (FCM). Download the service account JSON — note it as `FIREBASE_SERVICE_ACCOUNT_JSON`.

**Monitoring and Code Quality:**

- Sentry account — create a project for Next.js and a separate project for Node.js. Note both DSN values.
- GitHub repository — create a private repository named `investom`. Set up branch protection rules: require pull requests on `main`, require at least one review, require status checks to pass before merge.

---

### 0.2 Technology Stack Decisions (Final, Non-Negotiable for R1)

These decisions are fixed for Release 1. Do not let your AI assistant suggest alternatives unless explicitly noted.

**Frontend:**

- Framework: Next.js 15 with App Router. Use TypeScript strict mode throughout. Every file must have explicit TypeScript types — no `any` types permitted.
- Styling: TailwindCSS v3. No inline styles. No CSS modules.
- Components: shadcn/ui. Run the shadcn init command and install: button, input, dialog, sheet, badge, card, dropdown-menu, toast, skeleton, tabs, scroll-area, separator, avatar, command (for search), tooltip.
- Charts: TradingView Lightweight Charts for the heatmap color grid. Recharts for all other charts (donut, bar, sparklines).
- State: TanStack Query v5 for all server state. Zustand for client-only state (watchlist UI state, chat panel open/closed, alert drawer open/closed). No Redux, no Context API for state that TanStack Query or Zustand can handle.
- Forms: React Hook Form with Zod schemas. Zod schemas are the single source of truth for form validation.
- Real-time: Supabase Realtime only. No Socket.io.
- HTTP client inside Next.js server components and route handlers: native `fetch` with Next.js caching directives.
- HTTP client inside client components: TanStack Query's `useQuery` and `useMutation`.

**Backend (Node.js / Fastify):**

- Language: TypeScript strict mode.
- Framework: Fastify v4. Use the Fastify plugin system — no Express-style middleware chains.
- ORM: Prisma v5. Database schema is the single source of truth — never write raw SQL that is not generated from migrations.
- Validation: Zod on every route's request body, query parameters, and path parameters. Reject any request that does not match the schema before it reaches business logic.
- Authentication: Supabase Auth (JWT). The Node.js server validates the JWT on every protected route. Never store session data server-side.
- Queue: BullMQ with Upstash Redis as the backing store.
- Environment: All environment variables read from `process.env` and validated at startup with a Zod schema. If any required variable is missing, the server must refuse to start and log the missing variable name clearly.

**Backend (Python / FastAPI):**

- Language: Python 3.11+.
- Framework: FastAPI. Use Pydantic v2 models for all request and response types.
- LLM SDK: Anthropic Python SDK (primary). OpenAI Python SDK (fallback and embeddings only).
- Data processing: pandas + numpy.
- Technical indicators: pandas-ta (not TA-Lib — no compilation required).
- Deployment: Modal.com. Each AI function is a separate Modal function with appropriate CPU/memory allocation.
- Environment: All secrets injected as Modal secrets at deploy time.

**Database:**

- Primary: PostgreSQL via Supabase.
- Cache: Upstash Redis.
- Vector: pgvector extension inside Supabase (not Pinecone).
- Migrations: Prisma Migrate only. Never alter tables directly in the Supabase SQL editor in production.
- Row Level Security: Must be enabled on every user-data table before any data is written.

---

### 0.3 Folder Structure Decisions

Decide and lock this folder structure before generating any code. Your AI assistant must generate all files within this structure.

```
investom/
├── apps/
│   ├── web/                        ← Next.js 15 frontend
│   │   ├── app/                    ← App Router pages and layouts
│   │   │   ├── (auth)/             ← Auth group: login, signup, onboarding
│   │   │   ├── (dashboard)/        ← Protected pages: discover, ask-ai, alerts
│   │   │   ├── stock/[ticker]/     ← Stock detail page (SSR)
│   │   │   ├── api/                ← Next.js API route handlers
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── ui/                 ← shadcn/ui components (auto-generated, do not edit)
│   │   │   ├── layout/             ← Header, Sidebar, Footer, GlobalChatButton
│   │   │   ├── auth/               ← SignupForm, LoginForm, OnboardingWizard
│   │   │   ├── discover/           ← StockOverviewCard, SectorHeatmap, Screener, Watchlist
│   │   │   ├── ask-ai/             ← ChatPanel, MessageBubble, ConversationHistory
│   │   │   └── alerts/             ← AlertPanel, AlertBadge, AlertForm
│   │   ├── lib/
│   │   │   ├── supabase/           ← Supabase client (browser + server)
│   │   │   ├── tanstack/           ← TanStack Query client and query key factory
│   │   │   ├── zustand/            ← Zustand stores
│   │   │   └── utils/              ← Formatting helpers (currency, percentage, date)
│   │   ├── hooks/                  ← Custom React hooks
│   │   ├── types/                  ← Shared TypeScript types and Zod schemas
│   │   └── __tests__/              ← Vitest unit tests (mirrors component structure)
│   │
│   └── api/                        ← Node.js / Fastify API gateway
│       ├── src/
│       │   ├── routes/             ← One file per domain: auth, stocks, watchlist, screener, alerts, chat
│       │   ├── plugins/            ← Fastify plugins: auth, rate-limit, cors, sensible
│       │   ├── services/           ← Business logic: MarketDataService, WatchlistService, AlertService
│       │   ├── jobs/               ← BullMQ job definitions: price-sync, alert-check, digest
│       │   ├── workers/            ← BullMQ worker processors
│       │   ├── lib/
│       │   │   ├── redis/          ← Upstash Redis client
│       │   │   ├── supabase/       ← Supabase admin client
│       │   │   └── prisma/         ← Prisma client singleton
│       │   ├── types/              ← Shared TypeScript types and Zod schemas
│       │   └── __tests__/          ← Vitest unit and integration tests
│       └── prisma/
│           ├── schema.prisma       ← Single source of truth for all database tables
│           └── migrations/         ← Auto-generated migration files
│
├── services/
│   └── ai/                         ← Python / FastAPI AI microservices
│       ├── app/
│       │   ├── routers/            ← FastAPI routers: screener, chat, overview
│       │   ├── services/           ← LLM service, prompt builder, response parser
│       │   ├── models/             ← Pydantic request/response models
│       │   └── prompts/            ← System prompt strings (one file per feature)
│       ├── tests/                  ← pytest unit and integration tests
│       └── modal_functions/        ← Modal deployment entry points
│
├── packages/
│   └── shared/                     ← Shared TypeScript types used by both web and api
│       └── types/
│           ├── stock.ts
│           ├── user.ts
│           ├── alert.ts
│           └── chat.ts
│
├── scripts/
│   ├── seed-stocks-master.ts       ← One-time seed script for 5000+ tickers
│   └── backfill-fundamentals.ts    ← One-time fundamentals backfill from EODHD
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  ← Run all tests on every PR
│       └── deploy.yml              ← Deploy to Vercel + Railway on merge to main
│
└── docs/
    ├── indian_stock_platform_prompt_guide.md
    ├── architecture.md
    ├── tech-cost-analysis.md
    └── PROMPTS_RELEASE_1.md        ← This file
```

---

### 0.4 Database Schema Decisions

Define every table required for Release 1 before generating any migration. Your AI assistant must generate the Prisma schema from these definitions.

`**users` table** — managed by Supabase Auth, do not create manually. Supabase creates this in the `auth` schema.

`**user_profiles` table** — extends Supabase auth.users

- `id` UUID primary key, foreign key to auth.users(id) on delete cascade
- `username` TEXT unique not null
- `full_name` TEXT
- `avatar_url` TEXT
- `experience_level` ENUM: `beginner`, `intermediate`, `advanced` — set during onboarding
- `created_at` TIMESTAMPTZ default now()
- `updated_at` TIMESTAMPTZ default now()
- RLS Policy: users can only read and write their own row.

`**user_risk_profiles` table**

- `id` UUID primary key
- `user_id` UUID foreign key to user_profiles(id) on delete cascade, unique
- `risk_appetite` ENUM: `conservative`, `moderate`, `aggressive`
- `investment_horizon` ENUM: `short_term` (under 1 year), `medium_term` (1–3 years), `long_term` (over 3 years)
- `primary_goal` ENUM: `wealth_creation`, `regular_income`, `capital_preservation`, `learning`
- `monthly_investment_capacity` TEXT — free text, not a number, for privacy
- `created_at` TIMESTAMPTZ default now()
- `updated_at` TIMESTAMPTZ default now()
- RLS Policy: users can only read and write their own row.

`**stocks` table** — market master data, read-only for all users

- `id` UUID primary key
- `ticker_nse` TEXT unique — NSE symbol (e.g., "RELIANCE")
- `ticker_bse` TEXT unique — BSE symbol (e.g., "500325")
- `company_name` TEXT not null
- `sector` TEXT — e.g., "Information Technology"
- `industry` TEXT — more granular than sector (e.g., "IT Services")
- `market_cap_category` ENUM: `large_cap`, `mid_cap`, `small_cap`, `micro_cap`
- `exchange` ENUM: `NSE`, `BSE`, `BOTH`
- `isin` TEXT unique not null
- `is_active` BOOLEAN default true — false for delisted stocks
- `is_fo_eligible` BOOLEAN default false
- `index_memberships` TEXT[] — e.g., ["NIFTY50", "NIFTY500", "NIFTYMIDCAP150"]
- `logo_url` TEXT
- `website_url` TEXT
- `created_at` TIMESTAMPTZ default now()
- `updated_at` TIMESTAMPTZ default now()
- RLS Policy: all authenticated users can SELECT. No one can INSERT/UPDATE/DELETE (service role only).
- Index on: `ticker_nse`, `sector`, `market_cap_category`, `is_active`.

`**stock_prices_daily` table** — OHLCV data

- `id` UUID primary key
- `stock_id` UUID foreign key to stocks(id) on delete cascade
- `date` DATE not null
- `open` NUMERIC(12,2) not null
- `high` NUMERIC(12,2) not null
- `low` NUMERIC(12,2) not null
- `close` NUMERIC(12,2) not null
- `volume` BIGINT not null
- `adjusted_close` NUMERIC(12,2)
- `created_at` TIMESTAMPTZ default now()
- Unique constraint on `(stock_id, date)`.
- RLS Policy: all authenticated users can SELECT. Service role only for writes.
- Index on: `(stock_id, date DESC)` for time-series queries.

`**stock_fundamentals` table** — quarterly financial data

- `id` UUID primary key
- `stock_id` UUID foreign key to stocks(id) on delete cascade
- `period_type` ENUM: `annual`, `quarterly`
- `period_end_date` DATE not null — last day of the financial period
- `fiscal_year` INTEGER — e.g., 2024
- `fiscal_quarter` INTEGER nullable — 1, 2, 3, or 4
- `revenue` NUMERIC(18,2) — in INR crores
- `ebitda` NUMERIC(18,2)
- `pat` NUMERIC(18,2) — profit after tax
- `eps` NUMERIC(10,2) — earnings per share
- `total_assets` NUMERIC(18,2)
- `total_equity` NUMERIC(18,2)
- `total_debt` NUMERIC(18,2)
- `cash_and_equivalents` NUMERIC(18,2)
- `operating_cash_flow` NUMERIC(18,2)
- `capex` NUMERIC(18,2)
- `dividends_paid` NUMERIC(18,2)
- `shares_outstanding` BIGINT
- `roe` NUMERIC(8,4) — stored as decimal, e.g., 0.1850 = 18.5%
- `roce` NUMERIC(8,4)
- `debt_to_equity` NUMERIC(8,4)
- `current_ratio` NUMERIC(8,4)
- `gross_margin` NUMERIC(8,4)
- `ebitda_margin` NUMERIC(8,4)
- `pat_margin` NUMERIC(8,4)
- `data_source` TEXT — e.g., "eodhd", "bse_filing"
- `created_at` TIMESTAMPTZ default now()
- Unique constraint on `(stock_id, period_type, period_end_date)`.
- RLS Policy: all authenticated users can SELECT. Service role only for writes.

`**corporate_actions` table**

- `id` UUID primary key
- `stock_id` UUID foreign key to stocks(id)
- `action_type` ENUM: `dividend`, `bonus`, `split`, `rights`, `buyback`
- `ex_date` DATE not null
- `record_date` DATE
- `details` JSONB — structure varies by action type
- `created_at` TIMESTAMPTZ default now()
- RLS Policy: all authenticated users can SELECT. Service role only for writes.

`**watchlists` table**

- `id` UUID primary key
- `user_id` UUID foreign key to user_profiles(id) on delete cascade
- `name` TEXT not null default 'Default'
- `created_at` TIMESTAMPTZ default now()
- RLS Policy: users can only access their own rows.

`**watchlist_items` table**

- `id` UUID primary key
- `watchlist_id` UUID foreign key to watchlists(id) on delete cascade
- `stock_id` UUID foreign key to stocks(id) on delete cascade
- `noted_price` NUMERIC(12,2) nullable — the price when the user added the stock
- `user_notes` TEXT nullable — user's private note about why they added it
- `price_target` NUMERIC(12,2) nullable — user's self-defined level to watch
- `added_at` TIMESTAMPTZ default now()
- Unique constraint on `(watchlist_id, stock_id)`.
- RLS Policy: users can only access items in their own watchlists.

`**price_alerts` table**

- `id` UUID primary key
- `user_id` UUID foreign key to user_profiles(id) on delete cascade
- `stock_id` UUID foreign key to stocks(id) on delete cascade
- `alert_type` ENUM: `price_above`, `price_below`
- `target_price` NUMERIC(12,2) not null
- `is_active` BOOLEAN default true
- `is_triggered` BOOLEAN default false
- `triggered_at` TIMESTAMPTZ nullable
- `triggered_price` NUMERIC(12,2) nullable — the actual price when triggered
- `created_at` TIMESTAMPTZ default now()
- RLS Policy: users can only access their own alerts.
- Index on `(stock_id, is_active, is_triggered)` — used by the alert checker worker.

`**notifications` table**

- `id` UUID primary key
- `user_id` UUID foreign key to user_profiles(id) on delete cascade
- `type` ENUM: `price_alert`, `system`
- `title` TEXT not null
- `body` TEXT not null
- `metadata` JSONB nullable — e.g., `{ "stock_id": "...", "alert_id": "...", "triggered_price": 450 }`
- `is_read` BOOLEAN default false
- `created_at` TIMESTAMPTZ default now()
- RLS Policy: users can only SELECT their own rows. Service role for INSERT. Users can UPDATE `is_read` on their own rows only.
- Index on `(user_id, is_read, created_at DESC)`.

`**ai_response_cache` table** — prevents re-calling the LLM for identical requests

- `id` UUID primary key
- `cache_key` TEXT unique not null — deterministic hash of: feature + stock_id + date + relevant parameters
- `feature` TEXT not null — e.g., `stock_overview`, `screener_parse`
- `stock_id` UUID nullable
- `response_json` JSONB not null
- `model_used` TEXT not null — e.g., `claude-3-5-haiku-20241022`
- `created_at` TIMESTAMPTZ default now()
- `expires_at` TIMESTAMPTZ not null — set at INSERT time based on TTL rules
- RLS Policy: service role only for all operations.
- Index on `(cache_key)` and `(expires_at)` for cleanup jobs.

`**chat_conversations` table**

- `id` UUID primary key
- `user_id` UUID foreign key to user_profiles(id) on delete cascade
- `title` TEXT nullable — auto-generated from first message
- `created_at` TIMESTAMPTZ default now()
- `updated_at` TIMESTAMPTZ default now()
- RLS Policy: users can only access their own conversations.

`**chat_messages` table**

- `id` UUID primary key
- `conversation_id` UUID foreign key to chat_conversations(id) on delete cascade
- `role` ENUM: `user`, `assistant`
- `content` TEXT not null
- `metadata` JSONB nullable — e.g., `{ "stocks_mentioned": ["TCS", "INFY"], "query_type": "comparison" }`
- `token_count` INTEGER nullable — for cost tracking
- `created_at` TIMESTAMPTZ default now()
- RLS Policy: users can only access messages in their own conversations.
- Index on `(conversation_id, created_at ASC)`.

---

### 0.5 API Contract Decisions

Define all API routes before generating any handler code. Group by service.

**Node.js / Fastify API base URL:** `https://api.investom.in/v1`

**Auth routes (public):**

- `POST /auth/signup` — body: `{ email, password, full_name }`
- `POST /auth/login` — body: `{ email, password }`
- `POST /auth/logout` — requires auth header
- `POST /auth/refresh` — body: `{ refresh_token }`
- `POST /auth/forgot-password` — body: `{ email }`
- `POST /auth/reset-password` — body: `{ token, new_password }`

**Onboarding routes (requires auth):**

- `POST /onboarding/profile` — body: `{ username, experience_level }`
- `POST /onboarding/risk-profile` — body: `{ risk_appetite, investment_horizon, primary_goal, monthly_investment_capacity }`
- `GET /onboarding/status` — returns whether onboarding is complete

**Stocks routes (requires auth):**

- `GET /stocks/search?q={query}&limit=10` — returns matching stocks by name or ticker
- `GET /stocks/{ticker}` — returns stock overview card data (price + fundamentals + metadata)
- `GET /stocks/{ticker}/price` — returns current price and recent OHLCV
- `GET /stocks/trending` — returns top 10 trending stocks (most viewed today)
- `GET /stocks/heatmap` — returns sector-wise daily performance data for heatmap
- `GET /stocks/screener` — body via POST: `{ filters: [], sort_by, sort_order, limit, offset }`

**Watchlist routes (requires auth):**

- `GET /watchlist` — returns all watchlist items for the authenticated user
- `POST /watchlist` — body: `{ stock_id, noted_price?, user_notes?, price_target? }`
- `DELETE /watchlist/{watchlist_item_id}` — removes a stock from watchlist
- `PATCH /watchlist/{watchlist_item_id}` — body: `{ user_notes?, price_target? }`

**Alert routes (requires auth):**

- `GET /alerts` — returns all alerts (active and triggered) for the user
- `POST /alerts` — body: `{ stock_id, alert_type, target_price }`
- `DELETE /alerts/{alert_id}` — soft delete (sets `is_active = false`)
- `GET /notifications` — returns unread + recent notifications
- `PATCH /notifications/{notification_id}/read` — marks a notification as read
- `PATCH /notifications/read-all` — marks all notifications as read

**Chat routes (requires auth):**

- `GET /chat/conversations` — returns conversation list
- `GET /chat/conversations/{id}` — returns conversation with messages
- `POST /chat/message` — body: `{ conversation_id?, message: string }` — this proxies to the Python AI service and streams the response

**Python / FastAPI AI service base URL:** `https://ai.investom.in` (internal, not public)

- `POST /ai/chat` — body: `{ message, conversation_history, user_context? }` — returns streamed response
- `POST /ai/screener/parse` — body: `{ query }` — returns structured filter JSON
- `POST /ai/stock/overview` — body: `{ ticker, stock_data }` — returns AI narrative for overview card
- `GET /health` — returns 200 OK if service is healthy

---

### 0.6 Environment Variables Registry

Define every environment variable before writing any code. All must be added to Doppler before the first deployment. Your AI assistant must read all config from environment variables with Zod validation at startup.

> **Legend:** Variables marked **[REQUIRED]** must be set before the app starts. Variables marked **[OPTIONAL-DEV]** can be left unset in local development — the app must start and function without them (use a feature flag or null-check). Variables marked **[OPTIONAL-PROD]** are required in staging/production but optional in development.

---

**Next.js Frontend (web app):**

- `NEXT_PUBLIC_SUPABASE_URL` — **[REQUIRED]** Supabase project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` — **[REQUIRED]** Supabase publishable key (formerly anon key — safe to expose to browser, used in all client-side Supabase calls)
- `NEXT_PUBLIC_API_BASE_URL` — **[REQUIRED]** Node.js API server URL (use `http://localhost:3001` locally)
- `NEXT_PUBLIC_APP_URL` — **[REQUIRED]** frontend URL (use `http://localhost:3000` locally)
- `NEXT_PUBLIC_SENTRY_DSN` — **[OPTIONAL-DEV]** Sentry DSN for frontend errors; skip during development, errors are logged to console

**Node.js API Server:**

- `DATABASE_URL` — **[REQUIRED]** Prisma connection string (Supabase pooler URL)
- `DIRECT_DATABASE_URL` — **[REQUIRED]** Prisma direct connection string (for migrations only)
- `SUPABASE_URL` — **[REQUIRED]** Supabase project URL
- `SUPABASE_SECRET_KEY` — **[REQUIRED]** Supabase secret key (formerly service role key — bypasses RLS, never expose to browser, server-side only). Also used by `createServerClient` for JWT verification — no separate JWT secret is needed in the new Supabase key system.
- `REDIS_URL` — **[REQUIRED]** Upstash Redis REST URL — Upstash free tier (10,000 commands/day) is sufficient for development
- `REDIS_TOKEN` — **[REQUIRED]** Upstash Redis REST token
- `AI_SERVICE_URL` — **[REQUIRED]** internal URL of the Python FastAPI service (use `http://localhost:8000` locally)
- `AI_SERVICE_API_KEY` — **[REQUIRED]** shared secret for internal service-to-service auth; set any random string locally
- `EODHD_API_KEY` — **[OPTIONAL-PROD]** EODHD market data API key ($19/month); leave unset in development — the data pipeline will use yfinance when this is absent (controlled by `ENVIRONMENT` flag)
- `ALPHA_VANTAGE_API_KEY` — **[OPTIONAL-DEV]** Alpha Vantage free API key (25 req/day); use during development to test the OHLCV pipeline with a small number of stocks when yfinance is not available
- `RESEND_API_KEY` — **[OPTIONAL-DEV]** Resend email service key; leave unset in development — email sending is skipped and a console log is emitted instead. Set for staging/production.
- `FIREBASE_SERVICE_ACCOUNT_JSON` — **[OPTIONAL-DEV]** Firebase admin SDK credentials for push notifications; leave unset in development — push notifications are skipped gracefully. Set for staging/production.
- `SENTRY_DSN` — **[OPTIONAL-DEV]** Sentry DSN for backend errors; skip during development
- `PORT` — **[REQUIRED]** server port (default: `3001`)
- `NODE_ENV` — **[REQUIRED]** `development`, `staging`, or `production`
- `RATE_LIMIT_MAX` — **[REQUIRED]** maximum requests per minute per IP for public routes (default: `60`)
- `RATE_LIMIT_AUTH_MAX` — **[REQUIRED]** maximum requests per minute per user for auth routes (default: `300`)
- `RATE_LIMIT_AI_MAX` — **[REQUIRED]** maximum requests per minute per user for AI/chat routes (default: `10`)

**Python AI Service:**

*Free-tier providers are the default. Paid providers are optional overrides activated only in staging/production via the `ENVIRONMENT` variable.*

**— Free tier (use these to start, no credit card required):**

- `GEMINI_API_KEY` — **[REQUIRED for dev]** Google AI Studio key — **free, 1,500 req/day, 1M tokens/min**. This is the primary LLM in development. Get it at aistudio.google.com with your Google account, no credit card required.
- `GEMINI_MODEL` — **[REQUIRED for dev]** Gemini model name to use. Default: `gemini-1.5-flash`. Change to `gemini-2.0-flash` or newer without any code changes.
- `XAI_API_KEY` — **[REQUIRED for dev]** xAI Grok API key — **free tier available**. Used as the LLM fallback in development when Gemini is unavailable. Get it at console.x.ai with your X (Twitter) account, no credit card required. Uses the OpenAI SDK format with `base_url="https://api.x.ai/v1"`.
- `XAI_MODEL` — **[REQUIRED for dev]** xAI model name to use. Default: `grok-3-mini`. Change to `grok-4-mini` or newer without any code changes.
- `HUGGINGFACE_API_KEY` — **[REQUIRED for dev]** Hugging Face Inference API key — **free tier, no credit card**. Used for `sentence-transformers/all-MiniLM-L6-v2` embeddings (384-dim) in development. Get it at huggingface.co. Sufficient for all R1 development and early testing.
- `HUGGINGFACE_EMBEDDING_MODEL` — **[REQUIRED for dev]** HuggingFace embedding model name. Default: `sentence-transformers/all-MiniLM-L6-v2`.

**— Paid providers (optional, activate only for staging/production):**
- `ANTHROPIC_API_KEY` — **[OPTIONAL — staging/production only]** Claude API key ($0.80/1M input tokens for Haiku). When this key is present AND `ENVIRONMENT=production`, it overrides Gemini as the primary LLM. Enable prompt caching on your Anthropic account before using. Set a usage alert at $50/month.
- `ANTHROPIC_MODEL` — **[OPTIONAL — staging/production only]** Claude model name. Default: `claude-haiku-4-5`. Change to a newer Haiku version without any code changes.
- `OPENAI_API_KEY` — **[OPTIONAL — staging/production only]** OpenAI API key. Used for `text-embedding-3-small` embeddings (1536-dim, higher accuracy than HuggingFace) and as the production LLM fallback. Leave unset in development. Set a usage alert at $20/month.
- `OPENAI_LLM_MODEL` — **[OPTIONAL — staging/production only]** OpenAI fallback LLM model name. Default: `gpt-4o-mini`.
- `OPENAI_EMBEDDING_MODEL` — **[OPTIONAL — staging/production only]** OpenAI embedding model name. Default: `text-embedding-3-small`.

**— Always required:**

- `AI_SERVICE_API_KEY` — **[REQUIRED]** shared secret for service-to-service auth (must match the Node.js value); set any random UUID locally
- `SUPABASE_URL` — **[REQUIRED]** for reading and writing AI response cache
- `SUPABASE_SECRET_KEY` — **[REQUIRED]** Supabase secret key (same key as the Node.js service, used for cache reads/writes)
- `ENVIRONMENT` — **[REQUIRED]** `development`, `staging`, or `production` — this single variable controls which providers are active

**LLM Provider Selection Logic (controlled by `ENVIRONMENT` and key presence):**

```
ENVIRONMENT=development  (zero cost, start here):
  LLM primary   → GEMINI_API_KEY    (free, Google AI Studio)
  LLM fallback  → XAI_API_KEY       (free, xAI Grok)
  Embeddings    → HUGGINGFACE_API_KEY (free, sentence-transformers)
  Market data   → yfinance           (no key needed, Python library)

ENVIRONMENT=staging  (low cost, validate before production):
  LLM primary   → ANTHROPIC_API_KEY  (Claude 3.5 Haiku, ~$5–20/month)
  LLM fallback  → XAI_API_KEY        (free, xAI Grok — keep as fallback)
  Embeddings    → OPENAI_API_KEY     (text-embedding-3-small, ~$1/month)
  Market data   → yfinance (no key needed) + EODHD_API_KEY (if set, overrides yfinance)

ENVIRONMENT=production  (full paid stack):
  LLM primary   → ANTHROPIC_API_KEY  (Claude 3.5 Haiku + prompt caching)
  LLM fallback  → OPENAI_API_KEY     (GPT-4o-mini)
  Embeddings    → OPENAI_API_KEY     (text-embedding-3-small)
  Market data   → yfinance (primary) + EODHD_API_KEY (optional upgrade)
```

The startup validation must enforce: at least one LLM key is present AND at least one market data source is available. On startup, the service must log a clear provider summary, e.g.:

```
[AI Service] Active providers:
  LLM primary  : Gemini 1.5 Flash (FREE)
  LLM fallback : xAI Grok grok-3-mini (FREE)
  Embeddings   : HuggingFace all-MiniLM-L6-v2 (FREE)
  Market data  : yfinance (FREE)
```

---

### 0.7 Security Requirements (Must Be Implemented Before Any Feature Goes Live)

These are non-negotiable security controls. Your AI assistant must implement all of them.

**Input Validation and Sanitisation:**

- Every Fastify route must have a Zod schema for the request body, query parameters, and path parameters. If any field fails validation, return HTTP 400 with a descriptive error. Never pass unvalidated input to business logic, database queries, or LLM calls.
- All user-provided text that will be included in an AI prompt must be stripped of HTML tags, truncated to a maximum of 500 characters, and checked against a list of known prompt injection patterns (e.g., "ignore previous instructions", "you are now", "system:", "assistant:"). If a match is found, reject the request with HTTP 400 and log the attempt.
- Stock ticker inputs must be validated against the `stocks` master table — never pass a raw user-provided string as a ticker to any external API.

**Authentication and Authorisation:**
- Every protected route must validate the Supabase JWT using `createServerClient` from `@supabase/ssr` initialised with `SUPABASE_URL` and `SUPABASE_SECRET_KEY`. Call `supabase.auth.getUser()` to verify the token and extract the authenticated user — do not manually decode or verify JWTs. Supabase's new key system handles verification against the JWKS endpoint (`/auth/v1/.well-known/jwks.json`) internally. Never trust a `user_id` from the request body or query parameters — always use the value returned by `getUser()`.
- All database queries on user-owned data must include a `WHERE user_id = $authenticated_user_id` clause. Never rely solely on Row Level Security — defence in depth means the application layer also enforces ownership.
- Onboarding routes must be idempotent — calling them twice should update, not create duplicates.

**Rate Limiting:**

- Apply rate limiting as a Fastify plugin before any route handlers. Use Upstash Redis for distributed rate limit state so limits work correctly across multiple server instances.
- Public routes (search, stock data): 60 requests per minute per IP.
- Authenticated routes: 300 requests per minute per user.
- AI/chat routes: 10 requests per minute per user (prevents cost abuse).
- If a limit is exceeded, return HTTP 429 with a `Retry-After` header.

**HTTP Security Headers:**

- Use the Fastify `@fastify/helmet` plugin to set: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`.
- For the Next.js frontend, add all security headers in `next.config.ts` using the `headers()` function. Include a `Content-Security-Policy` that explicitly whitelists Supabase, your API domains, and Cloudflare.

**CORS:**

- The Fastify API must only accept requests from the frontend domain (configured via environment variable). Do not use `*` as the CORS origin in staging or production.

**Secrets:**

- No secrets in code, ever. All secrets come from environment variables. The Doppler CLI syncs secrets to `.env` files locally, never committed to git. Add `.env` and `.env.local` to `.gitignore` before the first commit.

**Supabase RLS:**
- Before writing any application data, verify Row Level Security is enabled on all user data tables by running a test: attempt to SELECT from a user_profiles row using the publishable key without any JWT — this should return an empty result, not the data.

**AI Output Handling:**

- Never render AI-generated text using `dangerouslySetInnerHTML`. Always render it as plain text or use a safe Markdown renderer that strips all HTML.
- Every AI-generated output displayed in the UI must include the disclaimer: `"This is data and analysis only — not investment advice. Investom is not a SEBI-registered investment adviser."`

---

### 0.8 Naming Conventions

Apply these conventions consistently. Your AI assistant must follow them.

- Database table names: `snake_case` plural (e.g., `user_profiles`, `stock_prices_daily`)
- Database column names: `snake_case` (e.g., `created_at`, `ticker_nse`)
- TypeScript types and interfaces: `PascalCase` (e.g., `StockOverview`, `UserProfile`)
- TypeScript functions: `camelCase` (e.g., `getStockOverview`, `createPriceAlert`)
- React components: `PascalCase` (e.g., `StockOverviewCard`, `SectorHeatmap`)
- React hooks: `use` prefix + `camelCase` (e.g., `useWatchlist`, `useStockPrice`)
- Next.js pages: `kebab-case` directories (e.g., `/app/(dashboard)/ask-ai/page.tsx`)
- Fastify routes: `kebab-case` paths (e.g., `/stocks/search`, `/price-alerts`)
- Python files: `snake_case` (e.g., `screener_service.py`, `chat_router.py`)
- Python classes: `PascalCase`
- Environment variables: `SCREAMING_SNAKE_CASE`
- Cache keys: `feature:identifier:parameter` format (e.g., `stock_overview:RELIANCE:2025-06-01`)
- Git branches: `feature/r1-auth`, `feature/r1-stock-overview`, `fix/r1-watchlist-delete`
- Git commit messages: Conventional Commits format (e.g., `feat(auth): add email verification step`)

---

### 0.9 Testing Strategy Overview

The full testing prompts are in Prompts 20–22. Define the strategy here so it guides all preceding prompts.

**Unit Tests:**

- Every pure function (formatting utils, calculation helpers, Zod schema validators, prompt builders) must have unit tests.
- Every React component that renders conditional states (loading, error, empty, populated) must have unit tests covering each state.
- Every Fastify route handler must have a unit test with a mocked database and mocked external services.
- Every Python AI service function must have a unit test with mocked Anthropic/OpenAI responses.
- Framework: Vitest for TypeScript (web + api). pytest for Python.
- Coverage target: 80% line coverage minimum on all non-UI code.

**Integration Tests:**

- Every API route must have an integration test that calls the actual route against a test database (Supabase local instance or a dedicated test Supabase project).
- Every data ingestion pipeline must have an integration test using recorded yfinance response fixtures (stored in `__tests__/fixtures/yfinance/`) — do not make live yfinance calls in CI as they are network-dependent and flaky in test environments.
- Every BullMQ job must have an integration test that enqueues the job and verifies the worker completes it correctly.

**End-to-End Tests:**

- Framework: Playwright.
- Every complete user journey in Release 1 must have an E2E test.
- E2E tests run against the staging environment (deployed app + real test database).
- All E2E tests must pass in CI before any deployment to production.

---

## Prompt 1 — Project Scaffolding

**[BLOCKING]**

Ask your AI assistant to scaffold the complete monorepo with the following instructions:

---

### 1.1 Root Monorepo Setup

Scaffold a TypeScript monorepo named `investom` using the exact folder structure defined in Prompt 0 Section 0.3. Use npm workspaces (not Turborepo — keep it simple for R1).

Create a root `package.json` with the following workspaces configuration:
```json
{
  "name": "investom",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev:web": "npm run dev --workspace=apps/web",
    "dev:api": "npm run dev --workspace=apps/api",
    "test": "npm run test --workspaces --if-present",
    "lint": "npm run lint --workspaces --if-present",
    "typecheck": "npm run typecheck --workspaces --if-present"
  }
}
```

Create a root `.gitignore` that includes: `node_modules`, `.env`, `.env.local`, `.env.*.local`, `dist`, `build`, `.next`, `__pycache__`, `*.pyc`, `.pytest_cache`, `.venv`, `*.egg-info`.

Copy the existing `.env.example` to the root — this is the single env file for local development shared across all services. Each service reads from `process.env` (Node.js) or `python-dotenv` (Python) pointing at the root `.env`.

Create a root `tsconfig.base.json` with strict mode settings that all TypeScript packages extend:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

---

### 1.2 Next.js Frontend (`apps/web`)

Initialise Next.js 15 with App Router and TypeScript strict mode. The `tsconfig.json` must extend the root `tsconfig.base.json`.

**Install all dependencies:**
```
next@15  react@19  react-dom@19
typescript  @types/node  @types/react  @types/react-dom
tailwindcss@3  postcss  autoprefixer
@tanstack/react-query@5  @tanstack/react-query-devtools@5
zustand@5
react-hook-form  @hookform/resolvers
zod
@supabase/supabase-js  @supabase/ssr
recharts
@sentry/nextjs
```

**shadcn/ui setup:** Run `npx shadcn@latest init` and select: New York style, zinc base colour, CSS variables enabled. Then install the following components one by one (do not use `add --all`):
```
npx shadcn@latest add button input dialog sheet badge card
npx shadcn@latest add dropdown-menu toast skeleton tabs
npx shadcn@latest add scroll-area separator avatar command tooltip
npx shadcn@latest add sonner  ← use Sonner for toasts, not the default Toast
```

**Configure `next.config.ts`** with:
- Security headers from Prompt 0 Section 0.7 (CSP, HSTS, X-Frame-Options, etc.)
- `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_SENTRY_DSN` all declared under `env` so Next.js validates they are present at build time

**Configure Sentry** using `npx @sentry/wizard@latest -i nextjs`. Use the `NEXT_PUBLIC_SENTRY_DSN` env var. Enable only in `ENVIRONMENT !== 'development'` so local dev is not cluttered with Sentry noise.

**Create the following foundational files** (empty implementations, wired up correctly):
- `apps/web/lib/supabase/client.ts` — browser Supabase client using `createBrowserClient` from `@supabase/ssr` with `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `apps/web/lib/supabase/server.ts` — server Supabase client using `createServerClient` from `@supabase/ssr` (reads cookies)
- `apps/web/lib/tanstack/provider.tsx` — TanStack Query client provider (`'use client'`, wraps children with `QueryClientProvider`)
- `apps/web/lib/tanstack/keys.ts` — query key factory (empty object to be filled per feature)
- `apps/web/lib/zustand/chat-store.ts` — Zustand store with `isOpen: false` and `setIsOpen` action
- `apps/web/lib/utils/format.ts` — empty stub with exported functions: `formatCurrency`, `formatPercentage`, `formatDate`, `formatRelativeTime`
- `apps/web/app/layout.tsx` — root layout wrapping children with the TanStack Query provider and `Toaster` (Sonner)

**Add scripts to `apps/web/package.json`:**
```json
"dev": "next dev",
"build": "next build",
"start": "next start",
"lint": "next lint",
"typecheck": "tsc --noEmit",
"test": "vitest run",
"test:watch": "vitest"
```

Install `vitest`, `@vitejs/plugin-react`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` as dev dependencies. Create `vitest.config.ts` with jsdom environment.

---

### 1.3 Node.js API Server (`apps/api`)

Initialise a Fastify v4 TypeScript project. The `tsconfig.json` must extend the root `tsconfig.base.json` and set `"module": "NodeNext"`, `"moduleResolution": "NodeNext"`.

**Install all dependencies:**
```
fastify@4
@fastify/cors  @fastify/helmet  @fastify/rate-limit  @fastify/sensible
@supabase/supabase-js  @supabase/ssr
@prisma/client  prisma
bullmq
@upstash/redis
@upstash/ratelimit  ← use Upstash's own rate limit library for distributed rate limiting
zod
@sentry/node
pino  pino-pretty  ← Fastify's built-in logger, pretty-print in development
```

**Install dev dependencies:** `typescript`, `@types/node`, `tsx` (for running TypeScript directly), `vitest`, `@vitest/coverage-v8`.

**Create `apps/api/src/lib/env.ts`** — Zod schema that validates all environment variables on import. Every required variable must be listed. If any are missing, throw with a clear message listing the missing variable name. Export the validated `env` object — all other files must import from this file, never from `process.env` directly:
```typescript
// Pattern — AI assistant must implement this fully
import { z } from 'zod'
const schema = z.object({
  DATABASE_URL: z.string().url(),
  SUPABASE_URL: z.string().url(),
  SUPABASE_SECRET_KEY: z.string().min(1),
  REDIS_URL: z.string().url(),
  REDIS_TOKEN: z.string().min(1),
  AI_SERVICE_URL: z.string().url(),
  AI_SERVICE_API_KEY: z.string().min(1),
  PORT: z.coerce.number().default(3001),
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
  ENVIRONMENT: z.enum(['development', 'staging', 'production']).default('development'),
  RATE_LIMIT_MAX: z.coerce.number().default(60),
  RATE_LIMIT_AUTH_MAX: z.coerce.number().default(300),
  RATE_LIMIT_AI_MAX: z.coerce.number().default(10),
  // Optional vars — presence checked at feature usage, not startup
  EODHD_API_KEY: z.string().optional(),
  ALPHA_VANTAGE_API_KEY: z.string().optional(),
  RESEND_API_KEY: z.string().optional(),
  FIREBASE_SERVICE_ACCOUNT_JSON: z.string().optional(),
  SENTRY_DSN: z.string().optional(),
})
export const env = schema.parse(process.env)
```

**Create the following foundational files:**
- `apps/api/src/lib/prisma/client.ts` — Prisma client singleton (create once, reuse across requests)
- `apps/api/src/lib/redis/client.ts` — Upstash Redis client using `REDIS_URL` and `REDIS_TOKEN` from `env`
- `apps/api/src/lib/supabase/admin.ts` — Supabase admin client using `SUPABASE_URL` and `SUPABASE_SECRET_KEY` (service role, for server operations)
- `apps/api/src/plugins/auth.ts` — Fastify plugin that adds a `preHandler` hook: calls `supabase.auth.getUser()` with the Bearer token and attaches `request.userId`. Returns 401 if token is missing or invalid.
- `apps/api/src/plugins/cors.ts` — `@fastify/cors` configured to allow only `NEXT_PUBLIC_APP_URL` origin
- `apps/api/src/plugins/rate-limit.ts` — `@fastify/rate-limit` using Upstash Redis store with limits from `env`
- `apps/api/src/server.ts` — Fastify instance wiring all plugins and a `GET /health` route that returns `{ status: 'ok', environment: env.ENVIRONMENT }`
- `apps/api/src/index.ts` — entry point that imports `env` first (triggers validation), then starts the server on `env.PORT`

**Prisma initialisation:** Run `npx prisma init --datasource-provider postgresql`. The `schema.prisma` will be populated in Prompt 2 — leave it with just the datasource and generator blocks for now.

**Add scripts to `apps/api/package.json`:**
```json
"dev": "tsx watch src/index.ts",
"build": "tsc",
"start": "node dist/index.js",
"typecheck": "tsc --noEmit",
"test": "vitest run",
"test:watch": "vitest",
"db:migrate": "prisma migrate dev",
"db:push": "prisma db push",
"db:studio": "prisma studio"
```

---

### 1.4 Python AI Service (`services/ai`)

Initialise a FastAPI project with Python 3.11+. Use a virtual environment at `services/ai/.venv`.

**Create `services/ai/pyproject.toml`** with all dependencies pinned to specific versions:
```toml
[project]
name = "investom-ai"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi==0.115.0",
  "uvicorn[standard]==0.30.6",
  "pydantic==2.9.2",
  "anthropic==0.34.2",
  "openai==1.47.0",
  "pandas==2.2.3",
  "pandas-ta==0.3.14b0",
  "numpy==1.26.4",
  "yfinance==0.2.44",
  "python-dotenv==1.0.1",
  "httpx==0.27.2",
  "supabase==2.7.4",
  "modal==0.64.10",
]

[project.optional-dependencies]
dev = [
  "pytest==8.3.3",
  "pytest-asyncio==0.24.0",
  "pytest-cov==5.0.0",
  "httpx==0.27.2",
]
```

**Create `services/ai/app/config.py`** — Pydantic Settings class that reads all env vars. Validate at import with clear error messages. Map to the same variable names as the `.env.example`:
```python
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # Required
    ai_service_api_key: str
    supabase_url: str
    supabase_secret_key: str
    environment: Literal['development', 'staging', 'production'] = 'development'

    # Free tier LLM (development)
    gemini_api_key: str | None = None
    gemini_model: str = 'gemini-1.5-flash'
    xai_api_key: str | None = None
    xai_model: str = 'grok-3-mini'
    huggingface_api_key: str | None = None
    huggingface_embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'

    # Paid providers (staging/production)
    anthropic_api_key: str | None = None
    anthropic_model: str = 'claude-haiku-4-5'
    openai_api_key: str | None = None
    openai_llm_model: str = 'gpt-4o-mini'
    openai_embedding_model: str = 'text-embedding-3-small'

    # Market data
    eodhd_api_key: str | None = None
    alpha_vantage_api_key: str | None = None

    class Config:
        env_file = '../../.env'  # reads from root .env during local development
        case_sensitive = False

settings = Settings()
```

**Create `services/ai/app/main.py`** — FastAPI app with:
- API key security dependency that checks `X-API-Key` header against `settings.ai_service_api_key`
- `GET /health` route returning active provider summary (which LLM and market data providers are active based on which keys are present and `ENVIRONMENT`)
- Router registration stubs for: `/ai/chat`, `/ai/screener`, `/ai/stock` (empty routers to be implemented in later prompts)
- Startup log listing active providers per the format in Prompt 0 Section 0.6

**Create `services/ai/app/services/llm_provider.py`** — provider selection logic implementing the fallback chain from Prompt 0 Section 0.6:
- In `development`: use Gemini (`GEMINI_API_KEY`) as primary, xAI Grok (`XAI_API_KEY`) as fallback
- In `staging/production`: use Anthropic (`ANTHROPIC_API_KEY`) as primary, OpenAI (`OPENAI_API_KEY`) as fallback
- Both Gemini and xAI use the OpenAI Python SDK with their respective `base_url` values
- Expose a single `async def call_llm(messages, system_prompt) -> str` function that picks the right provider automatically
- Expose a single `async def get_embedding(text) -> list[float]` function that picks HuggingFace (dev) or OpenAI (prod)

**Install `pydantic-settings`** separately: `pip install pydantic-settings==2.5.2`.

**Add `services/ai/pytest.ini`:**
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

---

### 1.5 Shared Types Package (`packages/shared`)

Create TypeScript type files that match the database schema from Prompt 0 Section 0.4 exactly. These types are imported by both `apps/web` and `apps/api`.

**`packages/shared/types/stock.ts`** — `Stock`, `StockPrice`, `StockFundamentals`, `CorporateAction`, `StockOverview` (assembled response type), `MarketCapCategory`, `Exchange`

**`packages/shared/types/user.ts`** — `UserProfile`, `UserRiskProfile`, `ExperienceLevel`, `RiskAppetite`, `InvestmentHorizon`, `PrimaryGoal`

**`packages/shared/types/alert.ts`** — `PriceAlert`, `Notification`, `AlertType`, `NotificationType`

**`packages/shared/types/chat.ts`** — `ChatConversation`, `ChatMessage`, `ChatRole`, `QueryType`

**`packages/shared/types/watchlist.ts`** — `Watchlist`, `WatchlistItem`

**`packages/shared/package.json`:**
```json
{
  "name": "@investom/shared",
  "version": "0.1.0",
  "main": "./types/index.ts",
  "types": "./types/index.ts"
}
```

**`packages/shared/types/index.ts`** — re-exports everything from all type files.

Reference this package in `apps/web` and `apps/api` as `"@investom/shared": "*"` in their `package.json` dependencies.

---

### 1.6 Verification Checklist

After scaffolding, verify all of the following before proceeding to Prompt 2:

**Next.js (`apps/web`):**
- [ ] `npm run dev` starts on port 3000 with no errors
- [ ] `http://localhost:3000` returns a page (even if blank)
- [ ] `npm run typecheck` exits with 0 errors
- [ ] `npm run test` runs Vitest and exits cleanly (zero tests is fine)
- [ ] Security headers are visible in browser DevTools → Network → response headers on the homepage
- [ ] Supabase browser client initialises without throwing (check console)

**Node.js API (`apps/api`):**
- [ ] `npm run dev` starts on port 3001 with no errors
- [ ] `curl http://localhost:3001/health` returns `{"status":"ok","environment":"development"}`
- [ ] `npm run typecheck` exits with 0 errors
- [ ] `npm run test` runs Vitest and exits cleanly
- [ ] If a required env var is removed from `.env`, the server refuses to start and logs the missing variable name clearly

**Python AI Service (`services/ai`):**
- [ ] `uvicorn app.main:app --reload` starts on port 8000 with no errors
- [ ] `curl http://localhost:8000/health` returns the active providers summary — it must show Gemini and xAI as active (since those keys are set in `.env`)
- [ ] `curl -H "X-API-Key: wrong"  http://localhost:8000/health` returns 403
- [ ] `pytest` runs and exits cleanly (zero tests is fine)
- [ ] Startup log clearly shows which LLM and market data providers are active

**Shared package:**
- [ ] `apps/web` and `apps/api` can both import `@investom/shared` types without TypeScript errors

---

## Prompt 2 — Database Schema and Migrations

**[BLOCKING]**

Ask your AI assistant to:

Generate the complete Prisma schema in `apps/api/prisma/schema.prisma` implementing every table defined in Prompt 0 Section 0.4. Each table must map to the exact column names, types, constraints, and indexes specified. Use `@db.Uuid` for UUID fields. Use `@default(dbgenerated("gen_random_uuid()"))` for UUID primary keys. Use `@db.Timestamptz(6)` for all timestamp fields.

For ENUMs, define them as Prisma enums at the top of the schema file.

After generating the schema, generate the first migration with the name `init_release_1_schema` and apply it to the Supabase development project using the `DIRECT_DATABASE_URL` connection string.

After the migration runs, manually verify in the Supabase dashboard that:

- All 13 tables exist with the correct column types
- All foreign key constraints are visible
- All indexes are created
- The `pgvector` extension is enabled (this was done manually in Prompt 0 but confirm it)

Then, in the Supabase SQL editor, manually create the following Row Level Security policies for every user-data table. Your AI assistant must generate the SQL for each policy:

- `user_profiles`: SELECT/UPDATE where auth.uid() = id; no INSERT from user (created by trigger)
- `user_risk_profiles`: SELECT/INSERT/UPDATE/DELETE where auth.uid() = user_id
- `watchlists`: SELECT/INSERT/UPDATE/DELETE where auth.uid() = user_id
- `watchlist_items`: SELECT/INSERT/UPDATE/DELETE where watchlist_id in (SELECT id FROM watchlists WHERE user_id = auth.uid())
- `price_alerts`: SELECT/INSERT/UPDATE/DELETE where auth.uid() = user_id
- `notifications`: SELECT where auth.uid() = user_id; UPDATE where auth.uid() = user_id (only is_read column); no INSERT from user (service role only)
- `chat_conversations`: SELECT/INSERT/DELETE where auth.uid() = user_id
- `chat_messages`: SELECT/INSERT where conversation_id in (SELECT id FROM chat_conversations WHERE user_id = auth.uid())

Also create a Supabase database function and trigger that automatically creates a `user_profiles` row and a default `watchlists` row whenever a new user signs up (insert into `auth.users`). This ensures every new user has a profile and an empty watchlist immediately after signup.

---

## Prompt 3 — User Authentication and Onboarding

### 3.1 Backend: Auth Routes

Ask your AI assistant to:

Build the authentication API routes in `apps/api/src/routes/auth.ts` using Supabase Auth on the backend. The Node.js server proxies auth operations to Supabase — it does not manage sessions directly.

Implement the following routes exactly as defined in Prompt 0 Section 0.5:

- `POST /auth/signup` — call Supabase Auth signUp, return access token and refresh token. Return HTTP 409 if email already exists. Return HTTP 422 if password is under 8 characters.
- `POST /auth/login` — call Supabase Auth signInWithPassword. Return HTTP 401 on invalid credentials with the message "Invalid email or password" (never distinguish which field is wrong, for security).
- `POST /auth/logout` — invalidate the session in Supabase Auth.
- `POST /auth/refresh` — exchange refresh token for a new access token.
- `POST /auth/forgot-password` — call Supabase Auth resetPasswordForEmail. Always return HTTP 200 even if the email does not exist (prevents email enumeration).
- `POST /auth/reset-password` — verify token and update password.

Build the onboarding routes:

- `POST /onboarding/profile` — validate input with Zod, upsert the `user_profiles` row, return the updated profile.
- `POST /onboarding/risk-profile` — validate input, upsert the `user_risk_profiles` row.
- `GET /onboarding/status` — return `{ is_complete: boolean }` where complete means both profile and risk profile rows exist.

Security requirements for auth routes:

- Apply a strict rate limit of 5 requests per 15 minutes per IP on signup and login routes specifically (brute force prevention).
- Log all failed login attempts (do not log passwords).
- The `signup` route must validate that the username is alphanumeric plus underscores, 3–20 characters, and not in a reserved words list (admin, investom, sebi, nse, bse, support, api).

### 3.2 Frontend: Auth Pages and Onboarding Wizard

Ask your AI assistant to:

Build the following Next.js pages:

- `/app/(auth)/login/page.tsx` — login form using React Hook Form + Zod. Fields: email, password. Show/hide password toggle. "Forgot password" link. "Sign up" link. Display API error messages below the form.
- `/app/(auth)/signup/page.tsx` — signup form. Fields: full name, email, password, confirm password (client-side match only, confirm password is not sent to server). Password strength indicator (show "Weak / Fair / Strong" based on length + character variety).
- `/app/(auth)/forgot-password/page.tsx` — single email field form.
- `/app/(auth)/reset-password/page.tsx` — new password + confirm password form. Read the reset token from the URL query parameter.
- `/app/(auth)/onboarding/page.tsx` — a multi-step wizard (3 steps):
  - Step 1: Username input (real-time availability check via debounced API call) + full name
  - Step 2: Experience level selection (Beginner / Intermediate / Advanced) — displayed as three cards with descriptions of each level, not a dropdown
  - Step 3: Risk profile (Risk Appetite + Investment Horizon + Primary Goal) — each displayed as radio button cards with explanations

All auth pages:

- Must be accessible before login (public routes).
- Must redirect to `/discover` if the user is already logged in.
- After successful signup, must redirect to `/onboarding`.
- After successful onboarding, must redirect to `/discover`.

Build a `middleware.ts` in `apps/web/` that:

- Redirects unauthenticated users to `/login` if they try to access any `(dashboard)` route.
- Redirects authenticated users who have not completed onboarding to `/onboarding`.
- Allows public access to `/login`, `/signup`, `/forgot-password`, `/reset-password`, and all `/stock/:ticker` pages (public SEO pages).

---

## Prompt 4 — Market Data Pipeline

**[BLOCKING] — Must be complete before Prompt 5 onwards, as all features depend on the stocks database.**

### 4.1 Stocks Master Seeding

Ask your AI assistant to:

Build a one-time seed script at `scripts/seed-stocks-master.ts`. This script:

- Calls the EODHD API to fetch the complete list of instruments for NSE exchange (`https://eodhd.com/api/exchange-symbol-list/NSE?api_token=...&fmt=json`)
- Calls the same endpoint for BSE exchange
- Maps the API response fields to the `stocks` table schema defined in Prompt 0
- Assigns `market_cap_category` based on a predefined cutoff table:
  - Large cap: companies in the Nifty 100 index (fetch the index constituents from BSE to determine this)
  - Mid cap: companies in Nifty Midcap 150 that are not in Nifty 100
  - Small cap: all others above a minimum market cap threshold
  - Micro cap: below that threshold
- Sets `is_active = true` for all currently listed stocks
- Sets `index_memberships` array based on EODHD index constituent data
- Upserts records (does not fail if run twice — use ON CONFLICT DO UPDATE on `isin`)
- Logs progress every 100 records
- Reports a summary at the end: total inserted, total updated, total skipped

The script must be idempotent and safe to run in any environment. It reads `EODHD_API_KEY` from environment. Run it against the development Supabase project first and verify the count (expect 4,000–6,000 rows).

### 4.2 Daily OHLCV Ingestion Pipeline

Ask your AI assistant to:

Build a BullMQ job in `apps/api/src/jobs/daily-price-sync.ts` with a corresponding worker in `apps/api/src/workers/daily-price-sync.worker.ts`.

The job runs every weekday at 7:00 PM IST (after NSE closing at 3:30 PM + 15 min delayed data + 3 hours buffer). Schedule it using BullMQ's `repeat` option with a cron expression.

The worker:

- Fetches the EODHD end-of-day data for all NSE stocks for the current date using the bulk endpoint
- For each stock, finds the corresponding `stock_id` from the `stocks` table using `ticker_nse`
- Upserts a row in `stock_prices_daily` (ON CONFLICT on `(stock_id, date)` DO UPDATE)
- After inserting prices, triggers the alert checker job (Prompt 16 — build the trigger here, the handler comes later)
- Handles errors gracefully: if a single stock fails, log the error and continue with the rest. Do not fail the entire job for one bad ticker.
- On complete success, write a job completion log with count of stocks updated.
- On partial failure (some stocks failed), write a warning log listing failed tickers.

Add a secondary job that runs on weekday mornings at 8:00 AM IST to update the `trending stocks` data (based on view counts from the previous day — this will come from a view counter built in Prompt 8).

### 4.3 Fundamentals Ingestion

Ask your AI assistant to:

Build a BullMQ job and worker for fundamentals ingestion. This job runs once per week on Sunday at 2:00 AM IST.

The worker:

- Iterates over all active stocks in the `stocks` table in batches of 50
- For each batch, calls the EODHD Fundamentals API to fetch the annual and quarterly financial data
- Maps the EODHD response to the `stock_fundamentals` schema exactly as defined in Prompt 0 Section 0.4
- Handles the unit difference: EODHD returns values in the company's reporting currency and scale. Normalise everything to INR crores before storing.
- Upserts rows with ON CONFLICT on `(stock_id, period_type, period_end_date)` DO UPDATE
- Computes and stores the derived ratios (ROE, ROCE, debt_to_equity, margins) from the raw figures before storing — do not rely on EODHD's pre-computed ratios as they sometimes use different denominators
- Respects EODHD rate limits: add a 200ms delay between each batch

Build a companion one-time backfill script at `scripts/backfill-fundamentals.ts` that runs the same logic but fetches 5 years of history for all stocks. Run this once after the seed script.

---

## Prompt 5 — Stock Search

Ask your AI assistant to:

### 5.1 Backend: Search Route

Build `GET /stocks/search` in the Fastify API.

The route:

- Accepts a query parameter `q` (string, minimum 2 characters, maximum 50 characters — validate with Zod)
- Accepts an optional `limit` parameter (integer, 1–20, default 10)
- Searches the `stocks` table using a PostgreSQL full-text search on `company_name` + `ticker_nse` + `ticker_bse`
- Also does a prefix match on `ticker_nse` (most users will type NSE tickers exactly)
- Orders results: exact ticker matches first, then starts-with matches on name, then full-text matches
- Returns only active stocks (`is_active = true`)
- Returns: `id, ticker_nse, ticker_bse, company_name, sector, market_cap_category, logo_url`
- Caches results in Upstash Redis with a 5-minute TTL — cache key: `search:{normalised_query}:{limit}`
- Bypasses cache for queries under 3 characters (too broad to be worth caching)

Edge cases to handle:

- Empty query: return HTTP 400
- Query with only special characters: sanitise and return empty results
- No matches found: return HTTP 200 with empty array (not 404)

### 5.2 Frontend: Search Component

Build a `StockSearchBar` component in `components/discover/StockSearchBar.tsx`.

The component:

- Is a text input with a dropdown results panel below it
- Uses a debounce of 300ms before calling the API to avoid a request on every keystroke
- Shows a loading spinner inside the input while the request is in flight
- Shows results in a dropdown, each result showing: company logo (with fallback), company name, NSE ticker, sector badge, market cap category badge
- On result click: navigates to `/stock/{ticker_nse}`
- Keyboard navigation: arrow keys to move through results, Enter to select, Escape to close
- Shows "No results for '{query}'" if the API returns empty
- On the desktop layout: appears in the top navigation bar. On mobile: appears as a full-screen search overlay triggered by a search icon button.
- Uses TanStack Query's `useQuery` with `enabled: query.length >= 2` to avoid fetching on empty input

---

## Prompt 6 — Stock Overview Card

### 6.1 Backend: Stock Overview Data Endpoint

Ask your AI assistant to:

Build `GET /stocks/{ticker}` in the Fastify API. This is the main stock page data endpoint.

The route:

- Validates `ticker` is a valid NSE ticker (alphanumeric, 2–20 characters)
- Looks up the stock in the `stocks` table by `ticker_nse`
- Returns 404 if not found or if `is_active = false`
- Fetches the latest price from `stock_prices_daily` (most recent date)
- Fetches the fundamentals from `stock_fundamentals` — latest annual period and latest quarterly period
- Fetches the last 3 corporate actions from `corporate_actions`
- Assembles the full response matching the `StockOverview` type from `packages/shared`
- Caches the assembled response in Upstash Redis with a 1-hour TTL. Cache key: `stock_overview:{ticker}:{today_date}`
- Checks the cache before hitting the database (cache-first strategy)

Also build `GET /stocks/{ticker}/price` which returns only the latest price data (close, open, high, low, volume, 1-day change %, 52-week high, 52-week low) with a 15-minute TTL cache.

### 6.2 AI: Stock Overview Card Narrative

Ask your AI assistant to:

Build a FastAPI endpoint `POST /ai/stock/overview` that accepts the structured stock data and generates the narrative sections using the system prompt from `indian_stock_platform_prompt_guide.md` Section 1.5.

Implementation requirements:

- The system prompt is stored in `services/ai/app/prompts/stock_overview.py` as a constant string. It must exactly match the system prompt in the guide document.
- Use Claude 3.5 Haiku for this task (it is a summary task, not complex analysis).
- Enable Anthropic prompt caching on the system prompt by adding the `cache_control` field to the system message.
- The user message contains only the structured stock data as JSON.
- Cache the AI response in the `ai_response_cache` Supabase table with a 24-hour expiry. Cache key format: `stock_overview:{ticker_nse}:{today_date}`.
- Before calling the LLM, check the database cache. If a valid (non-expired) cache entry exists, return it directly without calling the LLM.
- The response must be validated against a Pydantic model before returning.

### 6.3 Frontend: Stock Overview Page

Ask your AI assistant to:

Build the page at `/app/(dashboard)/stock/[ticker]/page.tsx` and the `StockOverviewCard` component.

The page:

- Is a Next.js server component that fetches the stock data using the `GET /stocks/{ticker}` endpoint server-side for SEO (so the stock data is in the HTML when search engines crawl it)
- Falls back to client-side data fetching for real-time price updates using TanStack Query polling every 60 seconds

The `StockOverviewCard` component shows:

- Company name and NSE ticker prominently at the top
- Current price, 1-day change (absolute ₹ and %, coloured green/red)
- 52-week high and low with the current price positioned as a percentage between the two (visual slider)
- Market cap, sector, industry as badges
- Key metrics in a responsive grid: P/E, P/B, EV/EBITDA, ROE, ROCE, Debt/Equity, Dividend Yield
- Each metric has a tooltip (using the shadcn Tooltip component) that shows a plain-English explanation from the Glossary data
- "Add to Watchlist" button — if already in watchlist, show "In Watchlist" with a checkmark and option to remove
- AI-generated business narrative section (the narrative from the AI service) — displayed with a "Powered by AI" subtle badge and the standard informational disclaimer
- A Skeleton loading state for all sections while data loads

---

## Prompt 7 — Sector Heatmap

### 7.1 Backend: Heatmap Data Endpoint

Ask your AI assistant to:

Build `GET /stocks/heatmap` in the Fastify API.

The endpoint:

- Fetches today's price data for all active stocks grouped by sector
- For each sector, computes:
  - Overall sector performance (market-cap-weighted average of daily % change)
  - Top 3 gaining stocks in the sector (by % change)
  - Top 3 losing stocks in the sector (by % change)
  - Number of stocks that are positive vs negative
- Returns the structured heatmap data matching the format expected by the heatmap AI prompt
- Caches results with a 5-minute TTL (heatmap refreshes every 5 minutes during market hours, hourly after market close)
- During market hours (9:15 AM – 3:30 PM IST on weekdays), serve fresh data with 5-minute cache. Outside these hours, serve the closing data with a 1-hour cache.

### 7.2 AI: Heatmap Narrative

Ask your AI assistant to:

Build `POST /ai/heatmap/summary` in the Python AI service. This accepts the heatmap JSON data and generates a 200-word plain-English market summary using the system prompt from Section 1.3 of the guide.

Use Claude 3.5 Haiku. Cache the response for 15 minutes. If called within 15 minutes of the previous call with the same data, return the cached response.

### 7.3 Frontend: Heatmap Component

Ask your AI assistant to:

Build the `SectorHeatmap` component in `components/discover/SectorHeatmap.tsx`.

The component:

- Renders a grid of sector tiles using TradingView Lightweight Charts' rectangle primitive, or if that is not suitable, use a custom SVG/div treemap approach where each tile's size is proportional to the sector's total market cap
- Each tile shows: sector name, today's % change, number of advancing/declining stocks
- Tile background colour: gradient from deep red (worst performance, e.g., -3% or worse) through white/neutral (flat) to deep green (best performance, e.g., +3% or better)
- Clicking a sector tile opens a side panel (shadcn Sheet component) showing:
  - Sector performance details
  - Top 5 stocks in that sector today (by absolute market cap)
  - AI-generated sector narrative for that day
- Shows a "Last updated: HH:MM AM/PM" timestamp
- Shows a pulsing green dot indicator during market hours to signal live data
- Auto-refreshes every 5 minutes during market hours using TanStack Query's `refetchInterval`
- Shows a full-screen Skeleton during the initial load

---

## Prompt 8 — AI Stock Screener

### 8.1 Backend: Screener Query Executor

Ask your AI assistant to:

Build `POST /stocks/screener` in the Fastify API.

The endpoint accepts two modes:

1. **Structured filter mode**: a JSON array of filters, each with `{ field, operator, value }`. Directly converts this to a Prisma query with WHERE clauses.
2. **Natural language mode**: a string query like "find IT stocks with high ROE and low debt". This is forwarded to the AI service to parse into structured filters, then the structured filters are executed.

Supported filter fields: `sector`, `industry`, `market_cap_category`, `p_e_ratio`, `p_b_ratio`, `roe`, `roce`, `debt_to_equity`, `revenue_growth_3y`, `pat_growth_3y`, `dividend_yield`, `promoter_holding`, `52_week_high_pct`, `52_week_low_pct`.

Supported operators: `gt` (greater than), `lt` (less than), `gte`, `lte`, `eq`, `neq`, `in` (for array values like `sector IN [IT, Pharma]`).

The query executor:

- Joins `stocks` with `stock_fundamentals` (latest annual period) and `stock_prices_daily` (latest date)
- Applies all filters as WHERE conditions
- Returns a maximum of 100 results (prevent abuse)
- Each result includes: `ticker_nse, company_name, sector, market_cap_category, current_price, p_e_ratio, roe, roce, debt_to_equity, revenue_growth_3y`
- Supports `sort_by` and `sort_order` parameters
- Caches results for 10 minutes with a cache key that is a hash of the full filter set

### 8.2 AI: Natural Language Screener Parser

Ask your AI assistant to:

Build `POST /ai/screener/parse` in the Python AI service.

This endpoint:

- Takes a natural language query string
- Uses Claude 3.5 Haiku with the system prompt from Section 1.1 of the guide document
- Returns a structured JSON matching the filter format that `POST /stocks/screener` accepts
- Validates the output with a Pydantic model before returning — if the LLM returns malformed JSON, retry once, then return a descriptive error
- Input length limit: 200 characters. Reject with HTTP 400 if longer.
- Prompt injection prevention: strip HTML, check for injection patterns before sending to LLM

### 8.3 Frontend: Screener UI

Ask your AI assistant to:

Build the Screener feature at `/app/(dashboard)/discover/screener/page.tsx`.

The page has two modes toggled by a tab:

**Natural Language Mode (default):**

- A prominent text input: "Describe the stocks you're looking for..." with a submit button
- Example queries shown as clickable chips below the input: "IT stocks with low debt and high ROE", "Profitable mid-cap pharma companies", "Dividend-paying PSU banks"
- After submitting, show the parsed filters as a visual filter list so the user can see and optionally edit what the AI extracted before running the screen
- A "Run Screen" button that executes the query

**Manual Filter Builder Mode:**

- A list of filter rows, each with: field selector dropdown + operator dropdown + value input
- "Add Filter" button to add a new row
- "Remove" button on each row
- Sector and industry fields show a multi-select dropdown
- Numeric fields show a numeric input with the correct unit label (₹, %, x)

Both modes share the same results table:

- Columns: Company, Sector, Market Cap, Price, P/E, ROE, ROCE, D/E, 3Y Revenue Growth
- Each row has an "Add to Watchlist" icon button
- Clicking a company name navigates to the stock overview page
- Shows the number of results found and a "Showing X of Y" indicator
- Shows a Skeleton while loading
- Shows "No stocks match your criteria. Try adjusting the filters." if empty

---

## Prompt 9 — Watchlist

### 9.1 Backend: Watchlist Routes

Ask your AI assistant to build all four watchlist routes as defined in Prompt 0 Section 0.5.

Additional requirements:

- `POST /watchlist`: before inserting, verify the `stock_id` exists in the `stocks` table (prevents adding invalid stocks). Return HTTP 409 if the stock is already in the watchlist.
- `PATCH /watchlist/{id}`: only `user_notes` and `price_target` can be updated — never `stock_id` or `watchlist_id`.
- All routes must enforce the user's ownership (authenticated user's `user_id` must match the watchlist's `user_id`) at the application layer, not just via RLS.
- After adding a stock to the watchlist, enqueue a BullMQ job to suggest relevant price alerts for that stock (this job will create the suggested alert data in Prompt 16 — build the job enqueue here).

### 9.2 Frontend: Watchlist Page

Ask your AI assistant to:

Build `/app/(dashboard)/discover/watchlist/page.tsx` and the `WatchlistTable` component.

The watchlist page:

- Shows all watchlisted stocks in a table with columns: Company Name & Ticker, Date Added, Noted Price, Current Price, Change Since Added (₹ and %), Price Target (if set), Actions
- The "Change Since Added" column: shows the % change from `noted_price` to `current_price` if `noted_price` was set, otherwise shows 1-day change
- Current prices are live (TanStack Query polling every 60 seconds)
- Clicking the company name opens the stock overview card in a side sheet (shadcn Sheet) without navigating away — the full stock page is still accessible via a "Full Details" link in the sheet
- Each row has an "Actions" column with: "Set Price Target", "Edit Notes", "Remove"
- "Set Price Target" opens a small inline form to set a price level. After setting it, also prompts "Would you like an alert when this level is reached?" with a one-click yes/no — this pre-fills the alert creation form
- Empty state: "Your watchlist is empty. Search for stocks above and add them here."
- Mobile layout: each stock is a card, not a table row

Build a `WatchlistButton` component used on the Stock Overview Card and Screener results — a single button/icon that:

- Shows a bookmark icon (not filled) if the stock is not in the watchlist
- Shows a filled bookmark if it is in the watchlist
- On click: calls the API to add or remove the stock
- Uses optimistic UI updates (update the UI immediately, revert if the API call fails)
- Shows a toast notification on add: "RELIANCE added to watchlist" and on remove: "RELIANCE removed from watchlist"

---

## Prompt 10 — Trending Stocks Widget

Ask your AI assistant to:

### 10.1 Backend: View Counter and Trending

Build a Redis-based view counter. Every time the `GET /stocks/{ticker}` endpoint is called by an authenticated user, increment a Redis sorted set key `trending:stocks:{today_date}` with the stock's NSE ticker as the member and the score as the view count.

Build `GET /stocks/trending` which:

- Reads the top 10 members from the sorted set by score (highest view count)
- Returns the stock details (name, ticker, current price, 1-day % change, sector) for each
- Cache this result for 5 minutes since it does not need to be real-time precise

### 10.2 Frontend: Trending Stocks Widget

Build `TrendingStocksWidget` in `components/discover/TrendingStocksWidget.tsx`.

The widget:

- Shows as a compact card or panel (not a full page — it appears in a sidebar or on the discover homepage)
- Lists 10 stocks with rank number, company name, ticker, sector, and 1-day % change
- % change is coloured green/red
- Each item links to the stock overview page
- Shows a "Most viewed today" heading with a fire emoji (🔥) to make it feel current
- Refreshes every 5 minutes
- Skeleton loading state

---

## Prompt 11 — Ask AI: Chat Interface and Infrastructure

**[BLOCKING] — Build this before Prompts 12–14, which add specific conversation modes on top of this infrastructure.**

### 11.1 Backend: Chat Proxy Route

Ask your AI assistant to:

Build `POST /chat/message` in the Fastify API.

This route:

- Validates the request: `{ message: string (max 500 chars), conversation_id?: string }`. Reject if message is empty or over 500 characters.
- Applies prompt injection sanitisation to the `message` field.
- If `conversation_id` is provided, verifies it belongs to the authenticated user. If not provided, creates a new conversation row.
- Loads the last 10 messages from the conversation as context (to give the AI memory within a session).
- Calls the Python AI service's `POST /ai/chat` endpoint, passing the message, conversation history, and the user's profile context (experience level, risk profile — to personalise responses).
- Receives the AI response (text only).
- Saves both the user's message and the AI response to `chat_messages`.
- Returns `{ conversation_id, message_id, content, metadata }` to the frontend.
- Rate limits this route at 10 requests per minute per user (defined in Prompt 0).

Also build:

- `GET /chat/conversations` — returns a list of the user's last 20 conversations (id, title, created_at, last message preview)
- `GET /chat/conversations/{id}` — returns a conversation with all its messages

### 11.2 AI: Global Chat Service

Ask your AI assistant to:

Build `POST /ai/chat` in the Python FastAPI service.

This endpoint receives: `{ message, conversation_history: [{ role, content }], user_context: { experience_level, risk_profile } }`.

The service:

- Selects the appropriate system prompt based on query classification:
  - First, run a lightweight Claude 3.5 Haiku call to classify the query type: `stock_qa`, `concept_explanation`, `stock_comparison`, `portfolio_qa`, `market_news`, `general`
  - Based on the type, select the appropriate system prompt (stock Q&A prompt, concept explainer prompt, comparison prompt, etc.)
- Builds the messages array: `[{ role: "system", content: system_prompt_with_cache_control }, ...conversation_history, { role: "user", content: message }]`
- Applies prompt caching on the system prompt (add `cache_control: { "type": "ephemeral" }` to the system message)
- Calls Claude 3.5 Haiku for `concept_explanation`, `stock_comparison`, and `general` types
- Calls Claude 3.5 Haiku for `stock_qa` with basic stock data
- Falls back to GPT-4o-mini if the Anthropic API returns an error (implement as a try/except with a fallback call)
- Returns the response text and the detected query type in metadata

All system prompts used in this service must be loaded from the `prompts/` directory — not hardcoded inline in the route handler.

### 11.3 Frontend: Floating Chat Interface

Ask your AI assistant to:

Build the global floating chat interface as a persistent UI element on all dashboard pages.

Architecture: The chat panel is a Zustand store (`useChatStore`) with state: `isOpen: boolean`, `conversations: Conversation[]`, `activeConversationId: string | null`.

Build the following components:

`GlobalChatButton` — a floating action button (bottom-right corner on all pages, z-index above all content). Shows a speech bubble icon. Shows a red badge with unread count if there are unread AI responses. Clicking it toggles `isOpen` in the Zustand store. Appears on every page via the root layout.

`ChatPanel` — a sliding panel (not a modal, not a page) that slides in from the right side. On desktop: 420px wide, full viewport height. On mobile: full screen.

The panel contains:

- A header with "Ask AI" title, a "New Chat" button, and a close button
- A conversation history sidebar (only on desktop, toggled by a history icon button) that lists past conversations
- The main chat area showing the current conversation's messages
- A text input at the bottom with a send button. The input expands for multi-line. Pressing Enter sends; Shift+Enter adds a new line.
- Character counter showing remaining characters (500 max)
- A "Clear" icon that clears the current conversation (with confirmation)

Message rendering:

- User messages: right-aligned, dark background bubble
- Assistant messages: left-aligned, light background bubble
- Assistant messages render Markdown (use a safe Markdown renderer — bold, italic, bullet points, tables are allowed; no HTML rendering)
- Every assistant message ends with the disclaimer text rendered in a smaller, muted style
- While waiting for a response, show a typing indicator (three animated dots)

Starter prompts: on a new conversation with no messages, show 4 clickable suggestion cards:

- "Tell me about a company (e.g., Reliance, TCS)"
- "Explain a financial concept"
- "Compare two stocks"
- "What's happening in the market today?"

---

## Prompt 12 — Ask AI: Stock Q&A Mode

Ask your AI assistant to:

### 12.1 Enhance the AI Chat Service for Stock Q&A

In the Python AI service, implement the `stock_qa` query handler.

When the query is classified as `stock_qa`:

- Extract the mentioned stock ticker or company name from the query using a lightweight Claude Haiku call
- Fetch the stock's current data from the Node.js API (price + key fundamentals) — the AI service calls the internal API to get this data
- Inject this structured data into the user message context before sending to Claude Haiku
- The system prompt used is exactly the system prompt from Section 5.1 of `indian_stock_platform_prompt_guide.md`
- The response must adhere to all STRICT RULES in that prompt — no buy/sell/directional language

### 12.2 Frontend Enhancements for Stock Q&A

In the ChatPanel, when the assistant response contains stock data:

- Render a compact `MiniStockCard` inline in the chat bubble — showing the stock's price, 1-day change, and 3 key metrics
- This card links to the full stock overview page
- The card appears above the text response, not replacing it

---

## Prompt 13 — Ask AI: Concept Explainer Mode

Ask your AI assistant to:

In the Python AI service, implement the `concept_explanation` handler.

When the query is classified as `concept_explanation`:

- Use the system prompt from Section 5.3 of the guide document exactly
- Use Claude 3.5 Haiku
- Structure the response to clearly separate: Definition → Example → Why It Matters → Rule of Thumb → Related Terms

In the ChatPanel frontend:

- When the assistant response contains a concept explanation, render it in a structured card layout (not just plain text bubbles) — each section (Definition, Example, etc.) as a clearly labelled sub-section
- At the bottom of a concept card, show "Related concepts" as clickable chips — clicking one sends a new message automatically asking about that concept

Ensure the glossary tooltip on the stock overview card also triggers this same concept explainer mode in the chat panel. When a user taps a ratio tooltip, it should open the chat panel and immediately show the concept explanation for that ratio.

---

## Prompt 14 — Ask AI: Stock Comparison Mode

Ask your AI assistant to:

In the Python AI service, implement the `stock_comparison` handler.

When the query is classified as `stock_comparison`:

- Extract the two (or more) stock names/tickers from the query
- Fetch the current data for each stock from the internal API
- Use the comparison system prompt from Section 5.4 of the guide document
- Note: Section 5.4's "verdict" language must be removed in line with the platform's no-influence policy — the response should present the comparison data and let the user draw their own conclusions. Adapt the system prompt accordingly. End the narrative with data observations only, not a directional conclusion.
- Use Claude 3.5 Haiku

In the ChatPanel frontend:

- When the response is a comparison, render the comparison table inline in the chat panel as a proper HTML table (not a text-art table) — use TailwindCSS for styling
- The table should be horizontally scrollable on mobile since it contains multiple columns
- Each stock name in the table is a link to its overview page

---

## Prompt 15 — Smart Alerts: Price Alert Setup

### 15.1 Backend: Alert Routes

Ask your AI assistant to:

Build all alert routes as defined in Prompt 0 Section 0.5.

Implementation details for `POST /alerts`:

- Validate that the `stock_id` exists and is active
- Validate that `target_price` is a positive number and is not greater than 10x or less than 0.1x the current price (prevent obviously wrong alerts)
- A user can have a maximum of 50 active alerts total — return HTTP 422 with a clear message if this limit is exceeded
- Each stock can have at most one `price_above` and one `price_below` alert per user — upsert instead of duplicate insert
- After creating, immediately check if the alert is already triggered (e.g., user sets a "price above" alert below the current price) — if so, mark it triggered immediately and send a notification

Implementation details for the alert checker worker (the job enqueued from the daily price sync in Prompt 4):

- This BullMQ worker runs after every daily price update
- Queries all `price_alerts` where `is_active = true` and `is_triggered = false`
- For each alert, fetches the stock's current (end-of-day) price
- Checks: if `alert_type = price_above` and `current_price >= target_price`, the alert is triggered
- Checks: if `alert_type = price_below` and `current_price <= target_price`, the alert is triggered
- On trigger: sets `is_triggered = true`, `triggered_at = now()`, `triggered_price = current_price`
- Creates a row in `notifications` for the triggered alert
- Broadcasts the notification via Supabase Realtime to the user's session

### 15.2 Frontend: Alert Creation Form

Ask your AI assistant to:

Build the alert creation UI in `components/alerts/AlertForm.tsx`.

The component is used in multiple places:

- As a standalone dialog triggered by an "Add Alert" button on the stock overview card
- As an inline form in the Watchlist when a user sets a price target

The form:

- Shows the stock name and current price prominently at the top
- Alert type selection: two large cards — "Alert me when price goes ABOVE ₹**" and "Alert me when price goes BELOW ₹**"
- The price input pre-fills with a suggested value: for "above", the nearest round number above current price; for "below", the nearest round number below
- Validation: price must be a positive number, between ₹0.01 and ₹1,000,000
- Shows the distance from current price: "₹45 below current price (−9.5%)"
- Submit button: "Set Alert"
- On success: shows a toast "Alert set for RELIANCE at ₹450"

---

## Prompt 16 — Smart Alerts: In-App Notification Panel

### 16.1 Backend: Notification Delivery

Ask your AI assistant to:

After the alert checker worker triggers an alert and creates a `notifications` row, broadcast it in real time using Supabase Realtime. Insert into the `notifications` table — Supabase Realtime automatically broadcasts the INSERT event to all subscribed clients.

The `notifications` row for a price alert must contain:

- `type: price_alert`
- `title`: "Price Alert: RELIANCE" 
- `body`: "RELIANCE (NSE) crossed your target of ₹450. Current price: ₹452.30"
- `metadata`: `{ stock_id, alert_id, ticker_nse, target_price, triggered_price, alert_type }`

Build `GET /notifications` which returns the user's last 50 notifications ordered by `created_at DESC`. Include `is_read` status for each.

Build `PATCH /notifications/{id}/read` and `PATCH /notifications/read-all`.

### 16.2 Frontend: Notification Bell and Drawer

Ask your AI assistant to:

Build the notification system as a persistent UI element in the top navigation bar.

`NotificationBell` component:

- A bell icon in the header navigation
- Shows a red badge with the count of unread notifications (max display: "9+" if over 9)
- Clicking it opens the `NotificationDrawer`
- Subscribes to Supabase Realtime for INSERT events on the user's `notifications` rows — when a new notification arrives, increment the badge count and show a toast notification as well
- When the drawer is opened, marks all visible notifications as read after 2 seconds

`NotificationDrawer` component (shadcn Sheet from the right side):

- Header: "Notifications" title and "Mark all read" link
- Each notification item shows: notification type icon (bell for price alert), title, body, time ago (e.g., "2 minutes ago"), and an unread dot if not read
- Price alert notifications have a "View Stock" button that navigates to the stock's overview page
- Empty state: "No notifications yet. Set price alerts on stocks you follow."
- Infinite scroll (load 50 more on scroll to bottom) using TanStack Query `useInfiniteQuery`

---

## Prompt 17 — Application Polish and Edge Cases

Before proceeding to testing prompts, ask your AI assistant to handle all the following cross-cutting concerns:

### 17.1 Loading States

Every data-fetching component must have three clearly implemented states:

- **Loading**: Show Skeleton components that match the shape of the actual content. Do not use generic spinners for content areas — Skeletons provide better perceived performance.
- **Error**: Show an error card with: error icon, a user-friendly message (never expose raw error messages or stack traces), and a "Try again" button that retries the query.
- **Empty**: Show a helpful empty state with: an icon, a clear explanation of why it is empty, and a call-to-action (e.g., "Add stocks to your watchlist to see them here").

### 17.2 Toasts and Feedback

Install and configure the shadcn/ui `Toaster` component globally. Every user action that modifies data must show a toast:

- Success: green, 3-second auto-dismiss
- Error: red, 5-second auto-dismiss, with the error message
- Info: neutral, 3-second auto-dismiss

### 17.3 Responsive Design

Verify all R1 pages on three viewport sizes: 375px (iPhone SE), 768px (iPad), 1440px (desktop). Every page must be fully functional and visually correct at all three sizes. Common issues to check: tables that overflow on mobile (must scroll horizontally), chat panel that must be full-screen on mobile, heatmap that must re-layout on smaller screens.

### 17.4 Accessibility

Every interactive element must have:

- Keyboard focus indicators (do not remove the default browser outline — style it with TailwindCSS `focus-visible:ring` classes)
- Appropriate ARIA labels on icon-only buttons (e.g., the close button on the chat panel must have `aria-label="Close chat panel"`)
- Colour is never the only means of communicating information (the green/red price change must also show a ▲/▼ arrow symbol)

### 17.5 SEO

The stock overview page at `/stock/{ticker}` is publicly crawlable. Ensure:

- `generateMetadata` in the page file returns `{ title: "{Company Name} ({TICKER}) — Stock Analysis | Investom", description: "..." }`
- The page has proper `<h1>` tags
- Structured data (`JSON-LD`) for the stock entity on the page

### 17.6 Disclaimer Enforcement

Audit every AI-generated output location in the frontend. Each one must display the exact disclaimer string: `"This is data and analysis only — not investment advice. Investom is not a SEBI-registered investment adviser."` Style it consistently: 12px font, muted colour, always visible below the AI content, never collapsible.

---

## Prompt 18 — CI/CD Pipeline

Ask your AI assistant to:

Build the GitHub Actions workflows in `.github/workflows/`.

`**ci.yml`** — runs on every pull request to `main`:

1. Checkout code
2. Install dependencies for all three services
3. Run TypeScript type checking: `tsc --noEmit` in `apps/web` and `apps/api`
4. Run ESLint in `apps/web` and `apps/api`
5. Run Vitest in `apps/web` and `apps/api` with coverage reporting
6. Run pytest in `services/ai` with coverage reporting
7. Build the Next.js app to verify no build errors
8. Post a coverage report as a comment on the pull request
9. Fail the PR if coverage drops below 80% on the API service

`**deploy.yml**` — runs only on merge to `main`:

1. Run all CI checks first (reuse the CI workflow as a dependency)
2. Deploy the Next.js app to Vercel (using the Vercel CLI and `VERCEL_TOKEN` secret)
3. Deploy the Node.js API to Railway (using the Railway CLI and `RAILWAY_TOKEN` secret)
4. Deploy the Python AI service to Modal.com (using the Modal CLI and `MODAL_TOKEN` secret)
5. Run database migrations against production using `prisma migrate deploy`
6. Send a deployment notification to a Slack channel (optional, configure `SLACK_WEBHOOK_URL` secret)

---

## Prompt 19 — Unit Tests

Ask your AI assistant to write complete unit tests for every function and component in Release 1. No code should be shipped without tests. Work through each area:

### 19.1 Backend Unit Tests (Vitest)

For each Fastify route, write unit tests that:

- Mock the Prisma client and all external service calls
- Test the happy path (correct input → correct response)
- Test validation errors: missing required fields, wrong types, values out of range
- Test authentication: unauthenticated request returns 401, wrong user's resource returns 403
- Test rate limiting: verify the rate limit headers are present in responses
- Test cache behaviour: first call hits the database, second call returns the cached result

Specific tests to write:

- `POST /auth/signup`: valid data succeeds; duplicate email returns 409; weak password returns 422; reserved username returns 422
- `GET /stocks/search`: query under 2 characters returns 400; valid query returns matching results; no results returns empty array with 200; injection characters are sanitised
- `GET /stocks/{ticker}`: invalid ticker returns 404; inactive stock returns 404; valid ticker returns 200 with correct shape; response is cached on second call
- `POST /watchlist`: adding same stock twice returns 409; adding to another user's watchlist returns 403; stock_id not found in stocks table returns 404
- `DELETE /watchlist/{id}`: deleting another user's item returns 403; deleting own item returns 200
- `POST /alerts`: price over 10x current price returns 422; price under 0.1x current price returns 422; 51st alert for a user returns 422; duplicate alert_type for same stock upserts, not duplicates
- `POST /chat/message`: message over 500 characters returns 400; injection patterns in message returns 400; unauthenticated returns 401

For each Zod schema:

- Test that all valid combinations of input pass
- Test that every invalid field (wrong type, missing required, over limit, under limit) fails with a descriptive error

For each utility function (`calculatePriceChange`, `formatCurrency`, `formatPercentage`, `buildCacheKey`, `sanitiseUserInput`):

- Test all edge cases: zero values, negative values, very large numbers, undefined/null inputs, special characters

### 19.2 Frontend Unit Tests (Vitest + Testing Library)

For each component, write tests covering:

- The component renders without crashing
- Loading state renders Skeleton correctly
- Error state renders the error card with retry button
- Empty state renders the correct empty message
- Happy path renders the correct data
- Interactive elements work (button clicks trigger the correct functions/store updates)

Specific component tests:

- `StockSearchBar`: debounce prevents API call on every keystroke; results dropdown appears after typing 2+ characters; keyboard navigation works (ArrowDown selects first result, Enter navigates); Escape closes dropdown; clicking outside closes dropdown
- `WatchlistButton`: renders "not in watchlist" state correctly; clicking adds to watchlist (optimistic update); if API fails, reverts the optimistic update and shows error toast; renders "in watchlist" state after adding
- `ChatPanel`: starts with empty state and starter prompt cards; sending a message adds a user bubble; typing indicator appears while waiting; assistant response appears and disclaimer is present; character counter updates as user types; send button disabled when input is empty
- `NotificationBell`: shows badge count of 0 initially; Realtime event increments badge; clicking bell opens drawer; opening drawer triggers mark-read after 2 seconds
- `AlertForm`: shows current price; validates price is in range; "above" type pre-fills with price above current; form submission calls the API; success shows toast
- `SectorHeatmap`: renders all sectors; clicking a sector tile opens the side sheet; during market hours shows pulsing dot indicator

For all Zustand stores:

- `useChatStore`: initial state is correct; `setIsOpen` updates the state; `addMessage` appends to the correct conversation
- `useAlertStore` (if created): adding an alert updates the list; removing an alert removes from list

### 19.3 Python Unit Tests (pytest)

For each AI service function:

- Mock all Anthropic and OpenAI API calls using `unittest.mock.patch`
- Test that the correct model is used for each query type (Haiku vs Sonnet)
- Test that prompt caching headers are included in system messages
- Test that the fallback to GPT-4o-mini occurs when Anthropic raises an exception
- Test that the cache check happens before the LLM call
- Test that malformed LLM responses (non-JSON when JSON is expected) trigger a retry

Specific tests:

- `classify_query_type`: each of the 6 query types is classified correctly from representative inputs; unknown types default to `general`
- `build_stock_qa_prompt`: stock data is correctly injected into the message context; injection patterns in the user query are sanitised before prompt building
- `parse_screener_query`: valid natural language returns correctly structured filters; LLM returns malformed JSON → retry → second attempt succeeds; second attempt also fails → returns HTTP 500 with error message
- `build_comparison_response`: two stocks are compared correctly; three stocks are handled; stocks with incomplete data show null values for missing metrics

---

## Prompt 20 — Integration Tests

Ask your AI assistant to write integration tests. These tests call the actual running services against a test database.

### 20.1 Test Environment Setup

Set up a dedicated integration test environment:

- A separate Supabase project named `investom-test`
- Upstash Redis with a test prefix on all keys to prevent pollution
- All tests run within database transactions that are rolled back after each test (for tests that write data)
- A test user is created once at the start of the test suite and a valid JWT is obtained to use in all authenticated route tests

Create a `test-setup.ts` file (for TypeScript) and `conftest.py` (for Python) that:

- Connects to the test database
- Seeds the minimum required data: 10 real NSE stocks with price data and fundamentals (use real EODHD data fixtures stored in `__tests__/fixtures/`)
- Creates a test user with a complete profile and risk profile
- Provides helper functions: `getAuthHeader()`, `createWatchlistItem(stockId)`, `createAlert(stockId, type, price)`

### 20.2 API Integration Tests

**Auth flow integration:**

- Sign up a new user → verify profile and watchlist rows are auto-created in the database → log in → get valid JWT → access protected route → log out → access protected route with old JWT returns 401

**Stocks data flow:**

- Call `GET /stocks/search?q=RELIANCE` → verify RELIANCE appears in results → call `GET /stocks/RELIANCE` → verify all fields are present and correctly typed → call the same endpoint again → verify the response has the `X-Cache: HIT` header (or equivalent)

**Watchlist flow:**

- Add a stock to watchlist → verify row in database → try to add same stock again → verify 409 → update notes → verify notes updated in database → remove from watchlist → verify row deleted

**Alert flow:**

- Create a `price_above` alert for stock at a price below current price → verify alert is immediately triggered and a notification is created → create a `price_below` alert at a reasonable price → verify alert is active and not triggered → simulate the alert checker worker with test price data that crosses the threshold → verify alert is triggered and notification is created

**Chat flow:**

- Send a message to the chat endpoint → verify conversation is created → verify message is saved → verify AI response is received and saved → send a follow-up message in the same conversation → verify conversation history is passed to the AI service (mock the AI service in this test) → verify the response is appended to the conversation

### 20.3 Data Pipeline Integration Tests

**EODHD ingestion:**

- Using a recorded API response fixture (not a live call — record the response once, store it in `__tests__/fixtures/eodhd/`), run the daily price sync job → verify the correct number of rows are upserted in `stock_prices_daily` → run the job again with the same data → verify it is idempotent (no new rows, existing rows updated)

**Alert checker:**

- Insert price data where stock X's close price is above an active alert's target price → run the alert checker worker → verify the alert is marked as triggered → verify a notification row is created → run the checker again → verify no duplicate notification is created

### 20.4 Supabase Realtime Integration Test

- Subscribe to the authenticated user's `notifications` channel using the Supabase JS client
- Insert a notification row via the service role (simulating the alert checker)
- Verify the Realtime event is received within 5 seconds
- Verify the event payload matches the inserted row

---

## Prompt 21 — End-to-End Tests

Ask your AI assistant to write Playwright E2E tests. These run against the staging environment.

### 21.1 Playwright Setup

Configure Playwright in `apps/web/playwright.config.ts`:

- Base URL: staging environment URL (from `PLAYWRIGHT_BASE_URL` environment variable)
- Browsers to test: Chromium (desktop), Chromium (mobile viewport — 390x844), Firefox (desktop)
- Retries: 2 on failure in CI, 0 locally
- Screenshots on failure: yes
- Video recording on failure: yes
- Test fixtures: a `loggedInPage` fixture that performs login once per test file and reuses the authenticated session (store session state in `playwright/.auth/user.json` and load it for authenticated tests)

### 21.2 User Journey Tests

Write complete E2E tests for every critical user journey in Release 1:

**Journey 1 — New User Signup and Onboarding:**

1. Navigate to the homepage — verify redirect to `/login`
2. Click "Sign up" — verify navigation to `/signup`
3. Fill in name, email (use a unique email with a timestamp to prevent conflicts), password
4. Submit — verify redirect to `/onboarding`
5. Enter username — verify real-time availability check
6. Select "Beginner" experience level
7. Select risk profile: Moderate risk, Medium term, Wealth creation
8. Click "Complete Setup" — verify redirect to `/discover`
9. Verify the welcome message or onboarding completion indicator is visible

**Journey 2 — Stock Discovery and Search:**

1. Log in as the test user
2. Click the search bar in the navigation
3. Type "INFY" — verify dropdown appears with Infosys as first result
4. Click Infosys — verify navigation to `/stock/INFY`
5. Verify the stock overview card shows: company name, current price, key metrics grid
6. Verify the "Add to Watchlist" button is visible
7. Verify the disclaimer text is present

**Journey 3 — Watchlist Management:**

1. From the stock overview page for INFY, click "Add to Watchlist"
2. Verify the button changes to "In Watchlist"
3. Verify a success toast appears
4. Navigate to `/discover/watchlist`
5. Verify INFY appears in the watchlist table
6. Click "Set Price Target" on the INFY row — fill in a price
7. Save — verify the price target appears in the table
8. Click "Remove" — confirm removal — verify INFY is no longer in the table

**Journey 4 — Sector Heatmap:**

1. Navigate to `/discover`
2. Verify the sector heatmap is visible with multiple sector tiles
3. Verify tiles have colour (not all grey — data must have loaded)
4. Click on the "IT" sector tile
5. Verify a side panel opens with IT sector details
6. Verify the panel shows top stocks and an AI-generated narrative
7. Verify the disclaimer is present in the AI narrative

**Journey 5 — AI Screener:**

1. Navigate to the screener page
2. Type "profitable mid-cap IT companies with low debt" in the natural language input
3. Click submit
4. Verify a filter preview appears (e.g., sector = IT, market_cap_category = mid_cap, debt_to_equity < 0.5)
5. Click "Run Screen"
6. Verify results appear in the table with at least one result
7. Click a stock name in the results — verify navigation to the stock overview page
8. Go back — click the "Add to Watchlist" icon on a screener result — verify it is added

**Journey 6 — Ask AI Chat:**

1. Click the floating chat button (bottom-right corner)
2. Verify the chat panel slides open
3. Verify starter prompt cards are visible
4. Click the "Explain a financial concept" starter card — or type "What is P/E ratio?"
5. Verify the typing indicator appears while the AI processes
6. Verify an AI response appears with the explanation
7. Verify the disclaimer text is present in the response
8. Type "Compare TCS and Infosys"
9. Verify a comparison table appears in the AI response
10. Click the close button — verify the panel closes
11. Click the chat button again — verify the conversation history is preserved

**Journey 7 — Stock Q&A via Chat:**

1. Open the chat panel
2. Type "Tell me about Reliance Industries"
3. Verify the response includes current price, key metrics, and sector information
4. Verify no buy/sell language is present in the response (search for the words "buy", "sell", "attractive", "avoid" in the response text — they must not appear in a directional context)
5. Type "Should I buy Reliance?"
6. Verify the response acknowledges the question but redirects to data only, ending with "The decision is entirely yours" or equivalent

**Journey 8 — Price Alert Setup and In-App Notification:**

1. Navigate to the stock overview page for TCS
2. Click "Add Alert"
3. Select "Alert me when price goes ABOVE"
4. Enter a price that is 0.1% above current price (to ensure it triggers in testing)
5. Click "Set Alert"
6. Verify success toast
7. Navigate to alerts page — verify alert appears as active
8. Simulate a price trigger (either set the price low enough that it triggers on next check, or use a test endpoint to trigger it manually)
9. Verify the notification bell badge count increases
10. Click the bell — verify the notification drawer opens with the triggered alert
11. Verify the notification body mentions the stock name and the triggered price
12. Click "Mark all read" — verify the badge disappears

**Journey 9 — Responsive Mobile Check:**
Run the following at 390x844 viewport (Playwright `use: { viewport: { width: 390, height: 844 } }`):

1. Open the homepage — verify it is not broken
2. Tap the search icon — verify the mobile search overlay opens
3. Search for a stock — verify results appear
4. Navigate to a stock page — verify the overview card is readable and not overflowing
5. Open the chat panel — verify it opens full-screen
6. Send a message — verify the keyboard does not cover the input field

**Journey 10 — Error and Edge Case Handling:**

1. Navigate to `/stock/INVALIDTICKER` — verify a "Stock not found" error page (not a 500 crash)
2. Open the chat and send an empty message — verify the send button is disabled
3. Type 501 characters in the chat input — verify the character counter goes red and the send button is disabled
4. With network throttling (Playwright's `page.route` to block API calls), open the watchlist — verify the loading skeleton appears and after unblocking the network, data loads correctly

---

## Prompt 22 — Final Pre-Launch Checklist

Before declaring Release 1 complete, ask your AI assistant to verify every item in this checklist:

### 22.1 Security Audit

- Run `npm audit` in all TypeScript packages — fix all critical and high severity vulnerabilities before launch
- Confirm all environment variables are in Doppler and none exist in `.env` files that are committed to git. Run `git grep -r "API_KEY\|api_key\|secret\|SECRET\|password\|PASSWORD"` and verify no hardcoded secrets appear in source files.
- Confirm all Supabase tables have RLS enabled: run `SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public'` in the Supabase SQL editor and verify `rowsecurity = true` for all 13 tables.
- Confirm rate limiting is working: write a quick script that sends 15 requests per minute to `POST /auth/login` and verify the 11th request receives HTTP 429.
- Confirm all AI outputs are sanitised before rendering: search the frontend codebase for `dangerouslySetInnerHTML` — there must be zero instances.
- Confirm the Content-Security-Policy header is present on all pages: use a browser dev tools network tab to check the response headers on the homepage.

### 22.2 Performance Audit

- Run Lighthouse on the stock overview page (`/stock/RELIANCE`) in the staging environment. Target scores: Performance ≥ 80, Accessibility ≥ 90, SEO ≥ 90.
- Verify the `GET /stocks/{ticker}` API endpoint responds in under 200ms on cache hit and under 1000ms on cache miss.
- Verify the `GET /stocks/search` endpoint responds in under 100ms on cache hit and under 500ms on cache miss.
- Verify the chat endpoint responds in under 5 seconds for 95th percentile.
- Check the Next.js bundle size: run `next build` with `ANALYZE=true` and verify the initial JS bundle is under 150kB gzipped.

### 22.3 Disclaimer Completeness Audit

Search the entire frontend codebase for all components that render AI-generated content. Verify that every single one has the disclaimer text: `"This is data and analysis only — not investment advice. Investom is not a SEBI-registered investment adviser."` Create a list of all AI output locations in the codebase and check them off one by one:

- Stock overview AI narrative
- Sector heatmap AI narrative
- Screener AI filter explanation
- Watchlist daily digest
- Chat panel every assistant message
- Any AI-generated content in the alert suggestion

### 22.4 Monitoring Verification

- Trigger an error deliberately (throw in a test route) and verify the error appears in Sentry within 2 minutes.
- Verify the Sentry alert is sent to the configured email.
- Log into the Anthropic console and verify the prompt caching hit rate is above 50% for the stock_qa query type (run 5 chat queries with the same stock and check the usage dashboard).
- Verify the Upstash Redis dashboard shows cache hits on stock overview requests.
- Verify the Railway deployment logs show no ERROR level messages during normal operation.

### 22.5 Beta Launch Readiness

- Create 3 test accounts with different profiles: Beginner/Conservative, Intermediate/Moderate, Advanced/Aggressive. Walk through the full user journey for each. Verify the experience is appropriate and consistent.
- Verify the platform handles concurrent users: use `k6` or `artillery` to simulate 50 concurrent users on the search endpoint and verify no 5xx errors.
- Set up a simple uptime monitor (UptimeRobot free tier is sufficient) for the three main endpoints: frontend homepage, API health check, and AI service health check.
- Write the beta launch invite email copy that clearly states: the platform provides financial data and analysis only, is not registered with SEBI, and is not financial advice.

---

## Appendix A — Prompt Dependency Map

```
Prompt 0 (Prerequisites)
    └── Prompt 1 (Scaffolding)
            └── Prompt 2 (Database)
                    ├── Prompt 3 (Auth)
                    ├── Prompt 4 (Data Pipeline) ← BLOCKING
                    │       └── Prompt 5 (Search)
                    │       └── Prompt 6 (Stock Overview)
                    │       └── Prompt 7 (Heatmap)
                    │       └── Prompt 8 (Screener)
                    │       └── Prompt 9 (Watchlist)
                    │       └── Prompt 10 (Trending)
                    │       └── Prompt 15 (Alerts)
                    │               └── Prompt 16 (Notifications)
                    └── Prompt 11 (Chat Infrastructure) ← BLOCKING
                            ├── Prompt 12 (Stock Q&A)
                            ├── Prompt 13 (Concept Explainer)
                            └── Prompt 14 (Comparison)
Prompt 17 (Polish) ← run after all feature prompts
Prompt 18 (CI/CD) ← run in parallel with feature prompts
Prompt 19 (Unit Tests) ← write alongside each feature prompt, not all at the end
Prompt 20 (Integration Tests)
Prompt 21 (E2E Tests)
Prompt 22 (Pre-Launch Checklist)
```

---

## Appendix B — LLM Routing Reference

When asking your AI assistant to build any AI feature, use this routing table to determine which model to use:


| Feature                          | Model            | Reason                                    |
| -------------------------------- | ---------------- | ----------------------------------------- |
| Query type classifier            | Claude 3.5 Haiku | Simple classification, very cheap         |
| Stock Q&A (basic data questions) | Claude 3.5 Haiku | Factual retrieval, no complex reasoning   |
| Concept explainer                | Claude 3.5 Haiku | Template-driven, structured output        |
| Stock comparison narrative       | Claude 3.5 Haiku | Structured comparison, sufficient quality |
| Screener NL parser               | Claude 3.5 Haiku | JSON extraction from short text           |
| Heatmap narrative                | Claude 3.5 Haiku | Short summary generation                  |
| Stock overview card narrative    | Claude 3.5 Haiku | Short narrative generation                |
| Watchlist digest                 | Claude 3.5 Haiku | Routine daily summary                     |
| AI moderation (future)           | Claude 3.5 Haiku | Simple classification                     |
| Fallback (Anthropic down)        | GPT-4o-mini      | Cost-efficient fallback                   |


No Sonnet calls are required in Release 1. All R1 AI features are served by Haiku with prompt caching.

---

## Appendix C — Cache TTL Reference


| Data                                  | Cache Location        | TTL                   | Notes                              |
| ------------------------------------- | --------------------- | --------------------- | ---------------------------------- |
| Stock search results                  | Upstash Redis         | 5 minutes             | Stale results acceptable           |
| Stock overview (price + fundamentals) | Upstash Redis         | 1 hour                | Prices update end of day           |
| Stock price only                      | Upstash Redis         | 15 minutes            | Acceptable market delay            |
| Sector heatmap (market hours)         | Upstash Redis         | 5 minutes             | Live data feel during trading      |
| Sector heatmap (after hours)          | Upstash Redis         | 1 hour                | Stable after market close          |
| Screener results                      | Upstash Redis         | 10 minutes            | Filters don't change that fast     |
| Trending stocks                       | Upstash Redis         | 5 minutes             | Updated regularly                  |
| AI stock overview narrative           | Supabase DB + Upstash | 24 hours              | AI calls are expensive             |
| AI heatmap narrative                  | Supabase DB           | 15 minutes            | Should refresh during market hours |
| Notifications unread count            | Upstash Redis         | Realtime subscription | No polling needed                  |


---

## Appendix D — Test Data Fixtures Required

These fixture files must be created in `__tests__/fixtures/` before writing integration tests:

- `eodhd-instruments-nse.json` — sample of 50 NSE instruments from the EODHD instruments endpoint
- `eodhd-eod-daily.json` — sample end-of-day data for 10 stocks
- `eodhd-fundamentals-reliance.json` — full fundamentals response for RELIANCE (5 years of annual + quarterly)
- `stock-overview-response.json` — expected response shape from `GET /stocks/RELIANCE`
- `screener-filters-valid.json` — 5 valid screener filter sets with expected result counts
- `claude-chat-response-stock-qa.json` — mocked Anthropic response for a stock Q&A
- `claude-chat-response-concept.json` — mocked Anthropic response for a concept explanation
- `alert-trigger-price-data.json` — price data that would trigger specific test alerts

---

*This document covers Release 1 completely. Prompts for Releases 2–5 will be created in separate documents following the same structure after Release 1 is deployed and verified.*