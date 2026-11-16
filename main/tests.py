from unittest import mock

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from . import content


class BookingTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse('main:booking')

    def test_index_ok(self):
        self.assertEqual(self.client.get(reverse('main:index')).status_code, 200)

    @mock.patch('main.views.notify_booking', return_value=True)
    def test_valid_booking_sent(self, notify):
        r = self.client.post(self.url, {'name': 'Анна', 'contact': '@anna', 'topic': 'тривога'})
        self.assertEqual(r.status_code, 200)
        notify.assert_called_once_with('Анна', '@anna', 'тривога')

    @mock.patch('main.views.notify_booking', return_value=False)
    def test_delivery_failure_reported(self, notify):
        r = self.client.post(self.url, {'name': 'Анна', 'contact': '@anna'})
        self.assertEqual(r.status_code, 502)

    @mock.patch('main.views.notify_booking')
    def test_missing_fields_rejected(self, notify):
        r = self.client.post(self.url, {'name': '', 'contact': ''})
        self.assertEqual(r.status_code, 400)
        notify.assert_not_called()

    @mock.patch('main.views.notify_booking')
    def test_honeypot_not_sent(self, notify):
        r = self.client.post(self.url, {'name': 'Бот', 'contact': 'x', 'website': 'http://spam'})
        self.assertEqual(r.status_code, 200)
        notify.assert_not_called()

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    @override_settings(DEBUG=False, TELEGRAM_BOT_TOKEN='', TELEGRAM_CHAT_ID='')
    def test_no_telegram_in_production_fails(self):
        r = self.client.post(self.url, {'name': 'Анна', 'contact': '@anna'})
        self.assertEqual(r.status_code, 502)


class TelegramNotificationTests(SimpleTestCase):
    @override_settings(TELEGRAM_BOT_TOKEN='fake-token', TELEGRAM_CHAT_ID='-100123')
    @mock.patch('urllib.request.urlopen')
    def test_notify_booking_success(self, mock_urlopen):
        from .notifications import notify_booking
        mock_resp = mock.MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = notify_booking('Олена', '@olena', 'тривога')
        self.assertTrue(result)
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        self.assertIn('botfake-token/sendMessage', req.full_url)
        self.assertIn(b'chat_id=-100123', req.data)
        self.assertIn('%D0%9E%D0%BB%D0%B5%D0%BD%D0%B0'.encode(), req.data)  # Олена urlencoded

    @override_settings(TELEGRAM_BOT_TOKEN='fake-token', TELEGRAM_CHAT_ID='-100123')
    @mock.patch('urllib.request.urlopen')
    def test_notify_booking_http_error_handled(self, mock_urlopen):
        import io
        import urllib.error
        from .notifications import notify_booking

        err = urllib.error.HTTPError(
            'https://api.telegram.org', 400, 'Bad Request',
            {}, io.BytesIO(b'{"ok":false,"description":"Bad Request: chat not found"}')
        )
        mock_urlopen.side_effect = err

        result = notify_booking('Олена', '@olena', 'тест')
        self.assertFalse(result)

    @override_settings(TELEGRAM_BOT_TOKEN='fake-token', TELEGRAM_CHAT_ID='-100123')
    @mock.patch('urllib.request.urlopen')
    def test_notify_booking_timeout_handled(self, mock_urlopen):
        import urllib.error
        from .notifications import notify_booking

        mock_urlopen.side_effect = urllib.error.URLError('timed out')
        result = notify_booking('Олена', '@olena')
        self.assertFalse(result)

    @override_settings(DEBUG=True, TELEGRAM_BOT_TOKEN='', TELEGRAM_CHAT_ID='')
    def test_notify_booking_debug_fallback(self):
        from .notifications import notify_booking
        # У режимі DEBUG без налаштованого токена заявка успішно логується
        self.assertTrue(notify_booking('Тест', '@contact'))

    @override_settings(DEBUG=False, TELEGRAM_BOT_TOKEN='', TELEGRAM_CHAT_ID='')
    def test_notify_booking_prod_missing_token_fails(self):
        from .notifications import notify_booking
        self.assertFalse(notify_booking('Тест', '@contact'))


class ContentTests(SimpleTestCase):
    def test_states_and_topics_present(self):
        self.assertEqual(len(content.get_states()), 3)
        self.assertEqual(len(content.get_topics()), 4)

    def test_topics_have_icon_and_booking_topic(self):
        for t in content.get_topics():
            self.assertTrue(t['icon_path'])
            self.assertTrue(t['booking_topic'])

    def test_index_renders_content(self):
        html = self.client.get(reverse('main:index')).content.decode()
        for t in content.get_topics():
            self.assertIn(t['title'], html)
