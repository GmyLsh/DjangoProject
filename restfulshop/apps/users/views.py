from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import UserInfo


class CustomAuthenticate(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserInfo.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception:
            return None


from rest_framework import mixins, viewsets
from rest_framework.response import Response
from .serializer import *
from .models import *
import random
from utils.sms import YunPianSMSService
from django.conf import settings
from rest_framework import status


class SMSCodeView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    create:
        向用户手机发送验证码接口：前端需要将用户手机号传给这个接口，这个接口会对这个手机号进行验证，如果是正确的手机号，那么这个接口回向该手机号发送一个4位的验证码，同时将手机号验证码的发送JSON结果返回
    """
    # 用户发送验证码的接口类
    serializer_class = SMSSerializer
    authentication_classes = []
    permission_classes = []

    def random_code(self):
        number = '0123456789'
        code = ''
        for x in range(4):
            code += random.choice(number)
        return code

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobile']
        # 先生成一个随机验证码
        code = self.random_code()

        # 调用云片网发送短信的接口
        sms = YunPianSMSService(API_KEY=settings.API_KEY)
        result = sms.send_sms(mobile=mobile, code=code)

        if result['code'] == 0:
            # 表示验证码发送成功，然后就可以将这个code验证码和这个手机号绑定，保存到验证码记录表中。
            code_record = SMSVerifyCode(code=code, mobile=mobile)
            code_record.save()
            headers = self.get_success_headers(serializer.data)
            data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            data = {
                'mobile': mobile,
                'code': result['code'],
                'msg': result['msg']
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler


class UserRegisterView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    # 用户注册接口类
    permission_classes = []
    authentication_classes = []
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        data = serializer.data

        # 生成JWT的Token
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        data['token'] = token

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class UserFavView(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = UserFav.objects.all()

    lookup_field = 'goods_id'

    # 判断用户的操作是post创建还是get获取所有收藏列表
    def get_serializer_class(self):
        if self.action == 'list':
            # 获取所有收藏列表
            return UserFavListSerializer
        else:
            #
            return USerFavSerializer

    def get_queryset(self):
        # 重写get_queryset函数，默认是获取所有数据，但是收藏记录只需要获取登录用户的就行了。
        return UserFav.objects.filter(user=self.request.user)


class UserInfoView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    retrieve:
        获取用户详细信息接口。
    """
    serializer_class = UserInfoSerializer
    queryset = UserInfo.objects.all()

    def get_object(self):
        """
        这个方法就是RetrieveModelMixin中获取某一个数据的方法，内置的get_object()是根据pk也就是数据的id来获取某一个数据的，但是现在获取用户详细信息没有传递这个id，所以咱们需要重写这个get_object()方法。
        :return:
        """
        return self.request.user


# 用户留言：获取所有留言、添加留言、删除留言
class UserMessageView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    list:
        获取当前用户的所有留言信息接口
    """
    serializer_class = UserMessageSerializer

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


# 用户收货地址：增删改查都包含
class UserAddressView(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    # 在添加收获地址的时候，需要判断这个收货地址是否已经添加过了，如果已经存在就不能在添加了。
    def create(self, request, *args, **kwargs):
        address = UserAddress.objects.filter(province=request.data['province'], city=request.data['city'],
                                             district=request.data['district'], address=request.data['address'],
                                             signer_name=request.data['signer_name'],
                                             signer_mobile=request.data['signer_mobile'])
        if address:
            raise serializers.ValidationError('收货地址已存在')
        # 如果不存在，开始执行数据的序列化
        # POST执行序列化：将前端传递的参数字典序列化成为ORM对象，然后存储save()。
        # GET执行序列化：将数据库查询出来的ORM对象序列化成JSON字符串，然后返回给前端。
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
