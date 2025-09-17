from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import uuid
from django.db import models, transaction
from .models import (
    Config, Usuario, Nivel, PlatformBankDetails, Deposito,
    ClientBankDetails, NivelAlugado, Saque, Renda, Tarefa, PremioSubsidio, Sobre
)
from .forms import UsuarioUpdateForm, ClientBankDetailsForm
from django.db import IntegrityError
from datetime import timedelta, datetime
from django.utils import timezone
import pytz
import random
from decimal import Decimal
from django.contrib.auth.forms import PasswordChangeForm
from collections import defaultdict

def cadastro_view(request):
    config = Config.objects.first()
    invitation_code_from_url = request.GET.get('convite')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        invitation_code_provided = request.POST.get('invitation_code')

        if not all([phone_number, password, password_confirm]):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('cadastro')

        if password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('cadastro')
        
        if len(password) < 4:
            messages.error(request, 'A senha deve ter no mínimo 4 dígitos.')
            return redirect('cadastro')

        if Usuario.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Este número de telefone já está em uso.')
            return redirect('cadastro')
            
        inviter_user = None
        if invitation_code_provided:
            try:
                inviter_user = Usuario.objects.get(invitation_code=invitation_code_provided)
            except Usuario.DoesNotExist:
                messages.error(request, 'Código de convite do indicador inválido.')
                return redirect('cadastro')

        try:
            with transaction.atomic():
                new_user_invitation_code = None
                while True:
                    temp_code = str(uuid.uuid4()).replace('-', '')[:10]
                    if not Usuario.objects.filter(invitation_code=temp_code).exists():
                        new_user_invitation_code = temp_code
                        break

                user = Usuario.objects.create_user(
                    phone_number=phone_number,
                    password=password,
                    invitation_code=new_user_invitation_code,
                    inviter=inviter_user
                )
                
                user.username = phone_number
                user.save()

            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('login')
        except IntegrityError as e:
            messages.error(request, 'Ocorreu um erro de duplicidade ao tentar cadastrar o usuário. Por favor, tente novamente ou contate o suporte.')
            return redirect('cadastro')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro inesperado ao tentar cadastrar: {e}')
            return redirect('cadastro')

    context = {
        'config': config,
        'convite_code': invitation_code_from_url
    }
    return render(request, 'eletrobras/cadastro.html', context)

def login_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login bem-sucedido.')
            return redirect('menu')
        else:
            messages.error(request, 'Número de telefone ou senha inválidos.')
            return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')

@login_required
def menu_view(request):
    niveis = Nivel.objects.all()
    config = Config.objects.first()
    context = {
        'niveis': niveis,
        'config': config,
    }
    return render(request, 'menu.html', context)

@login_required
def deposito_view(request):
    bancos = PlatformBankDetails.objects.all()
    banco_selecionado = None
    valor_deposito = None
    
    if request.method == 'POST':
        # Verifica qual formulário foi enviado
        if 'proof' in request.FILES:
            # Lógica para o formulário de envio de comprovante (Passo 3)
            try:
                valor_deposito_str = request.POST.get('valor_deposito')
                banco_nome = request.POST.get('banco_selecionado_nome')
                depositor_name = request.POST.get('depositor_name')
                comprovante = request.FILES['proof']

                # Limpeza e conversão do valor antes de criar o objeto Deposito
                if valor_deposito_str:
                    valor_deposito_str = valor_deposito_str.replace(',', '.')
                    valor_deposito = Decimal(valor_deposito_str)
                else:
                    raise ValueError('Valor do depósito não fornecido.')

                novo_deposito = Deposito.objects.create(
                    usuario=request.user,
                    valor=valor_deposito,
                    banco_destino_nome=banco_nome,
                    nome_cliente_banco=depositor_name,
                    comprovativo_imagem=comprovante,
                    status='Pendente'
                )
                
                messages.success(request, 'Comprovante enviado com sucesso! Aguarde a aprovação do administrador.')
                return redirect('menu')
                
            except Exception as e:
                # O erro de conversão será capturado aqui
                messages.error(request, f'Ocorreu um erro ao enviar o comprovante: {e}')
                # Redireciona para o passo 3, caso queira que o usuário tente novamente
                return redirect('deposito')
        else:
            # Lógica para o formulário de seleção do banco (Passo 1)
            valor_deposito = request.POST.get('valor_deposito')
            banco_nome = request.POST.get('method')
            
            try:
                banco_selecionado = PlatformBankDetails.objects.get(nome_banco=banco_nome)
            except PlatformBankDetails.DoesNotExist:
                messages.error(request, 'Banco não encontrado.')
                
    context = {
        'bancos': bancos,
        'banco_selecionado': banco_selecionado,
        'valor_deposito': valor_deposito,
    }
    return render(request, 'deposito.html', context)

def aprovar_deposito_com_subsidio(deposito_id):
    try:
        deposito = Deposito.objects.get(id=deposito_id)
    except Deposito.DoesNotExist:
        print(f"Erro: Depósito com ID {deposito_id} não encontrado.")
        return {'status': 'error', 'message': 'Depósito não encontrado.'}

    if deposito.status == 'Aprovado':
        print(f"Info: Depósito {deposito_id} já aprovado. Nenhuma ação necessária.")
        return {'status': 'info', 'message': 'Depósito já aprovado.'}

    try:
        with transaction.atomic():
            deposito.status = 'Aprovado'
            deposito.save()
            print(f"Depósito {deposito_id} marcado como 'Aprovado'.")

            deposito.usuario.saldo_disponivel += deposito.valor
            deposito.usuario.save()
            print(f"Valor do depósito ({deposito.valor:.2f} KZ) creditado ao saldo do usuário {deposito.usuario.phone_number}.")

            convidador = deposito.usuario.inviter
            if convidador:
                has_active_level_inviter = NivelAlugado.objects.filter(usuario=convidador, is_active=True).exists()
                if has_active_level_inviter:
                    percentagem_subs_convite = Decimal('0.15')
                    valor_subs_convite = deposito.valor * percentagem_subs_convite

                    convidador.saldo_subsidio += valor_subs_convite
                    convidador.saldo_disponivel += valor_subs_convite
                    convidador.save()
                    print(f"Subsídio de {valor_subs_convite:.2f} KZ concedido ao convidador {convidador.username if convidador.username else convidador.phone_number} (com nível ativo) pelo depósito de {deposito.usuario.username if deposito.usuario.username else deposito.usuario.phone_number}.")
                else:
                    print(f"Convidador {convidador.username if convidador.username else convidador.phone_number} NÃO tem nível ativo. Subsídio de convite NÃO concedido.")
            else:
                print("O usuário não foi convidado por ninguém. Nenhum subsídio de convite a ser processado.")
    
        return {'status': 'success', 'message': f'Depósito {deposito_id} aprovado e subsídio concedido, se aplicável.'}
    except Exception as e:
        print(f"Erro CRÍTICO ao aprovar depósito {deposito_id} e conceder subsídio: {e}")
        return {'status': 'error', 'message': f'Ocorreu um erro ao aprovar o depósito e processar o subsídio: {e}'}


@login_required
def saque_view(request):
    """
    Trata a exibição e a submissão de solicitações de saque (retirada) para o usuário.
    Implementa validações de horário, saldo mínimo, saldo disponível e taxa de saque.
    """
    # --- DEBUG START ---
    print("--- INICIANDO SAQUE_VIEW (GET/POST) ---")
    # --- DEBUG END ---

    usuario = request.user
    
    # --- DEBUG START ---
    print(f"Usuário logado: {usuario.phone_number}")
    # --- DEBUG END ---

    try:
        historico_saques = Saque.objects.filter(usuario=usuario).order_by('-data_saque')
    except Exception as e:
        print(f"ERRO CRÍTICO ao buscar histórico de saques: {e}")
        raise e # Levanta o erro para que o log do servidor o capture

    try:
        config = Config.objects.first()
        if not config:
            # Tratamento de erro já existente:
            messages.error(request, "Configurações da plataforma não encontradas. Por favor, contate o suporte.")
            return redirect('menu')

        # Configurações de saque
        SAQUE_MINIMO = config.saque_minimo
        TAXA_SAQUE = config.taxa_saque / 100 # Converte porcentagem para decimal
    
        # Configuração de fuso horário e horário de saque
        luanda_tz = pytz.timezone('Africa/Luanda')
        agora_luanda = datetime.now(luanda_tz)
    
        horario_inicio_saque = config.horario_saque_inicio
        horario_fim_saque = config.horario_saque_fim
        pode_sacar = horario_inicio_saque <= agora_luanda.time() <= horario_fim_saque
    
        mensagem_horario = f"Horário de saque permitido: {config.horario_saque_inicio.strftime('%H:%M')}h até {config.horario_saque_fim.strftime('%H:%M')}h (Horário de Angola)"
    
    except Exception as e:
        print(f"ERRO CRÍTICO ao buscar ou calcular Configurações/Horário: {e}")
        raise e # Levanta o erro para que o log do servidor o capture
        
    # Verifica se o usuário tem detalhes bancários cadastrados
    try:
        client_bank_details = ClientBankDetails.objects.get(usuario=usuario)
        tem_detalhes_bancarios = True
        nome_banco_cliente = client_bank_details.nome_banco
        iban_cliente = client_bank_details.iban
    except ClientBankDetails.DoesNotExist:
        tem_detalhes_bancarios = False
        nome_banco_cliente = None
        iban_cliente = None
    except Exception as e:
        print(f"ERRO CRÍTICO ao buscar ClientBankDetails: {e}")
        raise e # Levanta o erro para que o log do servidor o capture

    # --- DEBUG START ---
    print(f"Config OK: Saque Mínimo {SAQUE_MINIMO}, Taxa {TAXA_SAQUE * 100}%")
    print(f"Detalhes bancários cadastrados? {tem_detalhes_bancarios}")
    # --- DEBUG END ---

    if request.method == 'POST':
        # --- Processamento da Solicitação de Saque ---
        
        # 1. Validação de dados bancários
        if not tem_detalhes_bancarios:
            messages.error(request, "Você precisa cadastrar suas informações bancárias para sacar.")
            return redirect('saque')

        valor_saque_bruto_str = request.POST.get('amount')
        
        # 2. Validação de horário
        if not pode_sacar:
            messages.error(request, mensagem_horario)
            return redirect('saque')

        if not valor_saque_bruto_str:
            messages.error(request, 'O valor do saque é obrigatório.')
            return redirect('saque')
            
        try:
            # Converte a string do valor para Decimal
            valor_saque_bruto = Decimal(valor_saque_bruto_str)
        except (ValueError, TypeError):
            messages.error(request, 'Valor de saque inválido.')
            return redirect('saque')
            
        # 3. Validação do valor mínimo
        if valor_saque_bruto < SAQUE_MINIMO:
            messages.error(request, f'O saque mínimo é de {SAQUE_MINIMO:.2f} KZ.')
            return redirect('saque')
            
        # 4. Validação de saldo (o saldo disponível deve cobrir o valor bruto do saque)
        if valor_saque_bruto > usuario.saldo_disponivel:
            messages.error(request, f'Saldo insuficiente. Saldo disponível: {usuario.saldo_disponivel:.2f} KZ. Valor solicitado: {valor_saque_bruto:.2f} KZ.')
            return redirect('saque')
        
        # 5. Cálculo da taxa e valor líquido
        valor_taxa = valor_saque_bruto * TAXA_SAQUE
        valor_saque_liquido = valor_saque_bruto - valor_taxa

        try:
            with transaction.atomic():
                # Debita o valor bruto (saque + taxa) do saldo do usuário
                usuario.saldo_disponivel -= valor_saque_bruto
                
                # Cria a solicitação de saque
                Saque.objects.create(
                    usuario=usuario,
                    valor=valor_saque_bruto,        # Valor Bruto
                    valor_liquido=valor_saque_liquido, # Valor Líquido (a ser pago)
                    taxa=valor_taxa,
                    iban_cliente=iban_cliente,
                    nome_banco_cliente=nome_banco_cliente,
                    status='Pendente'
                )
                
                # Atualiza o total sacado com o valor líquido (o que o usuário efetivamente recebe)
                usuario.total_sacado += valor_saque_liquido
                usuario.save()
            
            messages.success(request, f'Solicitação de saque de {valor_saque_bruto:.2f} KZ enviada com sucesso! Uma taxa de {valor_taxa:.2f} KZ foi aplicada. Valor a receber: {valor_saque_liquido:.2f} KZ. Aguarde a aprovação.')
            return redirect('saque')
            
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao solicitar o saque: {e}')
            print(f"ERRO CRÍTICO ao salvar saque no banco de dados: {e}")
            return redirect('saque')

    # --- Exibição da Página de Saque (GET) ---
    context = {
        'usuario': usuario,
        'historico_saques': historico_saques,
        'SAQUE_MINIMO': SAQUE_MINIMO,
        'TAXA_SAQUE': TAXA_SAQUE * 100, # Envia a taxa em percentual para o template
        'mensagem_horario': mensagem_horario,
        'tem_detalhes_bancarios': tem_detalhes_bancarios,
    }
    
    # --- DEBUG START ---
    print("--- SAQUE_VIEW CONCLUÍDA SEM ERROS, RENDERIZANDO TEMPLATE ---")
    # --- DEBUG END ---

    return render(request, 'saque.html', context)


@login_required
def tarefa_view(request):
    usuario = request.user
    
    luanda_tz = pytz.timezone('Africa/Luanda')
    hoje_luanda = datetime.now(luanda_tz).date()
    
    # Verifica se o usuário tem um nível alugado ativo
    has_level = NivelAlugado.objects.filter(usuario=usuario, is_active=True).exists()
    
    # Pega o timestamp da última tarefa realizada
    last_task = Tarefa.objects.filter(usuario=usuario).order_by('-data_realizacao').first()
    
    # Verifica se a tarefa de hoje já foi realizada
    tarefa_realizada_hoje = Tarefa.objects.filter(
        usuario=usuario,
        data_realizacao__date=hoje_luanda
    ).exists()
    
    last_task_timestamp = None
    if last_task:
        # Pega a data e hora da última tarefa no fuso horário de Luanda
        last_task_luanda = last_task.data_realizacao.astimezone(luanda_tz)
        # Calcula o timestamp em milissegundos
        last_task_timestamp = int(last_task_luanda.timestamp() * 1000)

    context = {
        'last_task_timestamp': last_task_timestamp,
        'has_level': has_level,
        'tarefa_realizada_hoje': tarefa_realizada_hoje,
    }
    return render(request, 'tarefa.html', context)

@login_required
@require_POST
def realizar_tarefa(request):
    usuario = request.user
    
    niveis_alugados_ativos = NivelAlugado.objects.filter(usuario=usuario, is_active=True)

    if not niveis_alugados_ativos.exists():
        return JsonResponse({'status': 'error', 'message': 'Você não tem um nível alugado para realizar a tarefa.'}, status=403)

    # Verifica se a tarefa já foi realizada hoje no fuso horário de Luanda
    luanda_tz = pytz.timezone('Africa/Luanda')
    hoje_luanda = datetime.now(luanda_tz).date()
    
    tarefa_realizada_hoje = Tarefa.objects.filter(
        usuario=usuario,
        data_realizacao__date=hoje_luanda
    ).exists()

    if tarefa_realizada_hoje:
        return JsonResponse({'status': 'error', 'message': 'A tarefa diária já foi realizada. Volte amanhã.'}, status=403)
    
    try:
        with transaction.atomic():
            total_ganho_dia = Decimal('0.00')
            # Processa a tarefa para todos os níveis ativos
            for nivel_alugado in niveis_alugados_ativos:
                ganho_diario = nivel_alugado.nivel.ganho_diario
                
                # Adiciona o ganho ao saldo disponível para saque (saldo é saldo_total)
                usuario.saldo_disponivel += ganho_diario
                usuario.saldo += ganho_diario # Supondo que `saldo` é o saldo total
                total_ganho_dia += ganho_diario
                
            usuario.save()

            # Cria um único registro de tarefa para o dia
            Tarefa.objects.create(
                usuario=usuario,
                ganho=total_ganho_dia
            )
            
        return JsonResponse({'status': 'success', 'message': f'Tarefa realizada com sucesso! Você ganhou {total_ganho_dia:.2f} KZ.'})

    except Exception as e:
        print(f"Erro ao processar tarefa: {e}")
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro interno ao processar a tarefa: {e}'}, status=500)

@login_required
def nivel_view(request):
    niveis = Nivel.objects.all()
    context = {
        'niveis': niveis,
    }
    return render(request, 'nivel.html', context)

@login_required
@require_POST
def alugar_nivel(request):
    data = json.loads(request.body)
    nivel_id = data.get('nivel_id')
    usuario = request.user
    
    try:
        nivel_a_alugar = Nivel.objects.get(id=nivel_id)
    except Nivel.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Nível não encontrado.'}, status=404)

    if NivelAlugado.objects.filter(usuario=usuario, is_active=True).exists():
        return JsonResponse({'status': 'error', 'message': 'Você já tem um nível alugado ativo.'}, status=400)
    
    if usuario.saldo_disponivel < nivel_a_alugar.deposito_minimo:
        return JsonResponse({'status': 'error', 'message': 'Saldo insuficiente para alugar este nível.'}, status=400)
    
    try:
        with transaction.atomic():
            usuario.saldo_disponivel -= nivel_a_alugar.deposito_minimo
            
            NivelAlugado.objects.create(
                usuario=usuario,
                nivel=nivel_a_alugar,
                data_inicio=timezone.now(),
                data_expiracao=timezone.now() + timedelta(days=nivel_a_alugar.ciclo_dias),
                is_active=True
            )
            
            usuario.save()
        
        return JsonResponse({'status': 'success', 'message': f'Nível {nivel_a_alugar.nome_nivel} alugado com sucesso!'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro ao processar o aluguel: {e}'}, status=500)

@login_required
def equipa_view(request):
    usuario_logado = request.user
    
    # Busca os membros da equipe que se referem ao usuário logado
    membros_equipa = Usuario.objects.filter(inviter=usuario_logado)
    
    # Dicionário para armazenar a contagem de membros por nível
    niveis_contagem = defaultdict(int)
    
    lista_membros = []
    for membro in membros_equipa:
        # Tenta obter o nível alugado ativo do membro
        nivel_alugado_do_membro = NivelAlugado.objects.filter(usuario=membro, is_active=True).first()
        
        if nivel_alugado_do_membro:
            # Se tiver nível, adiciona na contagem do nível correspondente
            nivel_numero = nivel_alugado_do_membro.nivel.numero
            niveis_contagem[nivel_numero] += 1
            nivel_display = f"Nível {nivel_numero}"
        else:
            # Se não tiver nível ativo, trata como inativo
            nivel_display = "Nível Inativo"
            
        lista_membros.append({
            'nome': membro.username if membro.username else membro.phone_number,
            'numero': membro.phone_number,
            'nivel': nivel_alugado_do_membro.nivel if nivel_alugado_do_membro else None,
            'nivel_display': nivel_display
        })

    total_membros = len(lista_membros)
    link_convite = request.build_absolute_uri(f'/cadastro/?convite={usuario_logado.invitation_code}')
    
    context = {
        'link_convite': link_convite,
        'equipa_membros': lista_membros,
        'total_membros': total_membros,
        'niveis_contagem': dict(niveis_contagem) # Converte para dict para uso no template
    }
    
    return render(request, 'equipa.html', context)

@login_required
def perfil_view(request):
    usuario = request.user
    client_bank_details = None
    try:
        client_bank_details = ClientBankDetails.objects.get(usuario=usuario)
    except ClientBankDetails.DoesNotExist:
        pass

    context = {
        'usuario': usuario,
        'client_bank_details': client_bank_details,
    }
    return render(request, 'perfil.html', context)

@login_required
def editar_perfil_view(request):
    usuario = request.user
    
    if request.method == 'POST':
        user_form = UsuarioUpdateForm(request.POST, instance=usuario)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Informações do perfil atualizadas com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros nos campos do formulário.')
    else:
        user_form = UsuarioUpdateForm(instance=usuario)

    context = {
        'user_form': user_form,
    }
    return render(request, 'editar_perfil.html', context)

@login_required
def editar_senha_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sua senha foi atualizada com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
        
    context = {
        'form': form
    }
    return render(request, 'editar_senha.html', context)

@login_required
def editar_coordenadas_bancarias(request):
    usuario = request.user
    try:
        client_bank_details = ClientBankDetails.objects.get(usuario=usuario)
    except ClientBankDetails.DoesNotExist:
        client_bank_details = None

    if request.method == 'POST':
        bank_form = ClientBankDetailsForm(request.POST, instance=client_bank_details)
        if bank_form.is_valid():
            coordenadas = bank_form.save(commit=False)
            coordenadas.usuario = usuario
            coordenadas.save()
            messages.success(request, 'Coordenadas bancárias atualizadas com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário bancário.')
    else:
        bank_form = ClientBankDetailsForm(instance=client_bank_details)
    
    context = {
        'bank_form': bank_form
    }
    return render(request, 'editar_coordenadas_bancarias.html', context)

@login_required
def premios_subsidios_view(request):
    return render(request, 'roleta.html')

@login_required
def sobre_view(request):
    sobre_texto_obj = Sobre.objects.first()
    context = {
        'sobre_texto': sobre_texto_obj.conteudo if sobre_texto_obj else "Conteúdo da página 'Sobre' não disponível.",
    }
    return render(request, 'nos.html', context)

@login_required
def renda_view(request):
    usuario = request.user
    
    niveis_alugados = NivelAlugado.objects.filter(usuario=usuario, is_active=True).order_by('-data_inicio')
    if niveis_alugados.exists():
        nivel_cliente = niveis_alugados.first().nivel.nome_nivel
    else:
        nivel_cliente = "Nível Básico (Sem nível alugado)"

    depositos_aprovados_sum = Deposito.objects.filter(usuario=usuario, status='Aprovado').aggregate(models.Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    context = {
        'nivel_cliente': nivel_cliente,
        'depositos_aprovados': depositos_aprovados_sum,
        'saldo_disponivel': usuario.saldo_disponivel,
        'saldo_subsidio': usuario.saldo_subsidio,
        'total_sacado': usuario.total_sacado,
    }
    return render(request, 'renda.html', context)

# FUNÇÕES DA ROLETA (MODIFICADAS)

@login_required
def get_roleta_data(request):
    """
    Retorna os dados dos prêmios da roleta e o número de giros restantes do usuário.
    """
    premios = PremioSubsidio.objects.all().order_by('valor')
    premios_data = []
    for premio in premios:
        premios_data.append({
            'id': premio.id,
            'valor': float(premio.valor),
            'chance': float(premio.chance),
            'descricao': premio.descricao # Adicionado para melhor visualização, se necessário
        })

    usuario = request.user
    
    return JsonResponse({
        'status': 'success',
        'premios': premios_data,
        'spins_remaining': usuario.spins_remaining,
    })

@login_required
@require_POST
def girar_roleta(request):
    """
    Processa o giro da roleta, escolhe o prêmio vencedor e atualiza o saldo do usuário.
    """
    usuario = request.user
    
    # 1. Verificar pré-requisitos do usuário
    if not usuario.can_spin_roulette or usuario.spins_remaining <= 0:
        return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para girar a roleta ou não tem giros restantes.'}, status=403)
        
    has_approved_deposit = Deposito.objects.filter(usuario=usuario, status='Aprovado').exists()
    if not has_approved_deposit:
        return JsonResponse({'status': 'error', 'message': 'Você precisa ter um depósito aprovado para girar a roleta.'}, status=403)
    
    has_active_level = NivelAlugado.objects.filter(usuario=usuario, is_active=True).exists()
    if not has_active_level:
        return JsonResponse({'status': 'error', 'message': 'Você precisa ter um nível alugado ativo para girar a roleta.'}, status=403)
    
    try:
        with transaction.atomic():
            premios = list(PremioSubsidio.objects.all())
            if not premios:
                return JsonResponse({'status': 'error', 'message': 'Nenhum prêmio configurado.'}, status=500)

            total_chance = sum(p.chance for p in premios)
            if total_chance <= 0:
                premio_ganho = random.choice(premios)
            else:
                r = random.uniform(0, float(total_chance))
                acumulated_chance = 0.0
                premio_ganho = None
                
                for premio in premios:
                    acumulated_chance += float(premio.chance)
                    if r <= acumulated_chance:
                        premio_ganho = premio
                        break
                
                if premio_ganho is None:
                    premio_ganho = random.choice(premios)

            # Concede o prêmio ao usuário
            usuario.saldo_disponivel += premio_ganho.valor
            usuario.saldo_subsidio += premio_ganho.valor
            usuario.spins_remaining -= 1
            usuario.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Parabéns! Você ganhou {premio_ganho.valor:.2f} KZ!',
                'winning_id': premio_ganho.id,
                'spins_remaining': usuario.spins_remaining,
            })
    except Exception as e:
        print(f"Erro ao girar a roleta: {e}")
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro interno: {e}'}, status=500)
