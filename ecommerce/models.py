from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField


ADDRESS_CHOICES=(
    ('B','Billing'),
    ('S','Shipping'),
    )
# Create your models here.
class Category(models.Model):
	name=models.CharField(max_length=100)
	image=models.ImageField(upload_to='images/')

	def __str__(self):
		return self.name

class Item(models.Model):
	title = models.CharField(max_length=100)
	category_name = models.ForeignKey(Category,on_delete=models.CASCADE,blank=True,null=True)
	description = models.CharField(max_length=10000)
	original_price = models.FloatField()
	discount_price = models.FloatField(blank=True,null=True)
	first_image=models.ImageField(upload_to='images/')
	second_image=models.ImageField(upload_to='images/')

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("product_detail",kwargs={'id':self.id})

	def get_add_to_cart(self):
		return reverse("add_to_cart",kwargs={'id':self.id})

	def get_remove_from_cart(self):
		return reverse("remove_from_cart",kwargs={'id':self.id})

	
			
	

class OrderItem(models.Model):
	item = models.ForeignKey(Item,on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	quantity=models.IntegerField(default=1)
	ordered=models.BooleanField(default=False)
	


	def __str__(self):
		return f"{self.quantity} of {self.item.title}"

	def get_total_item_price(self):
		return self.quantity * self.item.original_price	

	def get_total_item_discount_price(self):
		return self.quantity * self.item.discount_price	

	def get_saved_amount(self):
		return self.get_total_item_price() - self.get_total_item_discount_price()

	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_item_discount_price()
		else:
			return self.get_total_item_price()		

	

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20,blank=True,null=True)
	items=models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered=models.BooleanField(default=False)
	shipping_address = models.ForeignKey('Address',related_name='shipping_address',on_delete=models.SET_NULL,blank=True,null=True)
	billing_address = models.ForeignKey('Address',related_name='billing_address',on_delete=models.SET_NULL,blank=True,null=True)
	payment = models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
	coupen=models.ForeignKey('Coupen',on_delete=models.SET_NULL,blank=True,null=True)
	being_delivered=models.BooleanField(default=False)
	received=models.BooleanField(default=False)
	refund_requested=models.BooleanField(default=False)
	refund_granted=models.BooleanField(default=False)
	





	def __str__(self):
		return self.user.username
		
	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total=total + order_item.get_final_price()
		if self.coupen:
		    total -=self.coupen.amount
		return total 		


		


class Address(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address=models.CharField(max_length=100)
    country=CountryField(multiple=False)
    zip_code=models.CharField(max_length=100)
    addres_type=models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    default=models.BooleanField(default=False)
   
   
    def __str__(self):
        return self.user.username
        
    class Meta:
        verbose_name_plural='Addresses'
        
        
        
class Payment(models.Model):
    stripe_charge_id=models.CharField(max_length=50)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True)
    amount=models.FloatField()
    timestamp=models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.user.username
        
        
class Coupen(models.Model):
    code=models.CharField(max_length=15)
    amount=models.FloatField(blank=False)
    
    def __str__(self):
        return self.code
        
class Refund(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    reason=models.TextField()
    accepted=models.BooleanField(default=False)
    email=models.EmailField()
    
    def __str__(self):
        return f"{self.pk}"
        
        

        
        
        
