# sgea_app/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Autentica contra o UserModel.
    Verifica o username ou email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # Tenta buscar o usuário combinando username OU email
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            # Caso existam múltiplos usuários com o mesmo email (evitar isso na validação de cadastro),
            # pega o primeiro encontrado para evitar erro 500.
            user = UserModel.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).order_by(
                'id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None