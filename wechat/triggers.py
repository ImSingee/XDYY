from wechat.models import TemplateMessageTrigger
from wechat.utils import send_template_message


def new(reserve_obj):
    """
    新预约
    :param reserve_obj: ReserveRecord 预约对象
    :return: None
    """
    # 发送给预约人 - 201
    reserver = reserve_obj.reserver
    if hasattr(reserver, 'wechat') and reserver.wechat.binded:
        # 发送模板消息
        to_weu = reserver.wechat
        triggers = TemplateMessageTrigger.objects.filter(type=201)
        for trigger in triggers:
            send_template_message(to_weu, trigger, data={
                'reservee_name': reserve_obj.reservee.name,
                'reservee_tel': reserve_obj.reservee.tel,
                'reserver_name': reserve_obj.reserver.name,
                'reserver_tel': reserve_obj.reserver.tel,
                'reserve_time': reserve_obj.main_time.display
            })

    # 发送给被预约人 - 301
    reservee = reserve_obj.reservee
    if hasattr(reservee, 'wechat') and reservee.wechat.binded:
        # 发送模板消息
        to_weu = reservee.wechat
        triggers = TemplateMessageTrigger.objects.filter(type=301)
        for trigger in triggers:
            send_template_message(to_weu, trigger, data={
                'reservee_name': reserve_obj.reservee.name,
                'reservee_tel': reserve_obj.reservee.tel,
                'reserver_name': reserve_obj.reserver.name,
                'reserver_tel': reserve_obj.reserver.tel,
                'reserve_time': reserve_obj.main_time.display,
                'reserve_content': reserve_obj.content,
            })


def reject(reserve_obj):
    """
    拒绝预约
    :param reserve_obj: ReserveRecord 预约对象
    :return: None
    """
    # 发送给预约人 - 202
    reserver = reserve_obj.reserver
    if hasattr(reserver, 'wechat') and reserver.wechat.binded:
        # 发送模板消息
        to_weu = reserver.wechat
        triggers = TemplateMessageTrigger.objects.filter(type=202)
        for trigger in triggers:
            send_template_message(to_weu, trigger, data={
                'reservee_name': reserve_obj.reservee.name,
                'reservee_tel': reserve_obj.reservee.tel,
                'reserver_name': reserve_obj.reserver.name,
                'reserver_tel': reserve_obj.reserver.tel,
                'reserve_time': reserve_obj.main_time.display
            })


def cancel(reserve_obj):
    """
    取消预约
    :param reserve_obj: ReserveRecord 预约对象
    :return: None
    """
    # 发送给预约人 - 203
    reserver = reserve_obj.reserver
    if hasattr(reserver, 'wechat') and reserver.wechat.binded:
        # 发送模板消息
        to_weu = reserver.wechat
        triggers = TemplateMessageTrigger.objects.filter(type=203)
        for trigger in triggers:
            send_template_message(to_weu, trigger, data={
                'reservee_name': reserve_obj.reservee.name,
                'reservee_tel': reserve_obj.reservee.tel,
                'reserver_name': reserve_obj.reserver.name,
                'reserver_tel': reserve_obj.reserver.tel,
                'reserve_time': reserve_obj.main_time.display
            })


def confirm(reserve_obj):
    """
    确认预约
    :param reserve_obj: ReserveRecord 预约对象
    :return: None
    """
    # 发送给预约人 - 204
    reserver = reserve_obj.reserver
    if hasattr(reserver, 'wechat') and reserver.wechat.binded:
        # 发送模板消息
        to_weu = reserver.wechat
        triggers = TemplateMessageTrigger.objects.filter(type=204)
        for trigger in triggers:
            send_template_message(to_weu, trigger, data={
                'reservee_name': reserve_obj.reservee.name,
                'reservee_tel': reserve_obj.reservee.tel,
                'confirm_time': reserve_obj.confirm_time.display,
                'confirm_place': reserve_obj.address.display,
            })


def absent(reserve_obj):
    """
    确认预约
    :param reserve_obj: ReserveRecord 预约对象
    :return: None
    """
    # 被标注为无故未出席 - 206
    reserver = reserve_obj.reserver
    if hasattr(reserver, 'wechat') and reserver.wechat.binded:
        # 发送模板消息
        to_weu = reserver.wechat
        triggers = TemplateMessageTrigger.objects.filter(type=206)
        for trigger in triggers:
            send_template_message(to_weu, trigger, data={
                'reservee_name': reserve_obj.reservee.name,
                'reservee_tel': reserve_obj.reservee.tel,
                'confirm_time': reserve_obj.confirm_time.display,
                'confirm_place': reserve_obj.address.display,
            })


def complete(reserve_obj):
    """
    完成预约
    :param reserve_obj: ReserveRecord 预约对象
    :return: None
    """
    pass
