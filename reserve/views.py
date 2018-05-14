import json
import datetime
from django.http import HttpResponseNotFound, HttpResponseNotAllowed
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.core import signing
from django.views.generic.base import TemplateView, TemplateResponseMixin, ContextMixin, View
from django.db.models.expressions import F, Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserAuthForm, ReserveTypeChooseForm, ReserveTypeConfirmForm, ReserveeSettingsForm
from .models import ReserveType, ReserveTime, ReserveRecord, ReservePlace
from account.models import User
from main.utils import GlobalSettings


# Create your views here.

class UserAuthView(TemplateView):
    template_name = 'reserve/user_auth.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            initial = {'auth_code': request.user.userinfo.auth_code,
                       'auth_name': request.user.userinfo.auth_name}
        else:
            initial = None
        form = UserAuthForm(initial=initial)
        self.extra_context = {'form': form}

        return super().get(request, *args, **kwargs)

    def post(self, request):
        form = UserAuthForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            auth_code = cleaned_data['auth_code']
            auth_name = cleaned_data['auth_name']
            auth_user = User.objects.filter(userinfo__reserver=True, userinfo__auth_code=auth_code,
                                            userinfo__auth_name=auth_name, is_active=True)

            if len(auth_user) > 1:
                messages.warning(request, '该用户信息不唯一，继续预约可能造成信息错误，建议停止预约并联系管理员')

            auth_user = auth_user.first()
            key = signing.dumps({
                'auth_code': auth_code,
                'auth_name': auth_name,
                'auth_user': auth_user.id,
            })
            return redirect(reverse('reserve:reserve_type_choose', kwargs={'key': key}))
        else:
            return self.render_to_response({'form': form})


class ReserveTypeChooseView(TemplateView):
    template_name = 'reserve/reserve_type_choose.html'

    def get(self, request, key='', **kwargs):

        form = ReserveTypeChooseForm()
        self.extra_context = {'form': form}

        return super().get(request, **kwargs)

    def post(self, request, key):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))
        # auth_user = User.objects.get(id=obj.get('auth_user'))
        form = ReserveTypeChooseForm(request.POST)
        if form.is_valid():
            r = form.cleaned_data.get('r')  # 预约问题种类（学习/非学习）
            t = form.cleaned_data.get('t')  # 预约人员种类（学导/老师）
            obj.update({'r': r,
                        't': t, })
            key = signing.dumps(obj)
            return redirect(reverse('reserve:reserve_type_confirm', kwargs={'key': key}))

        else:
            return self.render_to_response({'form': form})


class ReserveTypeConfirmView(TemplateView):
    template_name = 'reserve/reserve_type_confirm.html'

    def get(self, request, key='', **kwargs):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))

        form = ReserveTypeConfirmForm(key_obj=obj)

        data_url = reverse('reserve:reserve_type_data_get', kwargs={'key': key})

        self.extra_context = {'form': form, 'data_url': data_url}
        return super().get(request, key=key, **kwargs)

    def post(self, request, key='', **kwargs):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))

        form = ReserveTypeConfirmForm(obj, request.POST)

        if form.is_valid():
            _type = form.cleaned_data['type']
            content = form.cleaned_data['content']
            obj.update({'type': _type, 'content': content})
            key = signing.dumps(obj)
            return redirect(reverse('reserve:reservee_select', kwargs={'key': key}))
        else:

            data_url = reverse('reserve:reserve_type_data_get', kwargs={'key': key})

            self.extra_context = {'form': form, 'data_url': data_url}
            return super().get(request, key=key, **kwargs)


class ReserveTypeDataGetView(View):

    def get(self, request, key):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            return HttpResponse('')

        form = ReserveTypeConfirmForm(key_obj=obj)

        types = [{'id': x[0], 'subject': x[1]} for x in form.fields['type'].choices]

        ret = json.dumps({'value': types})
        return HttpResponse(ret, content_type='application/json')


class ReserveeSelectView(TemplateView):
    template_name = 'reserve/reservee_select.html'

    def get(self, request, key='', **kwargs):
        # print(key)
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))

        reservee = User.objects.filter(userinfo__reservee=True, userinfo__can_reserved=True, is_active=True)
        # 性别判断

        reserver = User.objects.get(id=obj.get('auth_user'))
        if reserver:
            gender = reserver.gender
            if gender == 1:
                reservee = reservee.filter(userinfo__can_reserve_gender__in=(0, 1))
            elif gender == 2:
                reservee = reservee.filter(userinfo__can_reserve_gender__in=(0, 2))
            else:
                reservee = reservee.filter(userinfo__can_reserve_gender__in=(0,))
        else:
            return HttpResponseNotFound
        # 人员种类判断
        t = obj.get('t')
        reservee = reservee.filter(userinfo__reservee_type=t)
        # TODO - 根据不同选择显示不同 reservee（科目判定）
        self.extra_context = {'reservee': reservee}
        return super().get(request, key=key, **kwargs)

    def post(self, request, key='', **kwargs):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))
        reservee_id = request.POST.get('reservee')
        try:
            reservee = User.objects.get(id=reservee_id)
        except User.DoesNotExist:
            return self.get(request, key, **kwargs)
        # TODO: 检测这个用户是否可以被预约
        obj.update({'reservee': reservee_id})
        key = signing.dumps(obj)
        return redirect(reverse('reserve:reserve_time_select', kwargs={'key': key}))


class ReserveTimeSelectView(TemplateView):
    template_name = 'reserve/reserve_time_select.html'

    def get(self, request, key='', **kwargs):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))

        # 被预约者
        reservee_id = obj.get('reservee')
        reservee = User.objects.get(id=reservee_id)
        # 可预约日期
        start_date = datetime.date.today() + datetime.timedelta(days=GlobalSettings('preDayMin').get())
        end_date = datetime.date.today() + datetime.timedelta(days=GlobalSettings('preDayMax').get())
        rts = ReserveTime.objects.filter(date__gte=start_date, date__lte=end_date, enabled=True,
                                         reservee=reservee, ed__lte=F('max'))
        # 备选数量
        extra_option = GlobalSettings('extraOption').get()
        extra_option_range = range(extra_option)

        self.extra_context = {'reservee': reservee, 'rts': rts, 'extra_option': extra_option_range}
        return super().get(request, key=key, **kwargs)

    def post(self, request, key='', **kwargs):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))
        main_time = request.POST.get('main_time')
        extra_time = request.POST.getlist('extra_time')
        extra_time = tuple({x for x in extra_time if x})
        obj.update({'main_time': main_time, 'extra_time': extra_time})
        key = signing.dumps(obj)
        return redirect(reverse('reserve:new_reserve_done', kwargs={'key': key}))


class ReserveTimeGetView(TemplateView):
    template_name = 'reserve/reserve_time_get.html'

    def get(self, request, key='', **kwargs):
        date = request.GET.get('date')
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))
        # 被预约者
        reservee_id = obj.get('reservee')
        reservee = User.objects.get(id=reservee_id)

        rts = ReserveTime.objects.filter(reservee=reservee, date=date, enabled=True, ed__lte=F('max'))

        self.extra_context = {'reservee': reservee, 'rts': rts}

        return super().get(request, key=key, **kwargs)


class NewReserveDoneView(TemplateView):
    template_name = 'reserve/new_reserve_done.html'

    def get(self, request, key='', **kwargs):
        try:
            obj = dict(signing.loads(key, max_age=600))
        except signing.BadSignature:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))

        try:
            auth_code = obj.get('auth_code')
            auth_name = obj.get('auth_name')
            type = obj.get('type')
            content = obj.get('content')
            main_time = obj.get('main_time')
            extra_time = tuple(obj.get('extra_time'))
            time = (main_time,) + extra_time
            time = tuple({int(x) for x in time if x})

            # TODO - 校验
            reserver = User.objects.filter(userinfo__auth_code=auth_code, userinfo__auth_name=auth_name, is_active=True,
                                           userinfo__reserver=True)
            if reserver.exists():
                reserver = reserver.first()
            else:
                raise Exception
            if request.user.is_anonymous:
                add_user = None
            else:
                add_user = request.user
            rr = ReserveRecord(reserver=reserver, main_time_id=main_time, content=content, add_user=add_user)
            rr.save()
            # TODO - 发送 ed-1 信号
            rr.type.set(ReserveType.objects.filter(id=type))
            rr.time.set(ReserveTime.objects.filter(id__in=time))
            rr.save()

        except Exception as e:
            try:
                rr.delete()
            except:
                pass
            messages.error(request, '预约失败（未知错误）：{}，请重试'.format(e))
            return redirect(reverse('reserve:user_auth'))
        else:
            rri = {
                'type': ', '.join([x.name for x in rr.type.all()]),
                'extra_time': [x for x in rr.time.all() if x != rr.main_time],
            }
            self.extra_context = {'rr': rr, 'rri': rri}
            messages.success(request, '预约成功！')

        return super().get(request, key=key, **kwargs)


class MyReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/my_reserve.html'

    def get(self, request, type='', **kwargs):
        if type == 'ing':
            title_small = '正在进行'
            condition = '今日及之后'
        elif type == 'ed':
            title_small = '已完成'
            condition = '昨日及之前'
        else:
            return HttpResponseNotFound()

        # 对于存在 confirm 的以 confirm 为准，否则以最晚的时间为准
        rrs = []
        rrs_o = ReserveRecord.objects.filter(reserver=request.user)
        for rr in rrs_o:
            if rr.order_date is None:
                continue
            if rr.order_date >= datetime.date.today() and type == "ing":
                rrs.append(rr)
            elif rr.order_date < datetime.date.today() and type == 'ed':
                rrs.append(rr)
        rris = []
        for rr in rrs:
            rris.append({
                'type': ', '.join([x.name for x in rr.type.all()]),
                'extra_time': [x for x in rr.time.all() if x != rr.main_time],
                'color': None,  # TODO - 不同状态不同颜色（Class）success/warning/info/danger
            })

        rrzs = list(zip(rrs, rris))
        self.extra_context = {'title_small': title_small, 'condition': condition, 'rrzs': rrzs}
        return super().get(request, type=type, **kwargs)

    def post(self, request, type='', **kwargs):
        _type = request.POST.get('type')
        id = request.POST.get('id')
        if _type not in ['mark']:
            messages.error(request, '操作失败')
            return super().get(request, type=type, **kwargs)
        try:
            rr = ReserveRecord.objects.get(id=id)
        except ReserveRecord.DoesNotExist:
            messages.error(request, 'ID 错误')
            return super().get(request, type=type, **kwargs)
        # TODO - 权限校验

        if _type == 'mark':
            mark = request.POST.get('mark')
            note = request.POST.get('note')
            if mark is None or not note:
                # TODO - 返回错误
                return HttpResponse('Error')
            try:
                mark = int(mark)
            except ValueError:
                return HttpResponse('Error')
            if mark not in range(1, 6):
                return HttpResponse('Error')
            # TODO - 权限判断
            rr.reserver_mark = mark
            rr.reserver_note = note
            rr.reserver_mark_time = datetime.datetime.now()
            rr.save()
            messages.success(request, '评价成功！')
            return redirect(reverse('reserve:my_reserve', kwargs={'type': type}))

        return super().get(request, type=type, **kwargs)


class ReserveMeView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/reserve_me.html'

    def get(self, request, type='', **kwargs):
        if type not in ['submited', 'confirmed', 'completed', 'canceled']:
            return HttpResponseNotFound()

        title_small = ''
        condition = ''
        query = Q()
        if type == 'submited':
            title_small = '已提交（等待确认）'
            condition = title_small
            query = Q(status=0)
        elif type == 'confirmed':
            title_small = '已确认'
            condition = title_small
            query = Q(status=100)
        elif type == 'completed':
            title_small = '已完成'
            condition = title_small
            query = Q(status__in=(200,))
        elif type == 'canceled':
            title_small = '已取消'
            condition = title_small
            query = Q(status__in=(-101, -102, -103, -104, -201))

        rrs = []
        rrs_o = ReserveRecord.objects.filter(main_time__reservee=request.user).filter(query)
        rrs = list(rrs_o)
        rris = []
        for rr in rrs:
            rris.append({
                'type': ', '.join([x.name for x in rr.type.all()]),
                'extra_time': [x for x in rr.time.all() if x != rr.main_time],
                'color': None,  # TODO - 不同状态不同颜色（Class）success/warning/info/danger
            })

        rrzs = list(zip(rrs, rris))
        self.extra_context = {'title_small': title_small, 'condition': condition, 'rrzs': rrzs}
        return super().get(request, type=type, **kwargs)

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        id = request.POST.get('id')
        if type not in ['confirm', 'complete', 'mark']:
            messages.error(request, '操作失败')
            return super().get(request, *args, **kwargs)
        try:
            rr = ReserveRecord.objects.get(id=id)
        except ReserveRecord.DoesNotExist:
            messages.error(request, 'ID 错误')
            return super().get(request, *args, **kwargs)
        # TODO - 权限校验
        if type == 'confirm':
            confirmed_time_id = request.POST.get('confirmed_time')
            try:
                confirmed_time = ReserveTime.objects.get(id=confirmed_time_id)
            except ReserveTime.DoesNotExist:
                # TODO
                return HttpResponse('')
            confirmed_place_id = request.POST.get('confirmed_place')
            try:
                confirmed_place = ReservePlace.objects.get(id=confirmed_place_id)
            except ReserveTime.DoesNotExist:
                # TODO
                return HttpResponse('')
            # TODO - ID 合法性校验
            rr.status = 100
            rr.confirm_time = confirmed_time
            rr.address = confirmed_place
            rr.save()
            messages.success(request, '预约确认成功！')
            return redirect(reverse('reserve:reserve_me', kwargs={'type': 'confirmed'}))
        if type == 'complete':
            rr.status = 200
            rr.save()
            messages.success(request, '预约确认完成成功！')
            return redirect(reverse('reserve:reserve_me', kwargs={'type': 'completed'}))
        if type == 'mark':
            mark = request.POST.get('mark')
            note = request.POST.get('note')

            try:
                mark = int(mark)
            except ValueError:
                messages.error(request, '评分数据错误，请重试')
                return redirect(reverse('reserve:reserve_me', kwargs={'type': 'completed'}))
            if not note:
                messages.error(request, '评价留言不能为空')
                return redirect(reverse('reserve:reserve_me', kwargs={'type': 'completed'}))
            if mark not in range(1, 6):
                messages.error(request, '评分数据错误，请重试')
                return redirect(reverse('reserve:reserve_me', kwargs={'type': 'completed'}))
            rr.reservee_mark = mark
            rr.reservee_note = note
            rr.reservee_mark_time = datetime.datetime.now()
            rr.save()
            messages.success(request, '评价成功！')
            return redirect(reverse('reserve:reserve_me', kwargs={'type': 'completed'}))

        return super().get(request, *args, **kwargs)


class ConfirmReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/confirm_reserve.html'

    def get(self, request, *args, **kwargs):
        id = request.GET.get('id')
        try:
            rr = ReserveRecord.objects.get(id=id)
        except ReserveRecord.DoesNotExist:
            return HttpResponseNotFound()

        # TODO - 权限校验
        if request.user != rr.main_time.reservee:
            return HttpResponseNotAllowed('')

        # 确认时间和地址
        # 性别判定
        reserver_gender = rr.reserver.gender
        reservee_gender = rr.reservee.gender
        types = (0,)
        if -1 not in (reserver_gender, reservee_gender):
            if reserver_gender == reservee_gender:  # 男1女2
                types = types + (1, reserver_gender + 2,)
            else:
                types = types + (2,)
        ps = ReservePlace.objects.filter(enabled=True, type__in=types)
        self.extra_context = {
            'rr': rr,
            'ps': ps,
        }
        return super().get(request, *args, **kwargs)


class RejectReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/reject_reserve.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CompleteReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/reject_reserve.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AbsentReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/reject_reserve.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CancelReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/reject_reserve.html'

    def get(self, request, type='', **kwargs):
        return super().get(request, type=type, **kwargs)


class MarkReserveView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/reject_reserve.html'

    def get(self, request, type='', **kwargs):
        return super().get(request, type=type, **kwargs)


class ReserveeSettingsView(LoginRequiredMixin, TemplateView):
    """
    预约管理 > 预约设置
    """
    template_name = 'reserve/reserve_settings.html'

    def get(self, request, *args, **kwargs):
        form = ReserveeSettingsForm(instance=request.user.userinfo)
        self.extra_context = {'form': form}

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = ReserveeSettingsForm(request.POST, instance=request.user.userinfo)
        if form.is_valid():
            form.save()
            messages.success(request, '修改成功！')
            return redirect(reverse('reserve:reservee_settings'))
        else:
            messages.error(request, '修改失败')
            self.extra_context = {'form': form}
            return super().get(request, *args, **kwargs)
