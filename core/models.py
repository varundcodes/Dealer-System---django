from decimal import Decimal
from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Executive(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100, default="demo")
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100, default="demo")
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class NewspaperPrice(models.Model):
    name = models.CharField(max_length=100, unique=True)
    weekday_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    weekend_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MagazinePrice(models.Model):
    CATEGORY_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class DailyIndent(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="indents")
    date = models.DateField()

    # issued newspapers
    udayavani = models.PositiveIntegerField(default=0)
    enadu = models.PositiveIntegerField(default=0)
    dnk = models.PositiveIntegerField(default=0)
    sakshi = models.PositiveIntegerField(default=0)
    b_standard = models.PositiveIntegerField(default=0)
    k_prabha = models.PositiveIntegerField(default=0)
    sk = models.PositiveIntegerField(default=0)

    # issued magazines
    tharanga = models.PositiveIntegerField(default=0)
    karma_veera = models.PositiveIntegerField(default=0)
    tushara = models.PositiveIntegerField(default=0)
    roopathara = models.PositiveIntegerField(default=0)

    # returned newspapers
    returned_udayavani = models.PositiveIntegerField(default=0)
    returned_enadu = models.PositiveIntegerField(default=0)
    returned_dnk = models.PositiveIntegerField(default=0)
    returned_sakshi = models.PositiveIntegerField(default=0)
    returned_b_standard = models.PositiveIntegerField(default=0)
    returned_k_prabha = models.PositiveIntegerField(default=0)
    returned_sk = models.PositiveIntegerField(default=0)

    # returned magazines
    returned_tharanga = models.PositiveIntegerField(default=0)
    returned_karma_veera = models.PositiveIntegerField(default=0)
    returned_tushara = models.PositiveIntegerField(default=0)
    returned_roopathara = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("vendor", "date")
        ordering = ["-date", "vendor__name"]

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"

    def calculate_amount(self):
        is_weekend = self.date.weekday() >= 5
        total = Decimal("0.00")

        newspaper_map = {
            "Udayavani": (self.udayavani, self.returned_udayavani),
            "Enadu": (self.enadu, self.returned_enadu),
            "DNK": (self.dnk, self.returned_dnk),
            "Sakshi": (self.sakshi, self.returned_sakshi),
            "B Standard": (self.b_standard, self.returned_b_standard),
            "K Prabha": (self.k_prabha, self.returned_k_prabha),
            "SK": (self.sk, self.returned_sk),
        }

        for name, (qty, ret) in newspaper_map.items():
            net = max(qty - ret, 0)
            if net > 0:
                paper = NewspaperPrice.objects.filter(name=name, is_active=True).first()
                if paper:
                    price = paper.weekend_price if is_weekend else paper.weekday_price
                    total += Decimal(net) * Decimal(price)

        magazine_map = {
            "Tharanga": (self.tharanga, self.returned_tharanga),
            "Karma Veera": (self.karma_veera, self.returned_karma_veera),
            "Tushara": (self.tushara, self.returned_tushara),
            "Roopathara": (self.roopathara, self.returned_roopathara),
        }

        for name, (qty, ret) in magazine_map.items():
            net = max(qty - ret, 0)
            if net > 0:
                mag = MagazinePrice.objects.filter(name=name, is_active=True).first()
                if mag:
                    total += Decimal(net) * Decimal(mag.price)

        return total


class VendorPayment(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True, null=True)
    screenshot = models.ImageField(upload_to="payment_screenshots/", blank=True, null=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.vendor.name} - {self.amount} - {self.date}"