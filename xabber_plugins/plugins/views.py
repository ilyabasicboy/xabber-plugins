from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from xabber_plugins.plugins.models import Plugin, Release, Track, PluginDescription
from xabber_plugins.plugins.forms import PluginForm
from xabber_plugins.utils import validate_module, get_upload_release_folder

import re


class PluginListView(LoginRequiredMixin, TemplateView):
    template_name = 'plugins/index.html'

    def get(self, request, *args, **kwargs):
        self.developer = request.user
        plugin_list = Plugin.objects.filter(developer=self.developer)
        context = {
            'plugin_list': plugin_list
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.developer = request.user

        plugin_name = request.POST.get('name', '').strip()
        data = {
            'developer': self.developer,
            'name': plugin_name,
            'display_name': request.POST.get('display_name'),
        }
        plugin_form = PluginForm(data)

        if not Plugin.objects.filter(name=plugin_name).exists():
            if plugin_form.is_valid():
                plugin = plugin_form.save()
                messages.success(request, 'Plugin created successfully.')
                return HttpResponseRedirect(reverse('plugins:plugin_detail', kwargs={'plugin_name': plugin.name}))
            else:
                messages.error(request, 'Invalid form data.')
        else:
            messages.error(request, 'Plugin with this name already exists.')

        plugin_list = Plugin.objects.filter(developer=self.developer)
        context = {
            'plugin_list': plugin_list,
            'plugin_form': plugin_form,
        }
        return self.render_to_response(context)


class PluginDetail(LoginRequiredMixin, TemplateView):
    template_name = 'plugins/detail.html'

    def get(self, request, plugin_name, *args, **kwargs):
        developer = request.user
        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        context = {
            'plugin': plugin,
        }

        return self.render_to_response(context)


class PluginDelete(LoginRequiredMixin, View):

    def get(self, request, plugin_name, *args, **kwargs):
        developer = request.user
        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        plugin.delete()
        messages.success(request, 'Plugin deleted successfully.')
        return HttpResponseRedirect(reverse('plugins:plugin_list'))


class PluginDescriptionList(LoginRequiredMixin, TemplateView):
    template_name = 'plugins/description_list.html'

    def get(self, request, plugin_name, *args, **kwargs):
        developer = request.user
        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        context = {
            'plugin': plugin,
        }
        return self.render_to_response(context)


class AddPluginDescription(LoginRequiredMixin, View):

    def post(self, request, plugin_name, *args, **kwargs):
        developer = request.user

        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        description = request.POST.get('description').strip()
        default = request.POST.get('default')
        language = request.POST.get('language', '').strip().lower()

        if PluginDescription.objects.filter(plugin=plugin, language=language).exists():
            messages.error(request, 'Description with this language code already exists')
        else:
            PluginDescription.objects.create(
                language=language,
                description=description,
                plugin=plugin,
                default=True if default else False,
            )
            messages.success(request, 'Description added successfully.')

        return HttpResponseRedirect(reverse('plugins:description_list', kwargs={'plugin_name': plugin.name}))


class DeletePluginDescription(LoginRequiredMixin, View):

    def get(self, request, plugin_name, description_id, *args, **kwargs):
        developer = request.user

        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        try:
            description = PluginDescription.objects.get(
                id=description_id,
                plugin=plugin
            )
        except PluginDescription.DoesNotExist:
            raise Http404

        description.delete()
        messages.success(request, 'Description deleted successfully.')

        return HttpResponseRedirect(reverse('plugins:description_list', kwargs={'plugin_name': plugin.name}))


class ReleaseList(LoginRequiredMixin, TemplateView):
    template_name = 'plugins/release_list.html'

    def get(self, request, plugin_name, *args, **kwargs):
        developer = request.user
        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        release_list = plugin.release_set.all()

        context = {
            'plugin': plugin,
            'release_list': release_list,
        }

        return self.render_to_response(context)


class ReleaseDetail(LoginRequiredMixin, TemplateView):
    template_name = 'plugins/release_detail.html'

    def get(self, request, plugin_name, release_id, *args, **kwargs):
        developer = request.user
        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        try:
            release = plugin.release_set.get(id=release_id)
        except Release.DoesNotExist:
            raise Http404

        context = {
            'plugin': plugin,
            'release': release,
        }

        return self.render_to_response(context)

    def post(self, request, plugin_name, release_id, *args, **kwargs):
        developer = request.user

        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        try:
            release = plugin.release_set.get(id=release_id)
        except Release.DoesNotExist:
            raise Http404

        track = request.POST.get('track')
        track_obj, created = Track.objects.get_or_create(
            name=track,
            plugin=plugin
        )

        file = request.FILES.get('file')

        xabber_server_versions = request.POST.get('xabber_server_versions')
        xabber_server_versions = [v for v in re.split(r'[;, ]+', xabber_server_versions) if v]

        xmpp_server_versions = request.POST.get('xmpp_server_versions')
        xmpp_server_versions = [v for v in re.split(r'[;, ]+', xmpp_server_versions) if v]

        xabber_server_panel_versions = request.POST.get('xabber_server_panel_versions')
        xabber_server_panel_versions = [v for v in re.split(r'[;, ]+', xabber_server_panel_versions) if v]

        version = request.POST.get('version')
        verified = request.POST.get('verified')

        if Release.objects.filter(track=track_obj, plugin=plugin, version=version).exclude(id=release_id).exists():
            messages.error(request, 'This release version already exists.')
        elif Release.objects.filter(file__contains=file.name, plugin=plugin).exclude(id=release_id).exists():
            messages.error(request, 'This archive already exists.')
        else:
            release.version = version
            release.verified = True if verified else False
            release.track = track_obj
            release.plugin = plugin
            release.xabber_server_versions = xabber_server_versions
            release.xmpp_server_versions = xmpp_server_versions
            release.xabber_server_panel_versions = xabber_server_panel_versions
            messages.success(request, 'Release changed successfully.')

            if file:
                validated = validate_module(file, plugin.name)
                if validated:
                    release.file = file
                else:
                    messages.error(request, 'Module archive is incorrect.')

            release.save()

        context = {
            'plugin': plugin,
            'release': release,
        }

        return self.render_to_response(context)


class ReleaseCreate(LoginRequiredMixin, View):

    def post(self, request, plugin_name, *args, **kwargs):
        developer = request.user

        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        file = request.FILES.get('file')
        validated = validate_module(file, plugin.name)

        track = request.POST.get('track')
        track_obj, created = Track.objects.get_or_create(
            name=track,
            plugin=plugin
        )

        xabber_server_versions = request.POST.get('xabber_server_versions')
        xabber_server_versions = [v for v in re.split(r'[;, ]+', xabber_server_versions) if v]

        xmpp_server_versions = request.POST.get('xmpp_server_versions')
        xmpp_server_versions = [v for v in re.split(r'[;, ]+', xmpp_server_versions) if v]

        xabber_server_panel_versions = request.POST.get('xabber_server_panel_versions')
        xabber_server_panel_versions = [v for v in re.split(r'[;, ]+', xabber_server_panel_versions) if v]
        print(file.name)
        version = request.POST.get('version')

        if Release.objects.filter(track=track_obj, plugin=plugin, version=version).exists():
            messages.error(request, 'This release version already exists.')
        elif Release.objects.filter(file__contains=file.name, plugin=plugin).exists():
            messages.error(request, 'This archive already exists.')
        elif validated:
            release = Release.objects.create(
                version=version,
                track=track_obj,
                plugin=plugin,
                xabber_server_versions=xabber_server_versions,
                xmpp_server_versions=xmpp_server_versions,
                xabber_server_panel_versions=xabber_server_panel_versions,
                file=file
            )
            messages.success(request, 'Release created successfully.')
            return HttpResponseRedirect(reverse('plugins:release_detail', kwargs={'plugin_name': plugin.name, 'release_id': release.id}))
        else:
            messages.error(request, 'Module archive is incorrect.')

        return HttpResponseRedirect(reverse('plugins:release_list', kwargs={'plugin_name': plugin.name}))


class ReleaseDelete(LoginRequiredMixin, View):

    def get(self, request, plugin_name, release_id, *args, **kwargs):
        developer = request.user

        try:
            plugin = Plugin.objects.get(
                developer=developer,
                name=plugin_name
            )
        except Plugin.DoesNotExist:
            raise Http404

        try:
            release = Release.objects.get(id=release_id, plugin__developer=developer)
        except Release.DoesNotExist:
            raise Http404

        release.delete()

        messages.success(request, 'Release deleted successfully.')

        return HttpResponseRedirect(reverse('plugins:release_list', kwargs={'plugin_name': plugin.name}))