#!/usr/bin/env python3
"""
CLI para probar el parser de rutinas sin usar Telegram.
Uso: python cli_test.py
"""

import json
import sys

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from func.routine_parser import parse_routine


def format_routine(structured_routine: list) -> str:
    """Formatea la rutina para mostrar en terminal."""
    lines = ["\n" + "=" * 50]
    lines.append("📋 RUTINA PARSEADA")
    lines.append("=" * 50 + "\n")

    for i, day in enumerate(structured_routine, 1):
        exercises = day.get("rutina", [])
        lines.append(f"📅 Día {i} ({len(exercises)} ejercicios)")
        lines.append("-" * 30)

        for ex in exercises:
            name = ex.get("ejercicio", "?")
            series = ex.get("series", "?")
            reps = ", ".join(ex.get("repeticiones", ["N/A"]))
            lines.append(f"  • {name}")
            lines.append(f"    Series: {series}")
            lines.append(f"    Reps: {reps}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("\n" + "=" * 50)
    print("🏋️  CLI - Parser de Rutinas")
    print("=" * 50)
    print("\nEscribe 'salir' para terminar")
    print("Escribe 'json' para ver el JSON raw")
    print("-" * 50 + "\n")

    show_json = False

    while True:
        try:
            print("📝 Introduce tu rutina (Enter vacío para enviar):")
            lines = []

            while True:
                line = input()
                if line == "":
                    break
                if line.lower() == "salir":
                    print("\n👋 ¡Hasta luego!")
                    sys.exit(0)
                if line.lower() == "json":
                    show_json = not show_json
                    print(f"📊 Modo JSON: {'ON' if show_json else 'OFF'}")
                    continue
                lines.append(line)

            if not lines:
                print("⚠️  No escribiste nada. Intenta de nuevo.\n")
                continue

            routine_text = "\n".join(lines)

            print("\n⏳ Procesando con Gemini...")

            try:
                result = parse_routine(routine_text)

                if show_json:
                    print("\n📊 JSON Raw:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                print(format_routine(result))
                print("✅ Rutina parseada correctamente!\n")

            except Exception as e:
                print(f"\n❌ Error al parsear: {e}\n")

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            sys.exit(0)


if __name__ == "__main__":
    main()
