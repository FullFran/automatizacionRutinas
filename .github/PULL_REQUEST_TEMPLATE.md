## 📋 Descripción

<!-- Descripción clara y concisa de los cambios -->

## 🔗 Issues relacionados

<!-- Formato: Closes #123, Relates to #456 -->

Closes #

## 🎯 Tipo de cambio

<!-- Marca con 'x' los que apliquen -->

- [ ] 🐛 Bug fix (cambio non-breaking que soluciona issue)
- [ ] ✨ Nueva feature (cambio non-breaking que añade funcionalidad)
- [ ] 💥 Breaking change (fix o feature que causa incompatibilidad)
- [ ] 📝 Documentación
- [ ] ♻️ Refactorización (sin cambio de comportamiento)
- [ ] ⚡ Mejora de rendimiento
- [ ] 🧪 Tests

## 🧪 Tests realizados

<!-- Describe qué tests has ejecutado y resultados -->

### Comandos ejecutados:

```bash
# Backend
pytest tests/test_new_feature.py -v
mypy app/ --strict
ruff check app/

# Frontend
pnpm test
pnpm typecheck
pnpm lint
```

**Resultados:**
- [ ] Tests unitarios pasan (100% coverage nuevo código)
- [ ] Tests integración pasan
- [ ] Linter (Ruff/ESLint) pasa sin warnings
- [ ] Type checking (mypy/tsc) pasa sin errores
- [ ] Manual testing completado

## 📸 Screenshots / Videos

<!-- Si aplica, añade evidencia visual de cambios UI -->

<details>
<summary>Ver screenshots</summary>

![Before](url)
![After](url)

</details>

## ✅ Checklist Pre-Merge

### Código
- [ ] El código sigue el Code Style de BlakIA (Black/Prettier)
- [ ] He realizado self-review del código
- [ ] He añadido comentarios en áreas complejas
- [ ] Commits siguen Conventional Commits
- [ ] No hay código comentado sin razón
- [ ] No hay console.log/print de debug

### Testing
- [ ] Tests nuevos para código nuevo (coverage >80%)
- [ ] Tests existentes siguen pasando
- [ ] Edge cases considerados y testeados
- [ ] Performance validado (si aplica)

### Documentación
- [ ] Docstrings/JSDoc actualizados (Google style)
- [ ] README actualizado (si aplica)
- [ ] OpenAPI spec actualizado (para endpoints API)
- [ ] CHANGELOG.md actualizado (si manual)
- [ ] Migraciones DB documentadas (si aplica)

### Seguridad & Infra
- [ ] Secrets no commiteados (.env en .gitignore)
- [ ] Validación input en endpoints públicos
- [ ] Permisos/roles verificados (si auth)
- [ ] Variables env documentadas (.env.example)
- [ ] Compatible con deploy actual (Dokploy/Railway)

### AI Agent Review (opcional)
- [ ] He solicitado GitHub Copilot review
- [ ] He revisado sugerencias del agente
- [ ] He validado código generado por IA

## 💬 Notas adicionales

<!-- Contexto adicional, decisiones técnicas, trade-offs -->

## 🚀 Plan de Deploy

<!-- Si requiere steps especiales de deployment -->

- [ ] Requiere migración DB (especificar comando)
- [ ] Requiere actualizar variables env
- [ ] Requiere restart servicios
- [ ] Puede deployarse directamente

---
**Para reviewers:** Enfocar review en [área específica] debido a [razón]
