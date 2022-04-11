
from django.urls import path
from . import views



urlpatterns = [
   
    path('',views.home,name='home'),
    path('contact',views.contact,name='contact'),
    path('about',views.about,name='about'),
    path('home/<int:id>',views.categorwise_product,name='catogorywise_home'),
    path('product/<int:id>',views.product_detail,name='product_detail'),
    path('order-summary',views.order_summary,name="order_summary"),
    path('checkout',views.checkout,name='checkout'),
    path('add-to-cart/<int:id>',views.add_to_cart,name='add_to_cart'),
    path('add-coupen/',views.add_coupen,name='add_coupen'),
    path('add-to-cart1/<int:id>',views.add_to_cart1,name='add_to_cart1'),
    path('remove-from-cart/<int:id>',views.remove_from_cart,name='remove_from_cart'),
    path('remove-from-cart1/<int:id>',views.remove_from_cart1,name='remove_from_cart1'),
    path('remove-single-item/<int:id>',views.remove_single_item_from_cart,name='remove_single_item_from_cart'),
    path('payment/<str:payment_option>',views.payment,name='payment_option'),
    path('pay',views.paypal,name="pay"),
    path('refund-request',views.Refund_request,name="refund_request"),
    path('search',views.search,name='search'),


]


