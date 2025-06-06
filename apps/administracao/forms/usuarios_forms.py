# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'identification_number', 
                 'date_of_birth', 'user_type', 'password1', 'password2')
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'identification_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            if field_name == 'user_type':
                field.widget.attrs['class'] = 'form-select'
            elif field_name == 'date_of_birth':
                field.widget.attrs.update({'type': 'date', 'class': 'form-control'})
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Configurar campos obrigatórios conforme o modelo
        self.fields['full_name'].required = True
        self.fields['email'].required = True
        self.fields['identification_number'].required = True
        
        # Adicionar labels e help_text
        self.fields['full_name'].label = 'Nome Completo'
        self.fields['email'].label = 'E-mail'
        self.fields['identification_number'].label = 'Número de Identificação'
        self.fields['identification_number'].help_text = 'BI, NIF'
        self.fields['date_of_birth'].label = 'Data de Nascimento'
        self.fields['user_type'].label = 'Tipo de Usuário'
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email
    
    def clean_identification_number(self):
        identification_number = self.cleaned_data.get('identification_number')
        if identification_number and User.objects.filter(identification_number=identification_number).exists():
            raise forms.ValidationError('Este número de identificação já está em uso.')
        return identification_number

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'identification_number', 'date_of_birth', 'user_type']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'identification_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar campos obrigatórios
        self.fields['full_name'].required = True
        self.fields['email'].required = True
        self.fields['identification_number'].required = True
        
        # Adicionar labels
        self.fields['full_name'].label = 'Nome Completo'
        self.fields['email'].label = 'E-mail'
        self.fields['identification_number'].label = 'Número de Identificação'
        self.fields['identification_number'].help_text = 'BI, NIF, etc.'
        self.fields['date_of_birth'].label = 'Data de Nascimento'
        self.fields['user_type'].label = 'Tipo de Usuário'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email
    
    def clean_identification_number(self):
        identification_number = self.cleaned_data.get('identification_number')
        if identification_number and User.objects.filter(identification_number=identification_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este número de identificação já está em uso.')
        return identification_number