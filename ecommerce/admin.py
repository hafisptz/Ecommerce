from django.contrib import admin
from .models import Item,OrderItem,Order,Category,Address,Payment,Coupen,Refund


def make_request_accepted(modeladmin,request,queryset):
    queryset.update(refund_requested=False,refund_granted=True)
make_request_accepted.short_description='Update refund request to  refund granted'    

def make_being_delivered(modeladmin,request,queryset):
    queryset.update(refund_granted=False,refund_requested=False,being_delivered=True)
    
make_being_delivered.short_description='Update order status to being_delivered'

def make_received(modeladmin,request,queryset):
    queryset.update(refund_requested=False,refund_granted=False,being_delivered=False,received=True)
make_received.short_description='Update order status to delivered'    
    

class OrderAdmin(admin.ModelAdmin):
    list_display=[
        'user','ordered','being_delivered','received','refund_requested','refund_granted','billing_address',
        'shipping_address',
        'payment','coupen',
        
        ]
        
        
    list_display_links =['user','billing_address',
    'shipping_address',
    'payment','coupen',]
    list_filter=['ordered',
        'being_delivered','received','refund_requested','refund_granted',
        ]
        
    search_fields=['user__username','ref_code']    
 
    actions=[make_request_accepted,make_being_delivered,make_received]       

class AddressAdmin(admin.ModelAdmin):
    
    list_display=[
        'user',
        'apartment_address',
        'street_address',
        'country',
        'zip_code',
        'addres_type',
        'default',]
        
    list_filter=['default','addres_type','country',]    
    
    search_fields=['user','apartment_address','street_address','zip_code']


# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Category)
admin.site.register(Address,AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupen)
admin.site.register(Refund)