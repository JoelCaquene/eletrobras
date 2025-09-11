from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.template.defaultfilters import pluralize
from .models import (
    Usuario, Config, Nivel, PlatformBankDetails, Deposito, 
    ClientBankDetails, NivelAlugado, Saque, Renda, Tarefa, 
    PremioSubsidio,
    Sobre
)
from .views import aprovar_deposito_com_subsidio # Importa a função do views.py

# Customização do Admin para o modelo Usuario
class UsuarioAdmin(BaseUserAdmin):
    # Campos que aparecerão na lista de usuários no admin
    list_display = ('phone_number', 'username', 'invitation_code', 'is_staff', 'is_active', 'spins_remaining', 'can_spin_roulette')
    
    # Campos pelos quais você pode filtrar a lista
    list_filter = ('is_staff', 'is_active', 'can_spin_roulette')
    
    # Campos pelos quais você pode pesquisar
    search_fields = ('phone_number', 'username', 'invitation_code')
    
    # A ordem dos campos na página de edição do usuário
    ordering = ('phone_number',)
    
    # Grupos de campos na página de edição do usuário
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Informações Pessoais', {'fields': ('username', 'invitation_code', 'inviter')}),
        ('Saldos', {'fields': ('saldo', 'saldo_disponivel', 'saldo_subsidio', 'total_sacado')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Controle de Prêmios de Subsídio', {'fields': ('can_spin_roulette', 'spins_remaining', 'last_spin_reset')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Campos somente leitura
    readonly_fields = ('last_login', 'date_joined')

admin.site.register(Usuario, UsuarioAdmin)

# Registrando outros modelos
@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('taxa_saque', 'saque_minimo', 'horario_saque_inicio', 'horario_saque_fim')
    fieldsets = (
        (None, {'fields': ('taxa_saque', 'saque_minimo', 'horario_saque_inicio', 'horario_saque_fim')}),
        ('Links de Suporte', {'fields': ('link_grupo_whatsapp', 'link_grupo_telegram', 'link_apoio_whatsapp_cadastro')}),
    )

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ('nome_nivel', 'deposito_minimo', 'ganho_diario', 'ciclo_dias')
    search_fields = ('nome_nivel',)

@admin.register(PlatformBankDetails)
class PlatformBankDetailsAdmin(admin.ModelAdmin):
    list_display = ('nome_banco', 'nome_titular_conta', 'iban')
    search_fields = ('nome_banco', 'iban')

@admin.register(Deposito)
class DepositoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'status', 'data_deposito', 'link_comprovativo') # Adicionado link para o comprovativo
    list_filter = ('status', 'data_deposito')
    search_fields = ('usuario__phone_number',)
    raw_id_fields = ('usuario',)

    # Ação personalizada para aprovar depósitos
    @admin.action(description="Aprovar depósitos selecionados e conceder subsídios")
    def aprovar_deposito_action(self, request, queryset):
        # Itera sobre os depósitos selecionados e chama a função de aprovação
        total_aprovados = 0
        for deposito in queryset:
            resultado = aprovar_deposito_com_subsidio(deposito.id)
            if resultado['status'] == 'success' or resultado['status'] == 'info':
                total_aprovados += 1
        
        # Mensagem para o usuário do admin
        if total_aprovados > 0:
            self.message_user(request, f"{total_aprovados} depósito{pluralize(total_aprovados)} aprovado{pluralize(total_aprovados)} com sucesso e subsídio{pluralize(total_aprovados)} concedido{pluralize(total_aprovados)}, se aplicável.")
        else:
            self.message_user(request, "Nenhum depósito foi aprovado ou já estavam aprovados.", level='warning')

    # Adiciona a ação personalizada à lista de ações do admin
    actions = [aprovar_deposito_action]

    # Função para exibir o link da imagem do comprovativo
    def link_comprovativo(self, obj):
        if obj.comprovativo_imagem:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank">Ver Comprovativo</a>', obj.comprovativo_imagem.url)
        return "Sem Comprovativo"
    link_comprovativo.short_description = "Comprovativo"


@admin.register(ClientBankDetails)
class ClientBankDetailsAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nome_banco', 'iban')
    search_fields = ('usuario__phone_number', 'iban')
    raw_id_fields = ('usuario',)

@admin.register(NivelAlugado)
class NivelAlugadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nivel', 'data_inicio', 'data_expiracao', 'is_active', 'ultima_tarefa')
    list_filter = ('is_active', 'nivel')
    search_fields = ('usuario__phone_number', 'nivel__nome_nivel')
    raw_id_fields = ('usuario', 'nivel')

@admin.register(Saque)
class SaqueAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'status', 'data_saque')
    list_filter = ('status', 'data_saque')
    search_fields = ('usuario__phone_number', 'iban_cliente')
    raw_id_fields = ('usuario',)

@admin.register(Renda)
class RendaAdmin(admin.ModelAdmin):
    list_display = ('usuario',) # Os campos de saldo estão em Usuario
    search_fields = ('usuario__phone_number',)
    raw_id_fields = ('usuario',)

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ganho', 'data_realizacao')
    list_filter = ('data_realizacao',)
    search_fields = ('usuario__phone_number',)
    raw_id_fields = ('usuario',)

# NOVO Registro para PremioSubsidio (substitui RoletaPremioAdmin)
@admin.register(PremioSubsidio)
class PremioSubsidioAdmin(admin.ModelAdmin):
    list_display = ('valor', 'chance', 'descricao')
    list_editable = ('chance', 'descricao') # Permite editar direto na lista

@admin.register(Sobre)
class SobreAdmin(admin.ModelAdmin):
    list_display = ('ultima_atualizacao',)
