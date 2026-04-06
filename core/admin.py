from django.contrib import admin
from .models import (
    Area,
    Executive,
    Vendor,
    NewspaperPrice,
    MagazinePrice,
    DailyIndent,
    VendorPayment,
)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "phone", "password", "is_active")
    search_fields = ("name", "phone", "area__name")
    list_filter = ("area", "is_active")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "phone", "password", "opening_balance", "is_active")
    search_fields = ("name", "phone", "area__name")
    list_filter = ("area", "is_active")


@admin.register(NewspaperPrice)
class NewspaperPriceAdmin(admin.ModelAdmin):
    list_display = ("name", "weekday_price", "weekend_price", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(MagazinePrice)
class MagazinePriceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active")
    search_fields = ("name",)
    list_filter = ("category", "is_active")


@admin.register(DailyIndent)
class DailyIndentAdmin(admin.ModelAdmin):
    list_display = (
        "vendor",
        "date",
        "udayavani",
        "enadu",
        "dnk",
        "sakshi",
        "b_standard",
        "k_prabha",
        "sk",
        "tharanga",
        "karma_veera",
        "tushara",
        "roopathara",
        "returned_udayavani",
        "returned_enadu",
        "returned_dnk",
        "returned_sakshi",
        "returned_b_standard",
        "returned_k_prabha",
        "returned_sk",
        "returned_tharanga",
        "returned_karma_veera",
        "returned_tushara",
        "returned_roopathara",
    )
    search_fields = ("vendor__name", "vendor__phone")
    list_filter = ("date", "vendor__area")
    date_hierarchy = "date"


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ("vendor", "date", "amount", "note")
    search_fields = ("vendor__name", "vendor__phone", "note")
    list_filter = ("date", "vendor__area")
    date_hierarchy = "date"
    