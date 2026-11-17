from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .content import get_states, get_topics
from .forms import BookingForm
from .notifications import notify_booking


def index(request):
    return render(request, 'main/index.html', {
        'topics': get_topics(),
        'states': get_states(),
        'telegram_url': getattr(settings, 'TELEGRAM_DIRECT_URL', 'https://t.me/prostir_mizhnami_bot'),
        'whatsapp_url': getattr(settings, 'WHATSAPP_DIRECT_URL', 'https://wa.me/380000000000'),
    })


@require_POST
def booking_create(request):
    form = BookingForm(request.POST)
    if not form.is_valid():
        if 'website' in form.errors:
            # спрацювала приманка: імітуємо успіх, нічого не надсилаючи
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    notified = notify_booking(
        form.cleaned_data['name'],
        form.cleaned_data['contact'],
        form.cleaned_data['topic'],
    )
    if not notified:
        return JsonResponse({'ok': False, 'errors': {'__all__': ['delivery']}}, status=502)
    return JsonResponse({'ok': True})
