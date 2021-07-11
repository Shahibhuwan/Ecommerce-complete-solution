from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from .utils import password_reset_token
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *
import requests


class EcomMixin(object):
    # when this mixin is inherited then this dispatch method executed first
    def dispatch(self, request, *args, **kwargs):
#when the user is not logged in and the items are added in cart , if user logged in then the cart has customer field where current logged in customer is assighned
        cart_id =request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)








class HomeView(EcomMixin,TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get('page')
       
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context

#paginator chunks the pages with different pagenumber(containing certain object s) and gets those pages according to page number passed as arguments 

class AllProductsView(EcomMixin, TemplateView):
    template_name ="allproducts.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['allcategories'] = Category.objects.all()
        return context
    
class ProductDetailView(EcomMixin,TemplateView):
    template_name="productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        slug_url = self.kwargs['slug']   
        product =  Product.objects.get(slug = slug_url)
        product.view_count += 1
        product.save()
        context['product'] = product 
        return context
    

class AddToCartView(EcomMixin,TemplateView):
    template_name="addtocart.html"

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #get product id from requested url
        product_id = self. kwargs['pro_id']
        #get product 
        product_obj = Product.objects.get(id = product_id)

        # check if cart exist then check the product in cart whether the adding item is in cart or not if it exists then increase the quantatiy/subtotal of that product and save it in database
        # if cart exist then card_id is given else None

        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj= Cart.objects.get(id =cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            
            #item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last() # last item of this_product_in_cart , also it contain only one item so we can write last or first
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
           
           #new item added in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj,product=product_obj ,rate= product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total+= product_obj.selling_price
                cart_obj.save()
            
# new cart is created and new cart produt is created
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id']=cart_obj.id
            cartproduct =CartProduct.objects.create(cart=cart_obj,product=product_obj, rate= product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total+= product_obj.selling_price
            cart_obj.save()

            #after creating cart obj , same the cat_obj id in session so that next time when we new iteam it will added to our same existing cart

        # check if product already exist in cart

        return context




class  MyCartView(EcomMixin,TemplateView):
    template_name="mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id",None)
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
        else:
            cart=None
        context['cart']=cart

        return context
    


class ManageCartView(EcomMixin,View):

    def get(self, request, *args, **kwargs):
        cp_id= self.kwargs['cp_id']
        action = request.GET['action']
        cp_obj= CartProduct.objects.get(id= cp_id)
        cart_obj =cp_obj.cart
        # check cartobj in session and cartobje in cartproduct are same or not .if different we caannot change the cartproduct of another cart
        # cart_id = request.session.get("cart_id",None)
        # if cart_id:
        #     cart1= Cart.objects.get(id=cart_id)
        #     if cart != cart1:
        #         return redirect("ecomapp:mycart")
        #     else:
        #         return redirect("ecomapp:mycart")
        if action =='inc':
            cp_obj.quantity+=1
            cp_obj.subtotal+= cp_obj.rate
            cp_obj.save()
            cart_obj.total+=cp_obj.rate
            cart_obj.save()
            
        elif action =='dcr':
            cp_obj.quantity-=1
            cp_obj.subtotal-=cp_obj.rate
            cart_obj.total-=cp_obj.rate
            cp_obj.save()
            cart_obj.save()

            if cp_obj.quantity==0:
                cp_obj.delete()
            
                
        elif action =="rmv":
            cart_obj.total-=cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass

        return redirect("ecomapp:mycart")
#action is url param so it can obtained from requst obj



class  EmptycartView(EcomMixin,View):
    
    def get(self, request, *args,**kwargs):
    
        cart_id=request.session.get("cart_id",None)
        if cart_id:
            cart =Cart.objects.get(id=cart_id )
            cart.cartproduct_set.all().delete()
            cart.total=0
            cart.save()
        return redirect("ecomapp:mycart")

class CheckoutView(EcomMixin,CreateView):
    template_name ="checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy('ecomapp:home')
     # self is the obj of cureent view class
        # if user is logged in it return loggedin user object else it return anynomous user
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

   
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj =None
        context['cart']= cart_obj
        return context
    # form instance iss used to access the model field and assign the data which are not given by user in form
    def form_valid(self, form):
        print("hello")
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            # form.instance.payment_method="Cash On Delivery"
            pm = form.cleaned_data.get("payment_method")
            del self.request.session['cart_id']
            order =form.save()
            if pm == "Khalti":
                return redirect(reverse('ecomapp:khaltirequest') + "?o_id="+str(order.id))
            
        
        else:
            return redirect("ecomapp:home")

        return super().form_valid(form)



class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id =request.GET.get("o_id")
        order = Order.objects.get(id =o_id)
        context ={"order":order}
        return render(request, "khaltirequest.html", context)


class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        print(token, amount, o_id)

        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": "Key test_secret_key_b353851a471942288dde2a5d0082eba1"
        }

        order_obj = Order.objects.get(id=o_id)

        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            success = True
            order_obj.payment_completed = True
            order_obj.save()
        else:
            success = False
        data = {
            "success": success
        }
        return JsonResponse(data)
# payment gateway button provide diaglogboxx for login with khalti accoutn and if credentital are right(success) then it will cut the amount and return token, amount and other data in json format , after that server side verifcation is done by passing these obtained token to the khalti server 
class CustomerRegistrationView(CreateView):

    template_name="customerregistration.html"
    form_class= CustomerRegistrationForm
    success_url= reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        username= form.cleaned_data.get("username")
        password= form.cleaned_data.get("password")
        email= form.cleaned_data.get("email")
        user = User.objects.create_user(username,email,password)
        form.instance.user=user
        login(self.request,user)
        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLoginView(FormView):
    template_name= "customerlogin.html"
    form_class=CustomerLoginForm
    success_url= reverse_lazy("ecomapp:home")

# form valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)
#ovveriding success url
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


       

class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("ecomapp:home")


class AboutView(EcomMixin,TemplateView):
    template_name = "about.html"

    
class ContactView(EcomMixin,TemplateView):
    template_name = "contact.html"


class CustomerProfileView(TemplateView):
    template_name="customerprofile.html"


    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer']= customer
        orders=Order.objects.filter(cart__customer= customer).order_by("-id")
        context["orders"] =orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name="customerorderdetail.html"
    model = Order
    context_object_name ="ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists:
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)



class SearchView(TemplateView):
    template_name ="search.html"

    def get_context_data(self, **kwargs):

        context= super().get_context_data(**kwargs)
        kw =self.request.GET["keyword"]

        results= Product.objects.filter(Q(title__icontains =kw) | Q(description__icontains=kw) | Q(return_policy__icontains=kw))
        context['results']=results
        return context


class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/forgot-password/?m=s"

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/domain
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + \
            "/" + password_reset_token.make_token(user) + "/"
        
        #generate token for user 
        send_mail(
            'Password Reset Link | Django Ecommerce',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"
#order flow:dispatch, cleaned field level validation and form valid
    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("ecomapp:passworforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)



# Admin parts
class AdminLoginView(FormView):
    template_name="adminpages/adminlogin.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("ecomapp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        #user.customer or Customer.objects.filter(user=usr).exists():
        #user.admin 0r Customer.objects.filter(user=usr).exists()
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})


        return super().form_valid(form)

class AdminRequiredMixin(object):
     def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists:
            #the order of other customer is restricted, current customer and the customer of that order is checked
           pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)



class AdminHomeView(AdminRequiredMixin,TemplateView):
    template_name="adminpages/adminhome.html"

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists:
    #         #the order of other customer is restricted, current customer and the customer of that order is checked
    #        pass
    #     else:
    #         return redirect("/admin-login/")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        
        context= super().get_context_data(**kwargs)
        context['pendingorders']= Order.objects.filter(order_status="Order Received").order_by("-id")

        return context



class AdminOrderDetailView(AdminRequiredMixin,DetailView):
    template_name ="adminpages/adminorderdetail.html"
    model =Order
    context_object_name="ord_obj"


    def get_context_data(self, **kwargs):
        
        context= super().get_context_data(**kwargs)
        context['allstatus']= ORDER_STATUS
        return context




class AdminOrderListView(AdminRequiredMixin,ListView):
    template_name ="adminpages/adminorderlist.html"
    queryset=Order.objects.all().order_by("-id")
    context_object_name="allorders"    



class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("ecomapp:adminorderdetail", kwargs={"pk": order_id}))

class AdminProductListView(AdminRequiredMixin, ListView):
    template_name="adminpages/adminproductlist.html"
    queryset =Product.objects.all().order_by("-id")
    context_object_name ="allproducts"

class AdminProductCreateView(AdminRequiredMixin,CreateView):
    template_name= "adminpages/adminproductcreate.html"
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("ecomapp:adminproductlist")

    def form_valid(self, form):

        p = form.save()
        #to get multiple images we use getlist and FILES cataches the file uploaded in file field from form
        images = self.request.FILES.getlist("more_images")
        for i in images:
            ProductImage.objects.create(product=p, image=i)

        return super().form_valid(form)