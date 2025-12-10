# GitHub Copilot Instructions - [Project Name]

> **Auto-loaded by GitHub Copilot for all developers in this repository.**  
> Optimized for Copilot Chat, Copilot Code Review, and inline suggestions.

---

## 📋 Project Summary

**What this repository does:**  
[1-2 sentence description of the project's purpose and main functionality]

**Repository size:** ~[X]k lines of code  
**Primary languages:** TypeScript (60%), Python (35%), SQL (5%)  
**Frameworks:** Next.js 15, FastAPI 0.115, Supabase  
**Target runtime:** Node.js 20, Python 3.11

---

## 🏗️ High-Level Architecture

### Components

1. **Frontend** (`src/app/`): Next.js 15 App Router with React Server Components
2. **Backend API** (`app/`): FastAPI REST API with async SQLModel ORM
3. **Database:** PostgreSQL 15 with Supabase (Row-Level Security enabled)
4. **AI Agents** (`app/agents/`): Pydantic AI + LangGraph multi-agent system
5. **Infrastructure:** Vercel (frontend), Railway (backend), Supabase (DB)

### Data Flow

```
User → Next.js UI → API Gateway (Vercel Edge) → FastAPI Backend → PostgreSQL
                              ↓
                         AI Agents (Pydantic AI)
                              ↓
                         OpenAI/Anthropic APIs
```

---

## 🛠️ Build and Validation Instructions

### Bootstrap (First-Time Setup)

```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head

# Frontend
cd frontend && pnpm install

# Database
docker-compose up -d postgres
# Seed test data
python scripts/seed_db.py
```

**IMPORTANT:** Always run `pnpm install` after pulling latest code (lock file may have changed).

### Build

```bash
# Backend (no build step, interpreted Python)
# Validate imports and syntax:
python -m compileall app/

# Frontend
pnpm build  # Outputs to .next/
# Build time: ~45 seconds on Apple M1
```

### Test

**Run tests in this order** (fastest to slowest):

```bash
# 1. Linting (~5 seconds)
ruff check app/ tests/
pnpm lint

# 2. Type checking (~10 seconds)
mypy app/ --strict
pnpm typecheck

# 3. Unit tests (~30 seconds)
pytest tests/unit/ -v
pnpm test:unit

# 4. Integration tests (~2 minutes)
pytest tests/integration/ -v
pnpm test:integration

# 5. E2E tests (~5 minutes, run in CI only)
pnpm test:e2e
```

**Common test failures:**

- **Database not running:** Start with `docker-compose up -d postgres`
- **Stale migrations:** Run `alembic upgrade head`
- **Port conflicts:** Kill process on port 8000: `lsof -ti:8000 | xargs kill`

### Lint

```bash
# Python
ruff check app/ tests/ --fix  # Auto-fix issues
black app/ tests/             # Format code

# TypeScript
pnpm lint --fix  # ESLint auto-fix
pnpm format      # Prettier formatting
```

**Pre-commit hook** runs all linters automatically (configured in `.pre-commit-config.yaml`).

### Run Locally

```bash
# Backend API
uvicorn app.main:app --reload --port 8000
# Available at: http://localhost:8000
# API docs: http://localhost:8000/docs

# Frontend
pnpm dev  # Runs on http://localhost:3000

# Both simultaneously (recommended)
pnpm dev:all  # Uses concurrently to run both
```

---

## 📁 Project Layout

### Configuration Files

| File                       | Purpose                                                   |
| -------------------------- | --------------------------------------------------------- |
| `pyproject.toml`           | Python project metadata, tool configs (Black, Ruff, mypy) |
| `alembic.ini`              | Database migration config                                 |
| `next.config.mjs`          | Next.js configuration                                     |
| `tsconfig.json`            | TypeScript compiler options (strict mode enabled)         |
| `.github/workflows/ci.yml` | CI pipeline (linting, tests, build)                       |

### Key Source Files

**Backend:**

- `app/main.py` - FastAPI app entry point, CORS config, error handlers
- `app/api/v1/router.py` - API route aggregator (all endpoints registered here)
- `app/core/config.py` - Pydantic Settings (env vars, secrets)
- `app/core/deps.py` - FastAPI dependencies (DB session, auth, etc.)
- `app/models/` - SQLModel database schemas
- `app/services/` - Business logic (keep views/routes thin)

**Frontend:**

- `src/app/layout.tsx` - Root layout (global providers, metadata)
- `src/app/page.tsx` - Homepage (Server Component)
- `src/lib/supabase/server.ts` - Supabase client for Server Components
- `src/lib/supabase/client.ts` - Supabase client for Client Components
- `src/hooks/` - Custom React hooks (useUser, useSubscription, etc.)

### Directory Structure Deep Dive

```
backend/
├── app/
│   ├── main.py             # FastAPI app + middleware
│   ├── api/v1/
│   │   ├── router.py       # Route aggregator
│   │   └── endpoints/      # API route handlers
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── items.py
│   ├── services/           # Business logic layer
│   │   ├── auth_service.py
│   │   └── user_service.py
│   ├── models/             # SQLModel schemas
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/            # Pydantic request/response
│   │   ├── user.py
│   │   └── item.py
│   ├── core/
│   │   ├── config.py       # Settings (env vars)
│   │   ├── deps.py         # FastAPI dependencies
│   │   └── security.py     # JWT, password hashing
│   └── utils/
│       ├── exceptions.py   # Custom exception classes
│       └── validators.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py         # Pytest fixtures
└── alembic/                # Database migrations

frontend/
├── src/
│   ├── app/                # Next.js App Router
│   │   ├── (auth)/         # Route group (no URL impact)
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/    # Protected routes
│   │   │   ├── settings/
│   │   │   └── analytics/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/             # Shadcn/ui components
│   │   └── features/       # Feature-specific
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts
│   │   │   └── server.ts
│   │   └── api.ts          # API client (Axios)
│   └── hooks/
└── public/
```

---

## ✅ Pre-Commit Validation Steps

**Before committing, verify:**

1. **Linting passes:**

   ```bash
   ruff check app/ tests/
   pnpm lint
   ```

   Expected: No errors

2. **Type checking passes:**

   ```bash
   mypy app/ --strict
   pnpm typecheck
   ```

   Expected: Success: no issues found

3. **Tests pass:**

   ```bash
   pytest tests/unit/ -v
   pnpm test:unit
   ```

   Expected: All tests pass

4. **Build succeeds:**
   ```bash
   python -m compileall app/
   pnpm build
   ```
   Expected: No syntax errors, build completes

**If any step fails:**

- **Linting:** Run `ruff check --fix` or `pnpm lint --fix`
- **Type errors:** Fix type annotations, don't use `# type: ignore` without reason
- **Test failures:** Fix the bug, don't skip tests
- **Build errors:** Check for import errors, missing dependencies

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

**Runs on:** Every push to `develop` or `main`, all PRs

**Steps:**

1. **Checkout code**
2. **Setup Python 3.11 + Node 20**
3. **Install dependencies:**
   - `pip install -r requirements-dev.txt`
   - `pnpm install`
4. **Lint:**
   - `ruff check app/ tests/`
   - `pnpm lint`
5. **Type check:**
   - `mypy app/ --strict`
   - `pnpm typecheck`
6. **Unit tests:**
   - `pytest tests/unit/ --cov=app --cov-report=xml`
   - `pnpm test:unit --coverage`
7. **Integration tests:**
   - `pytest tests/integration/`
8. **Build:**
   - `pnpm build`
9. **Upload coverage:**
   - Codecov (requires 80% coverage)

**Deployment:**

- **Staging (Railway):** Auto-deploy on push to `develop`
- **Production (Vercel + Railway):** Auto-deploy on push to `main` (requires PR approval)

---

## 🔐 Secrets and Environment Variables

**NEVER commit:**

- `.env` files (only `.env.example` is allowed)
- API keys, tokens, passwords
- Database credentials

**Required environment variables** (defined in `.env.example`):

```bash
# Database
DATABASE_URL="postgresql://user:pass@localhost:5432/db"
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_ANON_KEY="ey..."
SUPABASE_SERVICE_ROLE_KEY="ey..."  # Backend only

# AI/LLM
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."

# Auth
JWT_SECRET="random-256-bit-hex-string"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
STRIPE_API_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
SENDGRID_API_KEY="SG...."
```

---

## 🚨 Known Issues and Workarounds

### Issue: Database Connection Pool Exhaustion

**Symptom:** `FATAL: sorry, too many clients already`

**Workaround:**

```python
# In app/core/deps.py, limit pool size:
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,      # Max 5 connections
    max_overflow=10   # Allow 10 additional during spikes
)
```

### Issue: Next.js Build OOM (Out of Memory)

**Symptom:** Build fails with `JavaScript heap out of memory`

**Workaround:**

```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm build
```

### Issue: Supabase Local Dev Port Conflict

**Symptom:** `Error: Address already in use (port 54322)`

**Workaround:**

```bash
lsof -ti:54322 | xargs kill
supabase stop && supabase start
```

---

## 💡 Code Style Guidelines

### Python

- **Formatter:** Black (line-length 88)
- **Linter:** Ruff (replaces Flake8, isort, pyupgrade)
- **Type checker:** mypy --strict
- **Docstrings:** Google style

```python
async def create_user(
    db: AsyncSession,
    data: UserCreate
) -> User:
    """
    Create new user in database.

    Args:
        db: Async database session
        data: Validated user creation data

    Returns:
        User: Created user instance with ID

    Raises:
        ValueError: If email already exists
    """
    ...
```

### TypeScript

- **Formatter:** Prettier
- **Linter:** ESLint (Airbnb config)
- **Naming:** camelCase for variables/functions, PascalCase for components/types

```typescript
interface UserProfile {
  id: string;
  email: string;
  name: string;
}

export async function getUserProfile(userId: string): Promise<UserProfile> {
  // ...
}
```

---

## 🎯 Explicit Validation Steps

**AI agents should verify these before suggesting code:**

1. **Type safety:**

   - Python: All function params and returns have type hints
   - TypeScript: No `any` types (use `unknown` with type guards)

2. **Error handling:**

   - Async functions use try/except with specific exception types
   - API endpoints return proper HTTP status codes (400/404/500)

3. **Security:**

   - No hardcoded secrets
   - Input validation with Pydantic/Zod
   - SQL queries use ORM (no string interpolation)

4. **Testing:**

   - New features include unit tests
   - Coverage >80% on new code
   - Tests use mocks for external services

5. **Documentation:**
   - Public functions have docstrings
   - API changes update OpenAPI spec (`app/main.py`)
   - Breaking changes documented in PR description

**Consequences of skipping validation:**

- **No type hints:** PR blocked by mypy in CI
- **Missing tests:** PR blocked by coverage check (<80%)
- **Hardcoded secrets:** Security scan fails, PR rejected
- **No docstrings:** Code review requests changes

---

## 📚 Dependencies and External APIs

### Key Dependencies

**Python:**

- `fastapi[all]==0.115.*` - Web framework
- `sqlmodel==0.0.21` - ORM (SQLAlchemy + Pydantic)
- `pydantic-ai==0.0.13` - AI agent framework
- `langgraph==0.2.*` - Multi-agent workflows
- `alembic==1.13.*` - Database migrations

**TypeScript:**

- `next@15.*` - React framework
- `@supabase/ssr@0.5.*` - Supabase client
- `@tanstack/react-query@5.*` - Server state management
- `zustand@4.*` - Client state management
- `zod@3.*` - Runtime type validation

### External Services

| Service   | Purpose             | Auth Method                                      |
| --------- | ------------------- | ------------------------------------------------ |
| Supabase  | Database + Auth     | Service role key (backend), Anon key (frontend)  |
| OpenAI    | LLM API             | Bearer token (`OPENAI_API_KEY`)                  |
| Anthropic | Claude API          | `x-api-key` header                               |
| Stripe    | Payments            | Secret key (backend), Publishable key (frontend) |
| SendGrid  | Transactional email | API key                                          |

**Rate limits:**

- OpenAI GPT-4: 10k requests/min
- Anthropic Claude: 5k requests/min
- Supabase: 500 requests/second

---

## 🎓 For Reviewers

**Focus review on:**

1. **Security:** Any new auth/permissions code
2. **Performance:** Database queries (N+1 problems), unnecessary re-renders
3. **Type safety:** Ensure no `any` or missing type hints
4. **Test coverage:** New features must have tests
5. **Breaking changes:** API contract changes must be documented

**Automated checks in CI will catch:**

- Linting errors
- Type errors
- Test failures
- Coverage below 80%

**Manual review required for:**

- Architecture decisions
- UX changes
- Database schema modifications
- Security-sensitive code

---

**Last Updated:** 2025-11-29  
**Maintainer:** BlakIA Engineering Team  
**Questions?** Open issue or ask in #copilot-help channel
