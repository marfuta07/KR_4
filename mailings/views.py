from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.utils import timezone
from mailings.models import Recipient, Message, Mailing, MailingAttempt
from mailings.forms import RecipientForm, MessageForm, MailingForm


# ========== CRUD для Recipient ==========

class RecipientListView(ListView):
    """Список получателей"""
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'


class RecipientDetailView(DetailView):
    """Детали получателя"""
    model = Recipient
    template_name = 'mailings/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(CreateView):
    """Создание получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно создан! ✅')
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    """Редактирование получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель обновлён! ✅')
        return super().form_valid(form)


class RecipientDeleteView(DeleteView):
    """Удаление получателя"""
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель удалён! ✅')
        return super().form_valid(form)


# ========== CRUD для Message ==========

class MessageListView(ListView):
    """Список сообщений"""
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'


class MessageDetailView(DetailView):
    """Детали сообщения"""
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(CreateView):
    """Создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно создано! ✅')
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    """Редактирование сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено! ✅')
        return super().form_valid(form)


class MessageDeleteView(DeleteView):
    """Удаление сообщения"""
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение удалено! ✅')
        return super().form_valid(form)


# ========== CRUD для Mailing ==========

class MailingListView(ListView):
    """Список рассылок"""
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'


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


class MailingCreateView(CreateView):
    """Создание рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно создана! ✅')
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    """Редактирование рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена! ✅')
        return super().form_valid(form)


class MailingDeleteView(DeleteView):
    """Удаление рассылки"""
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка удалена! ✅')
        return super().form_valid(form)


# ========== MailingAttempt (только просмотр) ==========

class MailingAttemptListView(ListView):
    """Список попыток рассылок"""
    model = MailingAttempt
    template_name = 'mailings/mailingattempt_list.html'
    context_object_name = 'attempts'


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

        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status=Mailing.STATUS_STARTED
        ).count()
        context['unique_recipients'] = Recipient.objects.count()

        return context
    