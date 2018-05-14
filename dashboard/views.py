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
        index = request.GET.get('index', reverse('dashboard:indexR'))
        self.extra_context.update({'index': index})
        return super().get(request, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        from .models import Menu
        super().__init__(*args, **kwargs)
        menus = list(Menu.objects.all())
        ms = []
        for menu in menus:
            if menu.top:
                ms.append(menu)
        ms = [x for x in ms if x.show]
        ms.sort(key=lambda x: x.order)
        for m in ms:
            if not m.single:
                setattr(m, 'child', [x for x in m.children.all() if x.show])
                m.child.sort(key=lambda x: x.order)
        self.extra_context = {'menu': ms}
