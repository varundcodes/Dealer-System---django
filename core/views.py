from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Area,
    Executive,
    Vendor,
    DailyIndent,
    VendorPayment,
)


def dashboard(request):
    return render(request, "core/dashboard.html")


# ---------------- EXECUTIVE ----------------

def executive_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            executive = Executive.objects.get(
                phone=phone,
                password=password,
                is_active=True
            )
            request.session["executive_id"] = executive.id
            request.session["executive_area_id"] = executive.area_id
            return redirect("daily_indent")
        except Executive.DoesNotExist:
            messages.error(request, "Invalid phone number or password.")

    return render(request, "core/executive_login.html")


def executive_logout(request):
    request.session.pop("executive_id", None)
    request.session.pop("executive_area_id", None)
    return redirect("executive_login")


# ---------------- DAILY INDENT ----------------

def daily_indent(request):
    if not request.session.get("executive_id"):
        return redirect("executive_login")

    executive_area_id = request.session.get("executive_area_id")
    selected_area = request.GET.get("area") or request.POST.get("area") or str(executive_area_id or "")
    selected_date = request.GET.get("date") or request.POST.get("date")

    areas = Area.objects.all().order_by("name")
    vendors = Vendor.objects.filter(is_active=True)

    if selected_area:
        vendors = vendors.filter(area_id=selected_area)

    if request.method == "POST":
        if not selected_area or not selected_date:
            messages.error(request, "Please select area and date.")
            return redirect("daily_indent")

        for vendor in vendors:
            DailyIndent.objects.update_or_create(
                vendor=vendor,
                date=selected_date,
                defaults={
                    "udayavani": int(request.POST.get(f"udayavani_{vendor.id}", 0) or 0),
                    "enadu": int(request.POST.get(f"enadu_{vendor.id}", 0) or 0),
                    "dnk": int(request.POST.get(f"dnk_{vendor.id}", 0) or 0),
                    "sakshi": int(request.POST.get(f"sakshi_{vendor.id}", 0) or 0),
                    "b_standard": int(request.POST.get(f"b_standard_{vendor.id}", 0) or 0),
                    "k_prabha": int(request.POST.get(f"k_prabha_{vendor.id}", 0) or 0),
                    "sk": int(request.POST.get(f"sk_{vendor.id}", 0) or 0),
                    "tharanga": int(request.POST.get(f"tharanga_{vendor.id}", 0) or 0),
                    "karma_veera": int(request.POST.get(f"karma_veera_{vendor.id}", 0) or 0),
                    "tushara": int(request.POST.get(f"tushara_{vendor.id}", 0) or 0),
                    "roopathara": int(request.POST.get(f"roopathara_{vendor.id}", 0) or 0),

                    "returned_udayavani": int(request.POST.get(f"returned_udayavani_{vendor.id}", 0) or 0),
                    "returned_enadu": int(request.POST.get(f"returned_enadu_{vendor.id}", 0) or 0),
                    "returned_dnk": int(request.POST.get(f"returned_dnk_{vendor.id}", 0) or 0),
                    "returned_sakshi": int(request.POST.get(f"returned_sakshi_{vendor.id}", 0) or 0),
                    "returned_b_standard": int(request.POST.get(f"returned_b_standard_{vendor.id}", 0) or 0),
                    "returned_k_prabha": int(request.POST.get(f"returned_k_prabha_{vendor.id}", 0) or 0),
                    "returned_sk": int(request.POST.get(f"returned_sk_{vendor.id}", 0) or 0),

                    "returned_tharanga": int(request.POST.get(f"returned_tharanga_{vendor.id}", 0) or 0),
                    "returned_karma_veera": int(request.POST.get(f"returned_karma_veera_{vendor.id}", 0) or 0),
                    "returned_tushara": int(request.POST.get(f"returned_tushara_{vendor.id}", 0) or 0),
                    "returned_roopathara": int(request.POST.get(f"returned_roopathara_{vendor.id}", 0) or 0),
                },
            )

        messages.success(request, "Indent saved successfully.")
        return redirect(f"/daily-indent/?area={selected_area}&date={selected_date}")

    preview_data = []
    if selected_area and selected_date:
        preview_data = DailyIndent.objects.filter(
            vendor__area_id=selected_area,
            date=selected_date
        ).select_related("vendor", "vendor__area").order_by("vendor__name")

    return render(request, "core/daily_indent.html", {
        "areas": areas,
        "vendors": vendors,
        "selected_area": selected_area,
        "selected_date": selected_date,
        "preview_data": preview_data,
    })


# ---------------- VENDOR ----------------

def vendor_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            vendor = Vendor.objects.get(
                phone=phone,
                password=password,
                is_active=True
            )
            request.session["vendor_id"] = vendor.id
            return redirect("vendor_dashboard")
        except Vendor.DoesNotExist:
            messages.error(request, "Invalid phone number or password.")

    return render(request, "core/vendor_login.html")


def vendor_logout(request):
    request.session.pop("vendor_id", None)
    return redirect("vendor_login")


def vendor_dashboard(request):
    vendor_id = request.session.get("vendor_id")
    if not vendor_id:
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor).order_by("date")
    payments = VendorPayment.objects.filter(vendor=vendor).order_by("date")

    balance = Decimal(vendor.opening_balance)

    for indent in indents:
        balance += indent.calculate_amount()

    for payment in payments:
        balance -= payment.amount

    return render(request, "core/vendor_dashboard.html", {
        "vendor": vendor,
        "balance": balance,
    })


def vendor_ledger(request):
    vendor_id = request.session.get("vendor_id")
    if not vendor_id:
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)
    indents = DailyIndent.objects.filter(vendor=vendor).order_by("-date")

    return render(request, "core/vendor_ledger.html", {
        "vendor": vendor,
        "indents": indents,
    })


def make_payment(request):
    vendor_id = request.session.get("vendor_id")
    if not vendor_id:
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor)
    payments = VendorPayment.objects.filter(vendor=vendor)

    balance = Decimal(vendor.opening_balance)

    for indent in indents:
        balance += indent.calculate_amount()

    for payment in payments:
        balance -= payment.amount

    if request.method == "POST":
        VendorPayment.objects.create(
            vendor=vendor,
            date=request.POST.get("date"),
            amount=request.POST.get("amount"),
            note=request.POST.get("note"),
            screenshot=request.FILES.get("screenshot"),
        )
        messages.success(request, "Payment saved")
        return redirect("vendor_dashboard")

    return render(request, "core/make_payment.html", {
        "vendor": vendor,
        "balance": balance,
        "upi_id": "yourupi@okaxis",
    })