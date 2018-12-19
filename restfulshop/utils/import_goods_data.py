import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restfulshop.settings')
django.setup()

from goods.models import Goods, GoodsCategory, GoodsImage
from utils.data.product_data import row_data

for goods_detail in row_data:
    goods = Goods()
    goods.name = goods_detail["name"]
    goods.market_price = float(int(goods_detail["market_price"].replace("￥", "").replace("元", "")))
    goods.shop_price = float(int(goods_detail["sale_price"].replace("￥", "").replace("元", "")))
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] is not None else ""
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail["goods_desc"] is not None else ""
    # 封面图从图片列表中取出第一张图片
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""

    category_name = goods_detail["categorys"][-1]
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        # 指定商品的类别
        goods.category = category[0]
    goods.save()

    # 配置商品的轮播图
    for goods_image in goods_detail["images"]:
        goods_image_instance = GoodsImage()
        goods_image_instance.image = goods_image
        goods_image_instance.goods = goods
        goods_image_instance.save()