"""
Regla de autenticación personalizada para JWT.
Verifica que el usuario tenga la cuenta activada antes de emitir tokens.
"""


def user_authentication_rule(user):
    """
    Regla que se ejecuta antes de emitir un token JWT.
    Retorna True solo si el usuario existe y tiene la cuenta activa.
    Si is_active es False, retorna False y el login falla.
    """
    return user is not None and user.is_active
