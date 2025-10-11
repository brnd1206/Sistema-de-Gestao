# sgea_app/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Dashboards
    path('dashboard/participante/', views.participantes_dashboard, name='participantes_dashboard'),
    path('dashboard/organizador/', views.organizador_dashboard, name='organizador_dashboard'),

    # URLs para o CRUD de Eventos
    path('evento/criar/', views.criar_evento, name='criar_evento'),
    path('evento/<int:pk>/atualizar/', views.atualizar_evento, name='atualizar_evento'),
    path('evento/<int:pk>/deletar/', views.deletar_evento, name='deletar_evento'),

    # URLs para Inscrição e Cancelamento
    path('evento/<int:pk>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('evento/<int:pk>/cancelar/', views.cancelar_inscricao, name='cancelar_inscricao'),

    # URLs para Certificados
    path('evento/<int:pk>/participantes/', views.gerenciar_participantes, name='gerenciar_participantes'),
    path('inscricao/<int:inscricao_pk>/emitir_certificado/', views.emitir_certificado, name='emitir_certificado'),
]