from django import forms
from mailings.models import Recipient, Message, Mailing


class RecipientForm(forms.ModelForm):
    """Форма для получателя рассылки"""

    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий...',
            }),
        }


class MessageForm(forms.ModelForm):
    """Форма для сообщения"""

    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема письма',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Текст письма...',
            }),
        }


class MailingForm(forms.ModelForm):
    """Форма для рассылки"""

    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'message': forms.Select(attrs={
                'class': 'form-select',
            }),
            'recipients': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 10,
            }),
        }

    def clean(self):
        """Валидация дат"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        from django.utils import timezone

        if start_time and start_time < timezone.now():
            self.add_error('start_time', 'Дата начала не может быть в прошлом.')

        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'Дата окончания должна быть позже даты начала.')

        return cleaned_data