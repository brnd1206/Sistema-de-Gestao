from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# --- Modelos de Usuário ---

class Usuario(AbstractUser):
    PERFIL_CHOICES = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('organizador', 'Organizador'),
    )
    
    telefone = models.CharField(max_length=15, blank=True, null=True, help_text="Telefone de contato do usuário.")
    instituicao_ensino = models.CharField(max_length=255, blank=True, null=True, help_text="Instituição de ensino (obrigatório para alunos e professores).")
    perfil = models.CharField(max_length=15, choices=PERFIL_CHOICES, default='aluno', help_text="Perfil do usuário no sistema.")

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def save(self, *args, **kwargs):
        # Garante que instituição de ensino seja obrigatório para aluno e professor
        if self.perfil in ['aluno', 'professor'] and not self.instituicao_ensino:
            raise ValueError("Instituição de ensino é obrigatória para alunos e professores.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


# --- Modelos de Evento ---

class Evento(models.Model):
    """
    Modelo para armazenar as informações dos eventos.
    """
    TIPO_EVENTO_CHOICES = (
        ('seminario', 'Seminário'),
        ('palestra', 'Palestra'),
        ('congresso', 'Congresso'),
        ('workshop', 'Workshop'),
        ('outro', 'Outro'),
    )

    nome = models.CharField(max_length=200, help_text="Nome ou título do evento.")
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES, help_text="Tipo do evento (ex: seminário, palestra).")
    data_inicio = models.DateTimeField(help_text="Data e hora de início do evento.")
    data_fim = models.DateTimeField(help_text="Data e hora de término do evento.")
    local = models.CharField(max_length=255, help_text="Local onde o evento ocorrerá.")
    quantidade_participantes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Número máximo de participantes permitidos.")
    banner = models.ImageField(
        upload_to='eventos/banners/',
        blank=True,
        null=True,
        help_text="Imagem promocional do evento (apenas .jpg, .png, .jpeg).",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='eventos_organizados',
        limit_choices_to={'perfil': 'organizador'},
        help_text="Organizador responsável pelo evento."
    )
    participantes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='Inscricao', 
        related_name='eventos_inscritos',
        blank=True
    )
    professor_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_responsavel',
        limit_choices_to={'perfil': 'professor'},
        help_text="Professor responsável pelo evento."
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evento"
        ordering = ["-data_inicio", "nome"]
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def clean(self):
        # Validação de Data
        if self.data_inicio and self.data_inicio < timezone.now():
            raise ValidationError({'data_inicio': 'A data de início não pode ser anterior à data atual.'})

        # Validação extra: Data fim não pode ser antes do inicio
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({'data_fim': 'A data de término não pode ser anterior à data de início.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Chama o clean() antes de salvar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.data_inicio.strftime('%d/%m/%Y')}"


# --- Modelos de Relacionamento ---

class Inscricao(models.Model):
    """
    Modelo intermediário para vincular um Usuário a um Evento (inscrição).
    """
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscricoes")
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="inscricoes")
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inscricao"
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        unique_together = ('usuario', 'evento') # Garante que um usuário só se inscreva uma vez por evento

    def __str__(self):
        return f"{self.usuario.username} inscrito em {self.evento.nome}"


class Certificado(models.Model):
    """
    Modelo para registrar a emissão de certificados para usuários inscritos em eventos.
    """
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE, primary_key=True, help_text="A inscrição que deu origem a este certificado.")
    codigo_validacao = models.CharField(max_length=50, unique=True, help_text="Código único para validação do certificado.")
    data_emissao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "certificado"
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def __str__(self):
        return f"Certificado para {self.inscricao.usuario.username} no evento {self.inscricao.evento.nome}"