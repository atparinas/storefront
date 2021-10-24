from django.urls import path
from rest_framework import urlpatterns
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()

# Parent Router
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')

# basename will let the route to be called product-review-list or product-review-detail
products_router.register('reviews', views.ReviewViewSet, basename='product-reivews') 

# router = SimpleRouter()
# router.register('products', views.ProductViewSet)
# router.register('collections', views.CollectionViewSet)


urlpatterns = router.urls + products_router.urls

#URLConf
# urlpatterns = [
#     # path('products/', views.ProductList.as_view()),
#     # path('products/<int:pk>', views.ProductDetail.as_view()),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>', views.CollectionDetail.as_view()),

# ]
