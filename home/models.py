from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=100, null=True) 
    remaining = models.FloatField(default=0)
    default_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    date_created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class ExpensePurpose(models.Model):
    name = models.CharField(max_length=100, null=True) 
    date_created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class ShopProductPrice(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='shop_prices'
    )
    shop = models.ForeignKey(
        'Shop', 
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )

    class Meta:
        unique_together = ('product', 'shop')

    def __str__(self):
        return f"{self.product.name} price in {self.shop.name}"

class Shop(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} - {self.shop.name}"

class Expenses(models.Model):
    purpose = models.CharField(max_length=200, null=True)
    cost = models.FloatField(null=True)
    user_regst = models.CharField(max_length=200, null=True)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE,null=True)
    date_created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.purpose
    
class Sales(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    remainingJana = models.FloatField(null=True)
    received = models.FloatField(default=0, null=True)
    given = models.FloatField(default=0, null=True)
    total = models.CharField(max_length=200, null=True)
    sold = models.CharField(max_length=200, null=True)
    remaining = models.FloatField(default=0, null=True)
    spoiled = models.FloatField(default=0, null=True)
    amount = models.FloatField(default=0, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    counted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    difference = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the product's remaining value
        if self.remaining is not None:
            self.product.remaining = self.remaining
            self.product.save()

    def __str__(self):
        return self.product.name

class SupplierData(models.Model):
    name = models.CharField(max_length=200)
    liter = models.FloatField()
    receivedtime = models.DateTimeField(default=timezone.now)
    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_records'
    )

    def __str__(self):
        return f"{self.name} - {self.liter}L - {self.receivedtime}"

    class Meta:
        verbose_name = 'Supplier Data'
        verbose_name_plural = 'Supplier Data'

# Admin customization to simplify product registration
from django.contrib import admin

class ShopProductPriceInline(admin.TabularInline):
    model = ShopProductPrice
    extra = 1  # Number of empty forms to display

class ProductAdmin(admin.ModelAdmin):
    inlines = [ShopProductPriceInline]
    
    def save_model(self, request, obj, form, change):
        # Save the product first
        super().save_model(request, obj, form, change)
        
        # If this is a new product, create shop-specific prices with default price
        if not change:
            shops = Shop.objects.all()
            for shop in shops:
                ShopProductPrice.objects.create(
                    product=obj, 
                    shop=shop, 
                    price=obj.default_price
                )

class StoreTransfer(models.Model):
    received_liters = models.FloatField(null=True, blank=True, default=0)
    given_liters = models.FloatField(null=True, blank=True, default=0)
    from_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='transfers_from', null=True, blank=True)
    to_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='transfers_to', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create_daily_record(cls, user, from_shop=None, to_shop=None):
        today = timezone.now().date()
        
        # Try to find existing record for today with matching shops
        filters = {
            'date_created__date': today,
            'user': user
        }
        if from_shop:
            filters['from_shop'] = from_shop
        if to_shop:
            filters['to_shop'] = to_shop

        record = cls.objects.filter(**filters).first()
        
        if not record:
            record = cls.objects.create(
                user=user,
                from_shop=from_shop,
                to_shop=to_shop,
                received_liters=0,
                given_liters=0
            )
        
        return record

    def __str__(self):
        return f"Transfer from {self.from_shop} to {self.to_shop} on {self.date_created.date()}"
