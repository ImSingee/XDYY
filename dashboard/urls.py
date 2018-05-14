from django.urls import path

from .views import IndexView, TestView, EmptyView, IndexRView

app_name = 'dashboard'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexRView.as_view(), name='indexR'),

    path('default/', EmptyView.as_view(), name='default'),
    path('test/', TestView.as_view(), name='test')
]
