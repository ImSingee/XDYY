import datetime

from django.core import signing

from main.utils import Success, Error, GlobalSettings
from reserve.models import ReserveTime, RepeatReserveTime


def check_signature(key):
    try:
        obj = dict(signing.loads(key, max_age=600))
        return obj
    except signing.BadSignature:
        return False


def do_repeat_single(rrt_obj=None, *, rrt_id=None):
    if rrt_obj is None:
        if rrt_id is None:
            return Error(no=400, msg='无有效对象（未传入 obj 和 id）')
        else:
            try:
                rrt_obj = RepeatReserveTime.objects.get(id=rrt_id)
            except RepeatReserveTime.DoesNotExist:
                return Error(no=501, msg='无有效对象（ID 错误）')

    pre_repeat_days = GlobalSettings(key='preRepeatDays').get()
    if pre_repeat_days is None:
        pre_repeat_days = GlobalSettings(key='preDayMax').get()
        if pre_repeat_days is None:
            return Error(no=502, msg='preRepeatDays 与 preDayMax 未定义')
        else:
            pre_repeat_days += 3

    dates = [datetime.date.today() + datetime.timedelta(days=x) for x in range(pre_repeat_days + 1)]

    for date in dates:
        if rrt_obj.loop_start > date:
            continue
        if rrt_obj.loop_end is not None and rrt_obj.loop_end < date:
            continue

        if date.isoweekday() in rrt_obj.repeat:
            start_time = date.strftime('%Y-%m-%d ') + rrt_obj.start_time.strftime('%H:%M')
            end_time = date.strftime('%Y-%m-%d ') + rrt_obj.end_time.strftime('%H:%M')
            params = {
                'reservee': rrt_obj.reservee,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'repeat': rrt_obj,
            }
            if not ReserveTime.objects.filter(**params).exists():
                rt = ReserveTime(**params)
                rt.save()

    return Success()


def do_repeat_all():
    clear_overdue_repeat()
    rrts = RepeatReserveTime.objects.filter(enabled=True)
    for rrt in rrts:
        r = do_repeat_single(rrt)
        if not r:
            print(r)


def clear_overdue_repeat():
    # Todo - test
    rrts = RepeatReserveTime.objects.filter(enabled=True, loop_end__lt=datetime.date.today())
    for rrt in rrts:
        rrt.enabled = False
        rrt.save()
