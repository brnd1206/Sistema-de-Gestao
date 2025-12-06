import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexPasswordValidator:
    """
    Valida se a senha contém pelo menos uma letra, um número e um caractere especial.
    """
    def validate(self, password, user=None):
        # Verifica se tem pelo menos uma letra
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra."),
                code='password_no_letters',
            )

        # Verifica se tem pelo menos um número
        if not re.search(r'\d', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um número."),
                code='password_no_numbers',
            )

        # Verifica se tem pelo menos um caractere especial (não alfanumérico)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um caractere especial (ex: @, #, $, etc)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Sua senha deve conter letras, números e caracteres especiais."
        )