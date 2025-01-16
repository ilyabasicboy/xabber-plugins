from django.db import models
from django.contrib.postgres.fields import ArrayField

from xabber_plugins.custom_auth.models import Developer
from xabber_plugins.validators import validate_slug
from xabber_plugins.utils import get_upload_release_folder, get_language_codes

import os


class Plugin(models.Model):

    class Meta:
        ordering = ['name']

    name = models.SlugField(
        unique=True,
        validators=[validate_slug]
    )
    display_name = models.TextField()
    developer = models.ForeignKey(
        Developer,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class PluginDescription(models.Model):
    description = models.TextField()
    language = models.CharField(
        max_length=10,
        choices=get_language_codes(),
    )
    default = models.BooleanField(
        default=False
    )
    plugin = models.ForeignKey(
        Plugin,
        related_name='descriptions',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.plugin.name} - {self.language}'


class Track(models.Model):
    name = models.TextField()
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.plugin.name} - {self.name}'


class Release(models.Model):

    class Meta:
        unique_together = ['plugin', 'version', 'track']
        ordering = ['version']

    version = models.TextField()
    xabber_server_versions = ArrayField(
        models.TextField(),
        blank=True,
        null=True
    )
    xmpp_server_versions = ArrayField(
        models.TextField(),
        blank=True,
        null=True
    )
    xabber_server_panel_versions = ArrayField(
        models.TextField(),
        blank=True,
        null=True
    )
    file = models.FileField(
        upload_to=get_upload_release_folder
    )
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE
    )
    verified = models.BooleanField(
        default=False
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.plugin.name} - {self.version}'

    @property
    def filename(self):
        return os.path.basename(self.file.name)