from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# router.register(r'merchandise', views.MerchandiseView, base_name='merchandise')
# router.register(r'groups', GroupViewSet)


urlpatterns = format_suffix_patterns([

    path('auth/token/', obtain_auth_token),

    path('wechat/bind/', views.BindWechatView.as_view()),

])
