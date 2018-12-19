# 自定义过滤器，这个过滤器既能实现商品模糊搜索，又能实现价格区间的模糊搜索
from django_filters import rest_framework as filters
from .models import *

class GoodsListFilter(filters.FilterSet):
    # 该类中写你需要过滤的字段
    # field_name='name' 过滤name字段，要求是包含，也就是模糊搜索
    keyword = filters.CharFilter(field_name='name', lookup_expr='icontains', label='商品名称包含')
    # field_name='shop_price' 是作用于商品售价
    pricemin = filters.NumberFilter(field_name='shop_price', lookup_expr='gte', label='商品售价大于等于')
    pricemax = filters.NumberFilter(field_name='shop_price', lookup_expr='lte', label='商品售价小于等于')
    # 目前这个商品列表只接收以下的过滤条件：
    # keyword pricemin pricemax ordering search
    # 但是前端在请求某一个一级类目下的列表页的时候，又额外的传递了一个过滤条件top_category
    # 新增一个top_category(一级类目的ID)的过滤条件
    # 上面三个过滤条件都是依托于Goods模型中现有的一些字段进行的过滤，但是这个top_category是一级类目的ID，Goods这个模型中没有这个字段，所以不能指定field_name
    top_category = filters.NumberFilter(method='custom_top_category_filter', label='一级类目ID')

    is_hot = filters.BooleanFilter(field_name='is_hot', label='是否是热门商品')

    def custom_top_category_filter(self, *args, **kwargs):
        """
        自定义过滤字段
        :param args: 1. queryset(所有商品的集合) 2.str: top_category 3. int: 1(表示前端传递的一级类目的ID)
        :param kwargs:
        :return:
        """
        queryset = args[0].filter(category__parent_category_id=args[2])
        return queryset

    class Meta:
        # 指定过滤的模型：你需要对哪一个表的数据进行过滤
        model = Goods
        # 指定过滤字段
        # ?keyword=牛奶
        fields = ('keyword', 'pricemin', 'pricemax', 'top_category', 'is_hot')

