from typing import Optional

from src.dominio import Usuario


def exigir_autenticado(usuario: Optional[Usuario]) -> Usuario:
    if usuario is None or usuario.id is None:
        raise PermissionError("Usuario autenticado requerido.")
    return usuario


def exigir_admin(usuario: Optional[Usuario]) -> Usuario:
    usuario_autenticado = exigir_autenticado(usuario)
    if usuario_autenticado.cargo != "admin":
        raise PermissionError("Apenas administradores podem executar esta acao.")
    return usuario_autenticado
