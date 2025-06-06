from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from apps.usuarios.models import User
from apps.administracao.forms.usuarios_forms import UserRegistrationForm, UserUpdateForm
from apps.usuarios.authentication import EmailAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # Campo username recebe o email
        password = request.POST.get('password')
        
        # Autenticação utilizando nosso backend personalizado
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('administracao:home')
        else:
            messages.error(request, 'Credenciais inválidas')
    
    return render(request, 'administracao/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('administracao:login')

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'administracao/usuarios/listarUsuarios.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro de pesquisa
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(identification_number__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        
        # Filtro por tipo de usuário
        user_type = self.request.GET.get('user_type', '')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Filtro por status
        status = self.request.GET.get('status', '')
        if status == 'ativo':
            queryset = queryset.filter(is_active=True)
        elif status == 'inativo':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar formulário e filtros no contexto
        context['form'] = UserRegistrationForm()
        context['search_query'] = self.request.GET.get('search', '')
        context['user_type_selected'] = self.request.GET.get('user_type', '')
        context['status_selected'] = self.request.GET.get('status', '')
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário {user.get_full_name_display()} cadastrado com sucesso!')
            return redirect(user.get_absolute_url())
        
        # Se o formulário não for válido, retornar para a lista com erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'administracao/usuarios/detalhes.html'
    context_object_name = 'user_detail'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o formulário no contexto
        context['form'] = UserUpdateForm(instance=self.object)
        return context

class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    success_url = reverse_lazy('administracao:usuarios_lista')
    success_message = "Usuário removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'administracao/usuarios/detalhes.html'
    
    def get_success_url(self):
        return reverse_lazy('administracao:usuario_detalhe', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar usuário. Verifique os dados informados.')
        return self.render_to_response(self.get_context_data(form=form))

class ChangePasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Senha atual incorreta.')
            return redirect(reverse_lazy('administracao:usuario_detalhe', kwargs={'pk': request.user.pk}))
            
        if new_password != confirm_password:
            messages.error(request, 'As novas senhas não coincidem.')
            return redirect(reverse_lazy('administracao:usuario_detalhe', kwargs={'pk': request.user.pk}))
            
        if len(new_password) < 8:
            messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
            return redirect(reverse_lazy('administracao:usuario_detalhe', kwargs={'pk': request.user.pk}))
            
        # Verificar se a senha contém letras e números
        if not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
            messages.error(request, 'A senha deve conter letras e números.')
            return redirect(reverse_lazy('administracao:usuario_detalhe', kwargs={'pk': request.user.pk}))
        
        try:
            request.user.set_password(new_password)
            request.user.save()
            # Atualiza a sessão para manter o usuário logado
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao alterar a senha. Tente novamente.')
            
        return redirect(reverse_lazy('administracao:usuario_detalhe', kwargs={'pk': request.user.pk}))