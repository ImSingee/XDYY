from django.http import Http404
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from wechat.utils import get_bind_qrcode


class WeChatImageView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            raise Http404

        return redirect(get_bind_qrcode(request.user))


class BindView(TemplateView):
    template_name = 'wechat/bind.html'
