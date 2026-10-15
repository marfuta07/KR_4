from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from mailings.models import Mailing, MailingAttempt


def send_mailing(mailing_id):
    """
    Отправляет рассылку по её ID.

    :param mailing_id: ID рассылки
    :return: dict со статистикой: {'success': N, 'failed': M, 'error': 'текст'}
    """
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
    except Mailing.DoesNotExist:
        return {'success': 0, 'failed': 0, 'error': 'Рассылка не найдена'}

    # Обновляем статус
    mailing.update_status()

    # Проверяем, активна ли рассылка
    if not mailing.is_active:
        return {
            'success': 0,
            'failed': 0,
            'error': 'Рассылка отключена менеджером. Отправка невозможна.'
        }

    # Проверяем, разрешена ли отправка
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        return {
            'success': 0,
            'failed': 0,
            'error': f'Отправка невозможна. Рассылка доступна с '
                     f'{mailing.start_time:%d.%m.%Y %H:%M} до {mailing.end_time:%d.%m.%Y %H:%M}'
        }

    # Получаем получателей
    recipients = mailing.recipients.all()
    if not recipients.exists():
        return {'success': 0, 'failed': 0, 'error': 'У рассылки нет получателей'}

    success_count = 0
    failed_count = 0
    attempts_to_create = []   # ← batch-список

    # Отправляем каждому получателю
    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            attempts_to_create.append(MailingAttempt(
                status=MailingAttempt.STATUS_SUCCESS,
                server_response='OK',
                mailing=mailing,
            ))
            success_count += 1
        except Exception as e:
            attempts_to_create.append(MailingAttempt(
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e),
                mailing=mailing,
            ))
            failed_count += 1

    # ← BATCH-создание одним запросом
    MailingAttempt.objects.bulk_create(attempts_to_create)

    return {
        'success': success_count,
        'failed': failed_count,
        'error': None,
    }