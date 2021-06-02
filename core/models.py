from django.conf import settings
from django.db import models
from django.db.models.deletion import CASCADE
from django.shortcuts import render, reverse


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100)
    descripction = models.TextField()
   

    def __str__(self):
        return self.title
        

class Itemss(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField() 
    desc = models.TextField()   
    cat = models.ForeignKey(Category,on_delete=models.CASCADE)
    add_date = models.DateTimeField()
    slug = models.SlugField()
    discount_price = models.FloatField(blank=True, null=True)
    Author = models.CharField(max_length=100)
    LANGUAGE = models.CharField(max_length=100)
    


    
    def __str__(self):
        return self.title
        



    def get_absolute_url(self):
        return reverse("core:desc" , kwargs={
            'slug':self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart" , kwargs={
            'slug':self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart" , kwargs={
            'slug':self.slug
        })

    


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()

    def __str__(self):
        return self.title

    



class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Itemss, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    
    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now=True)
    ordered_date = models.DateTimeField()  
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL,blank=True,null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL,blank=True,null=True)
    

    def __str__(self):
        return self.user.username
          
      
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
     
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100) 
    zip = models.CharField(max_length=100)
    

   
    def __str__(self):
        return self.user.username
    


class Signup(models.Model):
    email = models.EmailField()
    timestemp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.email



class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone  = models.CharField(max_length=13)
    email = models.CharField(max_length=100)
    text = models.TextField()


    def __str__(self):
        return self.name
        