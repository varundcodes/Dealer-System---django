from decimal import Decimal
from django.db import models
from django.utils import timezone


class Area(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Newspaper(models.Model):
    name = models.CharField(max_length=100, unique=True)
    weekday_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    weekend_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Magazine(models.Model):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TYPE_CHOICES = [
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
    ]

    name = models.CharField(max_length=100, unique=True)
    magazine_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.magazine_type})"


class AreaNewspaper(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="area_newspapers")
    newspaper = models.ForeignKey(Newspaper, on_delete=models.CASCADE, related_name="newspaper_areas")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("area", "newspaper")

    def __str__(self):
        return f"{self.area.name} - {self.newspaper.name}"


class AreaMagazine(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="area_magazines")
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE, related_name="magazine_areas")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("area", "magazine")

    def __str__(self):
        return f"{self.area.name} - {self.magazine.name}"


class Executive(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100, default="demo@123")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="executives")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100, default="demo@123")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="vendors")
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def current_balance(self):
        balance = Decimal(self.opening_balance)

        headers = self.indents.all().prefetch_related("newspaper_items", "magazine_items")
        for indent in headers:
            balance += indent.total_amount()

        for payment in self.payments.all():
            balance -= payment.amount

        return balance


class VendorNewspaper(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="vendor_newspapers")
    newspaper = models.ForeignKey(Newspaper, on_delete=models.CASCADE, related_name="newspaper_vendors")
    is_active = models.BooleanField(default=True)
    stopped_from = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("vendor", "newspaper")

    def __str__(self):
        return f"{self.vendor.name} - {self.newspaper.name}"


class VendorMagazine(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="vendor_magazines")
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE, related_name="magazine_vendors")
    is_active = models.BooleanField(default=True)
    stopped_from = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("vendor", "magazine")

    def __str__(self):
        return f"{self.vendor.name} - {self.magazine.name}"


class DailyIndent(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="indents")
    date = models.DateField(default=timezone.now)
    
    area = models.ForeignKey(
    Area,
    on_delete=models.CASCADE,
    related_name="indents",
    null=True,
    blank=True
    )
    executive = models.ForeignKey(
        Executive,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_indents"
    )
    checked_by_admin = models.BooleanField(default=False)
    admin_note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("vendor", "date")
        ordering = ["-date", "vendor__name"]

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"

    def total_amount(self):
        total = Decimal("0.00")
        for item in self.newspaper_items.all():
            total += item.line_amount()
        for item in self.magazine_items.all():
            total += item.line_amount()
        return total


class DailyIndentNewspaperItem(models.Model):
    daily_indent = models.ForeignKey(
        DailyIndent,
        on_delete=models.CASCADE,
        related_name="newspaper_items"
    )
    newspaper = models.ForeignKey(Newspaper, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    returned_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("daily_indent", "newspaper")

    def net_quantity(self):
        return max(self.quantity - self.returned_quantity, 0)

    def line_amount(self):
        day_number = self.daily_indent.date.weekday()  # 0 Monday ... 6 Sunday
        price = self.newspaper.weekend_price if day_number in [5, 6] else self.newspaper.weekday_price
        return Decimal(self.net_quantity()) * Decimal(price)

    def __str__(self):
        return f"{self.daily_indent.vendor.name} - {self.newspaper.name}"


class DailyIndentMagazineItem(models.Model):
    daily_indent = models.ForeignKey(
        DailyIndent,
        on_delete=models.CASCADE,
        related_name="magazine_items"
    )
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    returned_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("daily_indent", "magazine")

    def net_quantity(self):
        return max(self.quantity - self.returned_quantity, 0)

    def line_amount(self):
        return Decimal(self.net_quantity()) * Decimal(self.magazine.price)

    def __str__(self):
        return f"{self.daily_indent.vendor.name} - {self.magazine.name}"


class VendorPayment(models.Model):
    PENDING = "pending"
    CHECKED = "checked"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CHECKED, "Checked"),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    screenshot = models.ImageField(upload_to="payment_screenshots/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.vendor.name} - {self.amount} - {self.status}"