from django.urls import path
from .views import profile_detail_view, link_click_view, contact_view

urlpatterns = [
    path('<slug:profile_slug>/contact/', contact_view, name='profile_contact'),
    path('<slug:profile_slug>/', profile_detail_view, name='profile_detail'),
    path('click/<int:link_id>/', link_click_view, name='link_click'),
]