from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
from links.models import Link
from analytics.models import LinkClick

def profile_detail_view(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug)
    links = profile.links.filter(is_active=True).order_by('order')
    
    context = {
        'profile': profile,
        'links': links
    }
    return render(request, 'profiles/index.html', context)


def link_click_view(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')
    
    LinkClick.objects.create(
        link=link,
        ip_address=ip,
        user_agent=user_agent
    )
    
    return redirect(link.url)