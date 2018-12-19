"""restfulshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
import xadmin
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.documentation import include_docs_urls
from django.views.generic import TemplateView
urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('users/', include('users.urls')),
    path('goods/', include('goods.urls')),
    path('trades/', include('trades.urls')),
    re_path('^media/(.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # 内置的认证类TokenAuthentication使用：用户登录接口，发送POST请求
    # path('login/', views.obtain_auth_token),

    # 第三方的JWT认证的使用
    path('login/', obtain_jwt_token),

    # 用于给Browserable API 提供登录接口(调试)。
    # 这个登录接口使用的是SessionAuthentication用户认证类，需要将它添加到REST_FRAMEWORK中。
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 配置接口文档访问地址
    path('docs/', include_docs_urls(title='商城API接口文档')),
    path('', TemplateView.as_view(template_name='index.html'), name='redirect_url'),
]
