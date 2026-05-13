from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.models import User
import openpyxl
from django.http import HttpResponse 
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Area,
    AreaNewspaper,
    DailyIndent,
    DailyIndentMagazineItem,
    DailyIndentNewspaperItem,
    Executive,
    ExecutiveVendor,
    Magazine,
    Newspaper,
    Payment,
    Vendor,
    AreaMagazine,
)
def paper_key(name):
    name = name.lower().strip()

    mapping = {
        "udayavani": "udayavani",
        "eenadu": "eenadu",
        "dinakaran": "dinakaran",
        "sakshi": "sakshi",
        "business standard": "business_standard",
        "k prabha": "k_prabha",
        "taranga": "taranga",
        "roopathara": "roopathara",
        "tushara": "tushara",
    }

    return mapping.get(name, name.replace(" ", "_"))

def update_vendor_running_balance(vendor):
    """Recalculate previous/current balance for all indents of one vendor."""
    balance = Decimal(vendor.opening_balance or 0)

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine",
    ).order_by("date", "id")

    for indent in indents:
        subtotal = indent.total_amount()
        cash = Decimal(indent.cash_collected or 0)
        indent.previous_balance = balance

        balance = balance + subtotal - cash
        indent.current_balance = balance
        indent.save(update_fields=["previous_balance", "current_balance"])


def build_indent_rows(indents, opening_balance=0):
    """Build table rows with paper counts, subtotal, cash and running balance."""
    balance = Decimal(opening_balance or 0)
    rows = []

    for indent in indents.order_by("date", "id"):
        row = {
            "indent": indent,
            "date": indent.date,
            "udayavani": 0,
            "eenadu": 0,
            "dinakaran": 0,
            "sakshi": 0,
            "business_standard": 0,
            "k_prabha": 0,
            "taranga": 0,
            "roopathara": 0,
            "tushara": 0,
            "cash": Decimal(indent.cash_collected or 0),
            "previous_balance": balance,
            "subtotal": Decimal("0.00"),
            "total": Decimal("0.00"),
            "balance": Decimal("0.00"),
        }

        subtotal = Decimal("0.00")

        for item in indent.newspaper_items.all():
            key = item.newspaper.name.lower().strip().replace(" ", "_")
            qty = item.quantity
            if key in row:
                row[key] = qty
            subtotal += item.line_amount()

        for item in indent.magazine_items.all():
            key = item.magazine.name.lower().strip().replace(" ", "_")
            qty = item.quantity
            if key in row:
                row[key] = qty
            subtotal += item.line_amount()

        balance = balance + subtotal - row["cash"]
        row["subtotal"] = subtotal
        row["total"] = subtotal
        row["balance"] = balance
        rows.append(row)

    return rows


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


def login(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if user_type == "admin":
            admin_username = "admin"
            admin_password = "admin@123"
            if username == admin_username and password == admin_password:
                request.session["is_admin_logged_in"] = True
                return redirect("admin_dashboard")
            else:
                messages.error(request, "Invalid admin credentials")

        elif user_type == "executive":
            phone = username  # For executive, username is phone
            try:
                executive = Executive.objects.get(phone=phone, password=password)
                request.session["executive_id"] = executive.id
                return redirect("daily_indent")
            except Executive.DoesNotExist:
                messages.error(request, "Invalid executive credentials")

        elif user_type == "vendor":
            phone = username  # For vendor, username is phone
            try:
                vendor = Vendor.objects.get(phone=phone, password=password, is_active=True)
                request.session["vendor_id"] = vendor.id
                return redirect("vendor_dashboard")
            except Vendor.DoesNotExist:
                messages.error(request, "Invalid vendor credentials")

        else:
            messages.error(request, "Please select a user type")

    return render(request, "core/login.html")


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
    return render(
        request,
        "core/add_vendor.html",
        {
            "vendors": vendors,
            "areas": areas,
        },
    )


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
    return render(
        request,
        "core/add_executive.html",
        {
            "executives": executives,
            "areas": areas,
        },
    )


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

    areas = Area.objects.all().order_by("name")
    selected_area = request.GET.get("area")
    selected_date = request.GET.get("date") or str(timezone.now().date())

    vendors = Vendor.objects.filter(area_id=selected_area, is_active=True).order_by("name") if selected_area else []

    paper_order = ["Udayavani", "Eenadu", "Dinakaran", "Sakshi", "Business Standard", "K Prabha"]

    newspapers = list(Newspaper.objects.filter(
        is_active=True,
        newspaper_areas__area_id=selected_area,
        newspaper_areas__is_active=True,
    ).distinct())

    newspapers.sort(key=lambda x: paper_order.index(x.name) if x.name in paper_order else 999)

    magazines = Magazine.objects.filter(is_active=True)

    indents = DailyIndent.objects.filter(
        area_id=selected_area,
        date=selected_date,
    ).prefetch_related("newspaper_items__newspaper", "magazine_items__magazine")

    indent_map = {}
    newspaper_item_map = {}
    magazine_item_map = {}

    for indent in indents:
        indent_map[indent.vendor_id] = indent

        newspaper_item_map[indent.vendor_id] = {}
        for item in indent.newspaper_items.all():
            newspaper_item_map[indent.vendor_id][item.newspaper_id] = item

        magazine_item_map[indent.vendor_id] = {}
        for item in indent.magazine_items.all():
            magazine_item_map[indent.vendor_id][item.magazine_id] = item

    if request.method == "POST":
        for vendor in vendors:
            opening_balance = request.POST.get(f"opening_balance_{vendor.id}", "0")
            vendor.opening_balance = Decimal(opening_balance or 0)
            vendor.save()

            indent = indent_map.get(vendor.id)

            if not indent:
                indent = DailyIndent.objects.create(
                    vendor=vendor,
                    area=vendor.area,
                    date=selected_date,
                )

            cash = request.POST.get(f"cash_{vendor.id}", "0")
            indent.cash_collected = Decimal(cash or 0)

            if hasattr(indent, "total_return"):
                ret = request.POST.get(f"return_{vendor.id}", "0")
                indent.total_return = int(ret or 0)

            indent.save()

            indent.newspaper_items.all().delete()
            indent.magazine_items.all().delete()

            for paper in newspapers:
                qty = request.POST.get(f"paper_{paper.id}_{vendor.id}", "0")
                qty = int(qty or 0)

                if qty > 0:
                    DailyIndentNewspaperItem.objects.create(
                        daily_indent=indent,
                        newspaper=paper,
                        quantity=qty,
                    )

            for mag in magazines:
                qty = request.POST.get(f"mag_{mag.id}_{vendor.id}", "0")
                qty = int(qty or 0)

                if qty > 0:
                    DailyIndentMagazineItem.objects.create(
                        daily_indent=indent,
                        magazine=mag,
                        quantity=qty,
                    )

            update_vendor_running_balance(vendor)

        messages.success(request, "Indent updated successfully")
        return redirect(request.get_full_path())

    balance_map = {}

    for vendor in vendors:
        previous_balance = Decimal(vendor.opening_balance or 0)

        old_indents = DailyIndent.objects.filter(
            vendor=vendor,
            date__lt=selected_date
        ).prefetch_related("newspaper_items__newspaper", "magazine_items__magazine").order_by("date")

        for old_indent in old_indents:
            previous_balance += old_indent.total_amount()
            previous_balance -= Decimal(old_indent.cash_collected or 0)

        today_indent = indent_map.get(vendor.id)
        today_subtotal = today_indent.total_amount() if today_indent else Decimal("0.00")
        today_cash = Decimal(today_indent.cash_collected or 0) if today_indent else Decimal("0.00")

        current_balance = previous_balance + today_subtotal - today_cash

        balance_map[vendor.id] = {
            "previous_balance": previous_balance,
            "today_subtotal": today_subtotal,
            "current_balance": current_balance,
        }

    return render(request, "core/admin_indent.html", {
        "areas": areas,
        "vendors": vendors,
        "newspapers": newspapers,
        "magazines": magazines,
        "indent_map": indent_map,
        "newspaper_item_map": newspaper_item_map,
        "magazine_item_map": magazine_item_map,
        "balance_map": balance_map,
        "selected_area": selected_area,
        "selected_date": selected_date,
    })


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
        executive_mappings__executive=executive,
        executive_mappings__is_active=True,
        is_active=True,
    ).distinct().order_by("name")

    selected_date = request.POST.get("date") or request.GET.get("date") or str(timezone.now().date())

    if request.method == "POST":
        for vendor in vendors:
            indent, created = DailyIndent.objects.get_or_create(
                vendor=vendor,
                date=selected_date,
                defaults={
                    "area": vendor.area,
                    "executive": executive,
                },
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
            if hasattr(indent, "total_return"):
                indent.total_return = return_value

            indent.area = vendor.area
            indent.executive = executive
            indent.save()

            indent.newspaper_items.all().delete()
            indent.magazine_items.all().delete()

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
                            quantity=qty,
                        )

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
                            quantity=qty,
                        )

            update_vendor_running_balance(vendor)

        messages.success(request, "Indent saved successfully")
        return redirect(f"/daily-indent/?date={selected_date}")

    return render(
        request,
        "core/daily_indent.html",
        {
            "vendors": vendors,
            "selected_date": selected_date,
        },
    )


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
                is_active=True,
            )

        messages.success(request, "Area newspapers mapped successfully")
        return redirect("map_area_newspaper")

    mappings = AreaNewspaper.objects.select_related("area", "newspaper").order_by(
        "area__name",
        "newspaper__name",
    )

    return render(
        request,
        "core/map_area_newspaper.html",
        {
            "areas": areas,
            "newspapers": newspapers,
            "mappings": mappings,
        },
    )


def map_executive_vendor(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    executives = Executive.objects.filter(is_active=True).select_related("area").order_by("name")
    vendors = Vendor.objects.filter(is_active=True).select_related("area").order_by("name")

    if request.method == "POST":
        executive_id = request.POST.get("executive")
        selected_vendors = request.POST.getlist("vendors")

        if not executive_id:
            messages.error(request, "Please select an executive")
            return redirect("map_executive_vendor")

        executive = get_object_or_404(Executive, id=executive_id)

        # Remove existing mappings for this executive
        ExecutiveVendor.objects.filter(executive=executive).delete()

        # Create new mappings
        for vendor_id in selected_vendors:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            ExecutiveVendor.objects.create(
                executive=executive,
                vendor=vendor,
                is_active=True,
            )

        messages.success(request, f"Executive {executive.name} mapped to {len(selected_vendors)} vendors successfully")
        return redirect("map_executive_vendor")

    # Get existing mappings
    mappings = ExecutiveVendor.objects.select_related(
        "executive", "executive__area", "vendor", "vendor__area"
    ).order_by("executive__name", "vendor__name")

    return render(
        request,
        "core/map_executive_vendor.html",
        {
            "executives": executives,
            "vendors": vendors,
            "mappings": mappings,
        },
    )


def payment_history(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    payments = Payment.objects.select_related("vendor").all().order_by("-date", "-id")

    return render(
        request,
        "core/payment_history.html",
        {
            "payments": payments,
        },
    )


def toggle_vendor_status(request, vendor_id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Toggle status
    vendor.is_active = not vendor.is_active
    vendor.save()

    if vendor.is_active:
        messages.success(request, f"{vendor.name} is now Active")
    else:
        messages.success(request, f"{vendor.name} is now Inactive")

    
    return redirect("vendor_detail", vendor_id=vendor.id)


def update_payment_status(request, payment_id, status):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    payment = get_object_or_404(Payment, id=payment_id)

    if status == "Verified":
        payment.is_paid = True
        messages.success(request, "Payment approved successfully")

    elif status == "Rejected":
        payment.is_paid = False
        messages.success(request, "Payment rejected successfully")

    else:
        messages.error(request, "Invalid payment status")

    payment.save()

    return redirect("payment_history")


def vendor_payment_page(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine",
    ).order_by("date")

    existing_payments = Payment.objects.filter(vendor=vendor)

    balance = Decimal(vendor.opening_balance or 0)
    total_indent_amount = Decimal("0.00")
    total_cash_collected = Decimal("0.00")

    for indent in indents:
        subtotal = indent.total_amount()
        cash = Decimal(indent.cash_collected or 0)

        total_indent_amount += subtotal
        total_cash_collected += cash
        balance = balance + subtotal - cash

    total_paid = Decimal("0.00")
    for payment in existing_payments:
        if payment.is_paid:
            total_paid += Decimal(payment.amount or 0)

    balance = balance - total_paid

    payable_amount = balance
    if payable_amount < 0:
        payable_amount = Decimal("0.00")

    upi_id = "9980021351@ybl"
    upi_name = "GANESHA D"
    upi_link = f"upi://pay?pa={upi_id}&pn={upi_name}&am={payable_amount}&cu=INR"
    qr_url = "/media/qr.png"

    if request.method == "POST":
        screenshot = request.FILES.get("screenshot")
        note = request.POST.get("note", "")

        paid_amount = request.POST.get("amount", "0")
        paid_amount = Decimal(paid_amount or 0)

        Payment.objects.create(
            vendor=vendor,
            amount=paid_amount,
            is_paid=False,
            screenshot=screenshot,
            note=note,
        )

        messages.success(request, "Payment screenshot uploaded")
        return redirect("vendor_payment_page", vendor_id=vendor.id)

    payments = Payment.objects.filter(vendor=vendor).order_by("-date", "-id")

    return render(request, "core/vendor_payment_page.html", {
        "vendor": vendor,
        "amount": payable_amount,
        "balance": balance,
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
        "magazine_items__magazine",
    ).order_by("date")

    payments = Payment.objects.filter(vendor=vendor).order_by("-date", "-id")

    total_indent_amount = Decimal("0.00")
    total_cash_collected = Decimal("0.00")

    balance = Decimal(vendor.opening_balance or 0)

    for indent in indents:
        subtotal = indent.total_amount()
        cash = Decimal(indent.cash_collected or 0)

        total_indent_amount += subtotal
        total_cash_collected += cash

        balance = balance + subtotal - cash

    total_paid = Decimal("0.00")
    for payment in payments:
        if payment.is_paid:
            total_paid += Decimal(payment.amount or 0)

    balance = balance - total_paid

    return render(request, "core/vendor_dashboard.html", {
        "vendor": vendor,
        "payments": payments[:5],
        "total_indent_amount": total_indent_amount,
        "total_cash_collected": total_cash_collected,
        "total_paid": total_paid,
        "balance": balance,
    })


def vendor_logout(request):
    request.session.pop("vendor_id", None)
    return redirect("vendor_login")


def home(request):
    return render(request, "core/home.html")


def vendor_indent_history(request):
    vendor_id = request.session.get("vendor_id")
    if not vendor_id:
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=vendor_id)

    date_from = request.GET.get("from_date")
    date_to = request.GET.get("to_date")

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine",
    ).order_by("-date")

    if date_from:
        indents = indents.filter(date__gte=date_from)
    if date_to:
        indents = indents.filter(date__lte=date_to)

    return render(
        request,
        "core/vendor_indent_history.html",
        {
            "vendor": vendor,
            "indents": indents,
            "date_from": date_from,
            "date_to": date_to,
        },
    )


def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="admin123",
        )
        return HttpResponse("Admin created successfully")
    return HttpResponse("Admin already exists")


def vendor_list(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendors = Vendor.objects.select_related("area").all().order_by("name")

    return render(request, "core/vendor_list.html", {
        "vendors": vendors,
    })

def vendor_detail(request, vendor_id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendor = get_object_or_404(Vendor.objects.select_related("area"), id=vendor_id)

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    ).order_by("date")

    data = []
    balance = Decimal(vendor.opening_balance or 0)

    for indent in indents:
        row = {
            "date": indent.date,
            "udayavani": 0,
            "eenadu": 0,
            "dinakaran": 0,
            "sakshi": 0,
            "business_standard": 0,
            "k_prabha": 0,
            "taranga": 0,
            "roopathara": 0,
            "tushara": 0,
            "cash": Decimal(indent.cash_collected or 0),
            "subtotal": indent.total_amount(),
            "previous_balance": balance,
            "total": Decimal("0.00"),
        }

        for item in indent.newspaper_items.all():
            key = item.newspaper.name.lower().strip().replace(" ", "_")
            if key == "business_standard" or key == "biasness_standard":
                row["business_standard"] = item.quantity
            elif key == "k_prabha" or key == "kannada_prabha":
                row["k_prabha"] = item.quantity
            elif key in row:
                row[key] = item.quantity

        for item in indent.magazine_items.all():
            key = item.magazine.name.lower().strip().replace(" ", "_")
            if key in row:
                row[key] = item.quantity

        balance = balance + row["subtotal"] - row["cash"]
        row["total"] = balance

        data.append(row)

    return render(request, "core/vendor_detail.html", {
        "vendor": vendor,
        "data": data,
        "grand_total": balance,
        "balance": balance,
    })

def vendor_ledger_page(request):
    if not request.session.get("vendor_id"):
        return redirect("vendor_login")

    vendor = get_object_or_404(Vendor, id=request.session["vendor_id"])

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    ).order_by("date")

    balance = Decimal(vendor.opening_balance or 0)
    data = []

    for indent in indents:
        subtotal = indent.total_amount()
        cash = Decimal(indent.cash_collected or 0)

        previous_balance = balance
        current_balance = previous_balance + subtotal - cash

        # paper counts
        row = {
            "date": indent.date,
            "previous_balance": previous_balance,
            "subtotal": subtotal,
            "cash": cash,
            "current_balance": current_balance,

            "udayavani": 0,
            "eenadu": 0,
            "dinakaran": 0,
            "sakshi": 0,
            "business_standard": 0,
            "k_prabha": 0,
            "taranga": 0,
            "roopathara": 0,
            "tushara": 0,
        }

        for item in indent.newspaper_items.all():
            key = paper_key(item.newspaper.name)
            if key in row:
                row[key] = item.quantity

        for item in indent.magazine_items.all():
            key = paper_key(item.magazine.name)
            if key in row:
                row[key] = item.quantity

        show = True
        if from_date and str(indent.date) < from_date:
            show = False
        if to_date and str(indent.date) > to_date:
            show = False

        if show:
            data.append(row)

        balance = current_balance

    return render(request, "core/vendor_ledger_page.html", {
        "vendor": vendor,
        "data": data,
        "from_date": from_date,
        "to_date": to_date,
    })


def executive_ledger_page(request):
    if not request.session.get("executive_id"):
        return redirect("executive_login")

    executive = get_object_or_404(
        Executive.objects.select_related("area"),
        id=request.session["executive_id"]
    )

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    vendors = Vendor.objects.filter(
        executive_mappings__executive=executive,
        executive_mappings__is_active=True,
        is_active=True
    ).distinct().order_by("name")

    data = []
    grand_total = Decimal("0.00")

    for vendor in vendors:
        all_indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
            "newspaper_items__newspaper",
            "magazine_items__magazine"
        ).order_by("date")

        filtered_indents = all_indents

        if from_date:
            filtered_indents = filtered_indents.filter(date__gte=from_date)

        if to_date:
            filtered_indents = filtered_indents.filter(date__lte=to_date)

        paper_counts = {
            "udayavani": 0,
            "eenadu": 0,
            "dinakaran": 0,
            "sakshi": 0,
            "business_standard": 0,
            "k_prabha": 0,
            "taranga": 0,
            "roopathara": 0,
            "tushara": 0,
        }

        balance = Decimal(vendor.opening_balance or 0)
        previous_balance = balance

        for indent in all_indents:
            day_subtotal = indent.total_amount()
            day_cash = Decimal(indent.cash_collected or 0)

            previous_balance = balance
            balance = balance + day_subtotal - day_cash

        present_subtotal = Decimal("0.00")
        vendor_cash = Decimal("0.00")

        for indent in filtered_indents:
            vendor_cash += Decimal(indent.cash_collected or 0)
            present_subtotal += indent.total_amount()

            for item in indent.newspaper_items.all():
                key = item.newspaper.name.lower().strip().replace(" ", "_")
                if key in paper_counts:
                    paper_counts[key] += item.quantity

            for item in indent.magazine_items.all():
                key = item.magazine.name.lower().strip().replace(" ", "_")
                if key in paper_counts:
                    paper_counts[key] += item.quantity

        data.append({
            "vendor_name": vendor.name,
            "area": vendor.area.name if vendor.area else "",

            "udayavani": paper_counts["udayavani"],
            "eenadu": paper_counts["eenadu"],
            "dinakaran": paper_counts["dinakaran"],
            "sakshi": paper_counts["sakshi"],
            "business_standard": paper_counts["business_standard"],
            "k_prabha": paper_counts["k_prabha"],
            "taranga": paper_counts["taranga"],
            "roopathara": paper_counts["roopathara"],
            "tushara": paper_counts["tushara"],

            "previous_balance": previous_balance,
            "cash": vendor_cash,
            "subtotal": present_subtotal,
            "total": balance,
        })

        grand_total += balance

    return render(request, "core/executive_ledger_page.html", {
        "executive": executive,
        "data": data,
        "from_date": from_date,
        "to_date": to_date,
        "grand_total": grand_total,
    })

def download_vendor_ledger_excel(request):
    vendor_id = request.GET.get("vendor")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    # Admin can download any vendor ledger
    if request.session.get("is_admin_logged_in"):
        if not vendor_id:
            return HttpResponse("Vendor is required")
        vendor = get_object_or_404(Vendor, id=vendor_id)

    # Vendor can download only own ledger
    elif request.session.get("vendor_id"):
        vendor = get_object_or_404(Vendor, id=request.session["vendor_id"])

    else:
        return redirect("vendor_login")

    indents = DailyIndent.objects.filter(vendor=vendor).prefetch_related(
        "newspaper_items__newspaper",
        "magazine_items__magazine"
    ).order_by("date")

    balance = Decimal(vendor.opening_balance or 0)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vendor Ledger"

    ws.append([
        "Date",
        "Vendor Name",
        "Area",
        "Udayavani",
        "Eenadu",
        "Dinakaran",
        "Sakshi",
        "Business Standard",
        "K Prabha",
        "Taranga",
        "Roopathara",
        "Tushara",
        "Previous Balance",
        "Subtotal",
        "Cash",
        "Current Balance",
    ])

    for indent in indents:
        subtotal = indent.total_amount()
        cash = Decimal(indent.cash_collected or 0)

        previous_balance = balance
        current_balance = previous_balance + subtotal - cash

        show_row = True

        if from_date and str(indent.date) < from_date:
            show_row = False

        if to_date and str(indent.date) > to_date:
            show_row = False

        papers = {
            "udayavani": 0,
            "eenadu": 0,
            "dinakaran": 0,
            "sakshi": 0,
            "business_standard": 0,
            "k_prabha": 0,
            "taranga": 0,
            "roopathara": 0,
            "tushara": 0,
        }

        for item in indent.newspaper_items.all():
            key = item.newspaper.name.lower().strip().replace(" ", "_")
            if key in papers:
                papers[key] = item.quantity

        for item in indent.magazine_items.all():
            key = item.magazine.name.lower().strip().replace(" ", "_")
            if key in papers:
                papers[key] = item.quantity

        if show_row:
            ws.append([
                str(indent.date),
                vendor.name,
                vendor.area.name if vendor.area else "",
                papers["udayavani"],
                papers["eenadu"],
                papers["dinakaran"],
                papers["sakshi"],
                papers["business_standard"],
                papers["k_prabha"],
                papers["taranga"],
                papers["roopathara"],
                papers["tushara"],
                float(previous_balance),
                float(subtotal),
                float(cash),
                float(current_balance),
            ])

        balance = current_balance

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="vendor_ledger_{vendor.name}.xlsx"'

    wb.save(response)
    return response


def map_area_magazine(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    areas = Area.objects.all().order_by("name")
    magazines = Magazine.objects.filter(is_active=True).order_by("name")

    if request.method == "POST":
        area_id = request.POST.get("area")
        selected_mags = request.POST.getlist("magazines")

        if not area_id:
            messages.error(request, "Select area")
            return redirect("map_area_magazine")

        area = get_object_or_404(Area, id=area_id)

        AreaMagazine.objects.filter(area=area).delete()

        for mag_id in selected_mags:
            mag = get_object_or_404(Magazine, id=mag_id)
            AreaMagazine.objects.create(
                area=area,
                magazine=mag,
                is_active=True
            )

        messages.success(request, "Magazines mapped successfully")
        return redirect("map_area_magazine")

    mappings = AreaMagazine.objects.select_related("area", "magazine").order_by(
        "area__name", "magazine__name"
    )

    return render(request, "core/map_area_magazine.html", {
        "areas": areas,
        "magazines": magazines,
        "mappings": mappings,
    })

def delete_area(request, id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    area = get_object_or_404(Area, id=id)
    area.delete()
    messages.success(request, "Area deleted successfully")
    return redirect("add_area")


def delete_newspaper(request, id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    newspaper = get_object_or_404(Newspaper, id=id)
    newspaper.delete()
    messages.success(request, "Newspaper deleted successfully")
    return redirect("add_newspaper")


def delete_magazine(request, id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    magazine = get_object_or_404(Magazine, id=id)
    magazine.delete()
    messages.success(request, "Magazine deleted successfully")
    return redirect("add_magazine")


def delete_vendor(request, id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    vendor = get_object_or_404(Vendor, id=id)
    vendor.delete()
    messages.success(request, "Vendor deleted successfully")
    return redirect("add_vendor")


def delete_executive(request, id):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    executive = get_object_or_404(Executive, id=id)
    executive.delete()
    messages.success(request, "Executive deleted successfully")
    return redirect("add_executive")