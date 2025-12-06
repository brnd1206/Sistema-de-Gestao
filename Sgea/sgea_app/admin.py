from django.contrib import admin
from .models import Usuario, Evento, Inscricao, Certificado

admin.site.register(Usuario)
admin.site.register(Evento)
admin.site.register(Inscricao)
admin.site.register(Certificado)
