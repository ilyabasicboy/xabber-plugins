from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, View
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages

from .models import Developer, EmailVerificationKey
from .forms import CustomAuthenticationForm, RegisterForm


class DeveloperLoginView(LoginView):
    template_name = 'custom_auth/login.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('plugins:plugin_list'))

        form = CustomAuthenticationForm()
        context = {
            'form': form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        next = request.POST.get('next')

        form = CustomAuthenticationForm(request.POST, request=request)

        if form.is_valid():

            if form.user.email.verified:
                login(request, form.user)
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse('plugins:plugin_list'))
            else:
                return HttpResponseRedirect(reverse('custom_auth:email_not_verified', kwargs={'user_id': form.user.id}))

        context = {
            'form': form
        }

        return self.render_to_response(context)


class DeveloperLogoutView(LogoutView):
    next_page = 'custom_auth:login'


class RegistrationView(TemplateView):
    template_name = 'custom_auth/registration.html'

    def get(self, request, *args, **kwargs):
        registration_form = RegisterForm()
        context = {'registration_form': registration_form}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        registration_form = RegisterForm(request.POST)

        if registration_form.is_valid():
            try:
                developer = Developer.objects.create_user(
                    username=registration_form.cleaned_data.get('username'),
                    email=registration_form.cleaned_data.get('email'),
                    password=registration_form.cleaned_data.get('password'),
                )
                messages.success(request, 'Registration is complete. A confirmation email has been sent to your email address.')
                return HttpResponseRedirect(reverse('custom_auth:login'))
            except IntegrityError:
                registration_form.add_error('username', 'Developer with this username/email already exists.')

        context = {'registration_form': registration_form}
        return self.render_to_response(context)


class VerifyEmail(View):

    def get(self, request, key, *args, **kwargs):

        try:
            verification_key = EmailVerificationKey.objects.get(key=key)
        except EmailVerificationKey.DoesNotExist:
            messages.error(request, "Invalid verification key.")
            return HttpResponseRedirect(reverse('custom_auth:login'))

        # Check if the key has expired
        if verification_key.expires < timezone.now():
            messages.error(request, "Verification key has expired.")
            return HttpResponseRedirect(reverse('custom_auth:login'))

        # Mark the email as verified
        email = verification_key.email
        email.verified = True
        email.save()

        login(request, email.developer)

        # Optionally, delete the verification key after use
        verification_key.delete()

        messages.success(request, 'Email verified successfully.')

        return HttpResponseRedirect(reverse('plugins:plugin_list'))


class EmailNotVerified(TemplateView):
    template_name = 'custom_auth/verify_email.html'

    def get(self, request, user_id, *args, **kwargs):

        try:
            developer = Developer.objects.get(id=user_id)
        except Developer.DoesNotExist:
            return Http404

        context = {'developer': developer}
        return self.render_to_response(context)


class ResendVerificationCode(View):

    def get(self, request, user_id, *args, **kwargs):

        try:
            developer = Developer.objects.get(id=user_id)
        except Developer.DoesNotExist:
            return Http404

        developer.email.send_verification_key()

        messages.success(request, 'A confirmation email has been sent to your email address.')
        return HttpResponseRedirect(reverse('custom_auth:login'))