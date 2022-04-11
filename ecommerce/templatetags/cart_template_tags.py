from django import template
from ecommerce.models import Order


register = template.Library() 

@register.filter
def cart_item_count(user):
	if user.is_authenticated:
	    
		if Order.objects.filter(user=user,ordered=False):
		    qs=Order.objects.filter(user=user,ordered=False)
		    return qs[0].items.count()

	return 0	 