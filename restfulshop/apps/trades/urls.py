from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('shopcarts', TradesCartView, base_name='shopcarts')
router.register('orders', TradesOrderView, base_name='orders')

urlpatterns = [
    path('', include(router.urls)),
    # 设置支付宝的回调地址
    path('alipay/redirect/', AliPayView.as_view()),
]