from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease-cart-item/<int:food_id>/', views.decrease_cart_item, name='decrease_cart_item'),
    path('cart/', views.view_cart, name='view_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('update-cart-quantity/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('delete-cart-item/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('create-stripe-session/', views.create_stripe_session, name='create_stripe_session'),
    path('address/', views.address, name='address'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('dummy-payment/', views.dummy_payment, name='dummy_payment'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/cart/', views.api_get_cart, name='api_get_cart'),
    path('cart/api/', views.api_get_cart, name='api_get_cart_alt'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register_view, name='register_view'),
    path('logout/', views.logout_view, name='logout_view'),
]