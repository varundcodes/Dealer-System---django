from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    # 🔹 Default Django Admin
    path('admin/', admin.site.urls),

    # 🔹 Homepage (Main Dashboard)
    path('', views.home, name='home'),

    # 🔹 Admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # 🔹 Master Data
    path('add-area/', views.add_area, name='add_area'),
    path('add-vendor/', views.add_vendor, name='add_vendor'),
    path('add-executive/', views.add_executive, name='add_executive'),
    path('add-newspaper/', views.add_newspaper, name='add_newspaper'),
    path('add-magazine/', views.add_magazine, name='add_magazine'),

    # 🔹 Mapping
    path('map-area-newspaper/', views.map_area_newspaper, name='map_area_newspaper'),

    # 🔹 Admin Features
    path('admin-indent/', views.admin_indent, name='admin_indent'),
    path('payment-history/', views.payment_history, name='payment_history'),

    # 🔹 Vendor Control
    path('toggle-vendor-status/<int:vendor_id>/', views.toggle_vendor_status, name='toggle_vendor_status'),

    # 🔹 Payment Status
    path('update-payment-status/<int:payment_id>/<str:status>/', views.update_payment_status, name='update_payment_status'),

    # 🔹 Vendor Payment Page
    path('vendor-payment/<int:vendor_id>/', views.vendor_payment_page, name='vendor_payment_page'),

    # 🔹 Executive
    path('executive-login/', views.executive_login, name='executive_login'),
    path('executive-logout/', views.executive_logout, name='executive_logout'),
    path('daily-indent/', views.daily_indent, name='daily_indent'),

    # 🔹 Vendor
    path('vendor-login/', views.vendor_login, name='vendor_login'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor-logout/', views.vendor_logout, name='vendor_logout'),
]