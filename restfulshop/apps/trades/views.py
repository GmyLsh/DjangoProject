from rest_framework import viewsets, mixins
from .models import *
from .serializer import *

# 购物车接口
class TradesCartView(viewsets.ModelViewSet):
    """
    list:
        查询所有购物车记录
    destory:
        删除某一个购物车记录
    create:
        添加购物车时，在数据库中生成购物车数据
    update:
        全部更新购物车信息
    partial_update:
        部分更新购物车信息
    """
    serializer_class = TradesCartSerializer
    lookup_field = 'goods_id'
    def get_queryset(self):
        # 获取当前用户的购物车记录
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return TradesCartListSerializer
        else:
            return TradesCartSerializer

# 订单接口
import time, random
class TradesOrderView(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # 订单列表、订单详情、取消订单、创建订单(订单不允许修改)
    serializer_class = TradesOrderSerializer
    def get_queryset(self):
        # 获取当前登录用户的所有订单
        return OrderInfo.objects.filter(user=self.request.user)
    # 处理前端生成订单的逻辑
    # 1. 后台接口要生成一个订单号，和前端传递的订单的基本信息一块保存到数据库中。
    # 2. 订单生成之后，购物车要清空。

    def get_order_sn(self):
        """
        生成订单号的函数: 日期+当前用户+随机数的形式，保证订单号的唯一性，支付宝对同一个订单号只允许支付一次，如果两个用户的订单号相同，只能有一个用户支付成功。
        :return:
        """
        order_sn = time.strftime('%Y%m%d%H%M%S') + str(self.request.user.id) + str(random.randint(100, 1000))
        return order_sn


    def perform_create(self, serializer):
        # 不能使用serializer.data，因为serializer.data必须在serializer.save()之后才能调用。
        # 如果需要在save()之前向数据字典中添加数据，一定要使用validated_data
        serializer.validated_data['order_sn'] = self.get_order_sn()
        # 保存数据之前，需要生成订单号，将这个订单号和前端传递的订单信息放在同一个字典中。
        order = serializer.save()

        # 订单数据保存成功之后，将购物车数据清空
        carts = ShoppingCart.objects.filter(user=self.request.user)
        for cart in carts:
            # 在购物车记录删除之前，应该将这个记录对应的商品保存在订单详情OrdersGoods中，这样在订单的详情页才能获取这个订单购买的所有商品。
            order_goods = OrderGoods()
            order_goods.goods = cart.goods
            order_goods.goods_num = cart.nums
            order_goods.order = order
            # 将该订单的所有商品信息保存至数据库
            order_goods.save()
            cart.delete()

from rest_framework.views import APIView
from utils.alipay import AliPay
from restfulshop import settings
from rest_framework.response import Response
from datetime import datetime
from django.shortcuts import redirect, reverse
class AliPayView(APIView):
    # 支付宝回调url的时候，view不能添加认证和权限，如果添加了，回调会出现401错误。
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # 处理支付宝回调return_url时，发送的GET请求
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value
        sign = processed_dict.pop('sign', None)
        # 然后将剩余的参数重新进行签名
        alipay = AliPay(
            appid="2016091100484002",
            app_notify_url="http://114.116.83.180:8000/trades/alipay/redirect/",
            app_private_key_path=settings.app_private_key_path,
            alipay_public_key_path=settings.alipay_public_key_path,
            debug=True,  # 默认False,
            return_url="http://114.116.83.180:8000/trades/alipay/redirect/"
        )
        result = alipay.verify(processed_dict, sign)
        if result:
            # 是支付宝回调f
            # 获取支付宝回传的订单号，利用这个订单号，修改数据库中订单的状态
            response = redirect(reverse('redirect_url'))
            response.set_cookie('nextPath', 'pay', max_age=10)
            return response
        else:
            return Response('')

    def post(self, request):
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value
        sign = processed_dict.pop('sign', None)
        # 将剩余的参数重新进行签名
        alipay = AliPay(
            appid="2016091100484002",
            app_notify_url="http://114.116.83.180:8000/trades/alipay/redirect/",
            app_private_key_path=settings.app_private_key_path,
            alipay_public_key_path=settings.alipay_public_key_path,
            debug=True,  # 默认False,
            return_url="http://114.116.83.180:8000/trades/alipay/redirect/"
        )
        result = alipay.verify(processed_dict, sign)
        if result:
            # 是支付宝回调
            # 获取支付宝回传的订单号，利用这个订单号，修改数据库中订单的状态
            order_sn = processed_dict.get('out_trade_no', None)
            order = OrderInfo.objects.filter(order_sn=order_sn).first()
            order.pay_status = processed_dict.get('trade_status')
            order.trade_no = processed_dict.get('trade_no')
            order.pay_time = datetime.now()
            order.save()
            return Response('success')
        else:
            return Response('')


