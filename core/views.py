from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from .models import Area, Vendor, Executive, Newspaper, Magazine, DailyIndent,DailyIndentNewspaperItem,AreaNewspaper,Payment

from .models import (
    Executive,
    Vendor,
    Newspaper,
    Magazine,
    DailyIndent,
    DailyIndentNewspaperItem,
    DailyIndentMagazineItem,
)


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


from django.utils import timezone

def admin_indent(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    areas = Area.objects.all().order_by("name")

    selected_area = request.GET.get("area")
    selected_date = request.GET.get("date") or str(timezone.now().date())

    vendors = Vendor.objects.filter(area_id=selected_area, is_active=True) if selected_area else []

    newspapers = Newspaper.objects.filter(
        is_active=True,
        newspaper_areas__area_id=selected_area,
        newspaper_areas__is_active=True
    ).distinct()

    magazines = Magazine.objects.filter(is_active=True)

    indents = DailyIndent.objects.filter(
        area_id=selected_area,
        date=selected_date
    ).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    )

    indent_map = {}
    for indent in indents:
        key = indent.vendor_id
        indent_map[key] = indent

    if request.method == "POST":
        for vendor in vendors:
            indent = indent_map.get(vendor.id)

            if not indent:
                indent = DailyIndent.objects.create(
                    vendor=vendor,
                    area=vendor.area,
                    date=selected_date
                )

            # cash
            cash = request.POST.get(f"cash_{vendor.id}", "0")
            indent.cash_collected = Decimal(cash or 0)

            # return
            ret = request.POST.get(f"return_{vendor.id}", "0")
            indent.total_return = int(ret or 0)

            indent.save()

        messages.success(request, "Indent updated successfully")
        return redirect(request.get_full_path())

    return render(request, "core/admin_indent.html", {
        "areas": areas,
        "vendors": vendors,
        "newspapers": newspapers,
        "magazines": magazines,
        "indent_map": indent_map,
        "selected_area": selected_area,
        "selected_date": selected_date,
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

    vendors = Vendor.objects.filter(
        area=executive.area,
        is_active=True
    ).order_by("name")

    selected_date = request.POST.get("date") or str(timezone.now().date())

    if request.method == "POST":
        for vendor in vendors:
            indent, created = DailyIndent.objects.get_or_create(
                vendor=vendor,
                date=selected_date,
                defaults={
                    "area": vendor.area,
                    "executive": executive
                }
            )

            cash_value = request.POST.get(f"cash_{vendor.id}", "0")
            try:
                cash_value = Decimal(cash_value)
            except:
                cash_value = Decimal("0.00")

            return_value = request.POST.get(f"return_{vendor.id}", "0")
            try:
                return_value = int(return_value)
            except:
                return_value = 0

            indent.cash_collected = cash_value

            if hasattr(indent, "return_quantity"):
                indent.return_quantity = return_value

            indent.area = vendor.area
            indent.executive = executive
            indent.save()

            indent.newspaper_items.all().delete()
            indent.magazine_items.all().delete()

            # newspapers
            paper_map = {
                "Udayavani": request.POST.get(f"qty_udayavani_{vendor.id}", "0"),
                "Eenadu": request.POST.get(f"qty_eenadu_{vendor.id}", "0"),
                "Dinakaran": request.POST.get(f"qty_dinakaran_{vendor.id}", "0"),
                "Sakshi": request.POST.get(f"qty_sakshi_{vendor.id}", "0"),
                "K Prabha": request.POST.get(f"qty_kprabha_{vendor.id}", "0"),
                "Business Standard": request.POST.get(f"qty_bstandard_{vendor.id}", "0"),
            }

            for paper_name, qty in paper_map.items():
                try:
                    qty = int(qty)
                except:
                    qty = 0

                if qty > 0:
                    paper = Newspaper.objects.filter(name=paper_name, is_active=True).first()
                    if paper:
                        DailyIndentNewspaperItem.objects.create(
                            daily_indent=indent,
                            newspaper=paper,
                            quantity=qty
                        )

            # magazines
            mag_map = {
                "Taranga": request.POST.get(f"mag_taranga_{vendor.id}", "0"),
                "Roopathara": request.POST.get(f"mag_roopathara_{vendor.id}", "0"),
                "Tushara": request.POST.get(f"mag_tushara_{vendor.id}", "0"),
            }

            for mag_name, qty in mag_map.items():
                try:
                    qty = int(qty)
                except:
                    qty = 0

                if qty > 0:
                    mag = Magazine.objects.filter(name=mag_name, is_active=True).first()
                    if mag:
                        DailyIndentMagazineItem.objects.create(
                            daily_indent=indent,
                            magazine=mag,
                            quantity=qty
                        )

        messages.success(request, "Indent saved successfully")
        return redirect("daily_indent")

    return render(request, "core/daily_indent.html", {
        "vendors": vendors,
        "selected_date": selected_date
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

    existing_payments = Payment.objects.filter(vendor=vendor)

    total_indent_amount = Decimal("0.00")
    total_cash_collected = Decimal("0.00")

    for indent in indents:
        total_indent_amount += indent.total_amount()
        total_cash_collected += Decimal(indent.cash_collected or 0)

    total_paid = Decimal("0.00")
    for payment in existing_payments:
        if payment.is_paid:
            total_paid += Decimal(payment.amount)

    amount = total_indent_amount - total_cash_collected - total_paid

    if amount < 0:
        amount = Decimal("0.00")

    upi_id = "9980021351@ybl"
    upi_name = "GANESHA D"

    upi_link = f"upi://pay?pa={upi_id}&pn={upi_name}&am={amount}&cu=INR"

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
    total_cash_collected = Decimal("0.00")

    for indent in indents:
        total_indent_amount += indent.total_amount()
        total_cash_collected += Decimal(indent.cash_collected or 0)

    total_paid = Decimal("0.00")
    for payment in payments:
        if payment.is_paid:
            total_paid += Decimal(payment.amount)

    balance = total_indent_amount - total_cash_collected - total_paid

    if balance < 0:
        balance = Decimal("0.00")

    context = {
        "vendor": vendor,
        "payments": payments[:5],
        "total_indent_amount": total_indent_amount,
        "total_cash_collected": total_cash_collected,
        "total_paid": total_paid,
        "balance": balance,
    }

    return render(request, "core/vendor_dashboard.html", context)

def vendor_logout(request):
    request.session.pop("vendor_id", None)
    return redirect("vendor_login")


def home(request):
    return render(request, 'core/home.html')


def vendor_indent_history(request):
    vendor_id = request.session.get("vendor_id")
    if not vendor_id:
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    date_from = request.GET.get("from_date")
    date_to = request.GET.get("to_date")

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    ).order_by("-date")

    if date_from:
        indents = indents.filter(date__gte=date_from)
    if date_to:
        indents = indents.filter(date__lte=date_to)

    return render(request, "core/vendor_indent_history.html", {
        "vendor": vendor,
        "indents": indents,
        "date_from": date_from,
        "date_to": date_to,
    })

def vendor_ledger(request):
    from django.utils import timezone
    from decimal import Decimal

    selected_date = request.GET.get("date") or str(timezone.now().date())
    vendors = Vendor.objects.filter(is_active=True).order_by("name")

    paper_names = {
        "Udayavani": "Udayavani",
        "Eenadu": "Eenadu",
        "Dinakaran": "Dinakaran",
        "Sakshi": "Sakshi",
        "K_Prabha": "K Prabha",
        "Business_Standard": "Business Standard",
    }

    data = []

    for vendor in vendors:
        indent = DailyIndent.objects.filter(
            vendor=vendor,
            date=selected_date
        ).prefetch_related("newspaper_items__newspaper").first()

        row = {
            "vendor": vendor.name,
            "cash": Decimal("0.00"),
            "papers": {key: 0 for key in paper_names.keys()},
            "total": Decimal("0.00"),
        }

        if indent:
            row["cash"] = indent.cash_collected or Decimal("0.00")
            row["total"] = indent.total_amount()

            for item in indent.newspaper_items.all():
                for key, label in paper_names.items():
                    if item.newspaper.name == label:
                        row["papers"][key] = item.quantity

        data.append(row)

    return render(request, "core/vendor_ledger.html", {
        "data": data,
        "selected_date": selected_date,
    })

def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="admin123"
        )
        return HttpResponse("Admin created successfully")
    return HttpResponse("Admin already exists")


def vendor_list(request):
    vendors = Vendor.objects.all()

    grand_total = 0   # 👈 ADD THIS

    for vendor in vendors:
        papers_total = sum([item.total for item in vendor.vendor_items.all()])
        magazines_total = sum([m.price for m in vendor.magazines.all()])

        vendor.total = papers_total + magazines_total
        grand_total += vendor.total

    return render(request, 'vendor/vendor_list.html', {
        'vendors': vendors,
        'grand_total': grand_total   # 👈 SEND TO HTML
    })


def vendor_detail(request, vendor_id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor).order_by("-date")

    data = []
    grand_total = Decimal("0.00")

    for indent in indents:
        row = {
            "date": indent.date,
            "cash": indent.cash_collected or 0,
            "return": getattr(indent, "return_quantity", 0),
            "papers": {},
            "total": 0
        }

        total = 0

        # Newspapers
        for item in indent.newspaper_items.all():
            safe_name = item.newspaper.name.replace(" ", "_")
            row["papers"][safe_name] = item.quantity
            total += item.quantity

        # Magazines
        for item in indent.magazine_items.all():
            safe_name = item.magazine.name.replace(" ", "_")
            row["papers"][safe_name] = item.quantity
            total += item.quantity

        row["total"] = total
        grand_total += total

        data.append(row)

    return render(request, "core/vendor_detail.html", {
        "vendor": vendor,
        "data": data,
        "grand_total": grand_total
    })


    def vendor_ledger(request):
     if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendors = Vendor.objects.all().order_by("name")

    vendor_id = request.GET.get("vendor")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    data = []
    grand_total = Decimal("0.00")
    selected_vendor = None

    if vendor_id:
        selected_vendor = get_object_or_404(Vendor, id=vendor_id)

        indents = DailyIndent.objects.filter(vendor=selected_vendor).order_by("date")

        if from_date:
            indents = indents.filter(date__gte=from_date)

        if to_date:
            indents = indents.filter(date__lte=to_date)

        for indent in indents:
            row = {
                "date": indent.date,
                "cash": indent.cash_collected or 0,
                "return": getattr(indent, "return_quantity", 0),
                "papers": {},
                "total": 0
            }

            total = 0

            for item in indent.newspaper_items.all():
                safe_name = item.newspaper.name.replace(" ", "_")
                row["papers"][safe_name] = item.quantity
                total += item.quantity

            for item in indent.magazine_items.all():
                safe_name = item.magazine.name.replace(" ", "_")
                row["papers"][safe_name] = item.quantity
                total += item.quantity

            row["total"] = total
            grand_total += total

            data.append(row)

    return render(request, "core/vendor_ledger.html", {
        "vendors": vendors,
        "selected_vendor": selected_vendor,
        "from_date": from_date,
        "to_date": to_date,
        "data": data,
        "grand_total": grand_total,
    })