from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.mail import send_mail
from django.conf import settings

from users.forms import UserRegisterForm, UserLoginForm


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
