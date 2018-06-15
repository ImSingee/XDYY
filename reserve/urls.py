from django.urls import path

from .views import UserAuthView, ReserveTypeChooseView, ReserveTypeConfirmView, ReserveTypeDataGetView, \
    ReserveeSelectView, ReserveTimeSelectView, ReserveTimeGetView, NewReserveDoneView, MyReserveView, ReserveMeView, \
    ConfirmReserveView, ReserveeSettingsView, CanReserveTimeSettingsView, CanReserveTimeRepeatSettingsView

app_name = 'reserve'

urlpatterns = [
    # 新预约
    path('user_auth/', UserAuthView.as_view(), name='user_auth'),
    path('reserve_type_choose/<key>/', ReserveTypeChooseView.as_view(), name='reserve_type_choose'),
    path('reserve_type_confirm/<key>/', ReserveTypeConfirmView.as_view(), name='reserve_type_confirm'),
    path('reservee_select/<key>/', ReserveeSelectView.as_view(), name='reservee_select'),
    path('reserve_time_select/<key>/', ReserveTimeSelectView.as_view(), name='reserve_time_select'),
    path('new_reserve_done/<key>/', NewReserveDoneView.as_view(), name='new_reserve_done'),

    # 我的预约
    path('my_reserve/<type>/', MyReserveView.as_view(), name='my_reserve'),

    # 预约管理
    path('reserve_me/<type>/', ReserveMeView.as_view(), name='reserve_me'),
    path('confirm_reserve/', ConfirmReserveView.as_view(), name='confirm_reserve'),  # 确认预约
    path('reservee_settings/', ReserveeSettingsView.as_view(), name='reservee_settings'),  # 预约设置
    path('can_reserve_time_settings/', CanReserveTimeSettingsView.as_view(), name='can_reserve_time_settings'),
    # 可预约时间设置
    path('can_reserve_time_repeat_settings/', CanReserveTimeRepeatSettingsView.as_view(),
         name='can_reserve_time_repeat_settings'),  # 可预约时间设置

    # 新预约（AJAX）
    path('reserve_type_data_get/<key>/', ReserveTypeDataGetView.as_view(), name='reserve_type_data_get'),
    path('reserve_time_get_view/<key>/', ReserveTimeGetView.as_view(), name='reserve_time_get_view'),
]
