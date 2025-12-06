# sgea_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.utils.dateparse import parse_date
import uuid

# --- Imports para E-mail e Ativação ---
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse

from .models import Evento, Inscricao, Certificado, LogAuditoria
from .forms import UsuarioCreationForm, EventoForm


# --- Funções Auxiliares ---

def registrar_log(request, acao, detalhes=""):
    """Salva um registro na tabela de auditoria"""
    ip = request.META.get('REMOTE_ADDR')
    user = request.user if request.user.is_authenticated else None

    LogAuditoria.objects.create(
        usuario=user,
        acao=acao,
        detalhes=detalhes,
        ip_usuario=ip
    )


def verificar_e_gerar_certificado(inscricao):
    """
    Verifica se a inscrição cumpre os requisitos e gera o certificado automaticamente.
    Requisitos: Evento finalizado + Presença confirmada + Sem certificado existente.
    """
    evento = inscricao.evento
    if inscricao.presenca and evento.data_fim < timezone.now():
        if not hasattr(inscricao, 'certificado'):
            codigo = uuid.uuid4().hex[:16].upper()
            Certificado.objects.create(inscricao=inscricao, codigo_validacao=codigo)
            return True
    return False


# --- Autenticação e Cadastro ---

def login_view(request):
    if request.user.is_authenticated:
        if request.user.perfil == 'organizador':
            return redirect('organizador_dashboard')
        else:
            return redirect('participantes_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                registrar_log(request, 'login', "Usuário realizou login.")
                if user.perfil == 'organizador':
                    return redirect('organizador_dashboard')
                else:
                    return redirect('participantes_dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'sgea_app/index.html', {'form': form})


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('participantes_dashboard')

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            # 1. Salva na memória mas não no banco ainda se for usar ativação
            user = form.save(commit=False)

            # Ajuste opcional para nome
            nome_digitado = form.cleaned_data.get('nome')
            if nome_digitado:
                user.first_name = nome_digitado

            # 2. Desativa para confirmação por email
            user.is_active = False
            user.save()

            registrar_log(request, 'criacao_usuario', f"Autocadastro: {user.username}")

            # 3. Envia E-mail de Ativação
            current_site = get_current_site(request)
            mail_subject = 'Confirmação de Cadastro - SGEA'

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            context = {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            }

            # Certifique-se de ter este template criado
            message = render_to_string('sgea_app/emails/acc_active_email.html', context)
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.content_subtype = "html"
            email.send()

            return render(request, 'sgea_app/usuarios/email_sent.html')

    else:
        form = UsuarioCreationForm()

    return render(request, 'sgea_app/usuarios/cadastro.html', {'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        registrar_log(request, 'ativacao_conta', f"Conta ativada: {user.username}")
        messages.success(request, 'Sua conta foi ativada com sucesso! Faça login para continuar.')
        return redirect('login')
    else:
        return HttpResponse('O link de ativação é inválido ou expirou!')


# --- Dashboards ---

@login_required
def participantes_dashboard(request):
    # 1. Automação: Gera certificados pendentes ao acessar o dashboard
    inscricoes_pendentes = Inscricao.objects.filter(
        usuario=request.user,
        presenca=True,
        certificado__isnull=True,
        evento__data_fim__lt=timezone.now()
    )
    for inscricao in inscricoes_pendentes:
        verificar_e_gerar_certificado(inscricao)

    # 2. Listas de Eventos
    eventos_inscritos = Evento.objects.filter(participantes=request.user)
    eventos_disponiveis = Evento.objects.exclude(
        participantes=request.user
    ).filter(
        data_fim__gte=timezone.now()
    )

    # 3. Lista de Responsabilidade do Professor
    eventos_responsavel = []
    if request.user.perfil == 'professor':
        eventos_responsavel = Evento.objects.filter(professor_responsavel=request.user)

    certificados_obtidos = Certificado.objects.filter(inscricao__usuario=request.user).select_related(
        'inscricao__evento')

    context = {
        'eventos_inscritos': eventos_inscritos,
        'eventos_disponiveis': eventos_disponiveis,
        'certificados_obtidos': certificados_obtidos,
        'eventos_responsavel': eventos_responsavel,
    }
    return render(request, 'sgea_app/dashboard/participantes_dashboard.html', context)


@login_required
def organizador_dashboard(request):
    if request.user.perfil != 'organizador':
        return redirect('participantes_dashboard')

    eventos = Evento.objects.filter(organizador=request.user).order_by('-data_inicio')
    context = {
        'eventos': eventos
    }
    return render(request, 'sgea_app/dashboard/organizador_dashboard.html', context)


# --- Gestão de Eventos (CRUD) ---

@login_required
def criar_evento(request):
    if request.user.perfil != 'organizador':
        return redirect('participantes_dashboard')

    if request.method == 'POST':
        # Importante: request.FILES para upload de banner
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()

            registrar_log(request, 'evento_cadastro', f"Evento criado: {evento.nome} (ID: {evento.id})")
            return redirect('organizador_dashboard')
    else:
        form = EventoForm()

    return render(request, 'sgea_app/eventos/evento_form.html', {'form': form, 'titulo': 'Criar Novo Evento'})


@login_required
def atualizar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            registrar_log(request, 'evento_edicao', f"Evento editado: {evento.nome} (ID: {evento.id})")
            return redirect('organizador_dashboard')
    else:
        form = EventoForm(instance=evento)

    return render(request, 'sgea_app/eventos/evento_form.html', {'form': form, 'titulo': 'Editar Evento'})


@login_required
def deletar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    if request.method == 'POST':
        nome_evento = evento.nome
        evento.delete()
        registrar_log(request, 'evento_exclusao', f"Evento deletado: {nome_evento}")
        return redirect('organizador_dashboard')

    return render(request, 'sgea_app/eventos/evento_confirm_delete.html', {'evento': evento})


def detalhes_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    inscrito = False
    if request.user.is_authenticated:
        inscrito = Inscricao.objects.filter(usuario=request.user, evento=evento).exists()

    context = {
        'evento': evento,
        'inscrito': inscrito
    }
    return render(request, 'sgea_app/eventos/detalhes_evento.html', context)


# --- Inscrições e Participantes ---

@login_required
def inscrever_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == 'POST':
        # Impede inscrição se o evento já terminou
        if evento.data_fim < timezone.now():
            messages.error(request, f"As inscrições para '{evento.nome}' estão encerradas (o evento já terminou).")
            return redirect('participantes_dashboard')

        # Regra: Limite de Vagas
        if evento.participantes.count() >= evento.quantidade_participantes:
            messages.error(request, f"Desculpe, as vagas para o evento '{evento.nome}' estão esgotadas.")
            return redirect('participantes_dashboard')

        ja_inscrito = Inscricao.objects.filter(usuario=request.user, evento=evento).exists()
        if not ja_inscrito:
            Inscricao.objects.create(usuario=request.user, evento=evento)
            registrar_log(request, 'inscricao', f"Inscrição realizada no evento: {evento.nome}")
            messages.success(request, f"Inscrição no evento '{evento.nome}' realizada com sucesso!")
        else:
            messages.warning(request, f"Você já está inscrito no evento '{evento.nome}'.")

    return redirect('participantes_dashboard')


@login_required
def cancelar_inscricao(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == 'POST':
        inscricao = Inscricao.objects.filter(usuario=request.user, evento=evento)
        if inscricao.exists():
            inscricao.delete()
            registrar_log(request, 'cancelamento', f"Cancelou inscrição no evento: {evento.nome}")
            messages.info(request, f"Sua inscrição no evento '{evento.nome}' foi cancelada.")

    return redirect('participantes_dashboard')


@login_required
def gerenciar_participantes(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    # Automação: Se o evento já acabou, verifica e gera certificados pendentes para quem tem presença
    if evento.data_fim < timezone.now():
        pendentes = Inscricao.objects.filter(evento=evento, presenca=True, certificado__isnull=True)
        gerados = 0
        for insc in pendentes:
            if verificar_e_gerar_certificado(insc):
                gerados += 1

        if gerados > 0:
            messages.success(request, f"{gerados} certificados foram gerados automaticamente.")

    inscricoes = Inscricao.objects.filter(evento=evento).select_related('usuario', 'certificado').order_by(
        'usuario__first_name')

    context = {
        'evento': evento,
        'inscricoes': inscricoes
    }
    return render(request, 'sgea_app/eventos/gerenciar_participantes.html', context)


@login_required
def marcar_presenca(request, inscricao_pk):
    inscricao = get_object_or_404(Inscricao, pk=inscricao_pk)
    evento = inscricao.evento

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    # Alterna status de presença
    inscricao.presenca = not inscricao.presenca
    inscricao.save()

    status_str = "Presente" if inscricao.presenca else "Ausente"
    registrar_log(request, 'presenca', f"Marcou {status_str} para {inscricao.usuario.username} no evento {evento.nome}")

    # Tenta gerar certificado automaticamente se o evento já acabou
    verificar_e_gerar_certificado(inscricao)

    return redirect('gerenciar_participantes', pk=evento.pk)


# --- Funcionalidades Extras do Organizador (Auditoria e Cadastro) ---

@login_required
def organizador_cadastrar_participante(request):
    """Permite ao organizador cadastrar novos usuários manualmente"""
    if request.user.perfil != 'organizador':
        return redirect('participantes_dashboard')

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            # Salva direto (sem enviar email de ativação, pois o organizador está criando)
            novo_usuario = form.save()

            registrar_log(
                request,
                'cadastro_usuario',
                f"Organizador cadastrou o usuário {novo_usuario.username} ({novo_usuario.perfil})"
            )

            messages.success(request, f"Usuário {novo_usuario.username} cadastrado com sucesso!")
            return redirect('organizador_dashboard')
    else:
        form = UsuarioCreationForm()

    # Reutiliza o template de cadastro, mas passa um título diferente
    return render(request, 'sgea_app/usuarios/cadastro.html', {
        'form': form,
        'titulo': 'Novo Participante (Admin)'
    })


@login_required
def logs_auditoria(request):
    """Exibe a lista de logs do sistema com filtros"""
    if request.user.perfil != 'organizador':
        return redirect('participantes_dashboard')

    # Busca logs e otimiza query com select_related
    logs = LogAuditoria.objects.all().select_related('usuario')

    # Filtros
    data_filtro = request.GET.get('data')
    usuario_filtro = request.GET.get('usuario')

    if data_filtro:
        data = parse_date(data_filtro)
        if data:
            logs = logs.filter(data_hora__date=data)

    if usuario_filtro:
        logs = logs.filter(usuario__username__icontains=usuario_filtro)

    return render(request, 'sgea_app/dashboard/logs_auditoria.html', {
        'logs': logs,
        'data_filtro': data_filtro,
        'usuario_filtro': usuario_filtro
    })