from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('executive-login/', views.executive_login, name='executive_login'),
    path('executive-logout/', views.executive_logout, name='executive_logout'),
    path('daily-indent/', views.daily_indent, name='daily_indent'),

    path('vendor-login/', views.vendor_login, name='vendor_login'),
    path('vendor-logout/', views.vendor_logout, name='vendor_logout'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor-ledger/', views.vendor_ledger, name='vendor_ledger'),
    path('make-payment/', views.make_payment, name='make_payment'),
]