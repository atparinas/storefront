from django.urls import path
from rest_framework import urlpatterns
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()

# Parent Router
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
# basename will let the route to be called product-review-list or product-review-detail
products_router.register('reviews', views.ReviewViewSet, basename='product-reivews') 

# (base route, prefix, lookup) lookup will prefix the pk cart_pk
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls

