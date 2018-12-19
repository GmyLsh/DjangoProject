import xadmin
from xadmin import views
from .models import *


class UserFavAdmin(object):
    list_display = ['user', 'goods', "add_time"]


class UserLeavingMessageAdmin(object):
    list_display = ['user', 'message_type', "message", "add_time"]


class UserAddressAdmin(object):
    list_display = ["signer_name", "signer_mobile", "district", "address"]


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

# 是一个xadmin的固定用法，主要是对xamdin后台进行全局配置
class GlobalSettings(object):
    site_title = "生鲜后台"
    site_footer = "mxshop"


class VerifyCodeAdmin(object):
    list_display = ['code', 'mobile', "add_time"]


xadmin.site.register(UserFav, UserFavAdmin)
xadmin.site.register(UserAddress, UserAddressAdmin)
xadmin.site.register(UserLeavingMessage, UserLeavingMessageAdmin)
xadmin.site.register(SMSVerifyCode, VerifyCodeAdmin)
# 下面两个是固定的配置
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
