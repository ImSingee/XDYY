from django.shortcuts import render
from django.urls.base import reverse
from django.views.generic.base import TemplateView, RedirectView


# Create your views here.

class IndexView(RedirectView):
    pattern_name = 'dashboard:index'

class RefreshView(TemplateView):
    template_name = 'base/refresh_parent.html'

