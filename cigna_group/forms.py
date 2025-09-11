from django import forms
from .models import Deposito, Saque, Usuario, ClientBankDetails

class DepositoForm(forms.ModelForm):
    class Meta:
        model = Deposito
        fields = ['valor', 'comprovativo_imagem'] 
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),
            'comprovativo_imagem': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SaqueForm(forms.ModelForm):
    class Meta:
        model = Saque
        fields = ['valor']
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),
        }

# Formulário para atualização do Usuário
class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de Usuário'}),
        }

# Formulário para Detalhes Bancários do Cliente
class ClientBankDetailsForm(forms.ModelForm):
    class Meta:
        model = ClientBankDetails
        fields = ['nome_banco', 'nome_titular_conta', 'iban']
        widgets = {
            'nome_banco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Banco'}),
            'nome_titular_conta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Titular da Conta'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IBAN'}),
        }
        