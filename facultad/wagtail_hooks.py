# facultad/wagtail_hooks.py
from django.urls import path
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse
from .views import metrics_dashboard

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('metrics/', metrics_dashboard, name='metrics_dashboard'),
    ]

@hooks.register('register_admin_menu_item')
def register_metrics_menu_item():
    return MenuItem('Métricas FOLP', reverse('metrics_dashboard'), icon_name='pick', order=10000)