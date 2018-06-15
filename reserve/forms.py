from django import forms
from django.forms import CharField, ValidationError

from account.models import UserInfo, User
from .models import ReserveType, ReserveTime, RepeatReserveTime


class CharFieldC(CharField):

    def __init__(self, *, placeholder=None, **kwargs):
        self.placeholder = placeholder
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.placeholder is not None and not widget.is_hidden:
            attrs['placeholder'] = str(self.placeholder)

        attrs.update({'class': ' '.join([attrs.get('class', ''), 'form-control']).strip()})
        return attrs


class UserAuthForm(forms.Form):
    auth_code = CharFieldC(label='学号', placeholder='请输入您的学号（12 位）', required=True)
    auth_name = CharFieldC(label='姓名', placeholder='请输入您的真实姓名', required=True)

    def clean_auth_code(self):
        auth_code = self.cleaned_data['auth_code']
        ui = UserInfo.objects.filter(reserver=True, auth_code=auth_code, user__is_active=True)
        if not ui.exists():
            raise ValidationError('学号不存在', code='auth_code_not_exist')
        return auth_code

    def clean(self):
        cleaned_data = super().clean()
        auth_code = cleaned_data.get('auth_code')
        auth_name = cleaned_data.get('auth_name')

        print(cleaned_data)
        if auth_code is None:
            # 未通过 auth_code 验证
            return

        ui = UserInfo.objects.filter(reserver=True, auth_code=auth_code, auth_name=auth_name, user__is_active=True)
        if not ui.exists():
            raise ValidationError('学号和姓名不匹配', code='auth_code_not_exist')
        if not ui.first().user.has_perm('reserve.new'):
            raise ValidationError('该用户无权进行预约', code='auth_code_not_exist')


class ReserveTypeChooseForm(forms.Form):
    R_CHOICES = (
        (1, '学习辅导'),
        (2, '其他问题'),
    )
    r = forms.ChoiceField(choices=R_CHOICES, widget=forms.RadioSelect)
    T_CHOICES = (
        (1, '学导'),
        (2, '老师'),
    )
    t = forms.ChoiceField(choices=T_CHOICES, widget=forms.RadioSelect)


class ReserveTypeConfirmForm(forms.Form):
    """获取并验证要预约的话题种类"""
    type = forms.ChoiceField(label='预约种类')
    content = forms.CharField(max_length=10000, label='预约内容', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 6
    }))

    def get_type_choices(self):
        # TODO - 根据 user 返回
        types = ReserveType.objects.filter(enabled=True)
        if self.r is not None:
            types = types.filter(type=self.r)
        types = types.order_by('order')
        types = [(x.id, x.name) for x in types]
        return types

    def __init__(self, key_obj, *args, **kwargs):
        obj = key_obj
        self.auth_user = User.objects.get(id=obj.get('auth_user'))
        self.r = obj.get('r')

        super().__init__(*args, **kwargs)
        self.fields['type'].choices = self.get_type_choices()


class ReserveeSettingsForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['can_reserved', 'can_reserve_gender', 'short_intro', 'intro', 'can_reserve_type']
        widgets = {
            'can_reserve_gender': forms.RadioSelect(),
            'short_intro': forms.TextInput(attrs={'class': 'form-control'}),
            'intro': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'can_reserve_type': forms.SelectMultiple(
                attrs={'class': 'form-control chosen-select', 'data-placeholder': '请选择接受预约的种类（直接输入可搜索）'}),
        }
        help_texts = {
            'can_reserve_type': '在电脑上设置时可以搜索',
        }


class NewCanReserveTime(forms.ModelForm):
    class Meta:
        model = ReserveTime
        fields = ['date', 'start_time', 'end_time', 'max', 'reservee']


class NewCanReserveRepeatTime(forms.ModelForm):
    class Meta:
        model = RepeatReserveTime
        fields = ['repeat', 'start_time', 'end_time', 'max', 'reservee', 'loop_start', 'loop_end']
