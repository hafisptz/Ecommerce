def checkout(request):
    if request.method == 'POST':
        form=CheckoutForm(request.POST or None)
	   try:
	       order=Order.objects.get(user=request.user,ordered=False)
		   if form.is_valid():
		      use_default_shipping_address=form.cleaned_data.get('use_default_shipping')
		      if use_default_shipping_address:
		        print("using default shipping address")
		           address_qs=Address.objects.filter(user=request.user,addres_type='S',default=True)
		           if address_qs.exists():
		               shipping_address=address_qs[0]
		           else:
		               messages.info(request,"No default shipping address available")
		               return redirect('checkout')
		                
		       else:
		           print("User entering new shipping address")
		           shipping_address1=form.cleaned_data.get('shipping_address')
		           shipping_address2=form.cleaned_data.get('shipping_address2')
			       shipping_country=form.cleaned_data.get('shipping_country')
			       shipping_zip_code=form.cleaned_data.get('zip_code')
			       if is_valid_form([shipping_address1,shipping_country,shipping_zip_code]):
			          shipping_address=Address(user=request.user,street_address=shipping_address1,apartment_address=shipping_address2,country=shipping_country,zip_code=shipping_zip_code,
			          address_type='S')
			          shipping_address.save()
			          order.shipping_address=shipping_address
			          order.save()
			          set_default_shipping_address=form.cleaned_data.get('set_default_shipping')
			          if set_default_shipping_address:
			             shipping_address.default=True
			             shipping_address.save()
			    
			            
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
