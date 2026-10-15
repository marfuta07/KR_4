from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.utils import timezone
from mailings.models import Recipient, Message, Mailing, MailingAttempt
from mailings.forms import RecipientForm, MessageForm, MailingForm
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from mailings.services import send_mailing
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

# ========== Миксины для фильтрации по владельцу ==========

class OwnerQuerysetMixin:
    """
    Миксин для фильтрации объектов по владельцу.
    Обычный пользователь видит только свои объекты.
    Менеджер видит все объекты.
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        # Менеджер видит всё
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return queryset

        # Обычный пользователь — только свои
        return queryset.filter(owner=self.request.user)


class OwnerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки прав на редактирование/удаление.
    Обычный пользователь может редактировать только свои объекты.
    """

    def test_func(self):
        obj = self.get_object()

        # Владелец может редактировать
        if obj.owner == self.request.user:
            return True

        return False

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied('Вы не являетесь владельцем этого объекта!')
        return super().handle_no_permission()

# ========== CRUD для Recipient ==========

class RecipientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    """Список получателей (только свои, для менеджера — все)"""
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'
    login_url = reverse_lazy('users:login')


class RecipientDetailView(DetailView):
    """Детали получателя"""
    model = Recipient
    template_name = 'mailings/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        form.instance.owner = self.request.user  # ← автозаполнение
        messages.success(self.request, 'Получатель успешно создан! ✅')
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование получателя (только владелец)"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель обновлён! ✅')
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Удаление получателя (только владелец)"""
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель удалён! ✅')
        return super().form_valid(form)


# ========== CRUD для Message ==========

class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    """Список сообщений (только свои, для менеджера — все)"""
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'
    login_url = reverse_lazy('users:login')


class MessageDetailView(DetailView):
    """Детали сообщения"""
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        form.instance.owner = self.request.user  # ← автозаполнение
        messages.success(self.request, 'Сообщение успешно создано! ✅')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование сообщения (только владелец)"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено! ✅')
        return super().form_valid(form)

class MessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Удаление сообщения (только владелец)"""
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение удалено! ✅')
        return super().form_valid(form)


# ========== CRUD для Mailing ==========

class MailingListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    """Список рассылок (только свои, для менеджера — все)"""
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'
    login_url = reverse_lazy('users:login')

class MailingDetailView(DetailView):
    """Детали рассылки (с обновлением статуса)"""
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        """Обновляем статус при просмотре"""
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        form.instance.owner = self.request.user  # ← автозаполнение
        messages.success(self.request, 'Рассылка успешно создана! ✅')
        return super().form_valid(form)



class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование рассылки (только владелец)"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена! ✅')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Удаление рассылки (только владелец)"""
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка удалена! ✅')
        return super().form_valid(form)


# ========== MailingAttempt (только просмотр) ==========

class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список попыток рассылок (только свои, для менеджера — все)"""
    model = MailingAttempt
    template_name = 'mailings/mailingattempt_list.html'
    context_object_name = 'attempts'
    login_url = reverse_lazy('users:login')

    def get_queryset(self):
        """Фильтрация по owner через mailing__owner"""
        queryset = MailingAttempt.objects.all()

        # Менеджер видит всё
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return queryset

        # Обычный пользователь — только свои (через mailing.owner)
        return queryset.filter(mailing__owner=self.request.user)

class MailingAttemptDetailView(DetailView):
    """Детали попытки рассылки"""
    model = MailingAttempt
    template_name = 'mailings/mailingattempt_detail.html'
    context_object_name = 'attempt'

# ========== Главная страница ==========

class HomeView(ListView):
    """Главная страница со статистикой"""
    model = Mailing
    template_name = 'mailings/home.html'
    context_object_name = 'mailings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user = self.request.user

        # Если пользователь не авторизован — показываем общую статистику
        if not user.is_authenticated:
            is_manager = False
            mailings = Mailing.objects.all()
            attempts = MailingAttempt.objects.all()
            recipients = Recipient.objects.all()
        else:
            # Менеджер видит общую статистику
            is_manager = user.groups.filter(name='Менеджеры').exists()

            if is_manager:
                mailings = Mailing.objects.all()
                attempts = MailingAttempt.objects.all()
                recipients = Recipient.objects.all()
            else:
                mailings = Mailing.objects.filter(owner=user)
                attempts = MailingAttempt.objects.filter(mailing__owner=user)
                recipients = Recipient.objects.filter(owner=user)

        context['total_mailings'] = mailings.count()
        context['active_mailings'] = mailings.filter(
            start_time__lte=now,
            end_time__gte=now,
            status=Mailing.STATUS_STARTED,
            is_active=True,
        ).count()
        context['unique_recipients'] = recipients.count()

        context['successful_attempts'] = attempts.filter(
            status=MailingAttempt.STATUS_SUCCESS
        ).count()
        context['failed_attempts'] = attempts.filter(
            status=MailingAttempt.STATUS_FAILED
        ).count()
        context['total_attempts'] = attempts.count()

        context['is_manager'] = is_manager

        return context

class MailingSendView(View):
    """Запуск рассылки вручную"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        result = send_mailing(mailing.pk)

        if result['error']:
            messages.error(request, f'❌ {result["error"]}')
        else:
            messages.success(
                request,
                f'✅ Рассылка запущена! Успешно: {result["success"]}, Неуспешно: {result["failed"]}'
            )

        return redirect('mailings:mailing_detail', pk=pk)

class MailingToggleActiveView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Отключение/включение рассылки (только для менеджеров)"""
    login_url = reverse_lazy('users:login')

    def test_func(self):
        """Только менеджеры могут отключать рассылки"""
        return self.request.user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied('Доступ только для менеджеров!')
        return super().handle_no_permission()

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Переключаем is_active
        mailing.is_active = not mailing.is_active
        mailing.save()

        action = 'включена' if mailing.is_active else 'отключена'
        messages.success(request, f'✅ Рассылка #{mailing.pk} {action}!')
        return redirect('mailings:mailing_detail', pk=pk)