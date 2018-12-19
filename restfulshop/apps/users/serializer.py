# 1. 定义序列化的类，用于验证手机号是否正确(是否是11位、是否已经被注册、是否符合手机号的规则)
import re
from datetime import datetime, timedelta
from rest_framework import serializers

from .models import *


class SMSSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=11, min_length=11, required=True, error_messages={
        'required': '手机号不能为空',
        'min_length': '手机号必须是11位',
        'max_length': '手机号必须是11位'
    }, help_text='发送短信的目标手机号')

    class Meta:
        model = SMSVerifyCode
        fields = ('mobile',)

    # 对手机号mobile这个字段进行验证
    def validate_mobile(self, mobile):
        if UserInfo.objects.filter(mobile=mobile):
            raise serializers.ValidationError('手机号已经被注册')
        mobile_re = '^1[356789]'
        if not re.match(mobile_re, mobile):
            raise serializers.ValidationError('非法手机号')
        one_minute_age_time = datetime.now() - timedelta(minutes=1)
        if SMSVerifyCode.objects.filter(add_time__gt=one_minute_age_time, mobile=mobile):
            raise serializers.ValidationError('请1分钟之后再发送验证码')

        # 将当前验证过后的手机号返回
        return mobile


from django.contrib.auth.hashers import make_password


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    注册接口序列化类，此时前端需要给这个序列化类提供三个参数：手机号、验证码、密码
    """
    # 关于验证码需要验证
    # write_only=True: 由于源码中data = serializer.data这句代码也会使用UserRegisterSerializer这个类对前端传递的字段进行序列化，设置write_only，相当于告诉serializer.data不去解析code字段了，该字段只允许保存数据库，不允许读取。
    code = serializers.CharField(max_length=4, min_length=4, required=True, error_messages={
        'required': '请输入验证码',
        'min_length': '验证码长度是4位',
        'max_length': '验证码长度是4位'
    }, label='验证码', write_only=True)
    # 手机号也需要验证：验证手机号是否已经被注册过了
    username = serializers.CharField(max_length=11, min_length=11, required=True, error_messages={
        'required': '手机号不能为空',
        'min_length': '手机号必须是11位',
        'max_length': '手机号必须是11位'
    }, label='用户名')
    # password也设置成了可以存储(写入)，但是serializer.data序列化的时候不能读取
    password = serializers.CharField(label='密码', write_only=True)

    def validate_username(self, username):
        # 手机号是否已经被注册
        if UserInfo.objects.filter(username=username):
            raise serializers.ValidationError('手机号已经被注册')
        # 验证成功之后的数据需要返回
        return username

    def validate_code(self, code):
        # 设置验证码的复杂验证
        # 根据手机号查询这个手机号的所有验证码，并按照时间的降序进行排列
        username = self.context['request'].data.get('username')
        code_records = SMSVerifyCode.objects.filter(mobile=username).order_by('-add_time')
        if code_records:
            # 如果存在记录，说明不是第一次发送验证码
            new_record = code_records[0]
            # 设置验证码的过期时间是20分钟，如果最新的验证码的发送时间在20分钟以内，就可以使用最新的验证码进行登录，如果超出20分钟，验证码失效；
            minute_ago_time = datetime.now() - timedelta(minutes=20)
            if new_record.add_time < minute_ago_time:
                # 最新验证码发送时间 < 20分钟之前的时间
                raise serializers.ValidationError('验证码已过期')
            if new_record.code != code:
                # 需要将之前的验证码删除(只保留最新的验证码)
                if len(code_records) > 1:
                    for code in code_records[1:]:
                        code.delete()
                raise serializers.ValidationError('验证码已失效')
        else:
            # 该手机号发送验证码的记录不存在，说明验证码是错误的
            raise serializers.ValidationError('验证码错误')

        return code

    def validate(self, attrs):
        # 所有的字段验证成功(内置的验证、自定义validate_code)之后，都会执行这个函数。
        del attrs['code']
        return attrs

    def create(self, validated_data):
        """
        这个create是serializer类中的create方法，ModelSerializer默认已经实现了create方法，这个方法就是将数据保存到数据库中的关键方法。但是默认的是前端传过来什么数据就保存什么数据，由于需要将密码的保存设置为加密存储，所以要重写这个函数。
        :param validated_data:
        :return:
        """
        user = UserInfo.objects.create(username=validated_data['username'], mobile=validated_data['username'])
        user.password = make_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = UserInfo
        fields = ('username', 'code', 'password')


from goods.serializer import GoodsModelSerializer


class UserFavListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    goods = GoodsModelSerializer()

    class Meta:
        model = UserFav
        fields = ('user', 'goods', 'id')
        validators = [
            # 需要保证user_id和goods_id组合起来，在收藏记录表中是唯一的。
            # 联合主键(收藏、点赞)
            serializers.UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message='商品已被收藏',
            )
        ]


class USerFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserFav
        fields = ('user', 'goods', 'id')
        validators = [
            # 需要保证user_id和goods_id组合起来，在收藏记录表中是唯一的。
            # 联合主键(收藏、点赞)
            serializers.UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message='商品已被收藏',
            )
        ]


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('username', 'birthday', 'gender', 'mobile', 'email')


class UserMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = UserLeavingMessage
        # 提交留言之后，将留言的id也返回给前端，因为前端需要这个id进行删除。
        fields = ('user', 'message_type', 'subject', 'message', 'file', 'id', 'add_time')


class UserAddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = UserAddress
        # 需要序列化id，因为前端需要这个id删除收货地址。
        fields = ('user', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'add_time', 'id')
