from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from decimal import Decimal
from .models import Area, Vendor, Executive, Newspaper, Magazine, DailyIndent,DailyIndentNewspaperItem,AreaNewspaper,Payment


def admin_login(request):
    admin_username = "admin"
    admin_password = "admin@123"

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if username == admin_username and password == admin_password:
            request.session["is_admin_logged_in"] = True
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid login details")

    return render(request, "core/admin_login.html")


def admin_dashboard(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    return render(request, "core/admin_dashboard.html")


def admin_logout(request):
    request.session.pop("is_admin_logged_in", None)
    return redirect("admin_login")


def add_area(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Area name is required")
        elif Area.objects.filter(name__iexact=name).exists():
            messages.error(request, "Area already exists")
        else:
            Area.objects.create(name=name)
            messages.success(request, "Area added successfully")
            return redirect("add_area")

    areas = Area.objects.all().order_by("name")
    return render(request, "core/add_area.html", {"areas": areas})


def add_vendor(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip() or "demo@123"
        area_id = request.POST.get("area")
        is_active = True if request.POST.get("is_active") == "on" else False

        if not name or not phone or not area_id:
            messages.error(request, "Name, phone and area are required")
        elif Vendor.objects.filter(phone=phone).exists():
            messages.error(request, "Vendor phone already exists")
        else:
            Vendor.objects.create(
                name=name,
                phone=phone,
                password=password,
                area_id=area_id,
                is_active=is_active,
            )
            messages.success(request, "Vendor added successfully")
            return redirect("add_vendor")

    vendors = Vendor.objects.select_related("area").all().order_by("name")
    areas = Area.objects.all().order_by("name")
    return render(request, "core/add_vendor.html", {
        "vendors": vendors,
        "areas": areas,
    })


def add_executive(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip() or "demo@123"
        area_id = request.POST.get("area")

        if not name or not phone or not area_id:
            messages.error(request, "Name, phone and area are required")
        elif Executive.objects.filter(phone=phone).exists():
            messages.error(request, "Executive phone already exists")
        else:
            Executive.objects.create(
                name=name,
                phone=phone,
                password=password,
                area_id=area_id,
            )
            messages.success(request, "Executive added successfully")
            return redirect("add_executive")

    executives = Executive.objects.select_related("area").all().order_by("name")
    areas = Area.objects.all().order_by("name")
    return render(request, "core/add_executive.html", {
        "executives": executives,
        "areas": areas,
    })


def add_newspaper(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        weekday_price = request.POST.get("weekday_price") or 0
        weekend_price = request.POST.get("weekend_price") or 0

        if not name:
            messages.error(request, "Newspaper name is required")
        elif Newspaper.objects.filter(name__iexact=name).exists():
            messages.error(request, "Newspaper already exists")
        else:
            Newspaper.objects.create(
                name=name,
                weekday_price=weekday_price,
                weekend_price=weekend_price,
            )
            messages.success(request, "Newspaper added successfully")
            return redirect("add_newspaper")

    newspapers = Newspaper.objects.all().order_by("name")
    return render(request, "core/add_newspaper.html", {"newspapers": newspapers})


def add_magazine(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        magazine_type = request.POST.get("magazine_type", "").strip()
        price = request.POST.get("price") or 0

        if not name or not magazine_type:
            messages.error(request, "Magazine name and type are required")
        elif Magazine.objects.filter(name__iexact=name).exists():
            messages.error(request, "Magazine already exists")
        else:
            Magazine.objects.create(
                name=name,
                magazine_type=magazine_type,
                price=price,
            )
            messages.success(request, "Magazine added successfully")
            return redirect("add_magazine")

    magazines = Magazine.objects.all().order_by("name")
    return render(request, "core/add_magazine.html", {"magazines": magazines})


def admin_indent(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    indents = DailyIndent.objects.select_related(
        "vendor", "area", "executive"
    ).prefetch_related(
        "newspaper_items__newspaper"
    ).order_by("-date", "-id")

    return render(request, "core/admin_indent.html", {
        "indents": indents
    })


def payment_history(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    return render(request, "core/payment_history.html")



def executive_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            executive = Executive.objects.get(phone=phone, password=password)
            request.session["executive_id"] = executive.id
            return redirect("daily_indent")
        except Executive.DoesNotExist:
            messages.error(request, "Invalid phone number or password")

    return render(request, "core/executive_login.html")


def executive_logout(request):
    request.session.pop("executive_id", None)
    return redirect("executive_login")


def daily_indent(request):
    if not request.session.get("executive_id"):
        return redirect("executive_login")

    executive = get_object_or_404(Executive, id=request.session["executive_id"])

    all_vendors = Vendor.objects.filter(area=executive.area).order_by("name")
    vendors = Vendor.objects.filter(area=executive.area, is_active=True).order_by("name")

    newspapers = Newspaper.objects.filter(
        is_active=True,
        newspaper_areas__area=executive.area,
        newspaper_areas__is_active=True
    ).distinct().order_by("name")

    selected_date = request.POST.get("date") or request.GET.get("date") or ""

    if request.method == "POST":
        if not selected_date:
            messages.error(request, "Date is required")
            return redirect("daily_indent")

        for vendor in vendors:
            daily_indent, created = DailyIndent.objects.get_or_create(
                vendor=vendor,
                date=selected_date,
                defaults={
                    "area": vendor.area,
                    "executive": executive,
                }
            )

            if not created:
                daily_indent.area = vendor.area
                daily_indent.executive = executive
                daily_indent.save()

            daily_indent.newspaper_items.all().delete()

            for paper in newspapers:
                qty = request.POST.get(f"qty_{vendor.id}_{paper.id}", 0)

                try:
                    qty = int(qty)
                except ValueError:
                    qty = 0

                if qty > 0:
                    DailyIndentNewspaperItem.objects.create(
                        daily_indent=daily_indent,
                        newspaper=paper,
                        quantity=qty
                    )

        messages.success(request, "Daily indent saved successfully")
        return redirect(f"{request.path}?date={selected_date}")

    return render(request, "core/daily_indent.html", {
        "executive": executive,
        "vendors": vendors,
        "all_vendors": all_vendors,
        "newspapers": newspapers,
        "selected_date": selected_date,
    })

def map_area_newspaper(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    areas = Area.objects.all().order_by("name")
    newspapers = Newspaper.objects.filter(is_active=True).order_by("name")

    if request.method == "POST":
        area_id = request.POST.get("area")
        selected_newspapers = request.POST.getlist("newspapers")

        if not area_id:
            messages.error(request, "Please select an area")
            return redirect("map_area_newspaper")

        area = get_object_or_404(Area, id=area_id)

        AreaNewspaper.objects.filter(area=area).delete()

        for newspaper_id in selected_newspapers:
            newspaper = get_object_or_404(Newspaper, id=newspaper_id)
            AreaNewspaper.objects.create(
                area=area,
                newspaper=newspaper,
                is_active=True
            )

        messages.success(request, "Area newspapers mapped successfully")
        return redirect("map_area_newspaper")

    mappings = AreaNewspaper.objects.select_related("area", "newspaper").order_by("area__name", "newspaper__name")

    return render(request, "core/map_area_newspaper.html", {
        "areas": areas,
        "newspapers": newspapers,
        "mappings": mappings,
    })


def payment_history(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    payments = Payment.objects.select_related("vendor").all().order_by("-date", "-id")

    return render(request, "core/payment_history.html", {
        "payments": payments
    })


def toggle_vendor_status(request, vendor_id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    vendor.is_active = not vendor.is_active
    vendor.save()

    if vendor.is_active:
        messages.success(request, f"{vendor.name} is now Active")
    else:
        messages.success(request, f"{vendor.name} is now Inactive")

    return redirect("add_vendor")


def update_payment_status(request, payment_id, status):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    payment = get_object_or_404(Payment, id=payment_id)
    vendor = payment.vendor

    if status == "paid":
        payment.is_paid = True
        vendor.is_active = True
        messages.success(request, f"{vendor.name} marked as Paid and Activated.")
    else:
        payment.is_paid = False
        vendor.is_active = False
        messages.success(request, f"{vendor.name} marked as Pending and Stopped.")

    payment.save()
    vendor.save()

    return redirect("payment_history")


def vendor_payment_page(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    )

    payments = Payment.objects.filter(vendor=vendor)

    total_indent_amount = Decimal("0.00")
    for indent in indents:
        total_indent_amount += indent.total_amount()

    total_paid = Decimal("0.00")
    for payment in payments:
        if payment.is_paid:
            total_paid += Decimal(payment.amount)

    amount = total_indent_amount - total_paid
    if amount < 0:
        amount = Decimal("0.00")

    upi_id = "yourupi@okaxis"
    upi_name = "Dealer System"
    upi_link = f"upi://pay?pa={upi_id}&pn={upi_name}&am={amount}"
    qr_url = "/media/qr.png"

    if request.method == "POST":
        screenshot = request.FILES.get("screenshot")
        note = request.POST.get("note", "")

        Payment.objects.create(
            vendor=vendor,
            amount=amount,
            is_paid=False,
            screenshot=screenshot,
            note=note,
        )

        messages.success(request, "Payment screenshot uploaded")
        return redirect("vendor_payment_page", vendor_id=vendor.id)

    payments = Payment.objects.filter(vendor=vendor).order_by("-date", "-id")

    return render(request, "core/vendor_payment_page.html", {
        "vendor": vendor,
        "amount": amount,
        "upi_id": upi_id,
        "upi_link": upi_link,
        "qr_url": qr_url,
        "payments": payments,
    })


def vendor_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        try:
            vendor = Vendor.objects.get(phone=phone, password=password, is_active=True)
            request.session["vendor_id"] = vendor.id
            return redirect("vendor_dashboard")
        except Vendor.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, "core/vendor_login.html")


def vendor_dashboard(request):
    vendor_id = request.session.get("vendor_id")

    if not vendor_id:
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    )

    payments = Payment.objects.filter(vendor=vendor).order_by("-date", "-id")

    total_indent_amount = Decimal("0.00")
    for indent in indents:
        total_indent_amount += indent.total_amount()

    total_paid =  Decimal("0.00")
    for payment in payments:
        if payment.is_paid:
            total_paid += Decimal(payment.amount)

    balance = total_indent_amount - total_paid
    if balance < 0:
        balance = Decimal("0.00")

    context = {
        "vendor": vendor,
        "payments": payments[:5],
        "total_indent_amount": total_indent_amount,
        "total_paid": total_paid,
        "balance": balance,
    }

    return render(request, "core/vendor_dashboard.html", context)

def vendor_logout(request):
    request.session.pop("vendor_id", None)
    return redirect("vendor_login")


def home(request):
    return render(request, 'core/home.html')
