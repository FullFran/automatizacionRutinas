# Workflow Guide - BlakIA

Guía rápida de workflows comunes para el equipo de desarrollo.

---

## 📋 Convenciones de Nombres

### Branches

| Tipo         | Pattern                          | Ejemplo                         |
| ------------ | -------------------------------- | ------------------------------- |
| **feature**  | `feature/<ticket>-<description>` | `feature/BLAK-123-oauth-google` |
| **fix**      | `fix/<ticket>-<description>`     | `fix/BLAK-456-token-refresh`    |
| **hotfix**   | `hotfix/<description>`           | `hotfix/critical-db-leak`       |
| **refactor** | `refactor/<description>`         | `refactor/extract-auth-service` |
| **release**  | `release/v<version>`             | `release/v1.2.0`                |

### Commits (Conventional Commits)

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Scopes:** `api`, `auth`, `agents`, `rag`, `db`, `services`, `core`, `ui`, `components`, `hooks`, `utils`, `pages`

---

## 🚀 Workflow: Nueva Feature

```bash
# 1. Actualizar develop
git checkout develop
git pull origin develop

# 2. Crear feature branch
git checkout -b feature/BLAK-234-user-analytics-dashboard

# 3. Desarrollar con commits frecuentes
git add src/components/Dashboard.tsx
git commit -m "feat(dashboard): add analytics chart component"

git add src/hooks/useAnalytics.ts
git commit -m "feat(dashboard): add analytics data fetching hook"

# Push diariamente
git push origin feature/BLAK-234-user-analytics-dashboard

# 4. Mantener branch actualizado (rebase diario)
git fetch origin
git rebase origin/develop
git push --force-with-lease origin feature/BLAK-234-user-analytics-dashboard

# 5. Añadir tests
git add tests/components/Dashboard.test.tsx
git commit -m "test(dashboard): add unit tests for analytics chart"

# 6. Ejecutar tests localmente
pnpm test
pnpm typecheck
pnpm lint
pnpm build

# 7. Abrir PR
gh pr create \
  --base develop \
  --title "feat(dashboard): implement user analytics dashboard" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --assignee @me \
  --label "type: feature"

# 8. Atender comentarios de review
# ... hacer cambios solicitados ...
git add .
git commit -m "refactor(dashboard): extract chart logic to custom hook"
git push origin feature/BLAK-234-user-analytics-dashboard

# 9. Después de aprobación y merge (vía GitHub UI)
git checkout develop
git pull origin develop
git branch -d feature/BLAK-234-user-analytics-dashboard
```

---

## 🐛 Workflow: Bug Fix Urgente (Hotfix)

```bash
# 1. Branch desde main (código en producción)
git checkout main
git pull origin main
git checkout -b hotfix/dashboard-sql-timeout

# 2. Fix mínimo (solo el bug)
git add app/services/analytics_service.py
git commit -m "fix(analytics): add database query timeout and index

Queries were timing out on large datasets. Added:
- 30s timeout on analytics queries
- Index on user_events.created_at column
- Pagination for large result sets

Fixes #890"

# 3. Test exhaustivamente
pytest tests/integration/test_analytics.py -v

# 4. PR a main (revisión urgente)
gh pr create \
  --base main \
  --title "HOTFIX: Dashboard SQL timeout" \
  --label "hotfix,priority: critical" \
  --assignee @FullFran

# 5. Después de merge a main, backport a develop
git checkout develop
git pull origin develop
gh pr create \
  --base develop \
  --head hotfix/dashboard-sql-timeout \
  --title "Backport: Dashboard SQL timeout fix"
```

---

## 📦 Workflow: Release

```bash
# 1. Crear release branch desde develop
git checkout develop
git pull origin develop
git checkout -b release/v1.3.0

# 2. Bump version
# Editar: pyproject.toml, package.json, __version__.py
git add pyproject.toml package.json app/__version__.py
git commit -m "chore(release): bump version to 1.3.0"

# 3. Actualizar CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs(release): update CHANGELOG for v1.3.0"

# 4. Solo bug fixes en release branch (NO features)

# 5. PR a main
gh pr create \
  --base main \
  --title "Release v1.3.0" \
  --body "$(cat CHANGELOG.md)" \
  --label "release"

# 6. Después de merge, crear tag
git checkout main
git pull origin main
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0

# 7. Backport a develop
git checkout develop
git merge main
git push origin develop
```

---

## 📝 Tips

### Commits Frecuentes

- Commit **al menos cada 2 horas** de trabajo activo
- Nunca terminar el día sin push

### Rebase Diario

- Rebase desde `develop` **diariamente** si develop está activo
- **Antes de abrir PR** (mandatory)

### PR Size

- **XS/S:** < 200 líneas ✅ Ideal
- **M:** 200-400 líneas ⚠️ Aceptable
- **L/XL:** > 400 líneas ❌ Dividir

### Review SLA

- **Peer review:** 24 horas max
- **Senior review:** 48 horas max para PRs > 200 LOC
- **Hotfix:** < 2 horas para `security`, < 4 horas para `critical`

---

## 🔗 Enlaces Útiles

- [BRANCH_PROTECTION.md](./BRANCH_PROTECTION.md) - Configuración de branch protection
- [Conventional Commits](https://www.conventionalcommits.org/) - Especificación completa
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow) - Workflow base
