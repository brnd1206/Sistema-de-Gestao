# sgea_app/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Evento, Inscricao
from .serializers import EventoSerializer, InscricaoSerializer


# 3.1. Consulta de Eventos
class EventoListAPIView(generics.ListAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]

    # Define o escopo para limitar a 20 requisições/dia (configurado no settings)
    throttle_scope = 'consulta_eventos'


# 3.2. Inscrição de Participantes
class InscricaoCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # Define o escopo para limitar a 50 requisições/dia
    throttle_scope = 'inscricao_participante'

    def post(self, request):
        serializer = InscricaoSerializer(data=request.data)
        if serializer.is_valid():
            evento = serializer.validated_data['evento']
            usuario = request.user

            # Verifica se já está inscrito (regra de negócio)
            if Inscricao.objects.filter(usuario=usuario, evento=evento).exists():
                return Response(
                    {"detail": "Você já está inscrito neste evento."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cria a inscrição vinculando ao usuário logado
            Inscricao.objects.create(usuario=usuario, evento=evento)
            return Response(
                {"detail": f"Inscrição realizada com sucesso no evento {evento.nome}!"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)