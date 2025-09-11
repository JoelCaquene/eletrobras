from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from decimal import Decimal

# Manager personalizado para o modelo de usuário
class UsuarioManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('O número de telefone é obrigatório')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Inicializa Renda para o novo usuário
        Renda.objects.create(usuario=user)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, password, **extra_fields)

# Modelo de Usuário Personalizado
class Usuario(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Número de Telefone")
    username = models.CharField(max_length=150, unique=True, blank=True, null=True, verbose_name="Nome de Usuário")
    invitation_code = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name="Código de Convite")
    inviter = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_users', verbose_name="Convidante")
    
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo Geral")
    saldo_disponivel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo Disponível para Saque")
    saldo_subsidio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo de Subsídios")
    total_sacado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Sacado")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Campos para controle de giros (agora usados para 'Abrir Prêmio')
    can_spin_roulette = models.BooleanField(default=False, verbose_name="Pode Abrir Prêmio")
    spins_remaining = models.IntegerField(default=0, verbose_name="Prêmios Restantes para Abrir")
    last_spin_reset = models.DateTimeField(null=True, blank=True, verbose_name="Último Reset de Prêmios")


    objects = UsuarioManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

# Modelo para Configurações Gerais da cigna_group
class Config(models.Model):
    taxa_saque = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Taxa de Saque (%)")
    saque_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, verbose_name="Saque Mínimo (USD)")
    horario_saque_inicio = models.TimeField(default=timezone.datetime(2000, 1, 1, 8, 0).time(), verbose_name="Início Horário de Saque")
    horario_saque_fim = models.TimeField(default=timezone.datetime(2000, 1, 1, 18, 0).time(), verbose_name="Fim Horário de Saque")
    link_grupo_whatsapp = models.URLField(blank=True, null=True, verbose_name="Link do Grupo WhatsApp")
    link_grupo_telegram = models.URLField(blank=True, null=True, verbose_name="Link do Grupo Telegram")
    link_apoio_whatsapp_cadastro = models.URLField(blank=True, null=True, verbose_name="Link de Apoio WhatsApp (Pág. Cadastro)")
    
    class Meta:
        verbose_name = "Configuração da cigna_group"
        verbose_name_plural = "Configurações da cigna_group"

    def __str__(self):
        return "Configurações da cigna_group Cigna Group"

# Modelo para Níveis de Investimento
class Nivel(models.Model):
    nome_nivel = models.CharField(max_length=100, unique=True, verbose_name="Nome do Nível")
    deposito_minimo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Depósito Mínimo para Alugar (USD)")
    ganho_diario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ganho Diário (USD)")
    ciclo_dias = models.IntegerField(verbose_name="Ciclo de Duração (dias)")
    imagem = models.ImageField(upload_to='niveis_imagens/', blank=True, null=True, verbose_name="Imagem do Nível")

    class Meta:
        verbose_name = "Nível de Investimento"
        verbose_name_plural = "Níveis de Investimento"

    def __str__(self):
        return self.nome_nivel
    
    @property
    def ganho_mensal(self):
        # Calcula o ganho mensal estimado (considerando 30 dias para simplificar)
        return self.ganho_diario * 30

# Modelo para Detalhes Bancários da cigna_group
class PlatformBankDetails(models.Model):
    nome_banco = models.CharField(max_length=100, unique=True, verbose_name="Nome do Banco")
    nome_titular_conta = models.CharField(max_length=200, verbose_name="Nome do Titular da Conta")
    iban = models.CharField(max_length=30, unique=True, verbose_name="IBAN")

    class Meta:
        verbose_name = "Detalhe Bancário da cigna_group"
        verbose_name_plural = "Detalhes Bancários da cigna_group"

    def __str__(self):
        return self.nome_banco

# Modelo para Depósitos
class Deposito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='depositos', verbose_name="Usuário")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Depósito (USD)")
    comprovativo_imagem = models.ImageField(upload_to='comprovantes_depositos/', verbose_name="Comprovativo de Depósito")
    status = models.CharField(max_length=20, default='Pendente', choices=[('Pendente', 'Pendente'), ('Aprovado', 'Aprovado'), ('Rejeitado', 'Rejeitado')], verbose_name="Status")
    data_deposito = models.DateTimeField(default=timezone.now, verbose_name="Data do Depósito")

    class Meta:
        verbose_name = "Depósito"
        verbose_name_plural = "Depósitos"

    def __str__(self):
        return f"Depósito de {self.valor} USD por {self.usuario.phone_number} - {self.status}"

# Modelo para Detalhes Bancários do Cliente
class ClientBankDetails(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='bank_details', verbose_name="Usuário")
    nome_banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome do Banco")
    nome_titular_conta = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Titular da Conta")
    iban = models.CharField(max_length=30, blank=True, null=True, verbose_name="IBAN")

    class Meta:
        verbose_name = "Detalhe Bancário do Cliente"
        verbose_name_plural = "Detalhes Bancários dos Clientes"

    def __str__(self):
        return f"Detalhes bancários de {self.usuario.phone_number}"

# Modelo para Níveis Alugados
class NivelAlugado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='niveis_alugados', verbose_name="Usuário")
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, verbose_name="Nível Alugado")
    data_inicio = models.DateTimeField(default=timezone.now, verbose_name="Data de Início")
    data_expiracao = models.DateTimeField(verbose_name="Data de Expiração")
    is_active = models.BooleanField(default=True, verbose_name="Está Ativo?")
    ultima_tarefa = models.DateTimeField(null=True, blank=True, verbose_name="Última Tarefa Realizada")

    class Meta:
        verbose_name = "Nível Alugado"
        verbose_name_plural = "Níveis Alugados"

    def __str__(self):
        return f"{self.usuario.phone_number} alugou {self.nivel.nome_nivel}"

    def save(self, *args, **kwargs):
        if not self.id:  # Apenas ao criar um novo objeto
            self.data_expiracao = self.data_inicio + timezone.timedelta(days=self.nivel.ciclo_dias)
        super().save(*args, **kwargs)

# Modelo para Saques
class Saque(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='saques', verbose_name="Usuário")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Saque (USD)")
    iban_cliente = models.CharField(max_length=30, blank=True, null=True, verbose_name="IBAN do Cliente")
    status = models.CharField(max_length=20, default='Pendente', choices=[('Pendente', 'Pendente'), ('Aprovado', 'Aprovado'), ('Rejeitado', 'Rejeitado')], verbose_name="Status")
    data_saque = models.DateTimeField(default=timezone.now, verbose_name="Data da Solicitação")

    class Meta:
        verbose_name = "Saque"
        verbose_name_plural = "Saques"

    def __str__(self):
        return f"Saque de {self.valor} USD por {self.usuario.phone_number} - {self.status}"

# Modelo para Renda (totaliza saldos do usuário)
class Renda(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='renda_geral', verbose_name="Usuário")
    # Os campos abaixo agora são gerenciados no modelo Usuario para simplificação
    # saldo_disponivel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # saldo_subsidio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # total_sacado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Renda do Usuário"
        verbose_name_plural = "Rendas dos Usuários"

    def __str__(self):
        return f"Renda de {self.usuario.phone_number}"

# Modelo para Tarefas
class Tarefa(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tarefas_realizadas', verbose_name="Usuário")
    data_realizacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Realização")
    ganho = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ganho da Tarefa (USD)")

    class Meta:
        verbose_name = "Tarefa Realizada"
        verbose_name_plural = "Tarefas Realizadas"

    def __str__(self):
        return f"Tarefa de {self.usuario.phone_number} - {self.ganho} USD"

# NOVO Modelo para Prêmios de Subsídio (substitui RoletaPremio)
class PremioSubsidio(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Prêmio (USD)")
    chance = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Chance (0.00 a 100.00)")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Prêmio de Subsídio"
        verbose_name_plural = "Prêmios de Subsídio"
        ordering = ['-chance']

    def __str__(self):
        return f"{self.valor} USD ({self.chance}%)"

# Modelo para o Conteúdo da Página "Sobre"
class Sobre(models.Model):
    conteudo = models.TextField(verbose_name="Conteúdo da Página 'Sobre'")
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Conteúdo 'Sobre'"
        verbose_name_plural = "Conteúdo 'Sobre'"

    def __str__(self):
        return "Conteúdo da Página 'Sobre' da cigna_group"
