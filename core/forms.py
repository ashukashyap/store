
from django import forms
from .models import Category, Itemss

PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('P','PayPal')
    
)

class checkoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'1234 Main st'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder':'Apartment or suite'}))
    state = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Enter state'}))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Enter City'}))
    zip = forms.CharField()
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect ,choices=PAYMENT_CHOICES)



class catForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        help_texts = {
            'title': 'Add Title',
            'descripction':'Write The Book Decripection',
            
        }



class IteForm(forms.ModelForm):
    class Meta:
        model = Itemss
        fields = ['title','price', 'desc', 'cat','image','slug','discount_price','Author','LANGUAGE' ]
        help_texts = {
            'title': 'Subject Title',
            'price':'Write the Subject Description',
            'cat':'Write the Category',
            'image':'Add book Image',
            'desc' : 'Write The Book Decripection',
            'discount_price' : 'Add Discount Price ',
            'Author' : 'Book Author',
            'LANGUAGE' : 'book Language'
            
        }
        labels = {
            'title':'Title'
        }
        widgets = {'user': forms.HiddenInput(), 'slug': forms.HiddenInput()}