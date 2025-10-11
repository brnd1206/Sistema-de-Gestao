from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Evento, Usuario

class UsuarioCreationForm(UserCreationForm):
    # Adicionando os campos extras que não estão no UserCreationForm padrão
    nome = forms.CharField(max_length=150, required=True, help_text="Nome é obrigatório.")
    telefone = forms.CharField(max_length=15, required=False, help_text="Ex: (11) 99999-9999")
    instituicao_ensino = forms.CharField(max_length=255, required=False, label="Instituição de Ensino")

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Define a ordem dos campos no formulário
        fields = (
            'username', 
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
            'quantidade_participantes'
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

    def __init__(self, *args, **kwargs):
        super(EventoForm, self).__init__(*args, **kwargs)
        # Adiciona uma classe CSS a todos os campos para estilização
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'