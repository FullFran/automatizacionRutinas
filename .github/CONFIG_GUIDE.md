# Configuración GitHub - BlakIA

Esta carpeta contiene la configuración estándar de GitHub para la organización BlakIA, incluyendo templates, workflows de CI/CD, y políticas de desarrollo.

## 📁 Estructura

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug-report.yml          # Template para reportar bugs
│   └── feature-request.yml     # Template para proponer features
├── workflows/
│   ├── commitlint.yml          # Valida conventional commits en PRs
│   ├── ci-backend.yml          # CI para backend (lint, test, coverage)
│   ├── ci-frontend.yml         # CI para frontend (lint, test, build)
│   ├── deploy-staging.yml      # Auto-deploy a staging (develop)
│   ├── deploy-production.yml   # Auto-deploy a production (main)
│   ├── issue-management.yml    # Automatización de issues
│   └── release.yml             # Releases automáticos (semantic-release)
├── CODEOWNERS                  # Ownership de código por áreas
├── PULL_REQUEST_TEMPLATE.md    # Template para PRs
├── BRANCH_PROTECTION.md        # Guía de branch protection rules
└── WORKFLOW_GUIDE.md           # Guía de workflows comunes
```

## 🚀 Implementación

### 1. Primeros Pasos

Para usar esta configuración en un repositorio nuevo:

```bash
# Copiar contenido de templates/.github a tu repositorio
cp -r templates/.github /path/to/your/repo/.github
cp templates/.commitlintrc.json /path/to/your/repo/
cp templates/.releaserc.json /path/to/your/repo/
```

### 2. Configurar Branch Protection

Seguir las instrucciones en [BRANCH_PROTECTION.md](./BRANCH_PROTECTION.md) para configurar las reglas de protección en GitHub UI.

### 3. Configurar Secrets

Los workflows requieren los siguientes secrets en GitHub:

**Repository Secrets (Settings → Secrets → Actions):**

- `RAILWAY_TOKEN` - Token de Railway para deploy staging
- `VERCEL_TOKEN` - Token de Vercel para deploy frontend
- `VERCEL_ORG_ID` - Organization ID de Vercel
- `VERCEL_PROJECT_ID` - Project ID de Vercel
- `GH_TOKEN` - GitHub Personal Access Token (para issue management)

### 4. Configurar Teams

Actualizar [CODEOWNERS](./CODEOWNERS) con los teams reales de tu organización:

- `@blakiatech/engineering-team`
- `@blakiatech/backend-team`
- `@blakiatech/frontend-team`
- `@blakiatech/ai-team`
- `@blakiatech/devops-team`

### 5. Instalar Dependencias

Para semantic-release y commitlint:

```bash
npm install --save-dev \
  semantic-release \
  @semantic-release/changelog \
  @semantic-release/git \
  @semantic-release/github \
  @commitlint/cli \
  @commitlint/config-conventional
```

## 📖 Guías

- **[WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md)** - Workflows comunes (features, hotfixes, releases)
- **[BRANCH_PROTECTION.md](./BRANCH_PROTECTION.md)** - Configuración de branch protection

## 🔧 Conventional Commits

Todos los commits deben seguir la especificación de [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Scopes:** `api`, `auth`, `agents`, `rag`, `db`, `services`, `core`, `ui`, `components`, `hooks`, `utils`, `pages`

**Ejemplo:**

```bash
git commit -m "feat(auth): add Google OAuth2 provider"
git commit -m "fix(api): resolve JWT token expiration edge case"
```

## 🌿 Estrategia de Branching

**GitHub Flow Modificado:**

```
main (production)
  └── develop (staging)
      ├── feature/BLAK-123-oauth-google
      ├── fix/BLAK-456-token-refresh
      └── hotfix/critical-security-patch
```

### Branch Naming:

- Features: `feature/<ticket>-<description>`
- Fixes: `fix/<ticket>-<description>`
- Hotfixes: `hotfix/<description>`
- Releases: `release/v<version>`

## 🔄 CI/CD Pipeline

### Backend (`ci-backend.yml`)

1. **Lint & Format** - Ruff, Black, isort
2. **Type Check** - mypy
3. **Tests** - pytest con coverage > 80%
4. **Security Scan** - Bandit

### Frontend (`ci-frontend.yml`)

1. **Lint & Format** - ESLint, Prettier
2. **Type Check** - TypeScript
3. **Tests** - Vitest con coverage
4. **Build** - Next.js build verification

### Deployment

- **Staging** - Auto-deploy en push a `develop`
- **Production** - Auto-deploy en push a `main` (requiere approval)

## 📦 Releases

Releases automáticos con semantic-release:

1. Commits en `main` activan workflow de `release.yml`
2. semantic-release analiza commits desde último release
3. Determina version bump según tipos de commits
4. Genera CHANGELOG.md automáticamente
5. Crea Git tag y GitHub Release

## 🎯 Code Reviews

- **PRs a `develop`**: Requiere 1 aprobación
- **PRs a `main`**: Requiere 2 aprobaciones + CODEOWNERS review
- **Hotfixes**: Review expedita < 2 horas para críticos

## 📋 Labels System

### Priority

- `priority: critical` 🔴 - Bloqueante, deploy roto
- `priority: high` 🟡 - Importante
- `priority: medium` 🟢 - Normal
- `priority: low` ⚪ - Nice-to-have

### Type

- `type: bug` 🐛
- `type: feature` ✨
- `type: enhancement` ⚡
- `type: docs` 📝

### Area

- `area: backend`
- `area: frontend`
- `area: ai-agents`
- `area: infra`

## 🔗 Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Semantic Versioning](https://semver.org/)
- [semantic-release](https://semantic-release.gitbook.io/)

---

**Última actualización:** 2025-11-30
**Versión:** 1.0.0
**Mantenedor:** BlakIA Engineering Team
