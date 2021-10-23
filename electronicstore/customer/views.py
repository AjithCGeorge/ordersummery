from django.shortcuts import render, redirect,reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from .forms import RegistrationForm,LoginForm,UpdateForm,ReviewForm,PlaceOrderForm,AddressForm
    # ,UserAddressForm
from .models import Cart,Review,Orders,Address
from seller.models import Products
from .decorators import signin_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, View

class RegistrationView(TemplateView):
    form_class = RegistrationForm
    template_name = "registration.html"
    model = User
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cust_signin")


class SignInView(TemplateView):
    template_name = "login.html"
    form_class = LoginForm
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("customer_home")
            else:
                self.context["form"] = form
                return render(request, self.template_name, self.context)


@method_decorator(signin_required, name="dispatch")
class HomePageView(TemplateView):
    template_name = 'homepage.html'
    context={}
    def get(self, request, *args, **kwargs):
        products = Products.objects.all()
        self.context['products']=products
        return render(request, self.template_name,self.context)

@signin_required
def signout(request):
    logout(request)
    return redirect("cust_signin")


@signin_required
def update_details(request):
    # detail=Userdetails.objects.get()
    form = UpdateForm()
    if request.method == "GET":
        context = {"form": form}
        return render(request, "user_details.html", context)
    elif request.method == "POST":
        form = UpdateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("customer_home")
        else:
            context = {"form": form}
            return render(request, "user_details.html", context)


class ViewProduct(TemplateView):
    template_name = 'productdetail.html'
    context = {}

    def get(self, request, *args, **kwargs):
        id = kwargs['pk']
        product = Products.objects.get(id=id)
        reviews = Review.objects.filter(product=product)
        self.context['product'] = product
        self.context['reviews'] = reviews
        return render(request, self.template_name, self.context)


def add_to_cart(request, *args, **kwargs):
    id = kwargs['pk']
    product = Products.objects.get(id=id)
    cart = Cart(product=product, user=request.user)
    cart.save()
    return redirect('mycart')


class MyCart(TemplateView):
    template_name = 'cart.html'
    context = {}

    def get(self, request, *args, **kwargs):
        cart_products = Cart.objects.filter(user=request.user, status='ordernotplaced')
        self.context['cart_products'] = cart_products
        return render(request, self.template_name, self.context)


class DeleteFromCart(TemplateView):
    def get(self, request, *args, **kwargs):
        id = kwargs['pk']
        cart_product = Cart.objects.get(id=id)
        cart_product.delete()
        return redirect('mycart')


class WriteReview(TemplateView):
    template_name = 'review.html'
    context = {}

    def get(self, request, *args, **kwargs):
        form = ReviewForm()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        id = kwargs['pk']
        product = Products.objects.get(id=id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data.get('review')
            new_review = Review(user=request.user, product=product, review=review)
            new_review.save()
            return redirect('viewproduct', product.id)

# def place_order(request,*args,**kwargs):
#     id=kwargs.get("id")
#     product=Products.objects.get(id=id)
#     address=Address.objects.filter(user=request.user)
#     print(address)
#     instance={
#         "product":product.product_name,
#         'address':address,
#
#     }
#     form = PlaceOrderForm(initial=instance)
#
#     context={}
#     context["form"]=form
#
#
#     if request.method=="POST":
#         cid=kwargs.get("cid")
#         # aid = kwargs.get('aid')
#         cart=Cart.objects.get(id=cid)
#         # print('Hello',request.POST.get('radioaddress'))
#
#         # form=PlaceOrderForm(request.POST,request.user)
#
#             # address= form.cleaned_data.get('address')
#         address=request.POST.get('radioaddress')
#         # address=Address.objects.get(user=request.user)
#         print(address)
#         product=product
#         order=Orders(product=product,user=request.user,seller=product.user.username,address=address)
#         print(product.user.username)
#         order.save()
#
#         cart.status="orderplaced"
#         cart.save()
#
#         return redirect("customer_home")
#
#
#     return render(request,"placeorder.html", {'address':address,'product':product,'count':[i for i in range(5)]})

def view_orders(request,*args,**kwargs):
    orders=Orders.objects.filter(user=request.user)

    context={
        "orders":orders,
    }
    return render(request,"vieworders.html",context)

def cancel_order(request,*args,**kwargs):
    id=kwargs.get("id")
    order=Orders.objects.get(id=id)
    order.status="cancelled"
    order.save()
    return redirect("vieworders")



def add_address(request):

    if request.method == 'POST':
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.user = request.user
            address_form.save()
            return redirect('mycart')
    else:
        address_form = UserAddressForm()
    return render(request,'add_address.html',{'form':address_form})

def view_address(request):

    addresses = Address.objects.filter(user=request.user)
    return render(request,'view_address.html',{'addresses':addresses})

def edit_address(request,id):

    if request.method == "POST":
        address = Address.objects.get(pk=id,user=request.user)
        address_form = UserAddressForm(instance=address,data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return redirect('view_address')
    else:
            address = Address.objects.get(pk=id, user=request.user)
            address_form = UserAddressForm(instance=address)

    return render(request,'edit_address.html',{'form':address_form})

def delete_address(request,id):

    address = Address.objects.filter(pk=id,user=request.user).delete()
    return redirect('view_address')


# ===================================================================================================================

def place_order(request,*args,**kwargs):
    id=kwargs.get("id")
    product=Products.objects.get(id=id)
    instance={
        "product":product.product_name
    }
    form=PlaceOrderForm(initial=instance)
    context={}
    context["form"]=form

    if request.method=="POST":
        cid=kwargs.get("cid")
        cart=Cart.objects.get(id=cid)

        form=PlaceOrderForm(request.POST)
        if form.is_valid():
            # address=form.cleaned_data.get("address")
            product=product
            order=Orders(product=product,user=request.user,seller=product.user.username)
            print(product.user.username)
            order.save()
            cart.status="orderplaced"
            cart.save()
            return redirect("checkout")

    return render(request,"placeorder.html",context)


# class CheckoutView(View):
#     def get(self, *args, **kwargs):
#         print(self.kwargs)
#         id = kwargs.get("cid")
#         # product = Products.objects.get(id=id)
#         form = AddressForm()
#         # order = Orders.objects.filter(user=self.request.user, status="ordered")
#         # print(len(order))
#         print('user : ', Cart.objects.get(id=id).user)
#         print('items :',Cart.objects.filter(user=Cart.objects.get(id=id).user))
#         items=Cart.objects.filter(user=Cart.objects.get(id=id).user,status="ordernotplaced")
#         cartitems=[]
#         for i in range(len(items)):
#             print('item no. {} : {}'.format(i,items[i].product_id))
#             cartitems.append(items[i])
#         print(cartitems)
#         address=Address.objects.filter(user=self.request.user)
#         print('addresses :',address)
#         context = {
#             'form': form,
#             # 'order': order
#             'address':address
#
#         }
#         return render(self.request, 'checkout.html',context)
#     def post(self, *args, **kwargs):
#         order = Orders.objects.filter(user=self.request.user, status="ordered")
#         print(order)
#         print('len of order :',len(order))
#
#         form = AddressForm(self.request.POST or None)
#         if form.is_valid():
#             street_address = form.cleaned_data.get('street_address')
#             apartment_address = form.cleaned_data.get('apartment_address')
#             country = form.cleaned_data.get('country')
#             zip = form.cleaned_data.get('zip')
#             save_info = form.cleaned_data.get('save_info')
#             use_default = form.cleaned_data.get('use_default')
#             payment_option = form.cleaned_data.get('payment_option')
#
#             address = Address(
#                 user=self.request.user,
#                 street_address=street_address,
#                 apartment_address=apartment_address,
#                 country=country,
#                 zip=zip,
#             )
#             address.save()
#             if save_info:
#                 address.default=True
#                 address.save()
#
#
#             print('address :',address)
#             order.save()
#             print(form.cleaned_data)
#             return redirect('checkout')
#         else:
#             print('form invalid')
#             return redirect('checkout')

def CheckoutView(request):
    address = Address.objects.filter(user=request.user)
    print('data :',address)

    addr=[]
    for i in address:
        data={}
        print(i.name)
        data['name']=i.name
        data['mob']=i.mob_no
        data['address']='{}, {}, {}, {}, India, {} '.format(i.house,i.street,i.town,i.state,i.pin)
        data['landmark']='{}'.format(i.landmark)
        data['id']=i.id
        addr.append(data)
    print('addresses :', addr)
    context = {
                'address':addr
            }
    if request.method == "POST":
        print(request.POST)
        x=request.POST
        new_address=Address()
        new_address.user=request.user
        new_address.name=x['name']
        new_address.mob_no=x['mob_no']
        new_address.house=x['house']
        new_address.street=x['street_address']
        new_address.town=x['town']
        new_address.state=x['state']
        new_address.pin=x['pin']
        new_address.landmark=x['landmark']
        if( Address.objects.filter(house=x['house'],pin=x['pin']).exists()):
            print('already exists')
        else:
            new_address.save()
            print(new_address.street)
            return redirect("checkout")
    return render(request, 'checkout.html', context)

def summery(request,*args,**kwargs):
    print(kwargs.get('id'))
    print(request.user)
    cart_item=Cart.objects.filter(user=request.user,status='ordernotplaced')

    for i in cart_item:
        print(Products.objects.get(id=i.product_id).id)
        order=Orders()
        if(Orders.objects.filter(product=Products.objects.get(id=i.product_id))).exists():
            print('already exists')
        else:
            order.product=Products.objects.get(id=i.product_id)
            order.user=request.user
            order.seller=Products.objects.get(id=i.product_id).user
            address=Address.objects.get(id=kwargs.get('id'))
            ad='{},{},{}, {}, {}, {}, India, {} '.format(address.name,address.mob_no,address.house,address.street,address.town,address.state,address.pin,address.landmark)
            order.address=ad
            order.save()
    data=[]
    for i in cart_item:
        content={}
        product=Products.objects.get(id=i.product_id)
        print(Products.objects.get(id=i.product_id).image.url)
        content['image']=product.image.url
        content['name']=product.product_name.capitalize()
        content['color']=product.color
        content['seller']=product.user
        content['price']=product.price
        content['offer']=product.offer
        data.append(content)

    return render(request,'order_summery.html',{'data':data})

def payment(request):
    return render(request,'payment.html')
