# 📁 legacy/ - Código Antiguo

Este directorio contiene el código original antes del refactor a Clean Architecture.

---

## 🎯 Propósito

Mantener el código antiguo como **referencia** durante la migración. Esto permite:

1. Consultar la implementación original
2. Copiar lógica específica que funcionaba
3. Comparar comportamiento antes/después
4. Rollback rápido si es necesario

---

## ⚠️ Importante

- **NO modificar** estos archivos
- **NO importar** desde aquí en el código nuevo
- Se eliminará cuando la migración esté completa

---

## 📂 Contenido

Archivos movidos del código original:

```
legacy/
├── main.py              # Handler del webhook original
├── func/
│   ├── config.py        # Configuración original
│   ├── routine_parser.py # Parser con Gemini
│   ├── google_slides.py  # Generador de slides
│   └── telegram_bot.py   # Funciones de Telegram
└── cli_test.py          # Script de prueba CLI
```

---

## 🗑️ Cuándo eliminar

Cuando se cumplan todas estas condiciones:

- [ ] Todos los endpoints funcionan correctamente
- [ ] Tests pasan al 100%
- [ ] Al menos 1 semana en producción sin problemas
- [ ] Documentación actualizada
