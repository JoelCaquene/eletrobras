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
    
    # Adicionando a URL para a edição de coordenadas bancárias
    path('editar-coordenadas-bancarias/', views.editar_coordenadas_bancarias, name='editar_coordenadas_bancarias'),

    # URL para a página da Roleta
    path('roleta/', views.premios_subsidios_view, name='roleta'),
    
    # URLs para a roleta funcionar corretamente
    path('get-roleta-data/', views.get_roleta_data, name='get_roleta_data'),
    path('girar-roleta/', views.girar_roleta, name='girar_roleta'),
    
    path('nos/', views.sobre_view, name='nos'),
    path('renda/', views.renda_view, name='renda'),
    path('saida/', views.logout_view, name='saida'),
]
