import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def _send(text):
    """Повертає True, якщо Telegram прийняв повідомлення."""
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    data = urllib.parse.urlencode({'chat_id': settings.TELEGRAM_CHAT_ID, 'text': text}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={'User-Agent': 'mizhnami-app/1.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode('utf-8', errors='replace')
        except Exception:
            body = ''
        logger.error('Помилка Telegram API HTTP %s: %s', exc.code, body)
        return False
    except Exception as exc:
        logger.exception('Не вдалося надіслати сповіщення в Telegram: %s', exc)
        return False


def notify_booking(name, contact, topic=''):
    """Надсилає заявку в Telegram синхронно (у serverless фонові потоки ненадійні).

    Повертає True при успіху. Без токена у режимі DEBUG заявка лише логується.
    """
    text = (
        '🌿 нова заявка\n'
        f'ім’я: {name}\n'
        f'контакт: {contact}\n'
        f'запит: {topic or "—"}'
    )
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        logger.error(
            'Telegram не налаштований у змінних оточення (TELEGRAM_BOT_TOKEN=%s, TELEGRAM_CHAT_ID=%s)',
            bool(settings.TELEGRAM_BOT_TOKEN),
            bool(settings.TELEGRAM_CHAT_ID),
        )
        if settings.DEBUG:
            logger.warning('Telegram не налаштований, заявка лише в логах:\n%s', text)
            return True
        return False
    return _send(text)
