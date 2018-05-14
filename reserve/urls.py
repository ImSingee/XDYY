from django.urls import path

from .views import UserAuthView, ReserveTypeChooseView, ReserveTypeConfirmView, ReserveTypeDataGetView, \
    ReserveeSelectView, ReserveTimeSelectView, ReserveTimeGetView, NewReserveDoneView, MyReserveView, ReserveMeView, \
    ConfirmReserveView, ReserveeSettingsView

app_name = 'reserve'

urlpatterns = [
    path('user_auth/', UserAuthView.as_view(), name='user_auth'),
    path('reserve_type_choose/<key>/', ReserveTypeChooseView.as_view(), name='reserve_type_choose'),
    path('reserve_type_confirm/<key>/', ReserveTypeConfirmView.as_view(), name='reserve_type_confirm'),
    path('reservee_select/<key>/', ReserveeSelectView.as_view(), name='reservee_select'),
    path('reserve_time_select/<key>/', ReserveTimeSelectView.as_view(), name='reserve_time_select'),
    path('new_reserve_done/<key>/', NewReserveDoneView.as_view(), name='new_reserve_done'),

    path('my_reserve/<type>/', MyReserveView.as_view(), name='my_reserve'),

    path('reserve_me/<type>/', ReserveMeView.as_view(), name='reserve_me'),
    path('confirm_reserve/', ConfirmReserveView.as_view(), name='confirm_reserve'),
    path('reservee_settings/', ReserveeSettingsView.as_view(), name='reservee_settings'),



    path('reserve_type_data_get/<key>/', ReserveTypeDataGetView.as_view(), name='reserve_type_data_get'),
    path('reserve_time_get_view/<key>/', ReserveTimeGetView.as_view(), name='reserve_time_get_view'),
]
