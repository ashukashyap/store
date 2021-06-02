from django.contrib import admin
from django.urls import path
from .views import HomeView ,product,test,contact,show_category,sell,add_book,search,Cate,ItemDetailView,add_to_cart,remove_from_cart,OrderSummaryView,remove_single_item_from_cart,CheckoutView,PaymentView



app_name = 'core'

urlpatterns = [
    path('', HomeView , name='home'),
    path('category/<int:cid>/', show_category, name='show_category'),
    path('desc/<slug>/', ItemDetailView.as_view(), name='desc'),
    path('remove_from_cart/<slug>/' , remove_from_cart, name='remove_from_cart'),
    path('add_to_cart/<slug>/' , add_to_cart, name='add_to_cart'),
    path('OrderSummaryView/' , OrderSummaryView.as_view(), name='OrderSummaryView'),
    path('remove_single_item_from_cart/<slug>/' , remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),

    path('product/', product, name='product'),
    path('test/', test, name='test'),
    path('search/', search, name='search'),
    path('contact/', contact, name='contact'),
    path('sell/', sell, name='sell'),
    path('Cate/class', Cate, name='Cate'),
    path('krijo/lende', add_book, name='add_book'),
    
    
   
   
]
