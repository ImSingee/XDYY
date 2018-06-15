from django.urls import path

from . import views

app_name = 'reserve'

urlpatterns = [
    path('bind-image/', views.WeChatImageView.as_view(), name='bind-image'),
    path('bind/', views.BindView.as_view(), name='bind'),
]
