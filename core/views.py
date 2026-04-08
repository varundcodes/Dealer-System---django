from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Area, Vendor, Executive, Newspaper, Magazine, DailyIndent


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

    indents = DailyIndent.objects.select_related("vendor").all().order_by("-date")

    return render(request, "core/admin_indent.html", {
        "indents": indents
    })


def payment_history(request):
    if not request.session.get("is_admin_logged_in"):
        return redirect("admin_login")

    return render(request, "core/payment_history.html")