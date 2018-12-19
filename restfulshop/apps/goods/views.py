from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializer import *


class GoodsListPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'size'
    page_query_param = 'page'
    max_page_size = 12

from django_filters.rest_framework import DjangoFilterBackend
from .filter import GoodsListFilter
from rest_framework import filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class GoodsListView(mixins.ListModelMixin, mixins.RetrieveModelMixin,  viewsets.GenericViewSet):
    """
        商品列list:表页接口：该接口默认获取第一页的12条数据，并且支持过滤参数；
    retrieve:
        商品详情数据接口：需要传递商品ID；
    """
    pagination_class = GoodsListPagination
    queryset = Goods.objects.all()
    authentication_classes = []
    permission_classes = []

    serializer_class = GoodsModelSerializer
    # 设置过滤类
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)

    filterset_class = GoodsListFilter

    # 配置SearchFilter，这个类默认就是模糊搜索。
    search_fields = ('name', 'goods_brief')

    # OrdingFilter()用来做排序的类
    ordering_fields = ('sold_num', 'shop_price', 'add_time')
    # 如果前端没有传?ording参数，指定一个默认的排序方式
    ordering = ('-add_time', )


# 设计商品类别接口：
# 1. 导航条上以及全局商品搜索使用同一个接口：这两块内容都需要返回商品的所有类别数据(一级、二级、三级)；
# 2. 如果访问的是某一个一级类别下的数据：只需要返回二级类别和三级类别。

from rest_framework_extensions.cache.mixins import CacheResponseMixin


class GoodsCategoryView(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    所有商品类别接口
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = GoodsCategorySerializer
    authentication_classes = []
    permission_classes = []

