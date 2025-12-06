# sgea_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid

from .models import Evento, Inscricao, Certificado
from .forms import UsuarioCreationForm, EventoForm
from django.utils import timezone

# --- Autenticação ---

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
    if request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UsuarioCreationForm()
    
    return render(request, 'sgea_app/usuarios/cadastro.html', {'form': form})


# --- Dashboard do Participante e Inscrições ---

@login_required
def participantes_dashboard(request):
    # --- AUTOMAÇÃO: Gera certificados pendentes ao acessar o dashboard ---
    inscricoes_pendentes = Inscricao.objects.filter(
        usuario=request.user,
        presenca=True,
        certificado__isnull=True,
        evento__data_fim__lt=timezone.now()  # Apenas eventos passados
    )
    for inscricao in inscricoes_pendentes:
        verificar_e_gerar_certificado(inscricao)
    eventos_inscritos = Evento.objects.filter(participantes=request.user)
    eventos_disponiveis = Evento.objects.exclude(participantes=request.user)

    # Professor responsavel
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
def inscrever_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if request.method == 'POST':
        # Sistema não permitirá inscrição quando limite for atingido
        if evento.participantes.count() >= evento.quantidade_participantes:
            messages.error(request, f"Desculpe, as vagas para o evento '{evento.nome}' estão esgotadas.")
            return redirect('participantes_dashboard')
        # Inscrição Única (Verificação na View para mensagem amigável)
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
    # Busca o evento ou retorna erro 404 se não existir
    evento = get_object_or_404(Evento, pk=pk)

    # Verifica se o usuário já está inscrito neste evento (para exibir botão correto)
    inscrito = False
    if request.user.is_authenticated:
        inscrito = Inscricao.objects.filter(usuario=request.user, evento=evento).exists()

    context = {
        'evento': evento,
        'inscrito': inscrito
    }
    return render(request, 'sgea_app/eventos/detalhes_evento.html', context)

# --- Gerenciamento de Certificados ---

@login_required
def gerenciar_participantes(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.organizador != request.user:
        return redirect('organizador_dashboard')
    # --- AUTOMAÇÃO: Varre a lista e gera o que estiver pendente ---
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

@login_required
def marcar_presenca(request, inscricao_pk):
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
    """Gera certificados para TODOS os presentes após o fim do evento"""
    evento = get_object_or_404(Evento, pk=pk)

    # 1. Segurança: Apenas organizador
    if evento.organizador != request.user:
        return redirect('organizador_dashboard')

    # 2. Validação de Data: Só gera se o evento já acabou
    if timezone.now() < evento.data_fim:
        messages.error(request, "Erro: O evento ainda não terminou. Aguarde a data de fim.")
        return redirect('gerenciar_participantes', pk=evento.pk)

    # 3. Busca alunos presentes que AINDA NÃO têm certificado
    inscricoes_validas = Inscricao.objects.filter(
        evento=evento,
        presenca=True,
        certificado__isnull=True
    )

    if not inscricoes_validas.exists():
        messages.warning(request, "Nenhum participante pendente com presença confirmada.")
        return redirect('gerenciar_participantes', pk=evento.pk)

    # 4. Gera em lote
    count = 0
    for inscricao in inscricoes_validas:
        codigo = uuid.uuid4().hex[:16].upper()
        Certificado.objects.create(inscricao=inscricao, codigo_validacao=codigo)
        count += 1

    messages.success(request, f"{count} certificados gerados com sucesso!")
    return redirect('gerenciar_participantes', pk=evento.pk)