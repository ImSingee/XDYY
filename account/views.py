from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic.base import View
from django.contrib import messages
from django.contrib.auth import logout
from .forms import LoginForm
from .utils import UserSettings


# Create your views here.
class LoginView(View):
    template_name = 'account/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            UserSettings().login(request, username, password)
            next = request.GET.get('next', reverse('refresh'))
            return redirect(next)
        else:
            messages.error(request, '请输入正确的用户名和密码，并且请注意他们都是区分大小写的。')
            return redirect(reverse('account:login'))


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('refresh'))
