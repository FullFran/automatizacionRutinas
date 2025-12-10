# Branch Protection Rules

Esta guía documenta las reglas de protección de branches que deben configurarse en GitHub.

## Configuración en GitHub

**Ruta:** Settings → Branches → Add rule

---

## `main` branch (Production)

### ✅ Reglas a habilitar:

- **Require a pull request before merging**

  - Require approvals: **2**
  - Dismiss stale PR approvals when new commits are pushed
  - Require review from Code Owners

- **Require status checks to pass before merging**

  - Require branches to be up to date before merging
  - **Required checks:**
    - `ci-backend` (lint, test, build)
    - `ci-frontend` (lint, test, build)
    - `commitlint` (validate commits)
    - `security-scan` (CodeQL)

- **Require conversation resolution before merging**

- **Require signed commits**

- **Require linear history**

- **Include administrators** (rules apply to everyone)

- **Restrict pushes that create matching branches**

- **Restrict who can push to matching branches**
  - Allowed: `@blakiatech/release-team`, `@FullFran`

### ❌ Reglas a deshabilitar:

- Allow force pushes
- Allow deletions

---

## `develop` branch (Staging)

### ✅ Reglas a habilitar:

- **Require a pull request before merging**

  - Require approvals: **1**
  - Dismiss stale PR approvals when new commits are pushed

- **Require status checks to pass before merging**

  - **Required checks:**
    - `ci-backend`
    - `ci-frontend`
    - `commitlint`

- **Require conversation resolution before merging**

- **Require linear history**

### ❌ Reglas a deshabilitar:

- Require Code Owners review (más flexible que main)
- Require signed commits (nice-to-have, no mandatory)
- Include administrators (admins pueden push directo en emergencia)

---

## Merge Strategies

**Repository Settings → Pull Requests:**

### ✅ Permitir:

- **Squash merging** (default para features)
- **Merge commits** (para release branches)

### ❌ Deshabilitar:

- **Rebase merging** (confunde historial en reviews)

### Auto-delete:

- **Automatically delete head branches** ✅

---

## Notas Importantes

1. Estas reglas garantizan calidad y seguridad en el código
2. Requieren que el equipo tenga suficientes reviewers disponibles
3. Las reglas se aplican a todos, incluyendo administradores
4. Para hotfixes críticos, usar el proceso de hotfix documentado
5. Las protection rules deben configurarse manualmente en GitHub UI
