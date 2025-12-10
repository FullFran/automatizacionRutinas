# 📁 src/ - Código Fuente Principal

Este directorio contiene todo el código fuente de la aplicación, organizado siguiendo los principios de **Clean Architecture**.

---

## 🏗️ ¿Qué es Clean Architecture?

Clean Architecture es un patrón de diseño creado por Robert C. Martin ("Uncle Bob") que organiza el código en **capas concéntricas**, donde:

- Las capas **internas** contienen la lógica de negocio (lo más importante)
- Las capas **externas** contienen detalles técnicos (frameworks, bases de datos, APIs)
- La **Regla de Dependencia**: las capas internas NUNCA dependen de las externas

```
         ┌──────────────────────────────────────┐
         │         api/ (Presentación)          │  ← FastAPI, endpoints
         ├──────────────────────────────────────┤
         │     infrastructure/ (Adaptadores)    │  ← Telegram, Google, Gemini
         ├──────────────────────────────────────┤
         │    application/ (Casos de Uso)       │  ← Lógica de aplicación
         ├──────────────────────────────────────┤
         │         domain/ (Núcleo)             │  ← Entidades, reglas de negocio
         └──────────────────────────────────────┘
```

---

## 📂 Estructura de Carpetas

| Carpeta           | Capa               | Descripción                                                       |
| ----------------- | ------------------ | ----------------------------------------------------------------- |
| `domain/`         | 🔵 Dominio         | Entidades y reglas de negocio puras. Sin dependencias externas.   |
| `application/`    | 🟢 Aplicación      | Casos de uso que orquestan la lógica. Usa interfaces del dominio. |
| `infrastructure/` | 🟠 Infraestructura | Implementaciones concretas: Gemini, Google Slides, Telegram.      |
| `api/`            | 🔴 Presentación    | Endpoints HTTP, schemas de request/response.                      |

---

## 🔄 Flujo de una Petición

```
Usuario envía rutina por Telegram
          │
          ▼
    ┌─────────────┐
    │   api/      │  Recibe webhook, valida request
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │ application/│  Ejecuta caso de uso "ParseRoutine"
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │infrastructure│ GeminiParser procesa con IA
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │   domain/   │  Devuelve entidad Routine validada
    └─────────────┘
```

---

## 🎯 ¿Por qué esta estructura?

### 1. **Testabilidad**

Cada capa se puede testear de forma aislada. El dominio no necesita Gemini ni Google para testearse.

### 2. **Flexibilidad**

¿Quieres cambiar de Gemini a OpenAI? Solo modificas `infrastructure/ai/`. El resto no cambia.

### 3. **Mantenibilidad**

Cada archivo tiene una única responsabilidad. Fácil de encontrar y modificar código.

### 4. **Escalabilidad**

Agregar nuevos clientes (web, mobile) es fácil: solo creates nuevos endpoints en `api/`.

---

## 📖 Lee más

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Clean Architecture en Python](https://www.cosmicpython.com/)
