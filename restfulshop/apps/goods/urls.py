from django.urls import path, include
from .views import *

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# 商品类别接口
router.register(r'categorys', GoodsCategoryView, base_name='categorys')
# 商品列表接口
router.register(r'', GoodsListView, base_name='list')



urlpatterns = [
    path('', include(router.urls)),
]
