from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.views import LogoutView

from .models import Developer
from .forms import CustomAuthenticationForm


class DeveloperLoginView(LoginView):
    template_name = 'custom_auth/login.html'

    def get(self, request, *args, **kwargs):
        form = CustomAuthenticationForm()
        context = {
            'form': form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        next = request.POST.get('next')

        form = CustomAuthenticationForm(request.POST, request=request)

        if form.is_valid():
            login(request, form.user)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('plugins:plugin_list'))

        context = {
            'form': form
        }

        return self.render_to_response(context)


class DeveloperLogoutView(LogoutView):
    next_page = 'custom_auth:login'
