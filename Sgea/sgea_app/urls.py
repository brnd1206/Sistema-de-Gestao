# sgea_app/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as token_views
from . import views
from . import api_views

urlpatterns = [
    # --- Autenticação ---
    path('', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # URL de Ativação por E-mail
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # --- Dashboards ---
    path('dashboard/participante/', views.participantes_dashboard, name='participantes_dashboard'),
    path('dashboard/organizador/', views.organizador_dashboard, name='organizador_dashboard'),

    # --- Log Organizador ---
    path('organizador/novo-participante/', views.organizador_cadastrar_participante, name='organizador_cadastrar_participante'),
    path('organizador/auditoria/', views.logs_auditoria, name='logs_auditoria'),

    # --- CRUD de Eventos ---
    path('evento/criar/', views.criar_evento, name='criar_evento'),
    path('evento/<int:pk>/atualizar/', views.atualizar_evento, name='atualizar_evento'),
    path('evento/<int:pk>/deletar/', views.deletar_evento, name='deletar_evento'),
    path('evento/<int:pk>/', views.detalhes_evento, name='detalhes_evento'),

    # --- Inscrição e Cancelamento ---
    path('evento/<int:pk>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('evento/<int:pk>/cancelar/', views.cancelar_inscricao, name='cancelar_inscricao'),

    # --- Gestão de Participantes e Certificados ---
    path('evento/<int:pk>/participantes/', views.gerenciar_participantes, name='gerenciar_participantes'),
    
    # Rota nova do seu amigo (Marcar Presença)
    path('inscricao/<int:inscricao_pk>/presenca/', views.marcar_presenca, name='marcar_presenca'),

    # --- API Endpoints ---
    # Endpoint para obter o token (Login da API)
    path('api/token-auth/', token_views.obtain_auth_token, name='api_token_auth'),

    # Consulta de Eventos (GET) - Limitada a 20/dia
    path('api/eventos/', api_views.EventoListAPIView.as_view(), name='api_eventos_list'),

    # Inscrição (POST) - Limitada a 50/dia
    path('api/inscrever/', api_views.InscricaoCreateAPIView.as_view(), name='api_inscrever'),
]