from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'code', SMSCodeView, base_name='code')
router.register(r'register', UserRegisterView, base_name='register')
router.register(r'fav', UserFavView, base_name='fav')
router.register(r'messages', UserMessageView, base_name='messages')
router.register(r'address', UserAddressView, base_name='address')

urlpatterns = [
    path('', include(router.urls)),
    # 'get': 'retrieve' 'get': 'list' 获取服务器资源
    # 'patch': 'partial_update' 部分更新
    # 'put': 'update' 全部更新
    # 'post': 'create' 在服务器上创建资源
    path('info/', UserInfoView.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
]
