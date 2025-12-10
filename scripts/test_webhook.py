"""
Test script para verificar el manejo de errores del webhook.
Simula diferentes escenarios sin necesidad de usar Telegram real.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

# Mockear dependencias externas para que el test corra sin instalarlas
sys.modules["google.generativeai"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.messages"] = MagicMock()
sys.modules["langchain_google_genai"] = MagicMock()
sys.modules["googleapiclient"] = MagicMock()
sys.modules["googleapiclient.discovery"] = MagicMock()
sys.modules["google.oauth2"] = MagicMock()
sys.modules["google.oauth2.service_account"] = MagicMock()

# Simular las dependencias antes de importar main
sys.path.insert(0, "/home/franblakia/blakia/automatizacionRutinas")


def test_short_routine():
    """Test con una rutina corta que debería funcionar"""
    print("\n" + "=" * 60)
    print("TEST 1: Rutina corta (debería funcionar)")
    print("=" * 60)

    with (
        patch("func.routine_parser.parse_routine") as mock_parse,
        patch("func.telegram_bot.send_telegram_message") as mock_send,
        patch(
            "func.telegram_bot.send_telegram_message_with_inline_keyboard"
        ) as mock_send_inline,
    ):
        # Simular respuesta exitosa del parser
        mock_parse.return_value = [
            {
                "rutina": [
                    {"ejercicio": "Pull ups", "series": "4", "repeticiones": ["10"]}
                ]
            }
        ]

        # Importar después de los mocks
        from fastapi import Request

        from main import telegram_webhook

        # Crear request simulado
        mock_request = Mock(spec=Request)
        mock_request.json = Mock(
            return_value={
                "message": {
                    "chat": {"id": 12345},
                    "text": "Pull ups 4 series de 10 reps",
                }
            }
        )

        # Ejecutar webhook
        import asyncio

        result = asyncio.run(telegram_webhook(mock_request))

        print(f"✅ Resultado: {result}")
        print(f"✅ parse_routine llamado: {mock_parse.called}")
        print(f"✅ Mensajes enviados: {mock_send.call_count}")
        print(f"✅ Mensaje con botones enviado: {mock_send_inline.called}")

        # Verificar que NO se envió "Procesando tu rutina..."
        for call in mock_send.call_args_list:
            message = call[0][1]
            if "Procesando tu rutina" in message:
                print("❌ ERROR: Se envió 'Procesando tu rutina...' (no debería)")
                return False

        print("✅ No se envió 'Procesando tu rutina...' (correcto)")
        return True


def test_parsing_error():
    """Test con error en el parsing (rutina inválida)"""
    print("\n" + "=" * 60)
    print("TEST 2: Error en parsing (rutina inválida)")
    print("=" * 60)

    with (
        patch("func.routine_parser.parse_routine") as mock_parse,
        patch("func.telegram_bot.send_telegram_message") as mock_send,
        patch(
            "func.telegram_bot.send_telegram_message_with_inline_keyboard"
        ) as mock_send_inline,
    ):
        # Simular error en el parser
        mock_parse.side_effect = ValueError(
            "La respuesta de Gemini no es un JSON válido."
        )

        # Importar después de los mocks
        from fastapi import Request

        from main import telegram_webhook

        # Crear request simulado
        mock_request = Mock(spec=Request)
        mock_request.json = Mock(
            return_value={
                "message": {
                    "chat": {"id": 12345},
                    "text": "rutina muy larga y compleja que falla al parsear...",
                }
            }
        )

        # Ejecutar webhook
        import asyncio

        result = asyncio.run(telegram_webhook(mock_request))

        print(f"✅ Resultado: {result}")
        print(f"✅ Status: {result.get('status')}")

        # Verificar que se devolvió status "error" (no excepción)
        if result.get("status") != "error":
            print(
                f"❌ ERROR: Se esperaba status 'error', se obtuvo '{result.get('status')}'"
            )
            return False

        # Verificar que se envió mensaje de error al usuario
        error_message_sent = False
        for call in mock_send.call_args_list:
            message = call[0][1]
            if "Error al procesar la rutina" in message:
                error_message_sent = True
                print(f"✅ Mensaje de error enviado al usuario: '{message}'")

        if not error_message_sent:
            print("❌ ERROR: No se envió mensaje de error al usuario")
            return False

        # Verificar que NO se envió mensaje con botones
        if mock_send_inline.called:
            print("❌ ERROR: Se enviaron botones a pesar del error")
            return False

        print("✅ No se enviaron botones (correcto)")
        return True


def test_presentation_creation_error():
    """Test con error al crear la presentación"""
    print("\n" + "=" * 60)
    print("TEST 3: Error al crear presentación")
    print("=" * 60)

    with (
        patch("func.routine_parser.parse_routine") as mock_parse,
        patch("func.google_slides.create_presentation") as mock_create,
        patch("func.telegram_bot.send_telegram_message") as mock_send,
        patch(
            "func.telegram_bot.send_telegram_message_with_inline_keyboard"
        ) as mock_send_inline,
    ):
        # Simular parsing exitoso pero error en creación de slides
        mock_parse.return_value = [
            {
                "rutina": [
                    {"ejercicio": "Pull ups", "series": "4", "repeticiones": ["10"]}
                ]
            }
        ]
        mock_create.side_effect = Exception("Error de Google API")

        # Importar después de los mocks
        from fastapi import Request

        from main import pending_routines, telegram_webhook

        # Limpiar rutinas pendientes
        pending_routines.clear()

        # Paso 1: Enviar rutina
        mock_request = Mock(spec=Request)
        mock_request.json = Mock(
            return_value={
                "message": {
                    "chat": {"id": 12345},
                    "text": "Pull ups 4 series de 10 reps",
                }
            }
        )

        import asyncio

        result = asyncio.run(telegram_webhook(mock_request))
        print(f"✅ Paso 1 - Rutina enviada: {result}")

        # Paso 2: Confirmar con callback
        mock_request2 = Mock(spec=Request)
        mock_request2.json = Mock(
            return_value={
                "callback_query": {
                    "message": {"chat": {"id": 12345}},
                    "data": "confirm",
                }
            }
        )

        result2 = asyncio.run(telegram_webhook(mock_request2))
        print(f"✅ Paso 2 - Confirmación: {result2}")

        # Verificar que se envió mensaje de error de presentación
        error_message_sent = False
        for call in mock_send.call_args_list:
            message = call[0][1]
            if "Error al crear la presentación" in message:
                error_message_sent = True
                print(f"✅ Mensaje de error enviado: '{message}'")

        if not error_message_sent:
            print("❌ ERROR: No se envió mensaje de error al usuario")
            return False

        return True


def test_webhook_always_returns_200():
    """Test que verifica que el webhook siempre devuelve 200 OK"""
    print("\n" + "=" * 60)
    print("TEST 4: Webhook siempre devuelve 200 OK (no excepciones)")
    print("=" * 60)

    with (
        patch("func.routine_parser.parse_routine") as mock_parse,
        patch("func.telegram_bot.send_telegram_message") as mock_send,
    ):
        # Simular un error catastrófico
        mock_parse.side_effect = Exception("Error inesperado catastrófico")

        from fastapi import Request

        from main import telegram_webhook

        mock_request = Mock(spec=Request)
        mock_request.json = Mock(
            return_value={"message": {"chat": {"id": 12345}, "text": "cualquier texto"}}
        )

        import asyncio

        try:
            result = asyncio.run(telegram_webhook(mock_request))
            print(f"✅ Resultado: {result}")
            print("✅ No se lanzó excepción (correcto)")

            # Verificar que devuelve un dict (no HTTPException)
            if not isinstance(result, dict):
                print(f"❌ ERROR: Se esperaba dict, se obtuvo {type(result)}")
                return False

            return True
        except Exception as e:
            print(f"❌ ERROR: Se lanzó excepción: {e}")
            return False


if __name__ == "__main__":
    print("\n🧪 INICIANDO TESTS DE WEBHOOK\n")

    tests = [
        ("Rutina corta exitosa", test_short_routine),
        ("Error en parsing", test_parsing_error),
        ("Error en creación de presentación", test_presentation_creation_error),
        ("Webhook siempre devuelve 200", test_webhook_always_returns_200),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' falló con excepción: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{total} tests pasados")

    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        sys.exit(1)
