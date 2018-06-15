from wechatpy.client import WeChatClient

from .databasestorage import DatabaseStorage
from .models import SessionStorage, WechatConfig, WechatUser

app_id = WechatConfig.get_value('app_id')
app_secret = WechatConfig.get_value('app_secret')

ds = DatabaseStorage(SessionStorage)

client = WeChatClient(app_id, app_secret, session=ds)


def bind_wechat(user_obj, openid):
    """
    绑定微信
    :param user_obj: 用户对象
    :param openid: Open Id
    :return:
    """
    wu, _ = WechatUser.objects.get_or_create(user=user_obj)
    wu.openid = openid
    wu.save()
    return True


def send_template_message():
    # TODO
    client.message.send_template()


def save_template_info():
    template_info = client.template.get_all_private_template()
    template_list = template_info['template_list']
    from wechat.models import TemplateMessageTemplate
    for template in template_list:
        template_id = template['template_id']
        title = template['title']
        content = template['content']
        tmt, created = TemplateMessageTemplate.objects.get_or_create(template_id=template_id)
        tmt.title = title
        tmt.content = content
        tmt.save()


def get_bind_qrcode(user_obj):
    """
    获取微信绑定二维码
    :param user_obj: 用户对象
    :return: Ticket Url
    """
    from urllib.parse import quote
    from rest_framework.authtoken.models import Token

    token_obj, _ = Token.objects.get_or_create(user=user_obj)
    key = token_obj.key

    res = client.qrcode.create({
        'expire_seconds': 1800,
        'action_name': 'QR_STR_SCENE',
        'action_info': {
            'scene': {'scene_str': 'BIND-XDYY_{}'.format(key)},
        }
    })

    ticket = res['ticket']
    return 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=' + quote(ticket)
