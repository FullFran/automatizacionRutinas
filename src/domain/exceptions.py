"""
Excepciones de Dominio

Excepciones específicas del negocio. Estas NO son errores técnicos,
sino situaciones de negocio que deben manejarse.
"""


class DomainException(Exception):
    """Excepción base para errores de dominio."""

    pass


class InvalidRoutineError(DomainException):
    """El texto de la rutina no tiene un formato válido."""

    pass


class EmptyRoutineError(DomainException):
    """La rutina no contiene ejercicios."""

    pass


class ParsingError(DomainException):
    """Error al intentar parsear la rutina con IA."""

    pass


class PresentationError(DomainException):
    """Error al generar la presentación."""

    pass
