from django.contrib import admin
from mailings.models import Recipient, Message, Mailing, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'comment')
    search_fields = ('email', 'full_name')
    list_display_links = ('id', 'email')
    ordering = ('full_name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject')
    search_fields = ('subject', 'body')
    list_display_links = ('id', 'subject')
    ordering = ('-id',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'message')
    list_filter = ('status', 'start_time')
    search_fields = ('message__subject',)
    list_display_links = ('id',)
    ordering = ('-start_time',)
    readonly_fields = ('status',)
    filter_horizontal = ('recipients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_time', 'status', 'mailing')
    list_filter = ('status', 'attempt_time')
    search_fields = ('mailing__message__subject', 'server_response')
    list_display_links = ('id',)
    ordering = ('-attempt_time',)
    readonly_fields = ('attempt_time',)
