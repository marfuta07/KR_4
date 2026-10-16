from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.mail import send_mail
from django.conf import settings

from users.forms import UserRegisterForm, UserLoginForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

class RegisterView(CreateView):
    """Регистрация пользователя"""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('mailings:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        # Автоматический вход после регистрации
        login(self.request, user)

        # Приветственное письмо
        send_mail(
            subject='Добро пожаловать в сервис рассылок!',
            message=f'Здравствуйте, {user.username}!\n\n'
                    f'Спасибо за регистрацию в нашем сервисе.\n'
                    f'Теперь вы можете управлять рассылками.\n\n'
                    f'С уважением,\n'
                    f'Команда сервиса рассылок',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать! ✅')
        return response


class UserLoginView(LoginView):
    """Вход пользователя"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('mailings:home')

    def form_valid(self, form):
        messages.success(self.request, 'Вы успешно вошли в систему! ✅')
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """Выход пользователя"""
    next_page = reverse_lazy('mailings:home')

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список пользователей (только для менеджеров)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    login_url = reverse_lazy('users:login')

    def test_func(self):
        """Только менеджеры могут видеть список пользователей"""
        return self.request.user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied('Доступ только для менеджеров!')
        return super().handle_no_permission()


class UserToggleActiveView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Блокировка/разблокировка пользователя (только для менеджеров)"""
    login_url = reverse_lazy('users:login')

    def test_func(self):
        """Только менеджеры могут блокировать"""
        return self.request.user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied('Доступ только для менеджеров!')
        return super().handle_no_permission()

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # Нельзя блокировать самого себя
        if user == request.user:
            messages.error(request, '❌ Нельзя заблокировать самого себя!')
            return redirect('users:user_list')

        # Переключаем is_active
        user.is_active = not user.is_active
        user.save()

        action = 'заблокирован' if not user.is_active else 'разблокирован'
        messages.success(request, f'✅ Пользователь {user.username} {action}!')
        return redirect('users:user_list')