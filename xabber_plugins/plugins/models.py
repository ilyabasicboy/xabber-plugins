from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils.text import slugify

from xabber_plugins.custom_auth.models import Developer
from xabber_plugins.validators import validate_slug

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


class PluginDescription(models.Model):
    description = models.TextField()
    language = models.TextField()
    plugin = models.ForeignKey(
        Plugin,
        related_name='descriptions',
        on_delete=models.CASCADE
    )


class Track(models.Model):
    name = models.TextField()
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE,
    )


def get_upload_release_folder(instance, filename):
    plugin_name = slugify(instance.plugin.name)
    return os.path.join(settings.RELEASE_UPLOAD_FOLDER, plugin_name, filename)


class Release(models.Model):

    class Meta:
        unique_together = ['plugin', 'version', 'track']

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
