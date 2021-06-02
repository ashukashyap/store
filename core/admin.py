from django.contrib import admin

# Register your models here.
from.models import Item, OrderItem, Order,Category,Itemss,BillingAddress,Signup,Payment,Contact

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user','ordered')

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Category)
admin.site.register(Itemss)
admin.site.register(BillingAddress)
admin.site.register(Signup)
admin.site.register(Payment)
admin.site.register(Contact)