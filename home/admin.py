# -*- encoding: utf-8 -*-
from django.contrib import admin

from .models import *

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at')
    search_fields = ('name', 'location')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop')
    list_filter = ('shop',)
    search_fields = ('user__username', 'shop__name')

admin.site.register(Shop, ShopAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Sales)
admin.site.register(Product)
admin.site.register(ExpensePurpose)
admin.site.register(Expenses)
admin.site.register(ShopProductPrice)
admin.site.register(SupplierData)
admin.site.register(StoreTransfer)
admin.site.register(DailyCount)
admin.site.register(Loan)
