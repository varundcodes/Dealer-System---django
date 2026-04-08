from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_login, name="admin_login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),

    path("add-area/", views.add_area, name="add_area"),
    path("add-vendor/", views.add_vendor, name="add_vendor"),
    path("add-executive/", views.add_executive, name="add_executive"),
    path("add-newspaper/", views.add_newspaper, name="add_newspaper"),
    path("add-magazine/", views.add_magazine, name="add_magazine"),
    path("admin-indent/", views.admin_indent, name="admin_indent"),
    path("payment-history/", views.payment_history, name="payment_history"),
]