import stripe
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from .models import Item,OrderItem,Order,Category,Address,Payment,Coupen,Refund
from django.http import HttpResponse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm,CoupenForm,RefundForm,SearchForm
from django.contrib.auth.models import User
from django.conf import settings
import string
import random



stripe.api_key = "sk_test_51JBd9nSH679UeII621ejfdybTMGHrTzt8XJUgAguqv3CCyaKCPpKROdNDrl9TixAwZIFzpVS8lCS22cRmNwgpLfx00vJaNwyNc"


# Create your views here.


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))
    
def is_valid_form(values):
    valid=True
    for field in values:
        if field=='':
            valid=False
    return valid
    
def home(request):
 items=Item.objects.filter(category_name=1)
 category=Category.objects.all()
 
 return render(request,'index.html',{'items':items,'category':category})

def categorwise_product(request,id):

    category=Category.objects.all()
    items=Item.objects.filter(category_name=id)
    return render(request,'index.html',{'items':items,'category':category})

def product_detail(request,id):
	item=Item.objects.get(id=id)
	return render(request,'product.html',{'item':item})




def contact(request):
	return render(request,'contact.html')

def about(request):
	return render(request,'about.html')
	


def search(request):
    if request.method=='POST':
        form=SearchForm()
        key_word=request.POST.get("key_word")
        try:
            try:
                
                category=Category.objects.get(name=key_word)
            
                print(category.id)
                if category:
            
                    return redirect("catogorywise_home",id=category.id)
            except ObjectDoesNotExist:
                pass
            item=Item.objects.get(title=key_word)
            print(item.category_name.name)
            if item:
                return redirect('catogorywise_home',id=item.category_name.id)
                
            
        except ObjectDoesNotExist:
            messages.info(request,"You entered wrong product or category items,Try another")
            return redirect('/')
        
        
    
            
        
@login_required
def order_summary(request):
	try:
		order = Order.objects.get(user=request.user, ordered =False)
		context={
		'object':order
		}
		return render(request,'order_summary.html',context)
	except ObjectDoesNotExist:
		messages.error(request,"You do not have an active order ")
		return redirect("/")	
		
		

@login_required
def add_to_cart(request,id):
	item = get_object_or_404(Item,id=id)
	order_item ,created=OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False)
	order_qs=Order.objects.filter(user=request.user,ordered=False)
	if order_qs.exists():
		order=order_qs[0]
		if order.items.filter(item__id=item.id).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request,"This item was updated successfully.")
		else:
			messages.info(request,"This item was added to your cart.")
			order.items.add(order_item)
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user,ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request,"This item was added to your cart.")
	return redirect("product_detail",id=id)




@login_required
def remove_from_cart(request,id):
	item = get_object_or_404(Item,id=id)
	order_qs=Order.objects.filter(user=request.user,ordered=False)
	if order_qs.exists():
		order=order_qs[0]
		if order.items.filter(item__id=item.id).exists():
			order_item=OrderItem.objects.filter(item=item,
				user=request.user,
				ordered=False
				)[0]
			order.items.remove(order_item)
			order_item.quantity = 1
			order_item.save()


			messages.info(request,"This item was removed from your cart.")
		else:
			messages.info(request,"This item was not in your cart.")
			return redirect("product_detail",id=id)

	else:
		messages.info(request,"You do not have any active order.")
		return redirect("product_detail",id=id)	
		
	return redirect("product_detail",id=id)
	
def checkout(request):
    if request.method == 'POST':
        form=CheckoutForm(request.POST or None)
        try:
	        order=Order.objects.get(user=request.user,ordered=False)
	        if form.is_valid():
	            use_default_shipping=form.cleaned_data.get('use_default_shipping')
	            if use_default_shipping:
	            	print("using default shipping address")
	            	address_qs=Address.objects.filter(user=request.user,addres_type='S',default=True)
	            	if address_qs.exists():
	            	    shipping_address=address_qs[0]
	            	    order.shipping_address=shipping_address
	            	    order.save()
	            	else:
		                messages.info(request,"No default shipping address available")
		                return redirect('checkout')
	            else:
		            print("User entering new shipping address")
		            shipping_address1=form.cleaned_data.get('shipping_address')
		            shipping_address2=form.cleaned_data.get('shipping_address2')
		            shipping_country=form.cleaned_data.get('shipping_country')
		            shipping_zip_code=form.cleaned_data.get('shipping_zip_code')
		            if is_valid_form([shipping_address1,shipping_country,shipping_zip_code]):
			            shipping_address=Address(user=request.user,street_address=shipping_address1,apartment_address=shipping_address2,country=shipping_country,zip_code=shipping_zip_code,
			            addres_type='S')
			            shipping_address.save()
			            order.shipping_address=shipping_address
			            order.save()
			            set_default_shipping_address=form.cleaned_data.get('set_default_shipping')
			            if set_default_shipping_address:
			                shipping_address.default=True
			                shipping_address.save() 
		            else:
			            messages.info(request,"Pls fill in the required billing address fields")
			            
			           
	            same_billing_address=form.cleaned_data.get('same_billing_address')     
	            use_default_billing=form.cleaned_data.get('use_default_billing')
	            if same_billing_address:
	                billing_address=shipping_address
	                billing_address.pk=None
	                billing_address.save()
	                billing_address.addres_type='B'
	                billing_address.save()
	                order.billing_address=billing_address
	                order.save()
	                
	            elif use_default_billing:
	            	print("using default billing address")
	            	address_qs=Address.objects.filter(user=request.user,addres_type='B',default=True)
	            	if address_qs.exists():
	            	    billing_address=address_qs[0]
	            	    order.billing_address=billing_address
	            	    order.save()
	            	else:
		                messages.info(request,"No default billing address available")
		                return redirect('checkout')
	            else:
		            print("User entering new billing address")
		            billing_address1=form.cleaned_data.get('billing_address')
		            billing_address2=form.cleaned_data.get('billing_address2')
		            billing_country=form.cleaned_data.get('billing_country')
		            billing_zip_code=form.cleaned_data.get('billing_zip_code')
		            if is_valid_form([billing_address1,billing_country,billing_zip_code]):
			            billing_address=Address(user=request.user,street_address=billing_address1,apartment_address=billing_address2,country=billing_country,zip_code=billing_zip_code,
			            addres_type='B')
			            billing_address.save()
			            order.billing_address=billing_address
			            order.save()
			            set_default_billing_address=form.cleaned_data.get('set_default_billing')
			            if set_default_billing_address:
			                billing_address.default=True
			                billing_address.save() 
		            else:
			            messages.info(request,"Pls fill in the required shipping address fields")
			            
	            payment_option=form.cleaned_data.get('payment_option')
	            if payment_option=='D':
	                return redirect("payment_option",payment_option)
	            if payment_option =='P':
	                return redirect("paypal")
	            return redirect('checkout')
	        else:
	            print("not valid")
	            print(form.cleaned_data)
	            return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warnning(request,"you do not have any active order")
            return redirect('checkout')
    else:
	    form=CheckoutForm()
	    
	    user=User.objects.get(username=request.user.username)
	    order=Order.objects.get(user=request.user,ordered=False)
	    
	    
	    context={
		'form':form,
		'user':user,
		'order':order,
		'coupenform':CoupenForm(),
		'DISPLAY_COUPEN_FORM':True,
		}
	    shipping_address_qs=Address.objects.filter(user=request.user,addres_type='S',default=True)
	    if shipping_address_qs.exists():
	        context.update({'default_shipping_address':shipping_address_qs[0]})
	    billing_address_qs=Address.objects.filter(user=request.user,addres_type='B',default=True)
	    if billing_address_qs.exists():
	        context.update({'default_billing_address':billing_address_qs[0]})     
	    return render(request,'checkout.html',context)
	


def remove_single_item_from_cart(request,id):
	item = get_object_or_404(Item,id=id)
	order_qs=Order.objects.filter(user=request.user,ordered=False)
	if order_qs.exists():
		order=order_qs[0]
		if order.items.filter(item__id=item.id).exists():
			order_item=OrderItem.objects.filter(item=item,
				user=request.user,
				ordered=False
				)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
					
				order.items.remove(order_item)	
			
			
		else:
			messages.info(request,"This item was not in your cart.")
			return redirect("product_detail",id=id)

	else:
		messages.info(request,"You do not have any active order.")
		return redirect("product_detail",id=id)	
		
	return redirect("order_summary")				


def add_to_cart1(request,id):
	item = get_object_or_404(Item,id=id)
	order_item ,created=OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False)
	order_qs=Order.objects.filter(user=request.user,ordered=False)
	if order_qs.exists():
		order=order_qs[0]
		if order.items.filter(item__id=item.id).exists():
			
				order_item.quantity += 1
				order_item.save()
			
		else:
			
			pass
	else:
		pass
		
	return redirect("order_summary")



def remove_from_cart1(request,id):
	item = get_object_or_404(Item,id=id)
	order_qs=Order.objects.filter(user=request.user,ordered=False)
	if order_qs.exists():
		order=order_qs[0]
		if order.items.filter(item__id=item.id).exists():
			order_item=OrderItem.objects.filter(item=item,
				user=request.user,
				ordered=False
				)[0]
			order.items.remove(order_item)
			order_item.quantity = 1
			order_item.save()

			
		else:
			pass
	else:
		pass
		
	return redirect("order_summary")
	
def payment(request,payment_option):
    if request.method=='POST':
        
        
        order=Order.objects.get(user=request.user,ordered=False)
        token=request.POST.get('stripeToken')
        amount=int(order.get_total()*100)
    
        
        try:
     # Use Stripe's library to make requests...
        
            
            charge=stripe.Charge.create(
                amount=amount,
                currency="INR",
                source=token)
            
            payment =Payment()
            payment.stripe_charge_id=charge['id']
            payment.user=request.user
            payment.amount=order.get_total()
            
            payment.save()
            messages.success(request,"Your order was successfull")
        
        except stripe.error.CardError as e:
            
        # Since it's a decline, stripe.error.CardError will be caught
                
            body=e.json_body
            err=body.get('error',{})
            messages.error(request,f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.error(request,"Rate limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(request,"Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.error(request,"Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
         # Network communication with Stripe failed
            messages.error(request,"Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
         # yourself an email
            messages.error(request,"Something went wrong,You were not charger,please try again")
            return redirect("/")
        except Exception as e:
        # Something else happened, completely unrelated to Stripe
            messages.error(request,"Serious error occured")
            
            
        
        
        
        
 
        order.ordered=True
        order_items=order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
        order.payment=payment
        order.ref_code=create_ref_code()
        
        order.save()
        
        return redirect ("/")


        
    else:
       
        order=Order.objects.get(user=request.user,ordered=False)
        if order.billing_address:
            context={
	            'order':order,
		        'coupenform':CoupenForm(),
		        'DISPLAY_COUPEN_FORM':False,
                    }
        
            return render(request,'stripe.html',context)
        else:
            messages.warning(request,"You have not added billing address")
            return redirect("checkout")
		

def paypal(request):
    return render(request,"paypal.html")
    
    
    

    
def add_coupen(request):
    if request.method == 'POST':
        form=CoupenForm(request.POST or None )
        if form.is_valid():
            try:
                code=form.cleaned_data.get('code')
                order=Order.objects.get(user=request.user,ordered=False)
                try:
                    coupen=Coupen.objects.get(code=code)
                    order.coupen=coupen
                    order.save()
                    messages.info(request," Coupen Successfully Added")
                    return redirect('checkout')
                except ObjectDoesNotExist:
                    messages.info(request,"Coupen does not exist,Try another")
                    return redirect("checkout")
    
                
                
            except ObjectDoesNotExist:
                messages.info(request,"You do not have an active order")
                return redirect("checkout")
    return redirect("checkout")
    
    
def Refund_request(request):
    if request.method=='POST':
        form=RefundForm(request.POST or None)
        if form.is_valid():
            ref_code=form.cleaned_data.get('ref_code')
            message=form.cleaned_data.get('message')
            email=form.cleaned_data.get('email')
            try:
                order=Order.objects.get(ref_code=ref_code)
                order.refund_requested=True
                order.save()
                
                refund=Refund()
                refund.order=order
                refund.reason=message
                refund.email=email
                refund.save()
                messages.info(request,"Your request was received")
                return redirect("refund_request")
            
            except ObjectDoesNotExist:
                messages.info(request,"This  order does not exist")
                return redirect("refund_request")
                
    else:
        form=RefundForm()
        context={
                'form':form,
            }
        return render(request,'request_refund.html',context)