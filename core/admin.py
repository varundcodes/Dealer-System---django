from django.contrib import admin
from .models import (
    Area,
    Vendor,
    Executive,
    Newspaper,
    Magazine,
    DailyIndent,
    DailyIndentNewspaperItem,
    Payment,
    AreaNewspaper
)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "area", "is_active", "opening_balance")
    list_filter = ("area", "is_active")
    search_fields = ("name", "phone")


@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "area")
    list_filter = ("area",)
    search_fields = ("name", "phone")


@admin.register(Newspaper)
class NewspaperAdmin(admin.ModelAdmin):
    list_display = ("name", "weekday_price", "weekend_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "magazine_type")
    search_fields = ("name",)


@admin.register(AreaNewspaper)
class AreaNewspaperAdmin(admin.ModelAdmin):
    list_display = ("area", "newspaper", "is_active")
    list_filter = ("area", "is_active")


@admin.register(DailyIndent)
class DailyIndentAdmin(admin.ModelAdmin):
    list_display = ("vendor", "date", "area")
    list_filter = ("area", "date")


@admin.register(DailyIndentNewspaperItem)
class DailyIndentItemAdmin(admin.ModelAdmin):
    list_display = ("daily_indent", "newspaper", "quantity")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "date", "is_paid")
    list_filter = ("is_paid", "date")