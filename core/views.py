from django.db import models
import stripe

from django import forms
from django.conf import settings
import secrets
from django.core import exceptions
from django.db.models import query
from django.http import request
from django.shortcuts import render,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView , DetailView,View
from .models import Item , Itemss,Category, Order, OrderItem,BillingAddress,Signup,Payment,Contact
from django.contrib import messages
from django.shortcuts import redirect,reverse
from django.utils import timezone
from.forms import checkoutForm, catForm , IteForm 



stripe.api_key = settings.STRIPE_SECRET_KEY
# stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"






# Create your views here.


class ItemDetailView(DetailView):
    model = Itemss
    template_name = "products.html" 

    def order_by(self, *args, **kwargs):
        latest = Itemss.objects.order_by('-timestamp')[0:3]
        context = {
            'latest':latest
        }
        return render(self.request,'products.html',context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")
   




def HomeView(request):
    cat = Category.objects.all()
    item = Itemss.objects.all()
    if request.method == "POST":
        email = request.POST["email"]
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    context = {
        'cats' : cat,
        'itemss' : item,
    }
    return render(request, "index.html", context)





def show_category(request,cid):
    
    cat = Category.objects.all()
    category = Category.objects.get(pk=cid)

    item = Itemss.objects.filter(cat=category)
    context = {
        'cats' : cat,
        'itemss' : item
    }
    return render(request, "index.html", context)


    

@login_required
def  add_to_cart(request,slug):
    item = get_object_or_404(Itemss,slug=slug)
    order_item,created= OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user,ordered=False,)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in tha order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"This book quantity updated")
            return redirect("core:OrderSummaryView" )
        else: 
            order.items.add(order_item)
            messages.info(request,"This book was added your Library")
            return redirect("core:OrderSummaryView")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This book was added your Library")
    return redirect("core:OrderSummaryView")


@login_required
def remove_from_cart(request,slug):
    item = get_object_or_404(Itemss,slug=slug)
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False,
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in tha order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request,"This book remove your Library")
            return redirect("core:OrderSummaryView")
        else:
            messages.info(request,"This book was not in your Library")
            return redirect("core:desc" , slug=slug)
    else:
        messages.info(request," You do not have activate order")
        return redirect("core:desc" , slug=slug)
    return redirect("core:desc" , slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Itemss, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item  quantity updated.")
            return redirect("core:OrderSummaryView")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)



class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = checkoutForm()
            context = {
                'form':form,
                'order':order
        }
            return render(self.request,'checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request,"you do not active order") 
            return redirect("core:checkout") 
      
        

    def post(self, *args, **kwargs):
        form = checkoutForm(self.request.POST or  None) 
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                state = form.cleaned_data.get('state')
                city = form.cleaned_data.get('city')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get(' same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    state = state,
                    city = city,
                    zip = zip
                )
                

                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect('core:payment' , payment_option='stripe')
                elif payment_option =='P':
                    return redirect('core:payment' , payment_option='paypal')
                else:
                    messages.warning(self.request ,'Invaild Payment option selected')    
                    return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:OrderSummaryView")
       
           
class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order':order,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
                
            }
            return render(self.request,'payment.html',context)
        else:
            messages.warning(self.request,"you have added billing address") 
            return redirect("core:checkout")    
    
    
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:

            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="INR",
                source=token,
                description="my first charge"
                
            ) 

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()      

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.save()     

            messages.success(self.request, "Your order was successful!")
            return redirect("/")  

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        
        
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

       


        
    


def product(request):
    return render(request,'product.html')    




def test(request):
    return render(request,'testimonial.html')


def sell(request):
    return render(request,'sell.html')    


@login_required
def Cate(request):
    if request.method == 'POST':
        form = catForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'Succesfully category Create')
            return redirect("/")  
    else:
        form = catForm()
    context = {
        'form':form
    }
    return render(request, 'cate.html', context)


@login_required
def add_book(request):
    if request.method == 'POST':
        form = IteForm(request.POST , files=request.FILES)
        if form.is_valid():
            form.save()
            cat = form.cleaned_data['cat']
            slug = cat.id
            messages.success(request, f'Succesfully Subject Create.')
            return redirect('/core:home/' + str(slug))
    else:
        form = IteForm(initial={'user':request.user.id,'slug':secrets.token_hex(nbytes=16)})
    context = {
        'form':form
    }
    return render(request, 'pro.html', context)


def search(request):
    query = request.GET['query']
    if len(query)>78:
        allPosts = Itemss.objects.none()
    else:
        allPoststitle = Itemss.objects.filter(title__icontains=query)
        allPostsauthor = Itemss.objects.filter(Author__icontains=query)
        allPostlanguage = Itemss.objects.filter(LANGUAGE__icontains=query)
        allPosts = allPoststitle.union(allPostsauthor,allPostlanguage)

    if allPosts.count() == 0: 
        messages.warning(request, "No search results found.please refine Your query")   
    parms = {'allPosts':allPosts , 'query':query}
    return render(request,'search.html', parms)


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        text = request.POST['text']
        if len(name)<2 or len(email)<3 or len(phone)<10 or len(text)<4 :
            messages.info(request,'Please Fill the form correctly')
        else:
            contact = Contact(name=name, email=email, phone=phone, text=text)
            contact.save()
            messages.success(request,'Your message has been sand')
      
    return render(request,'contact.html') 




  