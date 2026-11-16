import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Тестування відправки повідомлень у Telegram за налаштуваннями з .env'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('\n--- Перевірка інтеграції з Telegram ---'))

        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

        self.stdout.write(f'TELEGRAM_BOT_TOKEN: {token[:10]}... (довжина: {len(token)})' if token else self.style.ERROR('TELEGRAM_BOT_TOKEN не задано!'))
        self.stdout.write(f'TELEGRAM_CHAT_ID: {chat_id}' if chat_id else self.style.ERROR('TELEGRAM_CHAT_ID не задано!'))

        if not token:
            self.stdout.write(self.style.ERROR('\n❌ Задайте TELEGRAM_BOT_TOKEN у .env'))
            return

        # 1. Перевірка getMe
        self.stdout.write('\n1. Перевірка бота (getMe)...')
        try:
            req = urllib.request.Request(f'https://api.telegram.org/bot{token}/getMe')
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                bot_info = data.get('result', {})
                self.stdout.write(self.style.SUCCESS(
                    f'   ✓ Бот активний: {bot_info.get("first_name")} (@{bot_info.get("username")})'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Помилка підключення до бота: {e}'))
            return

        if not chat_id:
            self.stdout.write(self.style.ERROR('\n❌ TELEGRAM_CHAT_ID відсутній у .env'))
            return

        # 2. Спроба відправки повідомлення
        self.stdout.write(f'\n2. Спроба відправити тестове повідомлення у chat_id={chat_id}...')
        text = '🌿 Тестове повідомлення з сайту «mizhnami — простір опори».\nЯкщо ви бачите це — форма запису налаштована успішно!'
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode()

        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=payload), timeout=5) as resp:
                if resp.status == 200:
                    self.stdout.write(self.style.SUCCESS('\n🎉 УСПІХ! Тестове повідомлення надіслано в Telegram.'))
                    return
        except urllib.error.HTTPError as exc:
            body = exc.read().decode('utf-8', errors='replace')
            self.stdout.write(self.style.ERROR(f'   ❌ Помилка Telegram API (HTTP {exc.code}): {body}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Помилка мережі: {e}'))

        # 3. Допомога у знаходженні chat_id через getUpdates
        self.stdout.write('\n3. Пошук доступних чатів через getUpdates...')
        try:
            req = urllib.request.Request(f'https://api.telegram.org/bot{token}/getUpdates')
            with urllib.request.urlopen(req, timeout=5) as resp:
                updates = json.loads(resp.read().decode()).get('result', [])
                if not updates:
                    self.stdout.write(self.style.WARNING(
                        '   ⚠️ Останніх повідомлень у боті не знайдено.\n'
                        '   Щоб активувати чат:\n'
                        '   • Для приватного чату: відкрийте бота в Telegram та натисніть Start (/start).\n'
                        '   • Для групи: додайте бота в групу та напишіть туди будь-яке повідомлення.'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS('   Знайдено повідомлення у боті:'))
                    seen_chats = set()
                    for u in updates:
                        msg = u.get('message') or u.get('channel_post') or {}
                        chat = msg.get('chat', {})
                        cid = chat.get('id')
                        if cid and cid not in seen_chats:
                            seen_chats.add(cid)
                            cname = chat.get('title') or chat.get('username') or chat.get('first_name')
                            ctype = chat.get('type')
                            self.stdout.write(self.style.NOTICE(f'   → chat_id: {cid} (тип: {ctype}, назва/ім’я: {cname})'))
                    self.stdout.write(self.style.SUCCESS(
                        '\nСкопіюйте потрібний chat_id вище і запишіть його у .env: TELEGRAM_CHAT_ID=...'
                    ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   Не вдалося отримати getUpdates: {e}'))
