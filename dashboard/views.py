from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import TemplateView, View, RedirectView


class TestView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, World!')


class EmptyView(TemplateView):
    template_name = 'base.html'


class IndexRView(RedirectView):
    pattern_name = 'reserve:user_auth'


class IndexView(TemplateView):
    template_name = 'dashboard/index.html'

    def get(self, request, *args, **kwargs):
        from .models import Menu

        menus = list(Menu.objects.filter(show=True))
        ms = []

        for menu in menus:
            if menu.top:
                if not menu.auth:
                    ms.append(menu)
                else:
                    if menu.auth == 'is_staff':
                        if request.user.is_staff:
                            ms.append(menu)
                    elif menu.auth == 'is_authenticated':
                        if request.user.is_authenticated:
                            ms.append(menu)
                    elif menu.auth == 'is_reserver':
                        if request.user.is_authenticated and request.user.userinfo.reserver:
                            ms.append(menu)
                    elif menu.auth == 'is_reservee':
                        if request.user.is_authenticated and request.user.userinfo.reservee:
                            ms.append(menu)

        ms.sort(key=lambda x: x.order)
        for m in ms:
            if not m.single:
                setattr(m, 'child', [x for x in m.children.all() if x.show])
                m.child.sort(key=lambda x: x.order)
        self.extra_context = {'menu': ms}
        index = request.GET.get('index', reverse('dashboard:indexR'))
        self.extra_context.update({'index': index})
        return super().get(request, *args, **kwargs)
