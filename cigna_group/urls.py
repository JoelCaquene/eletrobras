# cigna_group/urls.py

from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Redireciona a URL raiz para a página de login
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('menu/', views.menu_view, name='menu'),
    path('deposito/', views.deposito_view, name='deposito'),
    path('saque/', views.saque_view, name='saque'),
    path('tarefa/', views.tarefa_view, name='tarefa'),
    path('realizar-tarefa/', views.realizar_tarefa, name='realizar_tarefa'),
    path('nivel/', views.nivel_view, name='nivel'),
    
    # URL para alugar o nível
    path('alugar-nivel/', views.alugar_nivel, name='alugar_nivel'),
    
    path('equipa/', views.equipa_view, name='equipa'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'),
    path('editar-senha/', views.editar_senha_view, name='editar_senha'),
    
    # NOVAS URLs para a funcionalidade de Prêmios de Subsídio (substituem a roleta)
    path('premios-subsidios/', views.premios_subsidios_view, name='premios_subsidios'),
    path('abrir-premio/', views.abrir_premio, name='abrir_premio'), 
    
    path('sobre/', views.sobre_view, name='sobre'),
    path('renda/', views.renda_view, name='renda'),
    path('saida/', views.logout_view, name='saida'),
]
