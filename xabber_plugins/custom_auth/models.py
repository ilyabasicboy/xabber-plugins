from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.apps import apps
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.conf import settings
from django.shortcuts import reverse

from datetime import timedelta

import uuid
import os


class DeveloperManager(UserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)

        # Create the Email object for the developer
        developer_email = Email.objects.create(
            email=email,
            verified=False,
            developer=user
        )

        developer_email.send_verification_key()

        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class Developer(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    contacts = models.TextField(
        blank=True,
        null=True
    )
    site = models.TextField(
        blank=True,
        null=True
    )

    objects = DeveloperManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email.email = self.__class__.objects.normalize_email(self.email.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email.email], **kwargs)


class Email(models.Model):

    email = models.EmailField(_('email address'), unique=True)
    verified = models.BooleanField(
        default=False
    )
    developer = models.OneToOneField(
        Developer,
        on_delete=models.CASCADE,
        related_name='email'
    )

    def send_verification_key(self):

        # Delete previous verification keys
        self.emailverificationkey_set.all().delete()

        # Generate the verification key for the email
        verification_key = EmailVerificationKey.objects.create(
            email=self,
            key=uuid.uuid4(),
            expires=timezone.now() + timedelta(hours=settings.VERIFICATION_KEY_EXPIRES)
        )

        verification_url = os.path.join(
            settings.SITE_URL,
            reverse('custom_auth:email_verification', kwargs={'key': verification_key.key})
        )

        try:
            send_mail(
                'Verify Your Email Address',
                f'Please click the following link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [self.email]
            )
        except Exception as e:
            print(e)


class EmailVerificationKey(models.Model):

    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE
    )
    expires = models.DateTimeField()

    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)