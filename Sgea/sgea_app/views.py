# sgea_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import uuid

# --- Imports para E-mail e Ativação (Vindos do seu Stash) ---
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse

from .models import Evento, Inscricao, Usuario, Certificado
from .forms import UsuarioCreationForm, EventoForm

# --- Autenticação (Com sua lógica de E-mail) ---

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
                if user.perfil == 'organizador':
                    return redirect('organizador_dashboard')
                else:
                    return redirect('participantes_dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'sgea_app/index.html', {'form': form})

def cadastro(request):
    # Lógica de E-mail mantida (Do seu Stash)
    if request.user.is_authenticated:
        return redirect('participantes_dashboard')

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            # 1. Salva na memória
            user = form.save(commit=False)
            
            nome_digitado = form.cleaned_data.get('nome')
            if nome_digitado:
                user.first_name = nome_digitado
            
            # 2. Desativa para confirmação
            user.is_active = False 
            user.save()

            # 3. Envia E-mail
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
    # Lógica de Ativação mantida (Do seu Stash)
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Sua conta foi ativada com sucesso! Faça login para continuar.')
        return redirect('login')
    else:
        return HttpResponse('O link de ativação é inválido ou expirou!')


# --- Funcionalidades Auxiliares (Do Upstream/Amigo) ---

def verificar_e_gerar_certificado(inscricao):
    """
    Verifica se a inscrição cumpre os requisitos e gera o certificado automaticamente.
    Mantido do código do seu amigo (funcionalidade importante).
    """
    evento = inscricao.evento
    if inscricao.presenca and evento.data_fim < timezone.now():
        if not hasattr(inscricao, 'certificado'):
            codigo = uuid.uuid4().hex[:16].upper()
            Certificado.objects.create(inscricao=inscricao, codigo_validacao=codigo)
            return True
    return False


# --- Dashboard do Participante e Inscrições ---

@login_required
def participantes_dashboard(request):
    # Mesclado: Usa a versão do seu amigo que gera certificados automáticos
    inscricoes_pendentes = Inscricao.objects.filter(
        usuario=request.user,
        presenca=True,
        certificado__isnull=True,
        evento__data_fim__lt=timezone.now()
    )
    for inscricao in inscricoes_pendentes:
        verificar_e_gerar_certificado(inscricao)

    eventos_inscritos = Evento.objects.filter(participantes=request.user)
    eventos_disponiveis = Evento.objects.exclude(participantes=request.user)

    # Suporte a professor (Do upstream)
    eventos_responsavel = []
    if request.user.perfil == 'professor':
        eventos_responsavel = Evento.objects.filter(organizador=request.user) # Ajustei para organizador pois professor_responsavel não estava no model original enviado, mas se existir, troque aqui.

    certificados_obtidos = Certificado.objects.filter(inscricao__usuario=request.user).select_related('inscricao__evento')

    context = {
        'eventos_inscritos': eventos_inscritos,
        'eventos_disponiveis': eventos_disponiveis,
        'certificados_obtidos': certificados_obtidos,
        'eventos_responsavel': eventos_responsavel,
    }
    return render(request, 'sgea_app/dashboard/participantes_dashboard.html', context)

@login_required
def inscrever_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if request.method == 'POST':
        # Mesclado: Mantida a verificação de limite de vagas (Do Upstream)
        if evento.participantes.count() >= evento.quantidade_participantes:
            messages.error(request, f"Desculpe, as vagas para o evento '{evento.nome}' estão esgotadas.")
            return redirect('participantes_dashboard')
            
        ja_inscrito = Inscricao.objects.filter(usuario=request.user, evento=evento).exists()
        if not ja_inscrito:
            Inscricao.objects.create(usuario=request.user, evento=evento)
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
            messages.info(request, f"Sua inscrição no evento '{evento.nome}' foi cancelada.")
        
    return redirect('participantes_dashboard')


# --- Dashboard do Organizador e CRUD de Eventos ---

@login_required
def organizador_dashboard(request):
    if request.user.perfil != 'organizador':
        return redirect('participantes_dashboard')
    
    eventos = Evento.objects.filter(organizador=request.user).order_by('-data_inicio')
    context = {
        'eventos': eventos
    }
    return render(request, 'sgea_app/dashboard/organizador_dashboard.html', context)

@login_required
def criar_evento(request):
    if request.user.perfil != 'organizador':
        return redirect('participantes_dashboard')

    if request.method == 'POST':
        # Mesclado: Adicionado request.FILES para permitir upload de Banner (Do Upstream)
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
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
        # Mesclado: Adicionado request.FILES aqui também
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
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
        evento.delete()
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

# --- Gerenciamento de Certificados (Versão Melhorada do Upstream) ---

@login_required
def gerenciar_participantes(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    # Mesclado: Varre a lista e gera o que estiver pendente
    if evento.data_fim < timezone.now():
        pendentes = Inscricao.objects.filter(evento=evento, presenca=True, certificado__isnull=True)
        for insc in pendentes:
            verificar_e_gerar_certificado(insc)

    inscricoes = Inscricao.objects.filter(evento=evento).select_related('usuario', 'certificado').order_by('usuario__first_name')

    context = {
        'evento': evento,
        'inscricoes': inscricoes
    }
    return render(request, 'sgea_app/eventos/gerenciar_participantes.html', context)

@login_required
def emitir_certificado(request, inscricao_pk):
    inscricao = get_object_or_404(Inscricao, pk=inscricao_pk)
    evento = inscricao.evento

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    if request.method == 'POST':
        if not hasattr(inscricao, 'certificado'):
            codigo = uuid.uuid4().hex[:16].upper()
            Certificado.objects.create(inscricao=inscricao, codigo_validacao=codigo)
            messages.success(request, f"Certificado para {inscricao.usuario.first_name} emitido com sucesso!")
        else:
            messages.warning(request, "Este participante já possui um certificado.")

    return redirect('gerenciar_participantes', pk=evento.pk)

@login_required
def marcar_presenca(request, inscricao_pk):
    # Funcionalidade do Upstream
    inscricao = get_object_or_404(Inscricao, pk=inscricao_pk)
    evento = inscricao.evento

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    # Alterna presença
    inscricao.presenca = not inscricao.presenca
    inscricao.save()

    # Tenta gerar certificado automaticamente
    verificar_e_gerar_certificado(inscricao)

    return redirect('gerenciar_participantes', pk=evento.pk)

@login_required
def gerar_certificados_evento(request, pk):
    # Funcionalidade do Upstream: Botão para gerar tudo de uma vez
    evento = get_object_or_404(Evento, pk=pk)

    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    if timezone.now() < evento.data_fim:
        messages.error(request, "Erro: O evento ainda não terminou. Aguarde a data de fim.")
        return redirect('gerenciar_participantes', pk=evento.pk)

    inscricoes_validas = Inscricao.objects.filter(
        evento=evento,
        presenca=True,
        certificado__isnull=True
    )

    if not inscricoes_validas.exists():
        messages.warning(request, "Nenhum participante pendente com presença confirmada.")
        return redirect('gerenciar_participantes', pk=evento.pk)

    count = 0
    for inscricao in inscricoes_validas:
        codigo = uuid.uuid4().hex[:16].upper()
        Certificado.objects.create(inscricao=inscricao, codigo_validacao=codigo)
        count += 1

    messages.success(request, f"{count} certificados gerados com sucesso!")
    return redirect('gerenciar_participantes', pk=evento.pk)