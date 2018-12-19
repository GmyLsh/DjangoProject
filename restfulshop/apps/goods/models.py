from django.db import models
from DjangoUeditor.models import UEditorField

# g1 = GoodsCategory(name='生鲜食品', id=1, category_type=1,parent_category=None)
# g2 = GoodsCategory(name='饼干', id=2, category_type=2,parent_category=1)
# g2 = GoodsCategory(name='烧饼', id=3, category_type=2,parent_category=1)
# g3 = GoodsCategory(name='郑州烧饼', id=4, category_type=3,parent_category=3)
#
# g3 = GoodsCategory(name='生猛海鲜', id=5, category_type=1,parent_category=None)
# g2 = GoodsCategory(name='生蚝', id=6, category_type=2,parent_category=4)
# g2 = GoodsCategory(name='海带', id=7, category_type=2,parent_category=4)

class GoodsCategory(models.Model):
    """
    商品类别：
        一级目录 生鲜食品
        二级目录 饼干
        三级目录

    """
    # help_text='类别名'：这个参数是设置API接口文档中表示该字段的中文含义的。
    name = models.CharField(max_length=30, verbose_name='类别名', help_text='类别名', default='')
    code = models.CharField(max_length=30, verbose_name='类别编号', help_text='类别编号', default='')
    desc = models.TextField(verbose_name='类别描述', help_text='类别描述', default='', null=True, blank=True)
    # category_type用于表明当前的分类属于哪一个级别的分类。
    category_type = models.IntegerField(choices=((1,'一级类录'), (2,'二级类录'), (3,'三级类录')), verbose_name='类目级别', help_text='类目级别')
    # parent_category：指定当前类别所属的父类类别是谁，比如精品肉类的父级类别是什么等。如果当前类别是一级分类，那么这个字段就是None了，一级分类没有父级类别。所以一定要设置null=True, blank=True
    parent_category = models.ForeignKey("self", null=True, blank=True, verbose_name='父类目录', related_name='sub_cat', on_delete=models.CASCADE)

    # 首页左侧是所有类别，但是在导航条上也展示了部分类别，所以设计了一个字段表示是否要展示所有分类，如果不是导航分类就展示全部，如果是导航分类，就展示部分数据。
    is_tab = models.BooleanField(default=False, verbose_name='导航分类', help_text='导航分类')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间', help_text='添加时间')

    class Meta:
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsCategoryBrand(models.Model):
    """
    一级分类对应的推荐品牌信息
    """
    category = models.ForeignKey(GoodsCategory, null=True, blank=True, verbose_name="商品类目", on_delete=models.CASCADE, help_text='推荐品牌所属类别id')
    name = models.CharField(max_length=30, verbose_name='品牌名', help_text='推荐品牌名称', default='')
    desc = models.TextField(verbose_name='推荐品牌描述', help_text='推荐品牌描述', default='')
    image = models.ImageField(upload_to='brands/images', help_text='推荐品牌图片')
    add_time = models.DateTimeField(auto_now_add=True, help_text='推荐品牌添加时间')

    class Meta:
        verbose_name = '品牌名'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Goods(models.Model):
    """
    商品
    """
    category = models.ForeignKey(GoodsCategory, verbose_name="商品类目", on_delete=models.CASCADE, help_text='商品所属类别id', null=True)
    goods_sn = models.CharField(max_length=50, default="", verbose_name="商品唯一货号", help_text='商品唯一货号')
    name = models.CharField(max_length=100, verbose_name="商品名", help_text='商品名')
    click_num = models.IntegerField(default=0, verbose_name="商品点击数", help_text='商品点击数')
    sold_num = models.IntegerField(default=0, verbose_name="商品销售量", help_text='商品销售量')
    fav_num = models.IntegerField(default=0, verbose_name="商品收藏数", help_text='商品收藏数')
    goods_num = models.IntegerField(default=0, verbose_name="商品库存数", help_text='商品库存数')
    market_price = models.FloatField(default=0, verbose_name="商品市场价格", help_text='商品市场价格')
    shop_price = models.FloatField(default=0, verbose_name="商品本店价格", help_text='商品本店价格')
    goods_brief = models.TextField(max_length=500, verbose_name="商品简短描述", help_text='商品简短描述')
    goods_desc = UEditorField(verbose_name=u"商品详情内容", imagePath="goods/images/", width=700, height=300, filePath="goods/files/", default='', help_text='商品详情内容')
    # 在商品详情页有一个是否承担运费的提示信息。
    ship_free = models.BooleanField(default=True, verbose_name="是否承担运费", help_text='是否承担运费')
    goods_front_image = models.ImageField(upload_to="goods/images/", null=True, blank=True, verbose_name="商品封面图", help_text='商品封面图')
    is_new = models.BooleanField(default=False, verbose_name="商品是否新品", help_text='商品是否新品')
    is_hot = models.BooleanField(default=False, verbose_name="商品是否热销", help_text='商品是否热销')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="商品添加时间", help_text='商品添加时间')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsImage(models.Model):
    """
    在商品详情页，构成商品和轮播图之间的一对多的关系。
    """
    goods = models.ForeignKey(Goods, verbose_name="商品", related_name="images", on_delete=models.CASCADE, help_text="轮播图所属商品ID", null=True)
    image = models.ImageField(upload_to="", verbose_name="图片", null=True, blank=True, help_text="轮播图图片")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间", help_text="轮播图添加时间")

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


class GoodsBanner(models.Model):
    """
    首页展示的轮播图图片model。点击轮播图图片可以直接跳转到商品详情页。
    """
    goods = models.ForeignKey(Goods, verbose_name="商品", on_delete=models.CASCADE, help_text="轮播图片所属商品ID", null=True)
    image = models.ImageField(upload_to='banner', verbose_name="轮播图图片", help_text="轮播图图片")
    index = models.IntegerField(default=0, verbose_name="轮播图播放顺序", help_text="轮播图播放顺序")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间", help_text="轮播图片添加时间")

    class Meta:
        verbose_name = '轮播商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name

