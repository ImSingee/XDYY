import base64
import datetime
import logging
import os
import re

from collections import Iterable

from django.conf import settings

from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.http import urlquote, urlunquote

from main.models import Global

logger = logging.getLogger('django')


class ResultBase:

    def __init__(self, no, msg, *args, **kwargs):
        self.no = no
        self.msg = msg
        self.args = tuple(args)
        self.kwargs = dict(kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return '{} - {}'.format(self.no, self.msg)



class Success(ResultBase):
    def __init__(self, no=200, msg='Success', *args, **kwargs):
        super().__init__(no, msg, *args, **kwargs)

    def __bool__(self):
        return True


class Error(ResultBase):
    def __init__(self, no=400, msg='Undefined Error', *args, **kwargs):
        super().__init__(no, msg, *args, **kwargs)

    def __bool__(self):
        return False



def choose_value(*values, allow_none=False, default=None):
    # print(values)
    for var in values:
        if var is not None:
            return var
    # None
    if allow_none:
        return None
    else:
        if default is not None:
            return default
        else:
            raise ValueError('Variable is None')


class GlobalSettings:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def get_default(self, key=None):
        key = choose_value(key, self.key)
        import json
        with open(os.path.join(settings.BASE_DIR, 'init_data', 'global.json'), 'r', encoding='utf-8') as f:
            global_default = json.load(f)

        item = global_default.get(key)

        return item.get('value') if item is not None else None

    def get_default_description(self, key=None):
        key = choose_value(key, self.key)
        import json
        with open(os.path.join(settings.BASE_DIR, 'init_data', 'global.json'), 'r', encoding='utf-8') as f:
            global_default = json.load(f)

        item = global_default.get(key)

        return item.get('description') if item is not None else None

    def get(self, key=None):
        key = choose_value(key, self.key)
        try:
            value = Global.objects.get(key=key).value
        except Global.DoesNotExist:
            value = self.get_default(key)
        return self.wrap(value)

    def get_description(self, key=None):
        key = choose_value(key, self.key)
        try:
            description = Global.objects.get(key=key).description
        except Global.DoesNotExist:
            description = self.get_default_description(key)
        return description

    @staticmethod
    def wrap(value):
        if type(value) is str:
            if value.lower() in ['true', 'yes', 'on']:
                return True
            if value.lower() in ['false', 'no', 'off']:
                return False
            if value.isdigit():
                return int(value)
        return value

    def set(self, key=None, value=None, description=None, order=None):
        key = choose_value(key, self.key)

        try:
            g = Global.objects.get(key=key)
        except Global.DoesNotExist:
            # 不存在
            value = choose_value(value, self.value, self.get_default(key))
            description = choose_value(description, self.get_default_description(key), '')
            g = Global(key=key, value=value, description=description, order=order)
            g.save()
            return True
        # 存在（不考虑默认值，不设置 order）
        try:
            g.value = choose_value(value, self.value)
            g.description = choose_value(description, g.description, '')
            g.save()
        except ValueError:
            return False
        return True


class GlobalMenu:
    def __init__(self):
        pass


def get_menu(request):
    menu = []
    return menu

# 以下请忽略

# class Settings:
#     class Keys:
#         actionBookShort = 'actionBookShort'
#         actionTypeOther = 'actionTypeOther'
#         preDayMin = 'preDayMin'
#         preDayMax = 'preDayMax'
#         minPerTime = 'minPerTime'
#         maxPerTime = 'maxPerTime'
#         minPerTimeNormal = 'minPerTimeNormal'
#         maxPerTimeNormal = 'maxPerTimeNormal'
#         bookCodeNumber = 'bookCodeNumber'
#         autoSignUp = 'autoSignUp'
#         preAutoBookDays = 'preAutoBookDays'
#         loginStatus = 'loginStatus'
#
#     class Values:
#         class ActionBookShort:
#             true = True
#             false = False
#
#         class ActionTypeOther:
#             false = False
#             true_all = 1
#             true_no = 2
#
#         class AutoSignUp:
#             true = True
#             false = False
#
#         class loginStatus:
#             normal = 0
#             admin = 1
#             superadmin = 2
#
#
# def get_global_setting(key):
#     value = Global.objects.get(key=key).value
#
#     if key == Settings.Keys.actionBookShort:
#         if value == '0':
#             return True
#         else:
#             return False
#     elif key == Settings.Keys.autoSignUp:
#         if value == '0':
#             return True
#         else:
#             return False
#     elif key == Settings.Keys.actionTypeOther:
#         if value == '-1':
#             return False
#         if value == '0' or value == '1':
#             return 1
#         if value == '2':
#             return 2
#         else:
#             return -1
#     elif key == Settings.Keys.preDayMax:
#         try:
#             value = int(value)
#         except:
#             value = 7
#         return value
#     elif key == Settings.Keys.preDayMin:
#         try:
#             value = int(value)
#         except:
#             value = 1
#         return value
#     elif key == Settings.Keys.minPerTime:
#         try:
#             value = int(value)
#         except:
#             value = 1
#         return value
#     elif key == Settings.Keys.maxPerTime:
#         try:
#             value = int(value)
#         except:
#             value = 3
#         return value
#     elif key == Settings.Keys.minPerTimeNormal:
#         try:
#             value = int(value)
#         except:
#             value = 1
#         return value
#     elif key == Settings.Keys.maxPerTimeNormal:
#         try:
#             value = int(value)
#         except:
#             value = 2
#         return value
#     elif key == Settings.Keys.bookCodeNumber:
#         try:
#             value = int(value)
#         except:
#             value = 8
#         return value
#     elif key == Settings.Keys.preAutoBookDays:
#         try:
#             value = int(value)
#         except:
#             value = 10
#         return value
#     elif key == Settings.Keys.loginStatus:
#         try:
#             value = int(value)
#         except:
#             value = 0
#         return value
#     else:
#         return value
#
#
# def set_global_setting(key, value):
#     try:
#         item = Global.objects.get(key=key)
#         item.value = value
#         item.save()
#         return True
#     except Global.DoesNotExist:
#         return False
#     except Global.MultipleObjectsReturned:
#         return False
#
#
# def verify_id_number(id_number: str) -> bool:
#     """
#     校验身份证号是否正确
#     :param id_number: 身份证号
#     :return: True 为 校验通过，False 为校验失败
#     """
#     if not id_number:
#         return False
#
#     # 校验数字长度
#     if len(id_number) not in [15, 18]:
#         return False
#
#     # 校验 1-2 位
#     area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
#             "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
#             "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
#             "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
#     if id_number[:2] not in area:
#         return False
#
#     # 校验生日位
#     if len(id_number) == 15:  # 15 位身份证号
#         if ((int(id_number[6:8]) + 1900) % 4 == 0 or (
#                 (int(id_number[6:8]) + 1900) % 100 == 0 and (int(id_number[6:8]) + 1900) % 4 == 0)):
#             ereg = re.compile(
#                 '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
#         else:
#             ereg = re.compile(
#                 '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
#         return bool(re.match(ereg, id_number))
#     else:  # 18 位身份证号
#         if (int(id_number[6:10]) % 4 == 0 or (int(id_number[6:10]) % 100 == 0 and int(id_number[6:10]) % 4 == 0)):
#             ereg = re.compile(
#                 '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')  # //闰年出生日期的合法性正则表达式
#         else:
#             ereg = re.compile(
#                 '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')  # //平年出生日期的合法性正则表达式
#
#         if not re.match(ereg, id_number):
#             return False
#
#     # 校验 18 位
#     str_to_int = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
#                   '6': 6, '7': 7, '8': 8, '9': 9, 'X': 10}
#     check_dict = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7',
#                   6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
#     check_num = 0
#     for index, num in enumerate(id_number):
#         if index == 17:
#             right_code = check_dict.get(check_num % 11)
#             if num == right_code:
#                 return True
#             else:
#                 return False
#         check_num += str_to_int.get(num) * (2 ** (17 - index) % 11)
#
#
# def create_user(username, password=None, email=None, role='Student', name=None, last_name=None, first_name=None,
#                 avatar=None, tel=None, student_id_number=None, id_number=None, teacher_note=None,
#                 teacher_choice1=None, teacher_choice2=None,
#                 teacher_can_booked=False, is_active=True, debug=False):
#     """
#     创建用户
#     A - All
#     T - Teacher
#     S - Student
#     M - Management (Admin & SuperAdmin)
#     :rtype: tuple
#     :param username: A - 用户名（必填）
#     :param password: A - 密码（选填，不填写则为用户名）
#     :param email: A - 邮箱（选填，不填写则按身份不同生成不同邮箱）
#     :param role: A - 角色：填写 Admin/Teacher/Student，选填，默认为 Student
#     :param name: A - 姓名：选填
#     :param last_name: A - 姓，选填，默认根据姓名自动判断
#     :param first_name: A - 名，选填，默认根据姓名自动判断
#     :param avatar: A - 头像文件路径，选填，字符串，应以 /uploads/avatars/ 开头
#     :param tel: A - 电话号码，选填
#     :param student_id_number: S - 学号，选填，仅适用于 Student，不填写则与用户名相同
#     :param id_number: A - 身份证号，选填
#     :param teacher_choice1: T - 教师可预约项一，选填
#     :param teacher_choice2: T - 教师可预约项二，选填
#     :param teacher_note: T - 教师说明，选填
#     :param teacher_can_booked: T - 教师可否预约，选填，默认为不可预约（False）
#     :param is_active: A - 用户是否活跃，用于替代删除，选填，默认为活跃（True）
#     :param debug: 是否为测试模式，暂时无用，默认为否（False）
#     :return: (True/False, 错误码, 错误原因)
#     """
#     if role not in ('Admin', 'Teacher', 'Student', 'SuperAdmin'):
#         return result.Error(401, '未定义人员身份或身份定义错误')
#
#     if not password:
#         password = username
#     if not email:
#         if role == 'Student':
#             email = '{}@stu.shmtu.edu.cn'.format(username)
#         elif role == 'Teacher':
#             email = '{}@shmtu.edu.cn'.format(username)
#         elif role == 'Admin':
#             email = '{}@singee.site'.format(username)
#         else:
#             return result.Error(401, '未定义人员身份或身份定义错误')
#     if not verify_id_number(id_number):
#         id_number = ''
#     if not name:
#         # name = username
#         if not last_name: last_name = ''
#         if not first_name: first_name = username
#     else:
#         if len(name) in (2, 3):
#             if not last_name: last_name = name[0]
#             if not first_name: first_name = name[1:]
#         elif len(name) == 4:
#             if not last_name: last_name = name[0:2]
#             if not first_name: first_name = name[2:]
#         else:
#             if not last_name: last_name = ''
#             if not first_name: first_name = name
#
#     try:
#         user = User.objects.create_user(username=username, password=password, email=email)
#     except:
#         return result.Error(501, 'User 对象创建错误，可能是用户名/密码/邮件格式错误或存在相同项引起的')
#
#     if not user:
#         return result.Error(502, 'User 对象创建失败，具体原因未知')
#
#     user.last_name = last_name
#     user.first_name = first_name
#     user.is_active = is_active
#     user.save()
#
#     Group.objects.get(name=role).user_set.add(user)
#
#     user = User.objects.get(username=username)  # 刷新缓存
#     user.save()
#
#     if not hasattr(user, 'userinfo'):
#         return result.Error(503, 'UserInfo 对象创建失败，具体原因未知')
#     else:
#         userinfo = user.userinfo
#         if avatar:
#             userinfo.avatar = avatar
#         if tel:
#             userinfo.tel = tel
#         if id_number:
#             userinfo.idNumber = id_number
#         userinfo.save()
#
#     if role == 'Student':
#         if not hasattr(user, 'student'):
#             return result.Error(504, 'Student 对象创建失败，具体原因未知')
#         else:
#             student = user.student
#             if student_id_number:
#                 student.idNumber = student_id_number
#             else:
#                 student.idNumber = username
#             student.save()
#     elif role == 'Teacher':
#         if not hasattr(user, 'teacher'):
#             return result.Error(505, 'Teacher 对象创建失败，具体原因未知')
#         else:
#             teacher = user.teacher
#             if teacher_note:
#                 teacher.note = teacher_note
#             if teacher_choice1:
#                 logger.info(teacher_choice1)
#                 teacher.choice1 = teacher_choice1
#             if teacher_choice2:
#                 logger.info(teacher_choice2)
#                 teacher.choice2 = teacher_choice2
#             teacher.canBooked = teacher_can_booked
#             teacher.save()
#
#     return result.Success(200, '<User {}#>{} 创建并初始化成功'.format(user.id, userinfo.name), user=user)
#
#
# def generate_code(n):  # 创建 n 位随机字符串
#     return base64.b32encode(os.urandom(n)).decode('utf-8')[:n]
#
#
# # def add_can_book_time(teacher, date, start_time, end_time, max=2):
# #     from book.models import Teacher2Booking
# #     t2b = Teacher2Booking(teacher=teacher, date=date, start_time=start_time, end_time=end_time, max_users=max)
# #     t2b.save()
# #     return t2b
# #
# #
# # def edit_teacher_can_book_types(teacher, types=None):
# #     from book.models import Type
# #     if not types:
# #         types = Type.objects.all()
# #     teacher.canBookedTypes = types
#
# def datetime_valid(v_date, start_time, end_time):
#     try:
#         r_date = datetime.datetime.strptime(v_date, '%Y-%m-%d')
#         r_date = datetime.date(r_date.year, r_date.month, r_date.day)
#
#         start_time = timezone.datetime.strptime('{} {}'.format(v_date, start_time), '%Y-%m-%d %H:%M')
#         end_time = timezone.datetime.strptime('{} {}'.format(v_date, end_time), '%Y-%m-%d %H:%M')
#
#         if start_time < end_time and not r_date < datetime.date.today():
#             return r_date, start_time, end_time
#         else:
#             return False
#     except ValueError:
#         return False
#
#
# def time_valid(start_time, end_time):
#     try:
#
#         start_time = timezone.datetime.strptime('2010-01-01 {}'.format(start_time), '%Y-%m-%d %H:%M')
#         end_time = timezone.datetime.strptime('2010-01-01 {}'.format(end_time), '%Y-%m-%d %H:%M')
#
#         if start_time < end_time:
#             return start_time, end_time
#         else:
#             return False
#     except ValueError:
#         return False
#
#
# def compare_user_group(u1, u2):
#     # 仅区分普通用户与管理员，相同返回 True，不同返回 False
#     a1 = True if u1.has_perm('settings.is_admin') else False
#     a2 = True if u2.has_perm('settings.is_admin') else False
#     return a1 == a2
#
#
# def compare_lists(l1, l2):
#     # 判断两个列表是否有交叉项
#     m1 = [(i if not isinstance(i, str) else i.lower()) for i in l1]
#     m2 = [(i if not isinstance(i, str) else i.lower()) for i in l2]
#     return bool([i for i in m1 if i in m2])
#
#
# def parse_get(uri, **kwargs):
#     """
#     在网址的基础上添加键值对
#     :param uri: 原网址
#     :param kwargs: 增加的 get 参数
#     :return: 新网址
#     """
#
#     u = uri.split('?')
#     path = u[0]
#     try:
#         q = u[1]
#     except IndexError:
#         q = ''
#     path += '/' if not path.endswith('/') else ''
#     # 上面获取到了一个以 / 结尾的 path
#     qs = q.split('&')
#     ql = {}
#     for q in qs:
#         dd = q.split('=')
#         try:
#             key = urlunquote(dd[0])
#             value = urlunquote(dd[1])
#         except IndexError:
#             continue
#         ql.update({key: value})
#
#     ql.update(kwargs)
#
#     full = path + '?' + '&'.join(['{}={}'.format(urlquote(key), urlquote(value)) for key, value in ql.items()])
#     return full
#
#
# def group(lst, get_key):
#     '''
#
#     :param lst: 要分组的列表
#     :param get_key: 取键函数（返回值需要是一个可哈希对象）
#     :return: 一个以 key:value 字典
#     '''
#     r = {}
#
#     for i in lst:
#         k = get_key(i)
#         found = False
#         if k in r:
#             r[k].append(i)
#         else:
#             r.setdefault(k, [i])
#     return r
#
#
# def get_page_range(paginator, page, ON_EACH_SIDE=3, ON_ENDS=2, MAX_ALL=10):
#     """
#     Generates the series of links to the pages in a paginated list.
#     """
#
#     DOT = '...'
#
#     page_num = page.number
#
#     if paginator.num_pages <= MAX_ALL:
#         page_range = range(1, paginator.num_pages + 1)
#     else:
#         page_range = []
#
#         if page_num > (ON_EACH_SIDE + ON_ENDS) + 2:
#             page_range.extend(range(1, ON_ENDS + 1))
#             page_range.append(DOT)
#             page_range.extend(range(page_num - ON_EACH_SIDE, page_num + 1))
#         else:
#             page_range.extend(range(1, page_num + 2))
#
#         if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
#             page_range.extend(range(page_num + 2, page_num + ON_EACH_SIDE + 1))
#             page_range.append(DOT)
#             page_range.extend(range(paginator.num_pages - ON_ENDS + 1, paginator.num_pages + 1))
#         else:
#             page_range.extend(range(page_num + 1, paginator.num_pages + 1))
#
#     return page_range
#
#
# def set_user_name(user_obj: User, name: str):
#     # if not type(user_obj) is User:
#     #     raise ValueError('传入的 user_obj 参数必须是用户对象')
#
#     ui = user_obj.userinfo
#     ui.name = name
#     ui.save()
#
#     if len(name) in (2, 3):
#         user_obj.last_name = name[0]
#         user_obj.first_name = name[1:]
#     elif len(name) == 4:
#         user_obj.last_name = name[0:2]
#         user_obj.first_name = name[2:]
#     else:
#         user_obj.last_name = ''
#         user_obj.first_name = name
#     user_obj.save()
#
#
# def get_referer(request, default: str = None):
#     r = request.META['HTTP_REFERER']
#     if r:
#         return r
#     else:
#         return default
#
#
# def force_log_in(request, user):
#     user = authenticate(user_obj=user, force=True)
#     if user is not None:
#         if user.is_active:
#             login(request, user)
#             return request
#         else:
#             return False
#     else:
#         return False
