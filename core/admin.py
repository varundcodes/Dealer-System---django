from django.contrib import admin
from .models import (
    Area,
    Newspaper,
    Magazine,
    AreaNewspaper,
    AreaMagazine,
    Executive,
    Vendor,
    VendorNewspaper,
    VendorMagazine,
    DailyIndent,
    DailyIndentNewspaperItem,
    DailyIndentMagazineItem,
    VendorPayment,
)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)


@admin.register(Newspaper)
class NewspaperAdmin(admin.ModelAdmin):
    list_display = ("name", "weekday_price", "weekend_price", "is_active")
    search_fields = ("name",)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ("name", "magazine_type", "price", "is_active")
    search_fields = ("name",)


@admin.register(AreaNewspaper)
class AreaNewspaperAdmin(admin.ModelAdmin):
    list_display = ("area", "newspaper", "is_active")
    list_filter = ("area", "is_active")


@admin.register(AreaMagazine)
class AreaMagazineAdmin(admin.ModelAdmin):
    list_display = ("area", "magazine", "is_active")
    list_filter = ("area", "is_active")


@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "area", "is_active")
    list_filter = ("area", "is_active")
    search_fields = ("name", "phone")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "area", "opening_balance", "is_active")
    list_filter = ("area", "is_active")
    search_fields = ("name", "phone")


@admin.register(VendorNewspaper)
class VendorNewspaperAdmin(admin.ModelAdmin):
    list_display = ("vendor", "newspaper", "is_active", "stopped_from")
    list_filter = ("is_active", "newspaper")


@admin.register(VendorMagazine)
class VendorMagazineAdmin(admin.ModelAdmin):
    list_display = ("vendor", "magazine", "is_active", "stopped_from")
    list_filter = ("is_active", "magazine")


class DailyIndentNewspaperItemInline(admin.TabularInline):
    model = DailyIndentNewspaperItem
    extra = 0


class DailyIndentMagazineItemInline(admin.TabularInline):
    model = DailyIndentMagazineItem
    extra = 0


@admin.register(DailyIndent)
class DailyIndentAdmin(admin.ModelAdmin):
    list_display = ("vendor", "date", "area", "executive", "checked_by_admin", "updated_at")
    list_filter = ("area", "date", "checked_by_admin")
    inlines = [DailyIndentNewspaperItemInline, DailyIndentMagazineItemInline]


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ("vendor", "date", "amount", "status")
    list_filter = ("status", "date", "vendor__area")