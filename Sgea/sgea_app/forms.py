from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Evento, Usuario

class UsuarioCreationForm(UserCreationForm):
    # Adicionando os campos extras que não estão no UserCreationForm padrão
    nome = forms.CharField(max_length=150, required=True, help_text="Nome é obrigatório.")
    email = forms.EmailField(required=True, help_text="Informe um endereço de email válido.")
    telefone = forms.CharField(max_length=15, required=False, help_text="Ex: (11) 99999-9999")
    instituicao_ensino = forms.CharField(max_length=255, required=False, label="Instituição de Ensino")

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Define a ordem dos campos no formulário
        fields = (
            'username',
            'email',
            'nome', 
            'perfil', 
            'telefone', 
            'instituicao_ensino'
        )

    def clean(self):
    # Validação personalizada para garantir que 'instituicao_ensino' seja
    # preenchido para alunos e professores.
        cleaned_data = super().clean()
        perfil = cleaned_data.get('perfil')
        instituicao_ensino = cleaned_data.get('instituicao_ensino')

        if perfil in ['aluno', 'professor'] and not instituicao_ensino:
            self.add_error('instituicao_ensino', "Instituição de ensino é obrigatória para alunos e professores.")

    def clean_email(self):
        # Validação para garantir que o email seja único no sistema
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este endereço de email já está em uso por outro usuário.")
        return email

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        # Validação simples de tamanho mínimo para evitar (__) ____-____ vazio ou incompleto
        if telefone and len(telefone) < 14:
            raise ValidationError("Por favor, insira um número de telefone válido com DDD.")
        return telefone
            
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(UsuarioCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nome', 
            'tipo_evento', 
            'data_inicio', 
            'data_fim', 
            'local', 
            'quantidade_participantes',
            'banner'
        ]
        # Widgets para facilitar a seleção de data e hora
        widgets = {
            'data_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'data_fim': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
        }

    def clean_quantidade_participantes(self):
        qtd = self.cleaned_data.get('quantidade_participantes')
        if qtd is not None and qtd < 0:
            raise ValidationError("A quantidade de participantes não pode ser negativa.")
        return qtd

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')
        if banner:
            # Verifica o tamanho do arquivo (exemplo: máx 5MB)
            if banner.size > 5 * 1024 * 1024:
                raise ValidationError("O tamanho da imagem não deve exceder 5MB.")
            # A validação se é imagem é feita automaticamente pelo ImageField do Django
        return banner

    def __init__(self, *args, **kwargs):
        super(EventoForm, self).__init__(*args, **kwargs)
        # Adiciona uma classe CSS a todos os campos para estilização
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'