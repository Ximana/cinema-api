# apps/usuarios/api/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.usuarios.serializers import (
    UsuarioSerializer, 
    UsuarioRegistroSerializer,
    UsuarioLoginSerializer,
    UsuarioPublicoSerializer
)

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada que permite apenas ao próprio usuário 
    ou administradores acessarem os dados
    """
    def has_object_permission(self, request, view, obj):
        # Administradores podem acessar qualquer objeto
        if request.user and request.user.is_admin_user():
            return True
        
        # Usuários podem acessar apenas seus próprios dados
        return obj == request.user


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de usuários"""
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        """Permissões personalizadas para diferentes ações"""
        if self.action == 'list':
            # Apenas administradores podem listar todos os usuários
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        elif self.action == 'create':
            # Apenas administradores podem criar usuários via este endpoint
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Usuário pode ver/editar seus próprios dados ou admin pode ver/editar qualquer um
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        elif self.action == 'destroy':
            # Apenas administradores podem excluir usuários
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filtra o queryset baseado no tipo de usuário"""
        user = self.request.user
        
        if user.is_admin_user():
            return User.objects.all()
        else:
            # Usuários comuns só podem ver seus próprios dados
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def meu_perfil(self, request):
        """Endpoint para o usuário ver seu próprio perfil"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def atualizar_perfil(self, request):
        """Endpoint para o usuário atualizar seu próprio perfil"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RegistroUsuarioView(generics.CreateAPIView):
    """API View para registro de novos usuários"""
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Criar token para o usuário recém-registrado
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Usuário registrado com sucesso',
            'token': token.key,
            'user': {
                'id': user.pk,
                'email': user.email,
                'full_name': user.full_name,
                'identification_number': user.identification_number,
                'user_type': user.user_type
            }
        }, status=status.HTTP_201_CREATED)


class LoginUsuarioView(ObtainAuthToken):
    """API View para login de usuários"""
    serializer_class = UsuarioLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Login realizado com sucesso',
            'token': token.key,
            'user': {
                'id': user.pk,
                'email': user.email,
                'full_name': user.full_name,
                'identification_number': user.identification_number,
                'user_type': user.user_type,
                'is_admin': user.is_admin_user()
            }
        })


class LogoutUsuarioView(APIView):
    """API View para logout de usuários"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Deletar o token do usuário para fazer logout
            request.user.auth_token.delete()
            return Response(
                {'message': 'Logout realizado com sucesso.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao realizar logout.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeuPerfilView(generics.RetrieveUpdateAPIView):
    """API View para visualizar e atualizar o próprio perfil"""
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retornar o usuário autenticado"""
        return self.request.user


class UsuarioPublicoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualização pública de usuários (dados limitados)"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UsuarioPublicoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Permitir busca por nome, email ou número de identificação"""
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | 
                Q(email__icontains=search) |
                Q(identification_number__icontains=search)
            )
        
        return queryset.order_by('full_name')

