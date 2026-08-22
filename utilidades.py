"""Utilidades transversales del servicio."""


def con_registro(func):
    """Registra la llamada y evita que un fallo tumbe el servicio."""
    def envoltura(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            print(f"[registro] {func.__name__} falló: {exc}")
            return None
    return envoltura
