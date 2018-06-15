import datetime
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import signing
from django.db.models.expressions import F, Q
from django.http import HttpResponseNotFound, HttpResponseNotAllowed
from django.shortcuts import HttpResponse, redirect, reverse
from django.views.generic.base import TemplateView, View

from account.models import User
from main.utils import GlobalSettings
from .forms import UserAuthForm, ReserveTypeChooseForm, ReserveTypeConfirmForm, ReserveeSettingsForm, NewCanReserveTime, \
    NewCanReserveRepeatTime
from .models import ReserveType, ReserveTime, ReserveRecord, ReservePlace, RepeatReserveTime
from .utils import check_signature


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

                'r': 1,
                't': 1,
            })
            # return redirect(reverse('reserve:reserve_type_choose', kwargs={'key': key}))
            return redirect(reverse('reserve:reserve_type_confirm', kwargs={'key': key}))
        else:
            return self.render_to_response({'form': form})


class ReserveTypeChooseView(TemplateView):
    template_name = 'reserve/reserve_type_choose.html'

    def get(self, request, key='', **kwargs):

        form = ReserveTypeChooseForm()
        self.extra_context = {'form': form}

        return super().get(request, **kwargs)

    def post(self, request, key):

        obj = check_signature(key)
        if not obj:
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
        obj = check_signature(key)
        if not obj:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))

        form = ReserveTypeConfirmForm(key_obj=obj)

        data_url = reverse('reserve:reserve_type_data_get', kwargs={'key': key})

        self.extra_context = {'form': form, 'data_url': data_url}
        return super().get(request, key=key, **kwargs)

    def post(self, request, key='', **kwargs):
        obj = check_signature(key)
        if not obj:
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
        obj = check_signature(key)
        if not obj:
            return HttpResponse('')

        form = ReserveTypeConfirmForm(key_obj=obj)

        types = [{'id': x[0], 'subject': x[1]} for x in form.fields['type'].choices]

        ret = json.dumps({'value': types})
        return HttpResponse(ret, content_type='application/json')


class ReserveeSelectView(TemplateView):
    template_name = 'reserve/reservee_select.html'

    def get(self, request, key='', **kwargs):
        # print(key)
        obj = check_signature(key)
        if not obj:
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

        reservee = reservee.filter(userinfo__can_reserve_type__in=[obj['type']])
        self.extra_context = {'reservee': reservee}
        return super().get(request, key=key, **kwargs)

    def post(self, request, key='', **kwargs):
        obj = check_signature(key)
        if not obj:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))
        reservee_id = request.POST.get('reservee')
        try:
            reservee = User.objects.get(id=reservee_id)
        except User.DoesNotExist:
            return self.get(request, key, **kwargs)

        if not (reservee.userinfo.reservee and reservee.userinfo.can_reserved):
            messages.error(request, '此人暂时无法预约，请更换预约科目或预约人')
            return redirect(reverse('reserve:user_auth'))

        print(reservee.userinfo.can_reserve_type.all())
        if not reservee.userinfo.can_reserve_type.filter(id=obj['type']).exists():
            messages.error(request, '此人暂时无法预约，请更换预约科目或预约人')
            return redirect(reverse('reserve:user_auth'))

        obj.update({'reservee': reservee_id})
        key = signing.dumps(obj)
        return redirect(reverse('reserve:reserve_time_select', kwargs={'key': key}))


class ReserveTimeSelectView(TemplateView):
    template_name = 'reserve/reserve_time_select.html'

    def get(self, request, key='', **kwargs):
        obj = check_signature(key)
        if not obj:
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
        obj = check_signature(key)
        if not obj:
            messages.error(request, '签名错误或已过期，请重新预约')
            return redirect(reverse('reserve:user_auth'))
        main_time = request.POST.get('main_time')

        if not main_time:
            messages.error(request, '主预约时间为必填项')
            return self.get(request, key=key, **kwargs)

        extra_time = request.POST.getlist('extra_time')
        extra_time = tuple({x for x in extra_time if x})
        obj.update({'main_time': main_time, 'extra_time': extra_time})
        key = signing.dumps(obj)
        return redirect(reverse('reserve:new_reserve_done', kwargs={'key': key}))


class ReserveTimeGetView(TemplateView):
    template_name = 'reserve/reserve_time_get.html'

    def get(self, request, key='', **kwargs):
        date = request.GET.get('date')
        obj = check_signature(key)
        if not obj:
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
        obj = check_signature(key)
        if not obj:
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

            # 校验 - 预约人
            reserver = User.objects.filter(userinfo__auth_code=auth_code, userinfo__auth_name=auth_name, is_active=True,
                                           userinfo__reserver=True)
            valid = False
            for r in reserver:
                if r.has_perm('reserve.new'):
                    reserver = reserver.first()
                    valid = True
                    break

            if not valid:
                messages.error(request, '预约人不存在或无预约权限，请重新预约')
                return redirect(reverse('reserve:user_auth'))

            # 校验 - 时间
            reservee_id = obj.get('reservee')
            # print(time)
            for t in time:
                try:
                    ReserveTime.objects.get(id=t, reservee_id=reservee_id, enabled=True, ed__lte=F('max'))
                except ReserveTime.DoesNotExist:
                    messages.error(request, '预约时间选择错误，请重试')
                    return redirect(reverse('reserve:user_auth'))

            if request.user.is_anonymous:
                add_user = None
            else:
                add_user = request.user

            rr = ReserveRecord(reserver=reserver, main_time_id=main_time, content=content, add_user=add_user)
            rr.save()

            rr.type.set(ReserveType.objects.filter(id=type))
            rr.time.set(ReserveTime.objects.filter(id__in=time))
            for c in rr.time.all():
                c.ed = F('ed') + 1
                c.save()
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
                'color': {
                    -201: 'danger',
                    -101: 'danger',
                    -102: 'danger',
                    -103: 'danger',
                    -104: 'danger',
                    0: 'info',
                    100: 'success',
                    200: 'info',
                }.get(rr.status, 'info'),  # 不同状态不同颜色（Class）success/warning/info/danger
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
                'color': {
                    -201: 'danger',
                    -101: 'danger',
                    -102: 'danger',
                    -103: 'danger',
                    -104: 'danger',
                    0: 'info',
                    100: 'success',
                    200: 'info',
                }.get(rr.status, 'info'),  # 不同状态不同颜色（Class）success/warning/info/danger
            })

        rrzs = list(zip(rrs, rris))
        self.extra_context = {'title_small': title_small, 'condition': condition, 'rrzs': rrzs}
        return super().get(request, type=type, **kwargs)

    def post(self, request, type='', **kwargs):
        _type = request.POST.get('type')
        id = request.POST.get('id')

        if _type not in ['confirm', 'complete', 'mark', 'reject']:
            messages.error(request, '操作未定义')
            return self.get(request, type=type, **kwargs)

        try:
            rr = ReserveRecord.objects.get(id=id)
        except Exception:
            messages.error(request, '操作的预约记录错误')
            return self.get(request, type=type, **kwargs)

        if _type == 'confirm':
            if not request.user.has_perm('reserve.confirm', rr):
                messages.error(request, '您无权确认此预约')
                return self.get(request, type=type, **kwargs)

            confirmed_time_id = request.POST.get('confirmed_time')
            try:
                confirmed_time = ReserveTime.objects.get(id=confirmed_time_id)
            except Exception:
                messages.error(request, '您选择的预约确认时间有误')
                return self.get(request, type=type, **kwargs)

            confirmed_place_id = request.POST.get('confirmed_place')
            try:
                confirmed_place = ReservePlace.objects.get(id=confirmed_place_id)
            except Exception:
                messages.error(request, '您选择的预约确认地点有误')
                return self.get(request, type=type, **kwargs)

            rr.status = 100
            rr.confirm_time = confirmed_time
            rr.address = confirmed_place
            rr.save()

            # 恢复时间
            for r in rr.time.filter(~Q(id=confirmed_time.id)):
                r.ed -= 1
                r.save()

            messages.success(request, '预约确认成功！')
            return redirect(reverse('reserve:reserve_me', kwargs={'type': 'confirmed'}))
        if _type == 'reject':

            if not request.user.has_perm('reserve.reject_reserverecord', rr):
                messages.error(request, '您无权拒绝此预约')
                return super().get(request, type=type, **kwargs)

            rr.status = -102
            rr.save()

            # 恢复时间
            for r in rr.time.all():
                r.ed -= 1
                r.save()

            messages.success(request, '预约拒绝成功')
            return redirect(reverse('reserve:reserve_me', kwargs={'type': type}))

        if _type == 'complete':
            # TODO - 完成预约
            rr.status = 200
            rr.save()
            messages.success(request, '预约确认完成成功！')
            return redirect(reverse('reserve:reserve_me', kwargs={'type': 'submited'}))
        if _type == 'mark':
            # TODO - 权限校验
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

        messages.error(request, '操作未定义')
        return super().get(request, type=type, **kwargs)


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


class CanReserveTimeSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/can_reserve_time_settings.html'

    def get(self, request, *args, **kwargs):
        data = ReserveTime.objects.filter(reservee=request.user).extra(order_by=['date', 'start_time'])

        data = data.filter(date__gte=datetime.datetime.today())
        data = data.filter(enabled=True)

        # print(data)
        self.extra_context = {'data': data}
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        _type = request.POST.get('type')

        if _type == 'new':
            # 权限校验
            if not request.user.has_perm('reserve.add_reservetime'):
                messages.error(request, '无权添加')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            r_post = dict(request.POST)

            for k, v in r_post.items():
                if type(v) is list:
                    r_post[k] = v[0]

            r_post['start_time'] = r_post.get('date') + ' ' + r_post.get('start_time', '')
            r_post['end_time'] = r_post.get('date') + ' ' + r_post.get('end_time', '')

            r_post['reservee'] = request.user.id
            r_post['add_user'] = request.user.id

            # print(r_post)

            form = NewCanReserveTime(r_post)

            if not form.is_valid():
                messages.error(request, '相关的日期/时间设置错误')
                messages.error(request, str(form.errors))
                return redirect(reverse('reserve:can_reserve_time_settings'))

            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            if date < datetime.date.today():
                messages.error(request, '可预约日期不能为过去')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            if start_time >= end_time:
                messages.error(request, '可预约开始时间必须早于结束时间')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            if not 60 * 30 <= (end_time - start_time).seconds <= 3 * 60 * 60:
                messages.error(request, '预约时长必须在 0.5 - 3h 之间')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            # if ReserveTime.objects.filter(reservee=request.user, date=date, start_time=start_time, end_time=end_time):
            #     messages.error(request, '此时间段已存在')
            #     return redirect(reverse('reserve:can_reserve_time_settings'))

            if ReserveTime.objects.filter(reservee=request.user, date=date, enabled=True).filter(
                    Q(start_time__lte=start_time, end_time__gte=end_time) |  # 内
                    Q(start_time__gte=start_time, end_time__lte=end_time) |  # 外
                    Q(start_time__lt=end_time, end_time__gte=end_time) |  # 左
                    Q(start_time__lte=start_time, end_time__gt=start_time)  # 右
            ).exists():
                messages.error(request, '此时间段与已有可预约时间段冲突')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            # print(form.cleaned_data)

            form.save()
            messages.success(request, '添加成功')
            return redirect(reverse('reserve:can_reserve_time_settings'))

        id = request.POST.get('id')
        try:
            rt = ReserveTime.objects.get(id=id)
        except ReserveTime.DoesNotExist:
            messages.error(request, '记录不存在')
            return redirect(reverse('reserve:can_reserve_time_settings'))

        if _type == 'disable':

            if not request.user.has_perm('reserve.disable', rt):
                messages.error(request, '无权操作')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            rt.enabled = False
            rt.save()

            messages.success(request, '禁用成功')
            return redirect(reverse('reserve:can_reserve_time_settings'))

        if _type == 'edit':
            if not request.user.has_perm('reserve.edit_max', rt):
                messages.error(request, '无权操作')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            try:
                new_max = int(request.POST.get('max'))
            except ValueError:
                messages.error(request, '最大值必须是数字')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            if rt.ed > new_max:
                messages.error(request, '最大值不能小于已预约人数')
                return redirect(reverse('reserve:can_reserve_time_settings'))

            rt.max = new_max
            rt.save()

            messages.success(request, '修改成功')
            return redirect(reverse('reserve:can_reserve_time_settings'))


class CanReserveTimeRepeatSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'reserve/can_reserve_time_repeat_settings.html'

    def get(self, request, *args, **kwargs):
        data = RepeatReserveTime.objects.filter(reservee=request.user).extra(order_by=['start_time', 'loop_start'])

        # data = data.filter(date__gte=datetime.datetime.today())
        data = data.filter(enabled=True)

        # print(data)
        self.extra_context = {'data': data}
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        _type = request.POST.get('type')

        if _type == 'new':

            if not request.user.has_perm('reserve.add_repeatreservetime'):
                messages.error(request, '无权添加')
                return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            r_post = dict(request.POST)

            for k, v in r_post.items():
                if type(v) is list:
                    r_post[k] = v[0]

            if not r_post.get('loop_end'):
                r_post['loop_end'] = None

            r_post['reservee'] = request.user.id

            repeat = r_post['repeat']

            if type(repeat) is str:
                repeat = str(repeat).replace('，', ',').strip()

                if repeat[0] == '[' and repeat[-1] == ']':
                    repeat = repeat[1:-1]

                t_repeat = []

                for r in repeat.split(','):
                    t_repeat.append(int(r.strip()))

                r_post['repeat'] = t_repeat

            # print(r_post)

            form = NewCanReserveRepeatTime(r_post)

            if not form.is_valid():
                messages.error(request, '相关设置错误')
                messages.error(request, str(form.errors))
                return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            repeat = form.cleaned_data['repeat']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            loop_start = form.cleaned_data['loop_start']
            # loop_end = form.cleaned_data['loop_end']

            # if not 60 * 30 <= (end_time - start_time).seconds <= 3 * 60 * 60:
            #     messages.error(request, '预约时长必须在 0.5 - 3h 之间')
            #     return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            if RepeatReserveTime.objects.filter(repeat=repeat, start_time=start_time, end_time=end_time,
                                                enabled=True, loop_start__lte=loop_start,
                                                loop_end__gt=loop_start).exists():
                messages.error(request, '与已有循环可预约时间段冲突')
                return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            form.save()
            messages.success(request, '添加成功')
            return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

        id = request.POST.get('id')
        try:
            rt = RepeatReserveTime.objects.get(id=id)
        except RepeatReserveTime.DoesNotExist:
            messages.error(request, '记录不存在')
            return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

        if _type == 'disable':

            if not request.user.has_perm('reserve.disable_repeatreservetime', rt):
                messages.error(request, '无权操作')
                return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            rt.enabled = False
            rt.save()

            messages.success(request, '禁用成功')
            return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

        if _type == 'edit':
            if not request.user.has_perm('reserve.change_repeatreservetime', rt):
                messages.error(request, '无权操作')
                return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            r_post = dict(request.POST)

            for k, v in r_post.items():
                if type(v) is list:
                    r_post[k] = v[0]

            r_post['start_time'] = rt.start_time
            r_post['end_time'] = rt.end_time
            r_post['reservee'] = request.user.id

            repeat = r_post['repeat']

            if type(repeat) is str:
                repeat = str(repeat).replace('，', ',').strip()

                if repeat[0] == '[' and repeat[-1] == ']':
                    repeat = repeat[1:-1]

                t_repeat = []

                for r in repeat.split(','):
                    t_repeat.append(int(r.strip()))

                r_post['repeat'] = t_repeat

            print(r_post)

            form = NewCanReserveRepeatTime(r_post, instance=rt)

            if not form.is_valid():
                messages.error(request, '相关设置错误')
                messages.error(request, str(form.errors))
                return redirect(reverse('reserve:can_reserve_time_repeat_settings'))

            form.save()

            messages.success(request, '修改成功')
            return redirect(reverse('reserve:can_reserve_time_repeat_settings'))
