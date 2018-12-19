import os
import django

# 获取当前文件所在目录
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restfulshop.settings')
django.setup()

# 引入Model的代码一定要放在django.setup()之后，否则会出错。
from goods.models import GoodsCategory
from utils.data.category_data import row_data

for level_one in row_data:
    l1 = GoodsCategory()
    l1.code = level_one["code"]
    l1.name = level_one["name"]
    l1.category_type = 1
    l1.save()

    for level_two in level_one["sub_categorys"]:
        l2 = GoodsCategory()
        l2.code = level_two["code"]
        l2.name = level_two["name"]
        l2.category_type = 2
        l2.parent_category = l1
        l2.save()

        for level_three in level_two["sub_categorys"]:
            l3 = GoodsCategory()
            l3.code = level_three["code"]
            l3.name = level_three["name"]
            l3.category_type = 3
            l3.parent_category = l2
            l3.save()

