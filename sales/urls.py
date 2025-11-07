from django.urls import path
from . import views

urlpatterns = [
    path("", views.pos_home, name="pos_home"),
    path("search/", views.pos_search, name="pos_search"),
    path("cart/", views.pos_cart, name="pos_cart"),
    path("add/", views.pos_add, name="pos_add"),
    path("inc/", views.pos_inc, name="pos_inc"),
    path("dec/", views.pos_dec, name="pos_dec"),
    path("remove/", views.pos_remove, name="pos_remove"),
    path("clear/", views.pos_clear, name="pos_clear"),
    path("checkout/", views.pos_checkout, name="pos_checkout"),

    # история и чек
    path("history/", views.sales_history, name="sales_history"),
    path("receipt/<int:sale_id>/", views.sale_receipt, name="sale_receipt"),
]