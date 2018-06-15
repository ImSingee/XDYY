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
    wu.enabled = True
    wu.save()
    return True


def send_template_message(weuser_obj, trigger_obj, data=None, url=None):
    """
    发送模板消息
    :param weuser_obj: WeUser 对象
    :param trigger_obj: TemplateMessageTrigger 对象
    :param data: TMT 中的变量值
    :param url: 点击跳转的 url
    :return:
    """
    if data is None:
        data = {}
    template_data = {
        'first': {'value': trigger_obj.first.replace('\\n', '\n').format(**data).rstrip('\n') + '\n',
                  'color': trigger_obj.first_color},
        'keyword1': {'value': trigger_obj.keyword1.replace('\\n', '\n').format(**data),
                     'color': trigger_obj.keyword1_color},
        'keyword2': {'value': trigger_obj.keyword2.replace('\\n', '\n').format(**data),
                     'color': trigger_obj.keyword2_color},
        'keyword3': {'value': trigger_obj.keyword3.replace('\\n', '\n').format(**data),
                     'color': trigger_obj.keyword3_color},
        'keyword4': {'value': trigger_obj.keyword4.replace('\\n', '\n').format(**data),
                     'color': trigger_obj.keyword4_color},
        'keyword5': {'value': trigger_obj.keyword5.replace('\\n', '\n').format(**data),
                     'color': trigger_obj.keyword5_color},
        'keyword6': {'value': trigger_obj.keyword6.replace('\\n', '\n').format(**data),
                     'color': trigger_obj.keyword6_color},
        'remark': {'value': '\n' + trigger_obj.remark.replace('\\n', '\n').format(**data).lstrip('\n'),
                   'color': trigger_obj.remark_color},
    }

    url = url or trigger_obj.url

    client.message.send_template(user_id=weuser_obj.openid,
                                 template_id=trigger_obj.template.template_id,
                                 data=template_data,
                                 url=url)


def trigger_submit():
    pass


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


def set_menu():
    """
    仅用于一次性使用
    :return:
    """

    return client.menu.create({
        "button": [
            {
                "type": "view",
                "name": "辅导员有约",
                "url": "https://kk.singee.site/"
            },
            {
                "type": "view",
                "name": "学导有约",
                "url": "https://vv.singee.site/"
            }
        ]
    })
