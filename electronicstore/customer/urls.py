from django.urls import path
from .views import (RegistrationView,
                    SignInView,
                    HomePageView,
                    update_details,
                    ViewProduct,
                    add_to_cart,
                    MyCart,
                    DeleteFromCart,
                    WriteReview,
                    place_order,
                    view_orders,
                    cancel_order,
                    add_address,
                    view_address,
                    edit_address,
                    delete_address,
                    CheckoutView,
                    summery,
                    payment)


urlpatterns=[
    path('register',RegistrationView.as_view(),name='register'),
    path('login',SignInView.as_view(),name='cust_signin'),
    path('home',HomePageView.as_view(),name='customer_home'),
    path("update",update_details,name="update"),
    path('viewproduct/<int:pk>',ViewProduct.as_view(),name='viewproduct'),
    path('addtocart/<int:pk>',add_to_cart,name='addtocart'),
    path('mycart',MyCart.as_view(),name='mycart'),
    path('removeitem/<int:pk>',DeleteFromCart.as_view(),name='deletecart'),
    path('review/<int:pk>',WriteReview.as_view(),name='review'),
    path("placeorder/<int:id>/<int:cid>", place_order, name="placeorder"),
    path("vieworders", view_orders, name="vieworders"),
    path("removeorder/<int:id>", cancel_order, name="removeorder"),
    path('add_address',add_address,name='add_address'),
    path('view_address',view_address,name='view_address'),
    path('address/change/<int:id>',edit_address,name='edit_address'),
    path('address/delete/<int:id>',delete_address,name='delete_address'),
    path("checkout", CheckoutView, name="checkout"),
    path('summery/<int:id>',summery,name='summery'),
    path('payment',payment,name='payment')




]
