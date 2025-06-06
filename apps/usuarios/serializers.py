# apps/usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de usuário"""
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'identification_number',
            'date_of_birth', 'user_type', 'is_active'
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Criar um novo usuário com senha criptografada"""
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Atualizar um usuário existente"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuários"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = (
            'email', 'password', 'password_confirm', 
            'full_name', 'identification_number', 'date_of_birth', 'user_type'
        )
        
    def validate_email(self, value):
        """Validar se o email já não está em uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Este email já está em uso.'))
        return value
        
    def validate_identification_number(self, value):
        """Validar se o número de identificação já não está em uso"""
        if User.objects.filter(identification_number=value).exists():
            raise serializers.ValidationError(_('Este número de identificação já está em uso.'))
        return value
        
    def validate(self, data):
        """Validar se as senhas correspondem"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _('As senhas não correspondem.')
            })
        return data
    
    def create(self, validated_data):
        """Criar um novo usuário com senha criptografada"""
        # Remover o campo password_confirm
        validated_data.pop('password_confirm')
        
        # Por padrão, novos usuários são do tipo 'regular'
        if 'user_type' not in validated_data:
            validated_data['user_type'] = 'regular'
        
        # Definir username como email se não fornecido
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email']
        
        # Criar o usuário
        return User.objects.create_user(**validated_data)


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para autenticação de usuários"""
    email = serializers.EmailField(
        help_text=_('Email do usuário')
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, data):
        """Validar e autenticar o usuário"""
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # Usar o authenticate que usará nosso backend personalizado
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Passamos email como username
                password=password
            )
            
            if not user:
                msg = _('Não foi possível autenticar com as credenciais fornecidas')
                raise serializers.ValidationError(msg, code='authentication')
                
            if not user.is_active:
                msg = _('Conta de usuário desativada')
                raise serializers.ValidationError(msg, code='authentication')
                
        else:
            msg = _('Deve incluir "email" e "password"')
            raise serializers.ValidationError(msg, code='authentication')
            
        data['user'] = user
        return data


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """Serializer para dados públicos do usuário (sem informações sensíveis)"""
    
    class Meta:
        model = User
        fields = ('id', 'full_name', 'email')
