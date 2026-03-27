from ninja import Router
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.db import transaction

from ..models import PerfilUsuario
from ..schemas import (
    UserProfileSchema,
    UpdateProfileSchema,
    ChangePasswordSchema,
)

router = Router(tags=["👤 Perfil"])


# --- DATOS DEL USUARIO LOGUEADO ---
@router.get("/me", response=UserProfileSchema, auth=JWTAuth())
def obtener_perfil(request):
    """
    Devuelve los datos del usuario logueado basándose en su Token.
    """
    return request.auth


# --- OBTENER DATOS EDITABLES ---
@router.get("/perfil", response=UserProfileSchema, auth=JWTAuth())
def obtener_perfil_editable(request):
    """
    Devuelve los datos editables del perfil: correo, nombre, apellido,
    teléfono, institución y cargo.
    """
    return request.auth


# --- ACTUALIZAR PERFIL ---
@router.put("/perfil", response=UserProfileSchema, auth=JWTAuth())
def actualizar_perfil(request, payload: UpdateProfileSchema):
    """
    Actualiza los datos del perfil del usuario logueado.
    Solo se actualizan los campos que se envíen (los demás no cambian).
    """
    user = request.auth
    data = payload.dict(exclude_none=True)

    try:
        with transaction.atomic():
            # Campos del modelo User
            campos_user = ["email", "first_name", "last_name"]
            user_actualizado = False
            for campo in campos_user:
                if campo in data:
                    if campo == "email":
                        if (
                            User.objects.filter(email=data["email"])
                            .exclude(pk=user.pk)
                            .exists()
                        ):
                            raise HttpError(
                                400, "Este correo ya está en uso por otro usuario"
                            )
                        user.username = data["email"]
                    setattr(user, campo, data[campo])
                    user_actualizado = True

            if user_actualizado:
                user.save()

            # Campos del modelo PerfilUsuario
            campos_perfil = ["telefono", "nombre_institucion_ente", "cargo"]
            perfil_data = {k: data[k] for k in campos_perfil if k in data}
            if perfil_data:
                PerfilUsuario.objects.update_or_create(user=user, defaults=perfil_data)

        user.refresh_from_db()
        return user

    except HttpError:
        raise
    except Exception as e:
        raise HttpError(500, f"Error al actualizar el perfil: {str(e)}")


# --- CAMBIAR CONTRASEÑA ---
@router.post("/auth/change-password", auth=JWTAuth())
def cambiar_contrasena(request, payload: ChangePasswordSchema):
    """
    Cambia la contraseña del usuario. Requiere la contraseña actual.
    """
    user = request.auth

    if not user.check_password(payload.current_password):
        raise HttpError(400, "La contraseña actual es incorrecta")

    user.set_password(payload.new_password)
    user.save()
    return {"message": "Contraseña actualizada exitosamente"}


# --- ELIMINAR CUENTA (Soft Delete) ---
@router.delete("/auth/delete-account", auth=JWTAuth())
def eliminar_cuenta(request):
    """
    Desactiva la cuenta del usuario logueado (soft delete).
    No borra datos de la base de datos, solo marca is_active=False.
    El usuario no podrá iniciar sesión nuevamente.
    """
    user = request.auth
    user.is_active = False
    user.save()
    return {"message": "Cuenta desactivada exitosamente"}
