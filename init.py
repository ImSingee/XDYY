import json
import os
import shutil

from django.conf import settings
from django.contrib.auth.models import Group, Permission

from account.models import User, UserInfo
from account.utils import UserSettings
from dashboard.models import Menu
from main.utils import Success, Error
from reserve.models import ReserveType, RepeatReserveTime, ReservePlace, ReserveTime

BASE_DIR = settings.BASE_DIR


def init_dir():
    paths = ['media', 'media/export', 'media/avatars']
    paths = [os.path.join(BASE_DIR, x) for x in paths]

    for t in paths:
        if not os.path.exists(t):
            os.mkdir(t)


def init_group():
    g1 = Group(id=1, name='管理员')
    g1.save()
    g2 = Group(id=2, name='学导')
    g2.save()
    g3 = Group(id=3, name='学生')
    g3.save()


def init_permission():
    g1 = Group.objects.get(id=1)  # 管理员
    g2 = Group.objects.get(id=2)  # 学导
    g3 = Group.objects.get(id=3)  # 学生

    # 管理员
    g1.permissions.add(Permission.objects.get(content_type__model='reserverecord', codename='confirm'))
    g1.permissions.add(Permission.objects.get(content_type__model='reserverecord', codename='reject_reserverecord'))
    g1.permissions.add(Permission.objects.get(content_type__model='reserverecord', codename='absent_reserverecord'))
    g1.permissions.add(Permission.objects.get(content_type__model='reserverecord', codename='cancel_reserverecord'))
    g1.permissions.add(Permission.objects.get(content_type__model='reservetime', codename='disable'))
    g1.permissions.add(Permission.objects.get(content_type__model='reservetime', codename='edit_max'))
    g1.permissions.add(Permission.objects.get(content_type__model='reservetime', codename='change_reservetime'))
    g1.permissions.add(
        Permission.objects.get(content_type__model='repeatreservetime', codename='change_repeatreservetime'))

    # 学导
    g2.permissions.add(Permission.objects.get(content_type__model='reservetime', codename='add_reservetime'))
    g2.permissions.add(
        Permission.objects.get(content_type__model='repeatreservetime', codename='add_repeatreservetime'))

    # 学生
    g3.permissions.add(Permission.objects.get(content_type__model='reserverecord', codename='new'))


def init_superuser():
    from configparser import ConfigParser
    cf = ConfigParser()
    cf.read(os.path.join(settings.CONFIG_DIR), encoding='utf-8')

    username = cf.get('SUPERUSER', 'username')
    password = cf.get('SUPERUSER', 'password')
    email = cf.get('SUPERUSER', 'email', fallback='')
    name = cf.get('SUPERUSER', 'name', fallback='')

    UserSettings().create_superuser(username=username, password=password, email=email, name=name)


def init_admin():
    from account.utils import UserSettings
    from configparser import ConfigParser
    cf = ConfigParser()
    cf.read(os.path.join(settings.CONFIG_DIR), encoding='utf-8')

    username = cf.get('ADMIN', 'username')
    password = cf.get('ADMIN', 'password')
    name = cf.get('ADMIN', 'name', fallback='')

    UserSettings().create_admin(username=username, password=password, name=name)


def init_global():
    from main.utils import GlobalSettings
    with open(os.path.join(BASE_DIR, 'init_data', 'global.json'), 'r', encoding='utf-8') as f:
        j = json.load(f)
    g = GlobalSettings()
    for i, k in enumerate(j, 0):
        g.set(k, order=i)


def init_menu():
    Menu.objects.all().delete()
    with open(os.path.join(BASE_DIR, 'init_data', 'menu.json'), 'r', encoding='utf-8') as f:
        js = json.load(f)
    for j in js:
        if 'children' in j:
            children = j.pop('children')
        else:
            children = []

        m = Menu(**j)
        m.save()
        for child in children:
            if 'children' in child:
                child.pop('children')
            # 忽略二级菜单 icon
            if 'icon' in child: child.pop('icon')
            if 'icon_name' in child: child.pop('icon_name')
            if 'icon_type' in child: child.pop('icon_type')
            c = Menu(parent=m, **child)
            c.save()


def init_type():
    ReserveType.objects.all().delete()
    with open(os.path.join(BASE_DIR, 'init_data', 'type.json'), 'r', encoding='utf-8') as f:
        js = dict(json.load(f))
    for k, v in js.items():
        t = ReserveType(name=k, **v)
        t.save()


def init_student():
    import xlrd
    import threading
    import queue
    import time

    User.objects.filter(groups__id=3).delete()

    data = xlrd.open_workbook(os.path.join(BASE_DIR, 'init_data', 'secret', 'student.xlsx'))
    table = data.sheets()[0]
    nrows = table.nrows

    students = []

    for i in range(1, nrows + 1):
        # if settings.DEBUG and not i in range(1, 101):
        #     # 100 个数据作为测试
        #     break
        # print('{} {}'.format(table.cell(i, 0).value, table.cell(i, 1).value))
        # print(i) 0 2
        try:
            name = table.cell(i, 0).value
            try:
                student_card_no = str(int(table.cell(i, 1).value))
            except ValueError:
                print('<Student {}l-{}> student_card_no is not Integer, Pass'.format(i, name))
                continue
            id_card_no = table.cell(i, 2).value

            tel = table.cell(i, 3).value

            try:
                tel = str(int(tel)) if tel != '' else None
            except ValueError:
                print('<Student {}l-{}#> Tel is not Integer, Set Blank'.format(i, name))
                tel = ''

            if len(id_card_no) != 18 or id_card_no[-3:] == '000':
                pwd = student_card_no
            else:
                pwd = id_card_no[-6:]

            students.append({
                'username': student_card_no,
                'password': pwd,
                'email': '{}@stu.shmtu.edu.cn'.format(student_card_no),
                'auth_code': student_card_no,
                'auth_name': name,
                'id_card_no': id_card_no,
                'name': name,
                'tel': tel,
            })

        except:
            print('<Student {}l#> Xls format error'.format(i))
            continue

    start_time = time.time()

    d = queue.Queue(len(students))

    for student in students:
        d.put(student)

    class AddStudentThread(threading.Thread):
        def run(self):
            try:
                while True:
                    student = dict(d.get(False))
                    ret = UserSettings().create_student(**student)
                    print(ret)

            except queue.Empty:
                print('Thread end')
                return

    threads = []
    for i in range(30):
        t = AddStudentThread()
        t.start()
        threads.append(t)

    [t.join() for t in threads]

    end_time = time.time()

    print(end_time - start_time)

    print('Complete Init Students')


def init_xuedao():
    import xlrd
    data = xlrd.open_workbook(os.path.join(BASE_DIR, 'init_data', 'secret', 'xuedao20180319.xlsx'))
    table = data.sheets()[0]
    nrows = table.nrows

    xuedaos = []

    for i in range(1, nrows + 1):
        # 序号 姓名 学号 专业	班级	用户名（改成小写）	 邮箱	手机号	简介
        try:
            name = table.cell(i, 1).value
            xuehao = table.cell(i, 2).value
            zhuanye = table.cell(i, 3).value
            banji = table.cell(i, 4).value
            username = str(table.cell(i, 5).value).lower()
            email = table.cell(i, 6).value
            tel = table.cell(i, 7).value
            intro = table.cell(i, 8).value

            short_intro = zhuanye

            try:
                tel = str(int(tel)) if tel != '' else None
            except ValueError:
                print('<Xuedao {}l-{}#> Tel is not Integer, Set Blank'.format(i, name))
                tel = ''

            password = username.capitalize() + str(tel)[-4:]

            xuedaos.append({
                'xuehao': xuehao,
                'name': name,
                'username': username,
                'password': password,
                'tel': tel,
                'short_intro': short_intro,
                'intro': intro,
                'zhuanye': zhuanye,
                'banji': banji,
            })

        except:
            print('<Xuedao {}l#> Xls format error'.format(i))
            continue

    def add(xuedao):
        xuedao = dict(xuedao)
        xuedao.setdefault('reservee', True)
        xuedao.setdefault('can_reserved', True)
        name = xuedao.get('name', '')
        xuehao = xuedao.get('xuehao', '')
        u = User.objects.filter(userinfo__auth_code=xuehao, is_active=True)
        if u.exists():
            if len(u) == 1:
                status = Success(e='成功', name=name)
            else:
                status = Error(e='不唯一', name=name)
        else:
            status = Error(e='不存在', name=name)
        if not status:
            return status

        u = u.first()
        u.tel = xuedao.get('tel', '')
        # 头像处理 - 开始
        avatar_bak_path = os.path.join(BASE_DIR, 'media', 'avatars.bak')
        avatar_path = os.path.join(BASE_DIR, 'media', 'avatars')
        username = xuedao.get('username' '')
        m_paths = ['jpg', 'jpeg', 'png']
        for m in m_paths:
            if os.path.isfile(os.path.join(avatar_bak_path, '{}.{}'.format(username, m))):
                shutil.copyfile(os.path.join(avatar_bak_path, '{}.{}'.format(username, m)),
                                os.path.join(avatar_path, '{}.{}'.format(username, m)))
                u.avatar = "avatars/{}.{}".format(username, m)
                u.save()
                break
        # 头像处理 - 结束
        u.save()
        ui = u.userinfo
        user_info_fields = [x.name for x in UserInfo._meta.get_fields()]
        for k, v in xuedao.items():
            if k in user_info_fields:
                setattr(ui, k, v)
        ui.save()
        UserSettings().add_group(user_obj=u, id=2)  # reservee
        # ret = utils.create_user(**xuedao)

        return status

    # print(xuedaos)

    results = [add(x) for x in xuedaos]
    for r in results:
        print('{} - {}'.format(r.name, r.e))

    print('Complete Init Xuedaos')


def init_xuedao_time():
    RepeatReserveTime.objects.all().delete()
    ReserveTime.objects.all().delete()

    us = User.objects.filter(userinfo__reservee=True, is_active=True)
    for u in us:
        rrt = RepeatReserveTime(reservee=u, start_time='08:20', end_time='09:55', repeat=(1, 2, 3, 4, 5))
        rrt.save()


def init_xuedao_type():
    us = User.objects.filter(userinfo__reservee=True)
    ta = ReserveType.objects.filter(enabled=True, type=1)
    for u in us:
        u.userinfo.can_reserve_type.set(ta)


def init_gender():
    us = User.objects.all()
    for u in us:
        if u.gender == -1 and u.id_card_no:
            try:
                u.gender = 2 - int(u.id_card_no[-2]) % 2  # 男1女2
            except ValueError:
                continue
            u.save()


def init_reserve_place():
    ReservePlace.objects.all().delete()
    with open(os.path.join(BASE_DIR, 'init_data', 'place.json'), 'r', encoding='utf-8') as f:
        js = dict(json.load(f))
    for k, v in js.items():
        t = ReservePlace(name=k, **v)
        t.save()


def init():
    init_dir()
    init_global()
    init_menu()
    init_type()
    # migrate account
    init_group()
    init_permission()
    init_superuser()
    init_admin()
    # student & xuedao
    init_student()
    init_xuedao()
    init_gender()


def init_test():
    init()
    init_xuedao_time()
    init_reserve_place()
    init_xuedao_type()


def init_minimal():
    init_dir()
    init_global()


def init_passauth():
    us = User.objects.all()
    for u in us:
        print('{}/{}'.format(u.id, len(us)))
        u.set_password('123456')
        u.save()


if __name__ == '__main__':
    raise EnvironmentError('Please run this through Django Environment, and run by "./manage.py init *"')
