from django.db.models.signals import post_delete
from django.dispatch import receiver

from xabber_plugins.plugins.models import Release


@receiver(post_delete, sender=Release)
def release_file_post_delete(*args, **kwargs):

    """ Delete files from storage"""

    release_file = kwargs.get('instance')
    if release_file.file.storage.exists(release_file.file.name):
        release_file.file.storage.delete(release_file.file.name)